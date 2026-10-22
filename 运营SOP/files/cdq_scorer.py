"""
Amazon CDQ (Composite Data Quality) 打分系统
================================================
基于 Amazon ASCS CDQ v3 方法论（2025年3月发布）复刻的规则引擎实现。

七大维度：
  1. Structured Attributes Quality  结构化属性质量   30%
  2. Title Quality (TQS)            标题质量         25%
  3. Bullet Points                  描述摘要/五点     5%
  4. Image Quality                  图片质量         15% (孤儿ASIN 18.75%)
  5. A+ Content Quality             A+页面质量        5%
  6. Variation Quality              变体质量         20% (孤儿ASIN N/A，权重重分配)
  7. Product Type Classification    可搜索性/加分项   0-20%

总分区间 0-120。触发"策略违规"强制等级 U；触发"严重缺陷"强制等级 D。

设计目标：作为规则引擎（L1）模块，可直接嵌入决策系统，
按 ASIN 批量跑分并输出可执行的优化建议（用于生成 TODOLIST / Merchant Action）。

用法示例见文件末尾 `__main__`。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# 基础权重配置
# ---------------------------------------------------------------------------

BASE_WEIGHTS = {
    "structured_attributes": 0.30,
    "title": 0.25,
    "bullet_points": 0.05,
    "image": 0.15,
    "aplus": 0.05,
    "variation": 0.20,  # 孤儿ASIN时此维度权重重分配至其余维度
}
DISCOVERABILITY_MAX_BONUS = 0.20  # 加分项，不计入100%基础，单独叠加


def resolve_weights(is_orphan: bool) -> dict:
    """孤儿ASIN：变体质量(20%)不适用，剩余80%权重等比放大到100%。"""
    if not is_orphan:
        return dict(BASE_WEIGHTS)
    remaining_total = 1.0 - BASE_WEIGHTS["variation"]  # 0.80
    weights = {
        k: (v / remaining_total)
        for k, v in BASE_WEIGHTS.items()
        if k != "variation"
    }
    weights["variation"] = 0.0
    return weights


# ---------------------------------------------------------------------------
# 通用结果容器
# ---------------------------------------------------------------------------

@dataclass
class DimensionResult:
    name: str
    raw_score: float          # 0.0 - 1.0，该维度内部得分
    weight: float              # 该维度在总分中的权重（0-1）
    weighted_score: float      # raw_score * weight * 100，计入总分的实际分值
    grade: Optional[str] = None
    defects: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1. 结构化属性质量 Structured Attributes Quality (30%)
# ---------------------------------------------------------------------------

@dataclass
class StructuredAttributesInput:
    top10_attributes: dict[str, bool]   # {attribute_name: is_complete_and_correct}
    top6_rai_errors: int = 0            # top6 RAI属性中出错的数量
    is_softline_pt: bool = False        # Softline品类排序逻辑不同，仅供标注


def score_structured_attributes(inp: StructuredAttributesInput) -> DimensionResult:
    defects, suggestions = [], []
    total = len(inp.top10_attributes) or 1
    complete_correct = sum(1 for v in inp.top10_attributes.values() if v)
    completeness_ratio = complete_correct / total

    raw_score = completeness_ratio  # 评分 = 完整且正确属性的权重总和（简化为等权重）

    # 严重缺陷判定
    severe = False
    if completeness_ratio < 0.5:
        severe = True
        defects.append(f"前10项相关属性完整性 {completeness_ratio:.0%} < 50%，触发严重缺陷")
        suggestions.append("优先补全缺失属性，尤其是Top 6 RAI属性")
    if inp.top6_rai_errors >= 4:  # "多数"按 >=4/6 判定
        severe = True
        defects.append(f"Top 6 RAI属性中 {inp.top6_rai_errors} 项出错（多数错误）")
        suggestions.append("核对并修正Top 6 RAI属性的准确性，正确性优先于完整性")

    missing = [k for k, v in inp.top10_attributes.items() if not v]
    if missing:
        suggestions.append(f"待补全属性：{', '.join(missing[:10])}")

    return DimensionResult(
        name="结构化属性质量",
        raw_score=raw_score,
        weight=0.0,  # 由聚合函数填入
        weighted_score=0.0,
        grade="严重缺陷" if severe else ("良好" if raw_score >= 0.9 else "待改善"),
        defects=defects,
        suggestions=suggestions,
        details={
            "completeness_ratio": round(completeness_ratio, 4),
            "severe_defect": severe,
            "is_softline_pt": inp.is_softline_pt,
        },
    )


# ---------------------------------------------------------------------------
# 2. 标题质量 Title Quality — TQS 逻辑 (25%)
# ---------------------------------------------------------------------------

RESTRICTED_SPECIAL_CHARS = set("!$?{}_^¬¦")

PROMOTIONAL_WORDS = {
    "free", "best seller", "top rated", "guarantee", "guaranteed", "gift",
    "warranty", "cheapest", "#1", "hot item", "sale", "discount", "free shipping",
}

SENSITIVE_BANNED_WORDS = {
    "antimicrobial", "antibacterial", "antifungal", "prevents bacteria",
    "resists mildew", "removes mold", "sanitize", "sanitizes", "disinfect",
    "disinfects", "sterilize", "sterilizes", "anti-mites", "detoxify",
    "uv sterilize", "pesticide", "pesticides", "insecticide", "marijuana",
    "heroin", "drugs", "bacteria",
}

STOPWORDS_FOR_REPEAT_CHECK = {"in", "on", "over", "with", "and", "or", "for", "the", "a", "an"}


@dataclass
class TitleInput:
    text: str
    has_brand: bool
    has_main_keyword: bool
    core_attribute_count: int          # 标注的核心属性数量
    has_audience_or_scenario: bool     # 是否标注适用人群/使用场景/意图
    no_grammar_errors: bool = True
    has_pipe_or_separator: bool = False  # 是否含 | 或明确分隔符
    policy_index_suppressed: bool = False
    policy_website_rejected: bool = False


def _word_max_repeat(text: str) -> tuple[str, int]:
    words = [w.strip(".,|!?").lower() for w in text.split() if w.strip(".,|!?")]
    counts: dict[str, int] = {}
    for w in words:
        if w in STOPWORDS_FOR_REPEAT_CHECK or len(w) <= 2:
            continue
        counts[w] = counts.get(w, 0) + 1
    if not counts:
        return "", 0
    word, count = max(counts.items(), key=lambda kv: kv[1])
    return word, count


def score_title_quality(inp: TitleInput) -> DimensionResult:
    defects, suggestions = [], []
    text = inp.text

    # 长度检查
    length = len(text)
    length_ok = length <= 200

    # 特殊字符检查
    special_chars_found = RESTRICTED_SPECIAL_CHARS.intersection(set(text))
    special_char_score = 0 if special_chars_found else 1

    # 促销/受限短语检查
    lower_text = text.lower()
    restricted_hits = [w for w in PROMOTIONAL_WORDS if w in lower_text]
    banned_hits = [w for w in SENSITIVE_BANNED_WORDS if w in lower_text]
    restricted_phrase_score = 0 if (restricted_hits or banned_hits) else 1

    # 冗余度检查
    repeat_word, repeat_count = _word_max_repeat(text)
    if repeat_count <= 1:
        redundancy_score = 1.0
    elif repeat_count == 2:
        redundancy_score = 0.6
    else:
        redundancy_score = 0.0

    # 完整性评分：5项各占0.2
    completeness_factors = [
        inp.has_brand,
        inp.has_main_keyword,
        inp.core_attribute_count >= 3,
        inp.has_audience_or_scenario,
        inp.no_grammar_errors,
    ]
    completeness_score = sum(0.2 for f in completeness_factors if f)

    pipe_score = 1 if inp.has_pipe_or_separator else 0

    # 策略违规：索引/网站抑制 或 命中受限短语/敏感词 或 长度超限
    policy_violation = (
        inp.policy_index_suppressed
        or inp.policy_website_rejected
        or completeness_score < 0.4
        or redundancy_score <= 0.6 and repeat_count > 2
        or length > 200
        or restricted_phrase_score < 1
    )

    if policy_violation:
        grade = "C"
        raw_score = 0.0
        defects.append("标题命中策略违规判定条件（详见details）")
    elif (
        completeness_score >= 0.6
        and redundancy_score == 1
        and length_ok
        and pipe_score > 0
        and special_char_score == 1
        and restricted_phrase_score == 1
    ):
        grade = "A"
        raw_score = 1.0
    else:
        grade = "B"
        # B级：至少一项未达标但未违规，按各子项综合给一个 0.5-0.99 的连续分数
        raw_score = round(
            0.5
            + 0.5
            * (
                min(completeness_score / 0.6, 1)
                + redundancy_score
                + (1 if length_ok else 0)
                + special_char_score
                + restricted_phrase_score
            )
            / 5,
            4,
        )
        raw_score = min(raw_score, 0.99)

    if special_chars_found:
        defects.append(f"含禁用特殊字符：{special_chars_found}")
        suggestions.append("移除禁用特殊字符 ! $ ? { } ^ ¬ ¦")
    if restricted_hits:
        defects.append(f"含促销/主观性用语：{restricted_hits}")
    if banned_hits:
        defects.append(f"含违禁/敏感词：{banned_hits}")
        suggestions.append("删除健康/杀虫/消毒类敏感声明词，避免触发合规审查")
    if repeat_count > 2:
        defects.append(f"关键词堆砌：'{repeat_word}' 重复 {repeat_count} 次")
        suggestions.append("减少重复关键词，同词不超过2次")
    if not length_ok:
        defects.append(f"标题长度 {length} 超过200字符上限")
    if not inp.has_pipe_or_separator:
        suggestions.append("建议添加分隔符（如 |）清晰分段信息")
    if completeness_score < 0.6:
        suggestions.append("补充品牌名/主关键词/≥3个核心属性/适用场景，提升标题完整性")

    return DimensionResult(
        name="标题质量",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        grade=grade,
        defects=defects,
        suggestions=suggestions,
        details={
            "length": length,
            "completeness_score": completeness_score,
            "redundancy_score": redundancy_score,
            "special_char_score": special_char_score,
            "restricted_phrase_score": restricted_phrase_score,
            "pipe_score": pipe_score,
            "policy_violation": policy_violation,
        },
    )


# ---------------------------------------------------------------------------
# 3. 描述摘要 / 五点描述 Bullet Points (5%)
# ---------------------------------------------------------------------------

@dataclass
class BulletPointsInput:
    bullets: list[str]
    banned_words: set[str] = field(default_factory=lambda: set(SENSITIVE_BANNED_WORDS))


def score_bullet_points(inp: BulletPointsInput) -> DimensionResult:
    defects, suggestions = [], []
    count = len(inp.bullets)

    if count >= 3:
        raw_score = 1.0
    elif count >= 1:
        raw_score = 0.5
    else:
        raw_score = 0.0
        defects.append("无五点描述")

    hit_words = []
    for b in inp.bullets:
        lower = b.lower()
        hit_words.extend([w for w in inp.banned_words if w in lower])
    if hit_words:
        raw_score = 0.0
        defects.append(f"五点描述命中违禁/敏感词：{sorted(set(hit_words))}")
        suggestions.append("移除五点描述中的违禁/敏感关键词")

    if count < 3:
        suggestions.append("补充五点描述至≥3条，遵循0/1/3原则（0项遗漏/1个核心卖点/≥3个魅力卖点）")

    return DimensionResult(
        name="描述摘要质量(五点)",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        defects=defects,
        suggestions=suggestions,
        details={"bullet_count": count},
    )


# ---------------------------------------------------------------------------
# 4. 图片质量 Image Quality (15% / 18.75%孤儿ASIN)
# ---------------------------------------------------------------------------

@dataclass
class ImageInput:
    image_count: int
    has_defects: bool
    iai_score: Optional[float] = None  # Imaging Attribute Index, 参考阈值 >=0.4
    main_image_supports_zoom: bool = True


def score_image_quality(inp: ImageInput) -> DimensionResult:
    defects, suggestions = [], []

    if inp.image_count >= 4 and not inp.has_defects:
        raw_score = 1.0
    elif inp.image_count >= 4 and inp.has_defects:
        raw_score = 0.4
        defects.append("图片数量达标但存在图片质量缺陷")
        suggestions.append("排查并修复图片缺陷（分辨率/合规性/展示问题）")
    elif inp.image_count < 4 and not inp.has_defects:
        raw_score = 0.6
        suggestions.append(f"当前仅{inp.image_count}张图，建议补充至≥4张")
    else:
        raw_score = 0.0
        defects.append("图片数量不足4张且存在缺陷")
        suggestions.append("优先补图至≥4张，同时修复图片缺陷")

    if inp.iai_score is not None and inp.iai_score < 0.4:
        defects.append(f"IAI图像属性指数 {inp.iai_score:.2f} < 0.4 阈值")
        suggestions.append("完善图片元数据/属性标签，对标同品类竞品图片完整度")

    if not inp.main_image_supports_zoom:
        defects.append("主图不支持缩放（建议≥1000像素）")
        suggestions.append("上传≥1000像素主图以支持缩放功能")

    return DimensionResult(
        name="图片质量",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        defects=defects,
        suggestions=suggestions,
        details={
            "image_count": inp.image_count,
            "has_defects": inp.has_defects,
            "iai_score": inp.iai_score,
        },
    )


# ---------------------------------------------------------------------------
# 5. A+页面质量 A+ Content (5%) — 二元判分
# ---------------------------------------------------------------------------

@dataclass
class APlusInput:
    has_aplus: bool


def score_aplus(inp: APlusInput) -> DimensionResult:
    raw_score = 1.0 if inp.has_aplus else 0.0
    suggestions = [] if inp.has_aplus else ["制作并上传A+页面内容（图文/对比图表/增强模块）"]
    return DimensionResult(
        name="A+页面质量",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={"has_aplus": inp.has_aplus, "note": "内容质量评估计划2026年上线，目前仅判有无"},
    )


# ---------------------------------------------------------------------------
# 6. 变体质量 Variation Quality (20%, 孤儿ASIN N/A)
# ---------------------------------------------------------------------------

@dataclass
class VariationInput:
    is_orphan: bool
    variation_count: int = 0
    wrong_attribute_values: int = 0     # 严重缺陷
    mixed_units: bool = False           # 严重缺陷
    redundant_variation_info: bool = False  # 严重缺陷
    localization_errors: bool = False   # 严重缺陷
    duplicate_children: bool = False    # 严重缺陷
    unstandardized_values: bool = False # 非严重缺陷
    format_mismatch: bool = False       # 非严重缺陷
    wrong_variation_theme: bool = False # 非严重缺陷


def score_variation_quality(inp: VariationInput) -> DimensionResult:
    if inp.is_orphan:
        return DimensionResult(
            name="变体质量",
            raw_score=0.0,
            weight=0.0,
            weighted_score=0.0,
            grade="N/A（孤儿ASIN，权重已重分配至其余维度）",
            details={"is_orphan": True},
        )

    defects, suggestions = [], []
    severe_flags = [
        (inp.wrong_attribute_values > 0, f"错误属性值 x{inp.wrong_attribute_values}"),
        (inp.mixed_units, "单位制混用"),
        (inp.redundant_variation_info, "变体信息冗余"),
        (inp.localization_errors, "本地化错误"),
        (inp.duplicate_children, "子项重复"),
    ]
    non_severe_flags = [
        (inp.unstandardized_values, "未标准化值"),
        (inp.format_mismatch, "格式不匹配"),
        (inp.wrong_variation_theme, "变异主题错误"),
    ]

    severe_count = sum(1 for hit, _ in severe_flags if hit)
    non_severe_count = sum(1 for hit, _ in non_severe_flags if hit)
    defects.extend(msg for hit, msg in severe_flags if hit)
    defects.extend(msg for hit, msg in non_severe_flags if hit)

    if severe_count > 0:
        raw_score = 0.0
        suggestions.append("立即修复变体严重缺陷（错误值/单位/冗余/本地化/重复子项）")
    elif non_severe_count > 0:
        raw_score = max(0.5, 1.0 - 0.15 * non_severe_count)
        suggestions.append("逐步统一变体主题属性的标准化格式")
    else:
        raw_score = 1.0

    if inp.variation_count < 2:
        suggestions.append("变体数量建议≥2个")

    return DimensionResult(
        name="变体质量",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        grade="严重缺陷" if severe_count else ("非严重缺陷" if non_severe_count else "良好"),
        defects=defects,
        suggestions=suggestions,
        details={
            "variation_count": inp.variation_count,
            "severe_count": severe_count,
            "non_severe_count": non_severe_count,
        },
    )


# ---------------------------------------------------------------------------
# 7. 产品类型分类 / 可搜索性 Discoverability (0-20% 加分)
# ---------------------------------------------------------------------------

@dataclass
class DiscoverabilityInput:
    has_accurate_leaf_node: bool
    keyword_coverage_ratio: float = 1.0  # 0-1，类目相关关键词覆盖率


def score_discoverability(inp: DiscoverabilityInput) -> DimensionResult:
    suggestions = []
    if not inp.has_accurate_leaf_node:
        raw_score = 0.0
        suggestions.append("为ASIN分配准确、相关的细分类目叶节点(Node ID)")
    else:
        raw_score = max(0.0, min(1.0, inp.keyword_coverage_ratio))
        if raw_score < 1.0:
            suggestions.append("补充类目相关搜索关键词覆盖，提升可搜索性")

    return DimensionResult(
        name="产品类型分类/可搜索性",
        raw_score=raw_score,
        weight=0.0,
        weighted_score=0.0,
        suggestions=suggestions,
        details={
            "has_accurate_leaf_node": inp.has_accurate_leaf_node,
            "keyword_coverage_ratio": inp.keyword_coverage_ratio,
        },
    )


# ---------------------------------------------------------------------------
# 等级映射
# ---------------------------------------------------------------------------

class CDQGrade(str, Enum):
    A_PLUS_PLUS = "A++"
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    U = "U"


def grade_from_score(total_score: float, policy_violation: bool, severe_defect: bool) -> tuple[CDQGrade, str]:
    """
    等级映射说明：原文 A+(85-100) 与 A(>85) 区间存在重叠表述（官方原文如此）。
    此处工程化处理为不重叠区间：A+: 95-100，A: 85-95。
    实际以卖家/供应商后台显示等级为准。
    """
    if policy_violation:
        return CDQGrade.U, "低质量-政策违规（N/A）"
    if severe_defect:
        return CDQGrade.D, "低质量-严重缺陷（0分）"
    if total_score > 100:
        return CDQGrade.A_PLUS_PLUS, "极高（加分档）"
    if total_score >= 95:
        return CDQGrade.A_PLUS, "高质量"
    if total_score >= 85:
        return CDQGrade.A, "尚可"
    if total_score >= 70:
        return CDQGrade.B, "低质量-无缺陷"
    return CDQGrade.C, "低质量-非严重缺陷"


# ---------------------------------------------------------------------------
# 聚合器：CDQ Scorer
# ---------------------------------------------------------------------------

@dataclass
class CDQScoreReport:
    asin: str
    total_score: float
    grade: CDQGrade
    grade_label: str
    is_orphan: bool
    dimensions: dict[str, DimensionResult]
    policy_violation: bool
    severe_defect: bool
    top_priority_actions: list[str]


class CDQScorer:
    """CDQ综合打分引擎：输入各维度数据，输出总分/等级/优先修复建议。"""

    def score(
        self,
        asin: str,
        title: TitleInput,
        structured_attrs: StructuredAttributesInput,
        bullets: BulletPointsInput,
        image: ImageInput,
        aplus: APlusInput,
        variation: VariationInput,
        discoverability: Optional[DiscoverabilityInput] = None,
    ) -> CDQScoreReport:
        is_orphan = variation.is_orphan
        weights = resolve_weights(is_orphan)

        results: dict[str, DimensionResult] = {
            "structured_attributes": score_structured_attributes(structured_attrs),
            "title": score_title_quality(title),
            "bullet_points": score_bullet_points(bullets),
            "image": score_image_quality(image),
            "aplus": score_aplus(aplus),
            "variation": score_variation_quality(variation),
        }

        base_score = 0.0
        for key, result in results.items():
            w = weights.get(key, 0.0)
            result.weight = w
            result.weighted_score = round(result.raw_score * w * 100, 2)
            base_score += result.weighted_score

        # Discoverability 加分项（不占base权重，独立叠加0-20分）
        if discoverability is not None:
            disc_result = score_discoverability(discoverability)
            disc_weight = DISCOVERABILITY_MAX_BONUS
            disc_result.weight = disc_weight
            disc_result.weighted_score = round(disc_result.raw_score * disc_weight * 100, 2)
            results["discoverability"] = disc_result
            total_score = round(base_score + disc_result.weighted_score, 2)
        else:
            total_score = round(base_score, 2)

        policy_violation = bool(results["title"].details.get("policy_violation"))
        severe_defect = bool(
            results["structured_attributes"].details.get("severe_defect")
            or results["variation"].details.get("severe_count", 0) > 0
        )

        grade, grade_label = grade_from_score(total_score, policy_violation, severe_defect)

        # 优先级建议：按 权重 * (1-raw_score) 的“损失分值”从高到低排序
        loss_ranked = sorted(
            (r for k, r in results.items() if k != "discoverability"),
            key=lambda r: r.weight * (1 - r.raw_score),
            reverse=True,
        )
        top_priority_actions = []
        for r in loss_ranked:
            if r.suggestions:
                top_priority_actions.append(f"[{r.name}] {r.suggestions[0]}")
            if len(top_priority_actions) >= 5:
                break

        return CDQScoreReport(
            asin=asin,
            total_score=total_score,
            grade=grade,
            grade_label=grade_label,
            is_orphan=is_orphan,
            dimensions=results,
            policy_violation=policy_violation,
            severe_defect=severe_defect,
            top_priority_actions=top_priority_actions,
        )


def print_report(report: CDQScoreReport) -> None:
    print(f"\n========== CDQ 打分报告：{report.asin} ==========")
    print(f"总分：{report.total_score} / 120  →  等级：{report.grade.value}（{report.grade_label}）")
    print(f"孤儿ASIN：{report.is_orphan}  策略违规：{report.policy_violation}  严重缺陷：{report.severe_defect}")
    print("-" * 60)
    for key, r in report.dimensions.items():
        print(f"[{r.name}] 权重{r.weight*100:.2f}%  原始得分{r.raw_score:.2f}  计入总分{r.weighted_score}")
        if r.defects:
            print(f"   缺陷：{r.defects}")
    print("-" * 60)
    print("优先修复建议（按影响分值排序）：")
    for i, action in enumerate(report.top_priority_actions, 1):
        print(f"  {i}. {action}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# 示例运行（对应原文档中的样例场景）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scorer = CDQScorer()

    report = scorer.score(
        asin="B0GDCZ7XXX",
        title=TitleInput(
            text="Acme Brand Stainless Steel Water Bottle | 32oz Insulated Sports Bottle for Kids Adults",
            has_brand=True,
            has_main_keyword=True,
            core_attribute_count=3,
            has_audience_or_scenario=True,
            has_pipe_or_separator=True,
        ),
        structured_attrs=StructuredAttributesInput(
            top10_attributes={
                "material": True, "capacity": True, "color": True, "item_weight": False,
                "maximum_current": False, "closure_type": True, "lid_type": True,
                "insulation_type": True, "age_range": True, "care_instructions": True,
            },
            top6_rai_errors=0,
        ),
        bullets=BulletPointsInput(bullets=[
            "Keeps drinks cold for 24 hours",
            "Leak-proof design",
            "BPA-free stainless steel",
            "Fits standard cup holders",
        ]),
        image=ImageInput(image_count=24, has_defects=False, iai_score=0.6),
        aplus=APlusInput(has_aplus=True),
        variation=VariationInput(is_orphan=False, variation_count=3),
        discoverability=DiscoverabilityInput(has_accurate_leaf_node=True, keyword_coverage_ratio=0.9),
    )

    print_report(report)
