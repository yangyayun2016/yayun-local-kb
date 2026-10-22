"""
ColdNet 新品推荐强度评分系统 (NPRS, New Product Recommendation Score)
================================================
复刻 Amazon ColdNet 论文（Tewatia/Rahman/Garg, CSS 2026）中推断时的核心规则：
  - 析取准则判定冷启动（Disjunctive Criterion）
  - 冷启动样本用相似样本群的分位数聚合估计，而非依赖自身历史
  - w=0.1（个体）/ 0.9（群体）混合公式（论文18组超参数扫描验证的最优值）
  - 暖启动样本直接用个体信号，不做群体混合（严格改善保证）

⚠️ 本系统不训练真正的DragonNet神经网络（需要百万级带处理标签数据+训练算力）。
   `individual_signal` 是SPR类工具早期指标的代理，不是论文里训练出来的
   潜在结果头 μ̂(X)。详见同目录 ColdNet冷启动推荐算法应用详解.md 第〇节。

标注说明：
  [论文] = 直接对应论文原文机制
  ⚙️ = 业务假设或工程扩展，非论文内容
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# 冷启动观察窗口计算器（⚙️ 你的实战经验：SPR周更节奏 -> 实际冷启动天数）
# ---------------------------------------------------------------------------

WEEKDAY_INDEX = {"周一": 0, "周二": 1, "周三": 2, "周四": 3, "周五": 4, "周六": 5, "周日": 6}


def compute_cold_start_window_days(
    collection_start_weekday: str,
    update_weekday: str = "周二",
    n_update_cycles: int = 2,
) -> int:
    """
    计算从ASIN开始被收录/产生数据，到系统完成 n_update_cycles 次更新为止的实际天数。
    亚马逊后台/SPR类工具通常每周固定某天更新一次ASIN表现判断（SPR关键词数据周二更新，
    发货数据据你反馈周三更新）。

    示例：周五开始收录，发货数据周三更新，2个更新周期 -> 12天（与你的手算一致）。
    """
    if collection_start_weekday not in WEEKDAY_INDEX or update_weekday not in WEEKDAY_INDEX:
        raise ValueError(f"星期名称必须是{list(WEEKDAY_INDEX.keys())}之一")

    start_idx = WEEKDAY_INDEX[collection_start_weekday]
    update_idx = WEEKDAY_INDEX[update_weekday]
    days_to_first_update = (update_idx - start_idx) % 7
    if days_to_first_update == 0:
        days_to_first_update = 7  # 开始当天正好是更新日，顺延到下周
    return days_to_first_update + 7 * (n_update_cycles - 1)


# ---------------------------------------------------------------------------
# 冷启动判定：析取准则 [论文 2.5节 + Appendix H.2]
# ---------------------------------------------------------------------------

NEW_PRODUCT_WINDOW_DAYS = 90  # ⚙️ 新品期业务定义


@dataclass
class NewProductInput:
    asin: str
    days_since_launch: int
    seller_tenure_years: float = 0.0
    is_merged_into_parent: bool = False
    days_since_parent_merge: Optional[int] = None
    # 析取准则所需的历史特征，对应论文6个特征的简化版（offer级2个 + ASIN级2个）
    offer_gms_90d: float = 0.0
    offer_units_90d: float = 0.0
    asin_gms_90d: float = 0.0
    asin_units_90d: float = 0.0
    collection_start_weekday: str = "周一"


@dataclass
class ColdStartClassification:
    in_new_product_window: bool
    is_cold_start: bool
    offer_level_zero: bool
    asin_level_zero: bool
    cold_start_window_days: int
    merge_risk_flag: bool
    merge_warning: str


def classify_cold_start(
    inp: NewProductInput,
    update_weekday: str = "周三",
    n_update_cycles: int = 2,
) -> ColdStartClassification:
    in_window = inp.days_since_launch <= NEW_PRODUCT_WINDOW_DAYS

    # [论文] 析取准则：offer级或ASIN级任一历史特征为零 -> 冷启动
    offer_level_zero = inp.offer_gms_90d == 0 or inp.offer_units_90d == 0
    asin_level_zero = inp.asin_gms_90d == 0 or inp.asin_units_90d == 0
    is_cold_start = in_window and (offer_level_zero or asin_level_zero)

    window_days = compute_cold_start_window_days(
        inp.collection_start_weekday, update_weekday, n_update_cycles
    )

    # ⚙️ 父体合并风险预警：offer级仍为零，但ASIN级因兄弟变体不再为零，
    # 若下游新品资格判断走ASIN/父体层级而非offer层级，可能被误判为"非新品"
    merge_risk_flag = False
    merge_warning = ""
    if inp.is_merged_into_parent and in_window and offer_level_zero and not asin_level_zero:
        merge_risk_flag = True
        merge_warning = (
            f"该ASIN已并入父体（{inp.days_since_parent_merge}天前），offer级历史仍为零"
            f"（本体从未售出），但ASIN级聚合数据因兄弟变体历史而非零。"
            f"若下游新品资格判断走ASIN/父体层级而非offer层级，该子体可能被误判为"
            f"'非新品'，从而失去新品推荐资格，建议核实该变体是否仍在新品推荐名单中。"
        )

    return ColdStartClassification(
        in_new_product_window=in_window,
        is_cold_start=is_cold_start,
        offer_level_zero=offer_level_zero,
        asin_level_zero=asin_level_zero,
        cold_start_window_days=window_days,
        merge_risk_flag=merge_risk_flag,
        merge_warning=merge_warning,
    )


# ---------------------------------------------------------------------------
# 相似群体估计：余弦相似度 + 分位数聚合 [论文 2.5节 + Algorithm 1，K-Means/FAISS的简化替代]
# ---------------------------------------------------------------------------

@dataclass
class SimilarNewLaunchPeer:
    peer_asin: str
    feature_vector: dict  # 品类/价格/属性等非历史特征，用于相似度计算（不含销量）
    peer_days_since_launch: int
    peer_early_performance: float  # 该peer的早期表现指标（如8天首页订单数/早期转化率），0-1或原始值


@dataclass
class ClusterConfig:
    quantile: float = 0.45  # [论文] q=0.45最优；论文证实均值聚合会使冷启动MAE恶化+1.3%，禁止用均值
    k_neighbors: int = 10   # [论文] k=10最优，局部性是最敏感的超参数（k:100->10，MAE改善-17.4%->-19.1%）
    require_same_cold_start_window: bool = True  # 只与"同样处于新品期"的竞品比较，对应你的核心洞察


def cosine_similarity(a: dict, b: dict) -> float:
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    dot = sum(a[k] * b[k] for k in keys)
    norm_a = math.sqrt(sum(a[k] ** 2 for k in keys))
    norm_b = math.sqrt(sum(b[k] ** 2 for k in keys))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * q
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - f) * (k - f)


def compute_cluster_estimate(
    target_feature_vector: dict,
    peers: list[SimilarNewLaunchPeer],
    config: ClusterConfig = ClusterConfig(),
) -> dict:
    eligible_peers = [
        p for p in peers
        if (not config.require_same_cold_start_window) or (p.peer_days_since_launch <= NEW_PRODUCT_WINDOW_DAYS)
    ]
    scored = sorted(
        ((cosine_similarity(target_feature_vector, p.feature_vector), p) for p in eligible_peers),
        key=lambda x: x[0],
        reverse=True,
    )
    top_k = scored[: config.k_neighbors]

    if not top_k:
        return {
            "cluster_estimate": 0.0,
            "avg_similarity": 0.0,
            "n_peers_used": 0,
            "peer_asins_used": [],
        }

    performances = [p.peer_early_performance for _, p in top_k]
    cluster_estimate = _quantile(performances, config.quantile)
    avg_similarity = sum(s for s, _ in top_k) / len(top_k)

    return {
        "cluster_estimate": round(cluster_estimate, 4),
        "avg_similarity": round(avg_similarity, 4),
        "n_peers_used": len(top_k),
        "peer_asins_used": [p.peer_asin for _, p in top_k],
    }


# ---------------------------------------------------------------------------
# 个体早期信号：SPR类工具代理指标（⚙️ 非论文的真实NCM预测头，仅为代理）
# ---------------------------------------------------------------------------

@dataclass
class EarlySignalInput:
    spr_8day_top_page_orders: int = 0     # SPR体系的8天关键词首页订单数
    observation_windows_elapsed: int = 0   # 已经历过几次系统更新周期
    normalization_cap: int = 20            # ⚙️假设：8天首页订单数达到20单视为强信号封顶


def score_individual_signal(inp: EarlySignalInput) -> float:
    return clamp(inp.spr_8day_top_page_orders / max(inp.normalization_cap, 1))


# ---------------------------------------------------------------------------
# 混合权重：w=0.1/0.9 [论文最优超参数] + ⚙️冷启动期内的爬升扩展
# ---------------------------------------------------------------------------

BASE_COLD_START_INDIVIDUAL_WEIGHT = 0.1  # [论文] w_NCM=0.1，即冷启动预测90%来自群体
WEIGHT_RAMP_PER_WINDOW = 0.15             # ⚙️非论文内容：每经历一次更新周期，个体权重+0.15
WEIGHT_CAP_WITHIN_COLD_START = 0.6        # ⚙️只要仍判定为冷启动，个体权重不超过此值


def effective_individual_weight(observation_windows_elapsed: int, is_cold_start: bool) -> float:
    if not is_cold_start:
        return 1.0  # [论文] 暖启动：直接使用个体信号，不做聚类混合（严格改善保证）
    return clamp(
        BASE_COLD_START_INDIVIDUAL_WEIGHT + WEIGHT_RAMP_PER_WINDOW * observation_windows_elapsed,
        BASE_COLD_START_INDIVIDUAL_WEIGHT,
        WEIGHT_CAP_WITHIN_COLD_START,
    )


# ---------------------------------------------------------------------------
# 老店铺加权（⚙️ 纯业务假设，论文仅将卖家经营年限列为协变量，未公开具体加权公式）
# ---------------------------------------------------------------------------

SELLER_TENURE_BONUS_TIERS = [
    (5.0, 0.15),
    (2.0, 0.08),
    (1.0, 0.03),
    (0.0, 0.0),
]


def seller_tenure_bonus(tenure_years: float) -> float:
    for min_years, bonus in SELLER_TENURE_BONUS_TIERS:
        if tenure_years >= min_years:
            return bonus
    return 0.0


# ---------------------------------------------------------------------------
# 聚合器：NPRS Scorer
# ---------------------------------------------------------------------------

@dataclass
class NPRSReport:
    asin: str
    is_cold_start: bool
    in_new_product_window: bool
    cold_start_window_days: int
    individual_signal: float
    individual_weight: float
    cluster_info: dict
    blended_score_raw: float
    seller_tenure_bonus_applied: float
    final_score: float
    tier: str
    merge_risk_flag: bool
    merge_warning: str
    diagnostics: list[str]


def tier_from_score(score: float) -> str:
    if score >= 0.75:
        return "强烈推荐 (High Recommend)"
    if score >= 0.5:
        return "推荐 (Recommend)"
    if score >= 0.25:
        return "观察 (Watch)"
    return "待优化 (Needs Improvement)"


class NPRSScorer:
    """新品推荐强度评分引擎：复刻ColdNet推断时的冷启动混合逻辑"""

    def score(
        self,
        product: NewProductInput,
        target_feature_vector: dict,
        peers: list[SimilarNewLaunchPeer],
        early_signal: EarlySignalInput,
        cluster_config: ClusterConfig = ClusterConfig(),
        update_weekday: str = "周三",
    ) -> NPRSReport:
        classification = classify_cold_start(product, update_weekday=update_weekday)
        cluster_info = compute_cluster_estimate(target_feature_vector, peers, cluster_config)
        individual_signal = score_individual_signal(early_signal)

        w = effective_individual_weight(
            early_signal.observation_windows_elapsed, classification.is_cold_start
        )
        blended_raw = round(
            w * individual_signal + (1 - w) * cluster_info["cluster_estimate"], 4
        )

        bonus = seller_tenure_bonus(product.seller_tenure_years)
        final_score = round(clamp(blended_raw * (1 + bonus)), 4)

        diagnostics = []
        if classification.is_cold_start:
            diagnostics.append(
                f"冷启动状态：个体信号权重{w:.0%}（第{early_signal.observation_windows_elapsed}个更新周期），"
                f"主要依赖{cluster_info['n_peers_used']}个相似新品竞品的早期表现"
                f"（平均相似度{cluster_info['avg_similarity']:.0%}）"
            )
            if cluster_info["n_peers_used"] == 0:
                diagnostics.append("⚠️ 未找到同新品期内的相似竞品，群体估计不可靠，建议扩大竞品池")
            if cluster_info["n_peers_used"] < cluster_config.k_neighbors:
                diagnostics.append(
                    f"⚠️ 相似竞品数量({cluster_info['n_peers_used']})不足k={cluster_config.k_neighbors}，"
                    f"群体估计的稳定性打折扣"
                )
        else:
            diagnostics.append("暖启动状态：直接使用个体信号，不做群体混合")

        if bonus > 0:
            diagnostics.append(f"老店铺加权：经营{product.seller_tenure_years}年，最终分数+{bonus:.0%}")

        if classification.merge_risk_flag:
            diagnostics.append(f"⚠️ {classification.merge_warning}")

        return NPRSReport(
            asin=product.asin,
            is_cold_start=classification.is_cold_start,
            in_new_product_window=classification.in_new_product_window,
            cold_start_window_days=classification.cold_start_window_days,
            individual_signal=individual_signal,
            individual_weight=w,
            cluster_info=cluster_info,
            blended_score_raw=blended_raw,
            seller_tenure_bonus_applied=bonus,
            final_score=final_score,
            tier=tier_from_score(final_score),
            merge_risk_flag=classification.merge_risk_flag,
            merge_warning=classification.merge_warning,
            diagnostics=diagnostics,
        )


def print_report(report: NPRSReport) -> None:
    print(f"\n========== NPRS 新品推荐强度报告：{report.asin} ==========")
    print(f"最终分数：{report.final_score} / 1.0  →  {report.tier}")
    print(f"冷启动状态：{report.is_cold_start}（新品期内：{report.in_new_product_window}，"
          f"计算得出的观察窗口：{report.cold_start_window_days}天）")
    print(f"个体信号：{report.individual_signal}（权重{report.individual_weight:.0%}）")
    print(f"群体估计：{report.cluster_info['cluster_estimate']}"
          f"（权重{1-report.individual_weight:.0%}，用了{report.cluster_info['n_peers_used']}个相似竞品）")
    print(f"混合原始分：{report.blended_score_raw}  老店加成：+{report.seller_tenure_bonus_applied:.0%}")
    print("-" * 60)
    print("诊断信息：")
    for d in report.diagnostics:
        print(f"  - {d}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# 示例运行
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scorer = NPRSScorer()

    # 示例1：典型冷启动新品，验证"周五收录+周三更新=12天窗口"的计算
    print("窗口计算验证：", compute_cold_start_window_days("周五", "周三", n_update_cycles=2), "天（预期12天）")

    product = NewProductInput(
        asin="B0NEWPRODXXX",
        days_since_launch=10,
        seller_tenure_years=3.5,
        is_merged_into_parent=False,
        offer_gms_90d=0.0,
        offer_units_90d=0.0,
        asin_gms_90d=0.0,
        asin_units_90d=0.0,
        collection_start_weekday="周五",
    )

    target_features = {"category_id": 1023, "price_bucket": 3, "material_electric": 1, "capacity_bucket": 2}

    peers = [
        SimilarNewLaunchPeer(
            peer_asin="B0PEER001",
            feature_vector={"category_id": 1023, "price_bucket": 3, "material_electric": 1, "capacity_bucket": 2},
            peer_days_since_launch=15,
            peer_early_performance=0.8,
        ),
        SimilarNewLaunchPeer(
            peer_asin="B0PEER002",
            feature_vector={"category_id": 1023, "price_bucket": 2, "material_electric": 1, "capacity_bucket": 2},
            peer_days_since_launch=20,
            peer_early_performance=0.6,
        ),
        SimilarNewLaunchPeer(
            peer_asin="B0PEER003",
            feature_vector={"category_id": 1023, "price_bucket": 3, "material_electric": 0, "capacity_bucket": 1},
            peer_days_since_launch=200,  # 已脱离新品期，会被排除
            peer_early_performance=0.95,
        ),
    ]

    early_signal = EarlySignalInput(spr_8day_top_page_orders=3, observation_windows_elapsed=1)

    report = scorer.score(product, target_features, peers, early_signal)
    print_report(report)

    print("\n\n--- 示例2：父体合并风险场景 ---")
    product2 = NewProductInput(
        asin="B0MERGEDCHILD",
        days_since_launch=5,
        seller_tenure_years=6.0,
        is_merged_into_parent=True,
        days_since_parent_merge=2,
        offer_gms_90d=0.0,
        offer_units_90d=0.0,
        asin_gms_90d=1500.0,  # 兄弟变体贡献的历史，使ASIN级不再为零
        asin_units_90d=50.0,
        collection_start_weekday="周一",
    )
    report2 = scorer.score(product2, target_features, peers, early_signal)
    print_report(report2)
