"""
批量跑分入口脚本 —— CDQ + PQS + SCS 三合一
================================================
读取一个 JSON 文件（多个ASIN的数据），对每个ASIN同时跑 CDQ / PQS / SCS 三套打分，
汇总输出一份 CSV 报告，可直接导入Excel/BI，或作为天机决策OS L1规则引擎的
批处理入口（后续可替换 load_records() 为从SQLite/PostgreSQL/MCP数据源读取）。

用法：
    # 1. 先生成一份输入模板，照着填真实ASIN数据
    python3 batch_score.py --template asins_template.json

    # 2. 跑批量打分，输出CSV报告
    python3 batch_score.py --input asins.json --output report.csv

单个ASIN数据结构（JSON）见 build_template() 函数，或运行 --template 生成示例。

设计要点：
  - cdq 与 pqs 的 image / aplus / bullets 若数据完全相同，pqs.idq 中对应字段
    可省略，脚本会自动复用 cdq 部分的同名数据，避免重复填写。
  - scs.recommendation_signals.structured_attrs_for_rufus 若省略，自动复用
    cdq.structured_attributes（Rufus/Cosmos读取的RAC Top10与CDQ结构化属性
    是同一份数据）。
  - 单个ASIN处理异常不会中断整批任务，错误会记录在CSV的 errors 列，
    CDQ/PQS/SCS三套分数相互独立计算，某一套失败不影响另外两套出分。
  - 若同目录存在 calibrated_weights.json（由 calibrate_weights.py 回归生成），
    PQS/SCS会自动使用校准后的权重，无需修改本脚本。
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Optional

from cdq_scorer import (
    CDQScorer,
    TitleInput,
    StructuredAttributesInput,
    BulletPointsInput,
    ImageInput,
    APlusInput,
    VariationInput,
    DiscoverabilityInput,
)
from pqs_scorer import (
    PQSScorer,
    IDQInput,
    KeywordCoverageInput,
    GlanceViewsInput,
    ReviewsRatingsInput,
    SalesTrendInput,
    PricingInput,
    BrandMetricsInput,
)
from scs_scorer import (
    SCSScorer,
    RankingBadgesInput,
    PlatformBadgesInput,
    CategoryStructureInput,
    RecommendationSignalsInput,
)


# ---------------------------------------------------------------------------
# Builder: JSON dict -> dataclass 输入对象
# ---------------------------------------------------------------------------

def build_title_input(d: dict) -> TitleInput:
    return TitleInput(
        text=d["text"],
        has_brand=d.get("has_brand", False),
        has_main_keyword=d.get("has_main_keyword", False),
        core_attribute_count=d.get("core_attribute_count", 0),
        has_audience_or_scenario=d.get("has_audience_or_scenario", False),
        no_grammar_errors=d.get("no_grammar_errors", True),
        has_pipe_or_separator=d.get("has_pipe_or_separator", False),
        policy_index_suppressed=d.get("policy_index_suppressed", False),
        policy_website_rejected=d.get("policy_website_rejected", False),
    )


def build_structured_attributes_input(d: dict) -> StructuredAttributesInput:
    return StructuredAttributesInput(
        top10_attributes=d["top10_attributes"],
        top6_rai_errors=d.get("top6_rai_errors", 0),
        is_softline_pt=d.get("is_softline_pt", False),
    )


def build_bullets_input(d: dict) -> BulletPointsInput:
    return BulletPointsInput(bullets=d.get("bullets", []))


def build_image_input(d: dict) -> ImageInput:
    return ImageInput(
        image_count=d.get("image_count", 0),
        has_defects=d.get("has_defects", False),
        iai_score=d.get("iai_score"),
        main_image_supports_zoom=d.get("main_image_supports_zoom", True),
    )


def build_aplus_input(d: dict) -> APlusInput:
    return APlusInput(has_aplus=d.get("has_aplus", False))


def build_variation_input(d: dict) -> VariationInput:
    return VariationInput(
        is_orphan=d.get("is_orphan", True),
        variation_count=d.get("variation_count", 0),
        wrong_attribute_values=d.get("wrong_attribute_values", 0),
        mixed_units=d.get("mixed_units", False),
        redundant_variation_info=d.get("redundant_variation_info", False),
        localization_errors=d.get("localization_errors", False),
        duplicate_children=d.get("duplicate_children", False),
        unstandardized_values=d.get("unstandardized_values", False),
        format_mismatch=d.get("format_mismatch", False),
        wrong_variation_theme=d.get("wrong_variation_theme", False),
    )


def build_discoverability_input(d: Optional[dict]) -> Optional[DiscoverabilityInput]:
    if d is None:
        return None
    return DiscoverabilityInput(
        has_accurate_leaf_node=d.get("has_accurate_leaf_node", False),
        keyword_coverage_ratio=d.get("keyword_coverage_ratio", 1.0),
    )


def build_keyword_coverage_input(d: dict) -> KeywordCoverageInput:
    return KeywordCoverageInput(
        covered_keywords=d.get("covered_keywords", 0),
        target_keywords=d.get("target_keywords", 1),
    )


def build_glance_views_input(d: dict) -> GlanceViewsInput:
    return GlanceViewsInput(
        current_per_100k=d["current_per_100k"],
        prior_per_100k=d["prior_per_100k"],
    )


def build_reviews_ratings_input(d: dict) -> ReviewsRatingsInput:
    return ReviewsRatingsInput(
        review_count_current=d["review_count_current"],
        review_count_prior=d["review_count_prior"],
        rating_current=d["rating_current"],
        rating_prior=d.get("rating_prior", 0.0),
    )


def build_sales_trend_input(d: dict) -> SalesTrendInput:
    return SalesTrendInput(
        trailing_30d_sales=d["trailing_30d_sales"],
        prior_30d_sales=d["prior_30d_sales"],
    )


def build_pricing_input(d: dict) -> PricingInput:
    return PricingInput(
        current_price=d["current_price"],
        category_avg_price=d["category_avg_price"],
        category_avg_discount_pct=d["category_avg_discount_pct"],
        current_discount_pct=d["current_discount_pct"],
        recent_90d_non_promo_min_price=d["recent_90d_non_promo_min_price"],
    )


def build_brand_input(d: dict) -> BrandMetricsInput:
    return BrandMetricsInput(
        brand_ops_current=d["brand_ops_current"],
        brand_ops_prior=d["brand_ops_prior"],
        unique_customers_current=d["unique_customers_current"],
        unique_customers_prior=d["unique_customers_prior"],
        brand_review_count_current=d["brand_review_count_current"],
        brand_review_count_prior=d["brand_review_count_prior"],
    )


def build_idq_input(pqs_d: dict, cdq_d: dict) -> IDQInput:
    """pqs.idq 中的 image/aplus/bullets 若省略，自动复用 cdq 同名字段。"""
    idq_d = pqs_d.get("idq", {})
    image_d = idq_d.get("image", cdq_d.get("image", {}))
    aplus_d = idq_d.get("aplus", cdq_d.get("aplus", {}))
    bullets_d = idq_d.get("bullets", cdq_d.get("bullets", {}))
    keywords_d = idq_d.get("keywords", {})
    return IDQInput(
        image=build_image_input(image_d),
        aplus=build_aplus_input(aplus_d),
        bullets=build_bullets_input(bullets_d),
        keywords=build_keyword_coverage_input(keywords_d),
    )


def build_ranking_badges_input(d: dict) -> RankingBadgesInput:
    return RankingBadgesInput(
        best_sellers_rank=d.get("best_sellers_rank"),
        hot_new_release_rank=d.get("hot_new_release_rank"),
        movers_shakers_rank=d.get("movers_shakers_rank"),
        most_wished_for_rank=d.get("most_wished_for_rank"),
        gift_ideas_rank=d.get("gift_ideas_rank"),
        max_rank_shown=d.get("max_rank_shown", 100),
    )


def build_platform_badges_input(d: dict) -> PlatformBadgesInput:
    return PlatformBadgesInput(
        has_amazons_choice=d.get("has_amazons_choice", False),
        has_customers_keep_item=d.get("has_customers_keep_item", False),
        is_featured_brand=d.get("is_featured_brand", False),
        brand_review_count=d.get("brand_review_count", 0),
        brand_positive_review_pct=d.get("brand_positive_review_pct", 0.0),
        brand_recent_orders=d.get("brand_recent_orders", 0),
        has_climate_pledge_friendly=d.get("has_climate_pledge_friendly", False),
    )


def build_category_structure_input(d: dict) -> CategoryStructureInput:
    return CategoryStructureInput(
        l1_category=d.get("l1_category", ""),
        l2_category=d.get("l2_category", ""),
        leaf_node=d.get("leaf_node", ""),
        has_correct_leaf_node=d.get("has_correct_leaf_node", True),
        category_relevance_score=d.get("category_relevance_score", 1.0),
        leaf_node_competing_asins=d.get("leaf_node_competing_asins", 0),
    )


def build_recommendation_signals_input(d: dict, cdq_d: dict) -> RecommendationSignalsInput:
    """structured_attrs_for_rufus 若省略，自动复用 cdq.structured_attributes（同一份RAC Top10数据）。"""
    structured_attrs_d = d.get("structured_attrs_for_rufus") or cdq_d.get("structured_attributes")
    structured_attrs = build_structured_attributes_input(structured_attrs_d) if structured_attrs_d else None
    return RecommendationSignalsInput(
        fbt_pairs_count=d.get("fbt_pairs_count", 0),
        fbt_saturation_count=d.get("fbt_saturation_count", 5),
        compare_similar_items_included=d.get("compare_similar_items_included", False),
        compare_similar_items_win_rate=d.get("compare_similar_items_win_rate", 0.0),
        viewed_together_inclusion_rate=d.get("viewed_together_inclusion_rate", 0.0),
        rufus_ai_recommended=d.get("rufus_ai_recommended", False),
        structured_attrs_for_rufus=structured_attrs,
        active_promotions=d.get("active_promotions", {}),
    )


# ---------------------------------------------------------------------------
# 单ASIN跑分
# ---------------------------------------------------------------------------

def score_one_asin(record: dict) -> dict:
    asin = record["asin"]
    row: dict = {"asin": asin, "errors": ""}

    cdq_d = record.get("cdq", {})
    pqs_d = record.get("pqs", {})
    scs_d = record.get("scs", {})

    # ---- CDQ ----
    try:
        cdq_scorer = CDQScorer()
        cdq_report = cdq_scorer.score(
            asin=asin,
            title=build_title_input(cdq_d["title"]),
            structured_attrs=build_structured_attributes_input(cdq_d["structured_attributes"]),
            bullets=build_bullets_input(cdq_d.get("bullets", {})),
            image=build_image_input(cdq_d.get("image", {})),
            aplus=build_aplus_input(cdq_d.get("aplus", {})),
            variation=build_variation_input(cdq_d.get("variation", {})),
            discoverability=build_discoverability_input(cdq_d.get("discoverability")),
        )
        row.update({
            "cdq_total_score": cdq_report.total_score,
            "cdq_grade": cdq_report.grade.value,
            "cdq_grade_label": cdq_report.grade_label,
            "cdq_is_orphan": cdq_report.is_orphan,
            "cdq_policy_violation": cdq_report.policy_violation,
            "cdq_severe_defect": cdq_report.severe_defect,
            "cdq_structured_attributes_score": cdq_report.dimensions["structured_attributes"].weighted_score,
            "cdq_title_score": cdq_report.dimensions["title"].weighted_score,
            "cdq_bullet_points_score": cdq_report.dimensions["bullet_points"].weighted_score,
            "cdq_image_score": cdq_report.dimensions["image"].weighted_score,
            "cdq_aplus_score": cdq_report.dimensions["aplus"].weighted_score,
            "cdq_variation_score": cdq_report.dimensions["variation"].weighted_score,
            "cdq_discoverability_score": cdq_report.dimensions.get("discoverability").weighted_score
            if "discoverability" in cdq_report.dimensions else "",
            "cdq_top_priority_actions": " | ".join(cdq_report.top_priority_actions),
        })
    except Exception as e:  # noqa: BLE001
        row["errors"] += f"CDQ跑分失败: {e}; "

    # ---- PQS ----
    try:
        pqs_scorer = PQSScorer()
        pqs_report = pqs_scorer.score(
            asin=asin,
            idq=build_idq_input(pqs_d, cdq_d),
            glance_views=build_glance_views_input(pqs_d["glance_views"]),
            reviews_ratings=build_reviews_ratings_input(pqs_d["reviews_ratings"]),
            sales_trend=build_sales_trend_input(pqs_d["sales_trend"]),
            pricing=build_pricing_input(pqs_d["pricing"]),
            brand=build_brand_input(pqs_d["brand"]),
        )
        row.update({
            "pqs_total_score": pqs_report.total_score,
            "pqs_tier": pqs_report.tier,
            "pqs_listing_quality_score": pqs_report.dimensions["listing_quality"].weighted_score,
            "pqs_brand_metrics_score": pqs_report.dimensions["brand_metrics"].weighted_score,
            "pqs_competitive_pricing_score": pqs_report.dimensions["competitive_pricing"].weighted_score,
            "pqs_top_priority_actions": " | ".join(pqs_report.top_priority_actions),
        })
    except Exception as e:  # noqa: BLE001
        row["errors"] += f"PQS跑分失败: {e}; "

    # ---- SCS ----
    try:
        scs_scorer = SCSScorer()
        scs_report = scs_scorer.score(
            asin=asin,
            ranking_badges=build_ranking_badges_input(scs_d.get("ranking_badges", {})),
            platform_badges=build_platform_badges_input(scs_d.get("platform_badges", {})),
            category_structure=build_category_structure_input(scs_d.get("category_structure", {})),
            recommendation_signals=build_recommendation_signals_input(
                scs_d.get("recommendation_signals", {}), cdq_d
            ),
        )
        row.update({
            "scs_total_score": scs_report.total_score,
            "scs_cdq_bonus_points": scs_report.cdq_bonus_points,
            "scs_ranking_badges_score": scs_report.dimensions["ranking_badges"].weighted_score,
            "scs_platform_badges_score": scs_report.dimensions["platform_badges"].weighted_score,
            "scs_category_structure_score": scs_report.dimensions["category_structure"].weighted_score,
            "scs_recommendation_signals_score": scs_report.dimensions["recommendation_signals"].weighted_score,
            "scs_top_priority_actions": " | ".join(scs_report.top_priority_actions),
        })
    except Exception as e:  # noqa: BLE001
        row["errors"] += f"SCS跑分失败: {e}; "

    return row


# ---------------------------------------------------------------------------
# CSV 输出
# ---------------------------------------------------------------------------

CSV_COLUMNS = [
    "asin",
    "cdq_total_score", "cdq_grade", "cdq_grade_label", "cdq_is_orphan",
    "cdq_policy_violation", "cdq_severe_defect",
    "cdq_structured_attributes_score", "cdq_title_score", "cdq_bullet_points_score",
    "cdq_image_score", "cdq_aplus_score", "cdq_variation_score", "cdq_discoverability_score",
    "cdq_top_priority_actions",
    "pqs_total_score", "pqs_tier",
    "pqs_listing_quality_score", "pqs_brand_metrics_score", "pqs_competitive_pricing_score",
    "pqs_top_priority_actions",
    "scs_total_score", "scs_cdq_bonus_points",
    "scs_ranking_badges_score", "scs_platform_badges_score",
    "scs_category_structure_score", "scs_recommendation_signals_score",
    "scs_top_priority_actions",
    "errors",
]


def load_records(input_path: Path) -> list[dict]:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("asins", [])
    if not isinstance(data, list):
        raise ValueError("输入JSON必须是ASIN记录数组，或包含 'asins' 键的对象")
    return data


def run_batch(input_path: Path, output_path: Path) -> None:
    records = load_records(input_path)
    rows = []
    for record in records:
        try:
            rows.append(score_one_asin(record))
        except Exception as e:  # noqa: BLE001
            rows.append({"asin": record.get("asin", "UNKNOWN"), "errors": f"记录解析失败: {e}"})

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    ok = sum(1 for r in rows if not r.get("errors"))
    print(f"批量跑分完成：共 {len(rows)} 个ASIN，成功 {ok} 个，失败 {len(rows) - ok} 个")
    print(f"报告已输出至：{output_path}")


# ---------------------------------------------------------------------------
# 模板生成
# ---------------------------------------------------------------------------

def build_template() -> list[dict]:
    return [
        {
            "asin": "B0GDCZ7XXX",
            "cdq": {
                "title": {
                    "text": "Acme Brand Stainless Steel Water Bottle | 32oz Insulated Sports Bottle for Kids Adults",
                    "has_brand": True,
                    "has_main_keyword": True,
                    "core_attribute_count": 3,
                    "has_audience_or_scenario": True,
                    "no_grammar_errors": True,
                    "has_pipe_or_separator": True,
                    "policy_index_suppressed": False,
                    "policy_website_rejected": False,
                },
                "structured_attributes": {
                    "top10_attributes": {
                        "material": True, "capacity": True, "color": True,
                        "item_weight": False, "maximum_current": False,
                        "closure_type": True, "lid_type": True,
                        "insulation_type": True, "age_range": True, "care_instructions": True,
                    },
                    "top6_rai_errors": 0,
                    "is_softline_pt": False,
                },
                "bullets": {
                    "bullets": [
                        "Keeps drinks cold for 24 hours",
                        "Leak-proof design",
                        "BPA-free stainless steel",
                        "Fits standard cup holders",
                    ]
                },
                "image": {"image_count": 24, "has_defects": False, "iai_score": 0.6, "main_image_supports_zoom": True},
                "aplus": {"has_aplus": True},
                "variation": {"is_orphan": False, "variation_count": 3},
                "discoverability": {"has_accurate_leaf_node": True, "keyword_coverage_ratio": 0.9},
            },
            "pqs": {
                "idq": {
                    # image/aplus/bullets 可省略，会自动复用上面 cdq 中的同名数据
                    "keywords": {"covered_keywords": 18, "target_keywords": 25},
                },
                "glance_views": {"current_per_100k": 1200, "prior_per_100k": 1000},
                "reviews_ratings": {
                    "review_count_current": 340, "review_count_prior": 300,
                    "rating_current": 4.4, "rating_prior": 4.3,
                },
                "sales_trend": {"trailing_30d_sales": 52000, "prior_30d_sales": 48000},
                "pricing": {
                    "current_price": 19.99, "category_avg_price": 22.50,
                    "category_avg_discount_pct": 0.10, "current_discount_pct": 0.15,
                    "recent_90d_non_promo_min_price": 21.99,
                },
                "brand": {
                    "brand_ops_current": 210000, "brand_ops_prior": 180000,
                    "unique_customers_current": 15000, "unique_customers_prior": 13000,
                    "brand_review_count_current": 2100, "brand_review_count_prior": 1900,
                },
            },
            "scs": {
                "ranking_badges": {
                    "best_sellers_rank": None,
                    "hot_new_release_rank": 12,
                    "movers_shakers_rank": None,
                    "most_wished_for_rank": 45,
                    "gift_ideas_rank": None,
                    "max_rank_shown": 100,
                },
                "platform_badges": {
                    "has_amazons_choice": True,
                    "has_customers_keep_item": False,
                    "is_featured_brand": False,
                    "brand_review_count": 4200,
                    "brand_positive_review_pct": 0.93,
                    "brand_recent_orders": 8500,
                    "has_climate_pledge_friendly": False,
                },
                "category_structure": {
                    "l1_category": "Home & Kitchen",
                    "l2_category": "Vacuum Cleaners & Floor Care",
                    "leaf_node": "Electric Brooms",
                    "has_correct_leaf_node": True,
                    "category_relevance_score": 0.95,
                    "leaf_node_competing_asins": 1200,
                },
                "recommendation_signals": {
                    # structured_attrs_for_rufus 可省略，会自动复用 cdq.structured_attributes
                    "fbt_pairs_count": 2,
                    "compare_similar_items_included": True,
                    "compare_similar_items_win_rate": 0.6,
                    "viewed_together_inclusion_rate": 0.5,
                    "rufus_ai_recommended": False,
                    "active_promotions": {"BD": False, "LD": True, "DOTD": False, "Outlet": False},
                },
            },
        }
    ]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="CDQ + PQS 批量跑分入口脚本")
    parser.add_argument("--input", type=str, help="输入JSON文件路径（ASIN数据数组）")
    parser.add_argument("--output", type=str, default="cdq_pqs_report.csv", help="输出CSV报告路径")
    parser.add_argument("--template", type=str, help="生成输入模板JSON到指定路径，不执行跑分")
    args = parser.parse_args()

    if args.template:
        template_path = Path(args.template)
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(build_template(), f, ensure_ascii=False, indent=2)
        print(f"输入模板已生成：{template_path}")
        return

    if not args.input:
        print("请指定 --input 输入JSON路径，或使用 --template 先生成模板", file=sys.stderr)
        sys.exit(1)

    run_batch(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
