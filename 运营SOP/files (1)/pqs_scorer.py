"""
Amazon PQS (Promotion Quality Score) 打分系统
================================================
基于 Amazon Vendor/Selling Partner Support 官方工单 (Case ID 12895480832) 复刻。

顶层公式（官方明确公开）：
    PQS = 71% x Listing Quality
        + 19% x Brand Metrics
        + 10% x Competitive Pricing (Product Promotion)

⚠️ 板块内部子指标权重亚马逊未公开，本文件中的子权重为工程化假设，
   详见同目录 PQS算法详解.md 第三~五节说明，使用前请结合实际后台
   PQS表现进行校准（可通过 PQS_SUB_WEIGHTS 常量直接调整）。

设计原则：Listing Quality 中的 IDQ（图片/A+/五点/关键词）与CDQ体系
共享同一份数据资产，因此本模块直接复用 cdq_scorer.py 中已验证的
score_image_quality / score_aplus / score_bullet_points 函数，
保证CDQ与PQS两套分数在listing质量维度口径一致。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cdq_scorer import (
    ImageInput,
    APlusInput,
    BulletPointsInput,
    score_image_quality,
    score_aplus,
    score_bullet_points,
    DimensionResult,
)
from weights_loader import load_group


# ---------------------------------------------------------------------------
# 顶层权重（官方公开，精确值）
# ---------------------------------------------------------------------------

TOP_LEVEL_WEIGHTS = {
    "listing_quality": 0.71,
    "brand_metrics": 0.19,
    "competitive_pricing": 0.10,
}

# 板块内部子权重（⚙️工程假设，可按实际情况调整）
# 若同目录存在 calibrated_weights.json（由 calibrate_weights.py 回归生成），
# 会自动覆盖下方默认值；未校准时使用下方硬编码默认值。
_DEFAULT_PQS_SUB_WEIGHTS = {
    "listing_quality": {
        "idq": 0.35,            # 图片+A+内容+五点+关键词
        "glance_views": 0.25,   # 曝光量增长
        "reviews_ratings": 0.25,  # 评论数量+评分
        "sales_trend": 0.15,    # 近30天销售额增长
    },
    "competitive_pricing": {
        "discount_depth": 0.60,   # 相对品类均价折扣深度
        "price_uniqueness": 0.40, # 相对近90天非促销价的稀缺性/最低价
    },
    "brand_metrics": {
        "ops_growth": 0.40,          # 品牌OPS增长
        "customer_growth": 0.30,     # 客户群体扩展
        "review_growth": 0.30,       # 品牌全系列评论增长
    },
}
PQS_SUB_WEIGHTS = {
    group: load_group(f"pqs.sub_weights.{group}", default)
    for group, default in _DEFAULT_PQS_SUB_WEIGHTS.items()
}

# IDQ内部权重（图片/A+/五点/关键词），⚙️工程假设，与CDQ权重呼应但非等同
IDQ_SUB_WEIGHTS = load_group("pqs.idq_sub_weights", {
    "image": 0.35,
    "aplus": 0.20,
    "bullets": 0.20,
    "keywords": 0.25,
})


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def growth_to_score(current: float, prior: float, saturation_growth: float = 0.5) -> float:
    """
    统一的“增长率 -> 0-1分数”映射模型：
      增长率=0        -> 0.5（持平为基准分）
      增长率=饱和增长率 -> 1.0（默认50%，可调）
      增长率=-饱和增长率 -> 0.0
    """
    if prior <= 0:
        return 1.0 if current > 0 else 0.5
    growth = (current - prior) / prior
    score = 0.5 + 0.5 * (growth / saturation_growth)
    return clamp(score)


# ---------------------------------------------------------------------------
# 1. Listing Quality (71%) 子模块
# ---------------------------------------------------------------------------

@dataclass
class KeywordCoverageInput:
    covered_keywords: int
    target_keywords: int  # 品类核心关键词总数（如DART/关键词工具输出的目标词表）


def score_keyword_coverage(inp: KeywordCoverageInput) -> DimensionResult:
    ratio = clamp(inp.covered_keywords / inp.target_keywords) if inp.target_keywords else 0.0
    suggestions = []
    if ratio < 1.0:
        suggestions.append(f"关键词覆盖率{ratio:.0%}，建议补充剩余{inp.target_keywords - inp.covered_keywords}个核心词到属性/五点/A+中")
    return DimensionResult(
        name="关键词覆盖",
        raw_score=ratio,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={"covered": inp.covered_keywords, "target": inp.target_keywords},
    )


@dataclass
class IDQInput:
    image: ImageInput
    aplus: APlusInput
    bullets: BulletPointsInput
    keywords: KeywordCoverageInput


def score_idq(inp: IDQInput) -> DimensionResult:
    image_r = score_image_quality(inp.image)
    aplus_r = score_aplus(inp.aplus)
    bullets_r = score_bullet_points(inp.bullets)
    keywords_r = score_keyword_coverage(inp.keywords)

    sub_results = {
        "image": image_r,
        "aplus": aplus_r,
        "bullets": bullets_r,
        "keywords": keywords_r,
    }
    raw_score = sum(sub_results[k].raw_score * w for k, w in IDQ_SUB_WEIGHTS.items())

    defects = []
    suggestions = []
    for key, r in sub_results.items():
        defects.extend(f"[{r.name}] {d}" for d in r.defects)
        suggestions.extend(f"[{r.name}] {s}" for s in r.suggestions)

    return DimensionResult(
        name="IDQ (Image and Detail Quality)",
        raw_score=round(raw_score, 4),
        weight=0.0,
        weighted_score=0.0,
        defects=defects,
        suggestions=suggestions,
        details={k: r.raw_score for k, r in sub_results.items()},
    )


@dataclass
class GlanceViewsInput:
    current_per_100k: float  # 当前周期 Glance Views per 100k customers
    prior_per_100k: float


def score_glance_views(inp: GlanceViewsInput) -> DimensionResult:
    raw_score = growth_to_score(inp.current_per_100k, inp.prior_per_100k)
    suggestions = []
    if raw_score < 0.5:
        suggestions.append("Glance Views呈下降趋势，检查搜索排名/广告曝光/类目节点是否正确")
    elif raw_score < 0.7:
        suggestions.append("加大搜索广告投放或优化标题/关键词覆盖以提升曝光")
    return DimensionResult(
        name="Glance Views 增长",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={"current": inp.current_per_100k, "prior": inp.prior_per_100k},
    )


@dataclass
class ReviewsRatingsInput:
    review_count_current: int
    review_count_prior: int
    rating_current: float       # 0-5
    rating_prior: float = 0.0


def score_reviews_ratings(inp: ReviewsRatingsInput) -> DimensionResult:
    count_growth_score = growth_to_score(inp.review_count_current, inp.review_count_prior, saturation_growth=0.3)
    rating_abs_score = clamp((inp.rating_current - 3.0) / 2.0)  # 3.0星=0分，5.0星=满分
    rating_trend_score = 0.5
    if inp.rating_prior > 0:
        rating_trend_score = clamp(0.5 + (inp.rating_current - inp.rating_prior) * 2)

    raw_score = round(0.5 * count_growth_score + 0.3 * rating_abs_score + 0.2 * rating_trend_score, 4)

    suggestions = []
    if inp.rating_current < 4.0:
        suggestions.append(f"当前评分{inp.rating_current}偏低，优先排查差评根因（质量/物流/说明书）")
    if count_growth_score < 0.5:
        suggestions.append("评论增速放缓，考虑Vine/索评邮件合规触达提升评论增量")

    return DimensionResult(
        name="评论与评分 (Reviews & Ratings)",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={
            "review_count_current": inp.review_count_current,
            "review_count_prior": inp.review_count_prior,
            "rating_current": inp.rating_current,
        },
    )


@dataclass
class SalesTrendInput:
    trailing_30d_sales: float
    prior_30d_sales: float


def score_sales_trend(inp: SalesTrendInput) -> DimensionResult:
    raw_score = growth_to_score(inp.trailing_30d_sales, inp.prior_30d_sales, saturation_growth=0.3)
    suggestions = []
    if raw_score < 0.5:
        suggestions.append("近30天销售额下滑，检查库存/转化率/价格竞争力")
    return DimensionResult(
        name="近30天销售额趋势",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={"trailing_30d": inp.trailing_30d_sales, "prior_30d": inp.prior_30d_sales},
    )


def score_listing_quality(
    idq: IDQInput,
    glance_views: GlanceViewsInput,
    reviews_ratings: ReviewsRatingsInput,
    sales_trend: SalesTrendInput,
) -> DimensionResult:
    sub = {
        "idq": score_idq(idq),
        "glance_views": score_glance_views(glance_views),
        "reviews_ratings": score_reviews_ratings(reviews_ratings),
        "sales_trend": score_sales_trend(sales_trend),
    }
    weights = PQS_SUB_WEIGHTS["listing_quality"]
    raw_score = sum(sub[k].raw_score * w for k, w in weights.items())

    defects, suggestions = [], []
    for key, r in sub.items():
        defects.extend(f"[{r.name}] {d}" for d in r.defects)
        suggestions.extend(f"[{r.name}] {s}" for s in r.suggestions)

    return DimensionResult(
        name="Listing Quality",
        raw_score=round(raw_score, 4),
        weight=0.0,
        weighted_score=0.0,
        defects=defects,
        suggestions=suggestions,
        details={k: v.raw_score for k, v in sub.items()},
    )


# ---------------------------------------------------------------------------
# 2. Competitive Pricing (10%) 子模块
# ---------------------------------------------------------------------------

@dataclass
class PricingInput:
    current_price: float
    category_avg_price: float
    category_avg_discount_pct: float  # 品类平均折扣力度 0-1
    current_discount_pct: float       # 当前折扣力度 0-1
    recent_90d_non_promo_min_price: float  # 近90天非促销最低价


def score_competitive_pricing(inp: PricingInput) -> DimensionResult:
    # 折扣深度：当前折扣相对品类均值折扣的领先幅度
    if inp.category_avg_discount_pct > 0:
        discount_ratio = inp.current_discount_pct / inp.category_avg_discount_pct
    else:
        discount_ratio = 1.0 if inp.current_discount_pct > 0 else 0.5
    discount_depth_score = clamp(discount_ratio / 1.5)  # 1.5倍品类均值折扣视为满分

    # 价格稀缺性：当前价是否为近90天非促销最低价
    if inp.recent_90d_non_promo_min_price > 0:
        price_uniqueness_score = clamp(
            1.0 - (inp.current_price - inp.recent_90d_non_promo_min_price)
            / inp.recent_90d_non_promo_min_price
        )
    else:
        price_uniqueness_score = 0.5

    weights = PQS_SUB_WEIGHTS["competitive_pricing"]
    raw_score = round(
        discount_depth_score * weights["discount_depth"]
        + price_uniqueness_score * weights["price_uniqueness"],
        4,
    )

    suggestions = []
    if discount_depth_score < 0.5:
        suggestions.append("当前折扣力度低于品类平均，可评估提升促销深度（需结合利润率）")
    if price_uniqueness_score < 0.5:
        suggestions.append("当前价格高于近90天非促销最低价，稀缺性不足")

    return DimensionResult(
        name="Competitive Pricing",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={
            "discount_depth_score": discount_depth_score,
            "price_uniqueness_score": price_uniqueness_score,
        },
    )


# ---------------------------------------------------------------------------
# 3. Brand Metrics (19%) 子模块
# ---------------------------------------------------------------------------

@dataclass
class BrandMetricsInput:
    brand_ops_current: float
    brand_ops_prior: float
    unique_customers_current: int
    unique_customers_prior: int
    brand_review_count_current: int
    brand_review_count_prior: int


def score_brand_metrics(inp: BrandMetricsInput) -> DimensionResult:
    ops_score = growth_to_score(inp.brand_ops_current, inp.brand_ops_prior, saturation_growth=0.3)
    customer_score = growth_to_score(
        inp.unique_customers_current, inp.unique_customers_prior, saturation_growth=0.3
    )
    review_score = growth_to_score(
        inp.brand_review_count_current, inp.brand_review_count_prior, saturation_growth=0.3
    )

    weights = PQS_SUB_WEIGHTS["brand_metrics"]
    raw_score = round(
        ops_score * weights["ops_growth"]
        + customer_score * weights["customer_growth"]
        + review_score * weights["review_growth"],
        4,
    )

    suggestions = []
    if ops_score < 0.5:
        suggestions.append("品牌OPS增速放缓，检查全品牌矩阵内主力SKU库存与转化")
    if customer_score < 0.5:
        suggestions.append("品牌独立购买客户数增长不足，考虑拓展新品/联合营销扩大触达")
    if review_score < 0.5:
        suggestions.append("品牌全系列评论增速偏低，统筹全品牌索评节奏")

    return DimensionResult(
        name="Brand Metrics",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={
            "ops_score": ops_score,
            "customer_score": customer_score,
            "review_score": review_score,
        },
    )


# ---------------------------------------------------------------------------
# 聚合器：PQS Scorer
# ---------------------------------------------------------------------------

@dataclass
class PQSScoreReport:
    asin: str
    total_score: float  # 0-100
    tier: str
    dimensions: dict[str, DimensionResult]
    top_priority_actions: list[str]


def tier_from_score(total_score: float) -> str:
    """
    ⚠️ 亚马逊未公开PQS的等级分档标准，此处按四分位数给出方向性分层，
    仅供内部优先级参考，不代表官方认证等级（不同于CDQ的A++~U，那是官方给出的）。
    """
    if total_score >= 85:
        return "优秀 (Excellent)"
    if total_score >= 70:
        return "良好 (Good)"
    if total_score >= 50:
        return "一般 (Fair)"
    return "待改善 (Needs Improvement)"


class PQSScorer:
    """PQS综合打分引擎：71% Listing Quality + 19% Brand Metrics + 10% Competitive Pricing"""

    def score(
        self,
        asin: str,
        idq: IDQInput,
        glance_views: GlanceViewsInput,
        reviews_ratings: ReviewsRatingsInput,
        sales_trend: SalesTrendInput,
        pricing: PricingInput,
        brand: BrandMetricsInput,
    ) -> PQSScoreReport:
        listing_quality_result = score_listing_quality(idq, glance_views, reviews_ratings, sales_trend)
        pricing_result = score_competitive_pricing(pricing)
        brand_result = score_brand_metrics(brand)

        dimensions = {
            "listing_quality": listing_quality_result,
            "brand_metrics": brand_result,
            "competitive_pricing": pricing_result,
        }

        total_score = 0.0
        for key, result in dimensions.items():
            w = TOP_LEVEL_WEIGHTS[key]
            result.weight = w
            result.weighted_score = round(result.raw_score * w * 100, 2)
            total_score += result.weighted_score
        total_score = round(total_score, 2)

        loss_ranked = sorted(
            dimensions.values(),
            key=lambda r: r.weight * (1 - r.raw_score),
            reverse=True,
        )
        top_priority_actions = []
        for r in loss_ranked:
            if r.suggestions:
                top_priority_actions.append(f"[{r.name}] {r.suggestions[0]}")
            if len(top_priority_actions) >= 5:
                break

        return PQSScoreReport(
            asin=asin,
            total_score=total_score,
            tier=tier_from_score(total_score),
            dimensions=dimensions,
            top_priority_actions=top_priority_actions,
        )


def print_report(report: PQSScoreReport) -> None:
    print(f"\n========== PQS 打分报告：{report.asin} ==========")
    print(f"总分：{report.total_score} / 100  →  分层：{report.tier}")
    print("-" * 60)
    for key, r in report.dimensions.items():
        print(f"[{r.name}] 权重{r.weight*100:.2f}%  原始得分{r.raw_score:.2f}  计入总分{r.weighted_score}")
        if r.defects:
            print(f"   问题：{r.defects[:3]}")
    print("-" * 60)
    print("优先提升建议（按影响分值排序）：")
    for i, action in enumerate(report.top_priority_actions, 1):
        print(f"  {i}. {action}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# 示例运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scorer = PQSScorer()

    report = scorer.score(
        asin="B0GDCZ7XXX",
        idq=IDQInput(
            image=ImageInput(image_count=10, has_defects=False, iai_score=0.5),
            aplus=APlusInput(has_aplus=True),
            bullets=BulletPointsInput(bullets=[
                "Keeps drinks cold for 24 hours",
                "Leak-proof design",
                "BPA-free stainless steel",
            ]),
            keywords=KeywordCoverageInput(covered_keywords=18, target_keywords=25),
        ),
        glance_views=GlanceViewsInput(current_per_100k=1200, prior_per_100k=1000),
        reviews_ratings=ReviewsRatingsInput(
            review_count_current=340, review_count_prior=300, rating_current=4.4, rating_prior=4.3
        ),
        sales_trend=SalesTrendInput(trailing_30d_sales=52000, prior_30d_sales=48000),
        pricing=PricingInput(
            current_price=19.99,
            category_avg_price=22.50,
            category_avg_discount_pct=0.10,
            current_discount_pct=0.15,
            recent_90d_non_promo_min_price=21.99,
        ),
        brand=BrandMetricsInput(
            brand_ops_current=210000,
            brand_ops_prior=180000,
            unique_customers_current=15000,
            unique_customers_prior=13000,
            brand_review_count_current=2100,
            brand_review_count_prior=1900,
        ),
    )

    print_report(report)
