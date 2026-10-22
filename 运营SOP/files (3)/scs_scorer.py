"""
Amazon SCS (Sub Category Score) 打分系统
================================================
⚠️ 本系统无官方公开公式，是基于以下业务信号做的工程化建模：
  - 5类叶节点排行榜徽章（Best Sellers / Hot New Release / Movers & Shakers /
    Most Wished For / Gift Ideas）
  - 4类平台AI/信任标签（Amazon's Choice / 保留标签 / 特色品牌 / 气候友好承诺）
  - 类目结构精准度（叶节点选择）
  - 推荐算法信号（FBT / Compare Similar Items / Viewed Together / Rufus-Cosmos AI推荐 / 促销加持）

详见同目录 SCS算法详解.md。所有权重常量集中在 SCS_WEIGHTS，可直接调整校准。

架构说明：Rufus/Cosmos AI推荐信号直接复用 cdq_scorer.py 中
StructuredAttributesInput 的完整度数据（RAC Top 10 与CDQ结构化属性质量
是同一份底层数据），避免重复建模。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from cdq_scorer import DimensionResult, StructuredAttributesInput, score_structured_attributes
from weights_loader import load_group


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# 权重配置（⚙️全部为工程化假设，需用真实数据校准）
# ---------------------------------------------------------------------------

# 权重配置（⚙️全部为工程化假设，需用真实数据校准）
# 若同目录存在 calibrated_weights.json（由 calibrate_weights.py 回归生成），
# 会自动覆盖下方默认值；未校准时使用下方硬编码默认值。
SCS_WEIGHTS = load_group("scs.weights", {
    "ranking_badges": 0.40,       # A. 排行榜徽章
    "platform_badges": 0.35,      # B. 平台AI/信任标签
    "category_structure": 0.10,   # C. 类目结构精准度
    "recommendation_signals": 0.15,  # D. 推荐算法信号
})

RANKING_BADGE_SUB_WEIGHTS = load_group("scs.ranking_sub_weights", {
    "best_sellers": 0.30,
    "hot_new_release": 0.15,
    "movers_shakers": 0.15,
    "most_wished_for": 0.20,
    "gift_ideas": 0.20,
})

PLATFORM_BADGE_SUB_WEIGHTS = load_group("scs.platform_sub_weights", {
    "amazons_choice": 0.25,
    "customers_keep_item": 0.25,
    "featured_brand": 0.25,
    "climate_pledge_friendly": 0.25,
})

RECOMMENDATION_SUB_WEIGHTS = load_group("scs.recommendation_sub_weights", {
    "fbt": 0.20,
    "compare_similar": 0.20,
    "viewed_together": 0.20,
    "rufus_ai_recommended": 0.30,
    "promotion_boost": 0.10,
})

CDQ_BONUS_MAX_POINTS = 10  # SCS对CDQ的加分上限（⚙️需你自行验证叠加逻辑，见文档第五节）


# ---------------------------------------------------------------------------
# A. 排行榜徽章
# ---------------------------------------------------------------------------

@dataclass
class RankingBadgesInput:
    best_sellers_rank: Optional[int] = None      # 叶节点内排名，None=未上榜
    hot_new_release_rank: Optional[int] = None
    movers_shakers_rank: Optional[int] = None
    most_wished_for_rank: Optional[int] = None
    gift_ideas_rank: Optional[int] = None
    max_rank_shown: int = 100  # 榜单通常展示Top 100


def _rank_to_score(rank: Optional[int], max_rank_shown: int) -> float:
    if rank is None or rank > max_rank_shown or rank < 1:
        return 0.0
    return clamp(1 - (rank - 1) / max_rank_shown)


def score_ranking_badges(inp: RankingBadgesInput) -> DimensionResult:
    sub_scores = {
        "best_sellers": _rank_to_score(inp.best_sellers_rank, inp.max_rank_shown),
        "hot_new_release": _rank_to_score(inp.hot_new_release_rank, inp.max_rank_shown),
        "movers_shakers": _rank_to_score(inp.movers_shakers_rank, inp.max_rank_shown),
        "most_wished_for": _rank_to_score(inp.most_wished_for_rank, inp.max_rank_shown),
        "gift_ideas": _rank_to_score(inp.gift_ideas_rank, inp.max_rank_shown),
    }
    raw_score = sum(sub_scores[k] * w for k, w in RANKING_BADGE_SUB_WEIGHTS.items())

    suggestions = []
    if sub_scores["best_sellers"] == 0:
        suggestions.append("未上榜Best Sellers，优先提升叶节点内销量排名（核心杠杆：转化率+曝光量）")
    if sub_scores["movers_shakers"] == 0:
        suggestions.append("可通过短期促销/秒杀集中拉升排名涨幅，冲击Movers & Shakers滚动榜")
    if sub_scores["most_wished_for"] == 0:
        suggestions.append("引导用户加入心愿单（收藏加购类广告位/落地页CTA）冲击Most Wished For")

    return DimensionResult(
        name="排行榜徽章",
        raw_score=round(raw_score, 4),
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details=sub_scores,
    )


# ---------------------------------------------------------------------------
# B. 平台AI/信任标签
# ---------------------------------------------------------------------------

@dataclass
class PlatformBadgesInput:
    has_amazons_choice: bool = False
    has_customers_keep_item: bool = False
    is_featured_brand: bool = False           # 是否已被官方授予该标签
    brand_review_count: int = 0                # 品牌层面评论数，用于核对达标门槛
    brand_positive_review_pct: float = 0.0     # 品牌层面好评率 0-1
    brand_recent_orders: int = 0                # 近期订单量
    has_climate_pledge_friendly: bool = False


FEATURED_BRAND_THRESHOLDS = load_group("scs.featured_brand_thresholds", {
    "min_review_count": 5000,
    "min_positive_pct": 0.92,
    "min_recent_orders": 10000,
})


def score_platform_badges(inp: PlatformBadgesInput) -> DimensionResult:
    # 特色品牌：若尚未被授予标签，但数据已达门槛，视为"待官方确认"给予部分分并提示
    meets_featured_brand_criteria = (
        inp.brand_review_count >= FEATURED_BRAND_THRESHOLDS["min_review_count"]
        and inp.brand_positive_review_pct >= FEATURED_BRAND_THRESHOLDS["min_positive_pct"]
        and inp.brand_recent_orders >= FEATURED_BRAND_THRESHOLDS["min_recent_orders"]
    )

    sub_scores = {
        "amazons_choice": 1.0 if inp.has_amazons_choice else 0.0,
        "customers_keep_item": 1.0 if inp.has_customers_keep_item else 0.0,
        "featured_brand": 1.0 if inp.is_featured_brand else (0.5 if meets_featured_brand_criteria else 0.0),
        "climate_pledge_friendly": 1.0 if inp.has_climate_pledge_friendly else 0.0,
    }
    raw_score = sum(sub_scores[k] * w for k, w in PLATFORM_BADGE_SUB_WEIGHTS.items())

    suggestions = []
    if not inp.has_amazons_choice:
        suggestions.append("Amazon's Choice基于评分/价格/库存/配送速度的搜索词级判定，优先保障FBA库存与Prime配送覆盖")
    if not inp.has_customers_keep_item:
        suggestions.append("排查退货率高的原因（尺寸/描述准确性/质量），降低退货率以获得保留标签")
    if not inp.is_featured_brand:
        if meets_featured_brand_criteria:
            suggestions.append("品牌数据已达特色品牌门槛（评论数/好评率/订单量），建议核实Brand Registry状态并联系客户经理确认")
        else:
            gap = []
            if inp.brand_review_count < FEATURED_BRAND_THRESHOLDS["min_review_count"]:
                gap.append(f"评论数缺口{FEATURED_BRAND_THRESHOLDS['min_review_count']-inp.brand_review_count}")
            if inp.brand_positive_review_pct < FEATURED_BRAND_THRESHOLDS["min_positive_pct"]:
                gap.append(f"好评率缺口{(FEATURED_BRAND_THRESHOLDS['min_positive_pct']-inp.brand_positive_review_pct):.1%}")
            if inp.brand_recent_orders < FEATURED_BRAND_THRESHOLDS["min_recent_orders"]:
                gap.append(f"订单量缺口{FEATURED_BRAND_THRESHOLDS['min_recent_orders']-inp.brand_recent_orders}")
            suggestions.append(f"距特色品牌门槛：{'; '.join(gap)}")
    if not inp.has_climate_pledge_friendly:
        suggestions.append("评估产品是否可申请第三方可持续认证以获得气候友好承诺标签")

    return DimensionResult(
        name="平台AI/信任标签",
        raw_score=round(raw_score, 4),
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={**sub_scores, "meets_featured_brand_criteria": meets_featured_brand_criteria},
    )


# ---------------------------------------------------------------------------
# C. 类目结构精准度
# ---------------------------------------------------------------------------

@dataclass
class CategoryStructureInput:
    l1_category: str = ""
    l2_category: str = ""
    leaf_node: str = ""
    has_correct_leaf_node: bool = True
    category_relevance_score: float = 1.0     # 0-1，叶节点与产品的相关性
    leaf_node_competing_asins: int = 0          # 叶节点内竞品ASIN数量，仅作决策参考，不直接拉分


def score_category_structure(inp: CategoryStructureInput) -> DimensionResult:
    raw_score = round(
        0.5 * (1.0 if inp.has_correct_leaf_node else 0.0)
        + 0.5 * clamp(inp.category_relevance_score),
        4,
    )
    suggestions = []
    if not inp.has_correct_leaf_node:
        suggestions.append("核对当前叶节点分类是否准确，错误分类会导致排行榜资格失效")
    if inp.category_relevance_score < 0.8:
        suggestions.append("叶节点相关性偏低，评估是否有更贴合产品定位的相邻叶节点")

    return DimensionResult(
        name="类目结构精准度",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={
            "category_path": f"{inp.l1_category} > {inp.l2_category} > {inp.leaf_node}",
            "leaf_node_competing_asins": inp.leaf_node_competing_asins,
        },
    )


# ---------------------------------------------------------------------------
# D. 推荐算法信号
# ---------------------------------------------------------------------------

@dataclass
class RecommendationSignalsInput:
    fbt_pairs_count: int = 0                    # 强关联FBT搭档数量
    fbt_saturation_count: int = 5                # 达到满分所需的搭档数量（⚙️假设）
    compare_similar_items_included: bool = False
    compare_similar_items_win_rate: float = 0.0   # 0-1，对比中胜出的属性占比估计
    viewed_together_inclusion_rate: float = 0.0   # 0-1，出现在"看了又看"模块的估计比例
    rufus_ai_recommended: bool = False
    structured_attrs_for_rufus: Optional[StructuredAttributesInput] = None  # 复用CDQ数据驱动
    active_promotions: dict[str, bool] = field(default_factory=dict)  # {"BD":True,"LD":False,...}


def score_recommendation_signals(inp: RecommendationSignalsInput) -> DimensionResult:
    fbt_score = clamp(inp.fbt_pairs_count / max(inp.fbt_saturation_count, 1))
    compare_score = (
        clamp(inp.compare_similar_items_win_rate) if inp.compare_similar_items_included else 0.0
    )
    viewed_score = clamp(inp.viewed_together_inclusion_rate)

    # Rufus/Cosmos AI推荐：若已明确获得标签给满分；否则用CDQ结构化属性完整度作为"资格接近度"的代理分
    rufus_detail = {}
    if inp.rufus_ai_recommended:
        rufus_score = 1.0
    elif inp.structured_attrs_for_rufus is not None:
        sa_result = score_structured_attributes(inp.structured_attrs_for_rufus)
        rufus_score = round(sa_result.raw_score * 0.7, 4)  # 未正式获标签，打七折作为"接近度"而非坐实分数
        rufus_detail = {"proxy_from_cdq_structured_attributes": sa_result.raw_score}
    else:
        rufus_score = 0.0

    promo_score = 1.0 if any(inp.active_promotions.values()) else 0.0

    sub_scores = {
        "fbt": fbt_score,
        "compare_similar": compare_score,
        "viewed_together": viewed_score,
        "rufus_ai_recommended": rufus_score,
        "promotion_boost": promo_score,
    }
    raw_score = sum(sub_scores[k] * w for k, w in RECOMMENDATION_SUB_WEIGHTS.items())

    suggestions = []
    if fbt_score < 0.5:
        suggestions.append("通过'买A加购B'广告或Virtual Bundles人为建立FBT强关联")
    if not inp.compare_similar_items_included:
        suggestions.append("检查是否进入Compare with similar items对比模块，必要时通过ASIN投放广告争夺该位置")
    if rufus_score < 0.7 and not inp.rufus_ai_recommended:
        suggestions.append("补全PT属性与RAC Top10（即CDQ结构化属性质量），提升Rufus/Cosmos的AI Recommended触发概率")
    if promo_score == 0:
        suggestions.append("评估参与BD/LD/DOTD等促销的可行性，短期拉升销售速度带动排名类徽章")

    return DimensionResult(
        name="推荐算法信号",
        raw_score=round(raw_score, 4),
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={**sub_scores, **rufus_detail, "active_promotions": inp.active_promotions},
    )


# ---------------------------------------------------------------------------
# 聚合器：SCS Scorer
# ---------------------------------------------------------------------------

@dataclass
class SCSScoreReport:
    asin: str
    total_score: float  # 0-100
    cdq_bonus_points: float  # 0-10，可选叠加到CDQ的加分（需自行验证叠加逻辑）
    dimensions: dict[str, DimensionResult]
    top_priority_actions: list[str]


def to_cdq_bonus(total_score: float) -> float:
    """SCS总分(0-100) -> CDQ加分(0-10)。⚙️叠加逻辑未经官方确认，见文档第五节。"""
    return round(clamp(total_score / 100) * CDQ_BONUS_MAX_POINTS, 2)


class SCSScorer:
    """SCS综合打分引擎：40%排行榜徽章 + 35%平台标签 + 10%类目结构 + 15%推荐信号"""

    def score(
        self,
        asin: str,
        ranking_badges: RankingBadgesInput,
        platform_badges: PlatformBadgesInput,
        category_structure: CategoryStructureInput,
        recommendation_signals: RecommendationSignalsInput,
    ) -> SCSScoreReport:
        dimensions = {
            "ranking_badges": score_ranking_badges(ranking_badges),
            "platform_badges": score_platform_badges(platform_badges),
            "category_structure": score_category_structure(category_structure),
            "recommendation_signals": score_recommendation_signals(recommendation_signals),
        }

        total_score = 0.0
        for key, result in dimensions.items():
            w = SCS_WEIGHTS[key]
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

        return SCSScoreReport(
            asin=asin,
            total_score=total_score,
            cdq_bonus_points=to_cdq_bonus(total_score),
            dimensions=dimensions,
            top_priority_actions=top_priority_actions,
        )


def print_report(report: SCSScoreReport) -> None:
    print(f"\n========== SCS 打分报告：{report.asin} ==========")
    print(f"总分：{report.total_score} / 100  （可选CDQ加分：+{report.cdq_bonus_points} / 10，需自行验证叠加逻辑）")
    print("-" * 60)
    for key, r in report.dimensions.items():
        print(f"[{r.name}] 权重{r.weight*100:.2f}%  原始得分{r.raw_score:.2f}  计入总分{r.weighted_score}")
    print("-" * 60)
    print("优先提升建议（按影响分值排序）：")
    for i, action in enumerate(report.top_priority_actions, 1):
        print(f"  {i}. {action}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# 示例运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scorer = SCSScorer()

    report = scorer.score(
        asin="B0GDCZ7XXX",
        ranking_badges=RankingBadgesInput(
            best_sellers_rank=None,
            hot_new_release_rank=12,
            movers_shakers_rank=None,
            most_wished_for_rank=45,
            gift_ideas_rank=None,
        ),
        platform_badges=PlatformBadgesInput(
            has_amazons_choice=True,
            has_customers_keep_item=False,
            is_featured_brand=False,
            brand_review_count=4200,
            brand_positive_review_pct=0.93,
            brand_recent_orders=8500,
            has_climate_pledge_friendly=False,
        ),
        category_structure=CategoryStructureInput(
            l1_category="Home & Kitchen",
            l2_category="Vacuum Cleaners & Floor Care",
            leaf_node="Electric Brooms",
            has_correct_leaf_node=True,
            category_relevance_score=0.95,
            leaf_node_competing_asins=1200,
        ),
        recommendation_signals=RecommendationSignalsInput(
            fbt_pairs_count=2,
            compare_similar_items_included=True,
            compare_similar_items_win_rate=0.6,
            viewed_together_inclusion_rate=0.5,
            rufus_ai_recommended=False,
            structured_attrs_for_rufus=StructuredAttributesInput(
                top10_attributes={
                    "material": True, "capacity": True, "color": True, "item_weight": False,
                    "maximum_current": False, "closure_type": True, "lid_type": True,
                    "insulation_type": True, "age_range": True, "care_instructions": True,
                },
                top6_rai_errors=0,
            ),
            active_promotions={"BD": False, "LD": True, "DOTD": False, "Outlet": False},
        ),
    )

    print_report(report)
