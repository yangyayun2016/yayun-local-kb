from __future__ import annotations

from dataclasses import dataclass
from math import exp, log1p, sqrt
from pathlib import Path
from statistics import median, pstdev
from typing import Any, Dict, Iterable, List, Tuple

import json


HISTORY_FIELDS = [
    "offer_net_ordered_gms_amt_sum_90d",
    "offer_net_ordered_gms_amt_sum_365d",
    "offer_net_shipped_units_sum_90d",
    "offer_net_shipped_units_sum_365d",
    "offer_asin_net_ord_gms_sum_90d",
    "offer_asin_net_ship_units_sum_90d",
]

FEATURE_FIELDS = [
    "price",
    "rating",
    "reviews",
    "inventory_days",
    "bsr_percentile",
    "organic_rank",
    "ad_spend_7d",
    "acos",
    "conversion_rate",
    "buybox_share",
    "category_demand",
    "margin",
    "coupon_rate",
    "content_score",
    "keyword_gap",
    "review_velocity",
    *HISTORY_FIELDS,
]

COLD_CLUSTER_FIELDS = [
    "price",
    "rating",
    "reviews",
    "inventory_days",
    "bsr_percentile",
    "organic_rank",
    "acos",
    "conversion_rate",
    "buybox_share",
    "category_demand",
    "margin",
    "coupon_rate",
    "content_score",
    "keyword_gap",
    "review_velocity",
]


def load_records(data_path: Path) -> List[Dict[str, Any]]:
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-clamp(value, -16, 16)))


def quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def l2_normalize(vector: List[float]) -> List[float]:
    norm = sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


@dataclass
class ModelOutput:
    member: int
    mu0: float
    mu1: float
    propensity: float
    tau: float


class ColdNetEngine:
    """ColdNet-inspired inference engine for Amazon operations decisions.

    The production paper trains neural DragonNet members. This local version keeps
    the same decision structure with deterministic scoring functions so the UI and
    API can run without external ML dependencies.
    """

    M = 10
    K = 20
    NEIGHBORS = 10
    NCM_WEIGHT = 0.1
    Q = 0.45

    def __init__(self, records: List[Dict[str, Any]]) -> None:
        self.records = records
        self.scaler = self._fit_scaler(records, FEATURE_FIELDS)
        self.cluster_scaler = self._fit_scaler(records, COLD_CLUSTER_FIELDS)
        self.reference = self._build_reference(records)
        self.cluster_centers, self.clusters = self._fit_clusters(self.reference)

    def is_cold_start(self, record: Dict[str, Any]) -> bool:
        return any(float(record.get(field, 0) or 0) <= 0 for field in HISTORY_FIELDS)

    def predict_all(self) -> List[Dict[str, Any]]:
        return [self.predict(record) for record in self.records]

    def find_record(self, asin: str) -> Dict[str, Any] | None:
        asin_upper = asin.upper()
        return next((record for record in self.records if record["asin"].upper() == asin_upper), None)

    def predict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        model_outputs = [self._model_member(record, member) for member in range(self.M)]
        median_tau = median([item.tau for item in model_outputs])
        selected = min(model_outputs, key=lambda item: abs(item.tau - median_tau))
        cold_start = self.is_cold_start(record)

        enhanced_mu0 = selected.mu0
        enhanced_mu1 = selected.mu1
        cluster_info = None

        if cold_start:
            cluster_info = self._cluster_enhance(record)
            cluster_baseline = cluster_info["q45_neighbor_outcome"]
            enhanced_mu0 = self.NCM_WEIGHT * selected.mu0 + (1 - self.NCM_WEIGHT) * cluster_baseline
            enhanced_mu1 = self.NCM_WEIGHT * selected.mu1 + (1 - self.NCM_WEIGHT) * cluster_baseline

        cate = enhanced_mu1 - enhanced_mu0
        spread = pstdev([item.tau for item in model_outputs]) if len(model_outputs) > 1 else 0
        confidence = self._confidence(record, selected.propensity, spread, cluster_info)
        score = self._opportunity_score(record, cate, confidence)
        risks = self._risk_flags(record, confidence, cate)
        action = self._recommended_action(record, score, confidence, cate, risks)

        return {
            "asin": record["asin"],
            "product_name": record["product_name"],
            "category": record["category"],
            "stage": record["stage"],
            "cold_start": cold_start,
            "score": round(score, 1),
            "confidence": round(confidence, 1),
            "recommended_action": action,
            "risk_flags": risks,
            "features": self._public_features(record),
            "prediction": {
                "mu0": round(enhanced_mu0, 2),
                "mu1": round(enhanced_mu1, 2),
                "cate": round(cate, 2),
                "raw_ncm_cate": round(selected.tau, 2),
                "propensity": round(selected.propensity, 3),
                "selected_member": selected.member + 1,
                "ensemble_median_cate": round(median_tau, 2),
                "ensemble_spread": round(spread, 2),
                "method": "ColdNet cluster enhancement" if cold_start else "NCM median ensemble",
            },
            "cluster": cluster_info,
            "playbook": self._playbook(record, score, confidence, cate, risks),
        }

    def dashboard(self) -> Dict[str, Any]:
        predictions = self.predict_all()
        cold_count = sum(1 for item in predictions if item["cold_start"])
        high_confidence = [item for item in predictions if item["score"] >= 70 and item["confidence"] >= 60]
        risk_items = [item for item in predictions if item["risk_flags"]]
        total_cate = sum(max(0, item["prediction"]["cate"]) for item in predictions)
        avg_confidence = sum(item["confidence"] for item in predictions) / max(1, len(predictions))
        category_summary: Dict[str, Dict[str, Any]] = {}
        for item in predictions:
            bucket = category_summary.setdefault(
                item["category"],
                {"category": item["category"], "count": 0, "avg_score": 0.0, "avg_cate": 0.0},
            )
            bucket["count"] += 1
            bucket["avg_score"] += item["score"]
            bucket["avg_cate"] += item["prediction"]["cate"]
        for bucket in category_summary.values():
            bucket["avg_score"] = round(bucket["avg_score"] / bucket["count"], 1)
            bucket["avg_cate"] = round(bucket["avg_cate"] / bucket["count"], 2)

        lanes = {
            "进攻": [p for p in predictions if p["score"] >= 80 and p["confidence"] >= 65],
            "验证": [p for p in predictions if 62 <= p["score"] < 80],
            "修复": [p for p in predictions if p["score"] < 62 or p["risk_flags"]],
        }

        return {
            "metrics": {
                "total_asins": len(predictions),
                "cold_start_asins": cold_count,
                "cold_start_rate": round(cold_count / max(1, len(predictions)) * 100, 1),
                "high_confidence_actions": len(high_confidence),
                "risk_queue": len(risk_items),
                "avg_confidence": round(avg_confidence, 1),
                "projected_increment": round(total_cate, 1),
            },
            "algorithm": {
                "ensemble_members": self.M,
                "clusters": self.K,
                "neighbors": self.NEIGHBORS,
                "ncm_weight": self.NCM_WEIGHT,
                "quantile": self.Q,
                "cold_start_rule": "任一 90/365 天历史活动字段为 0 即判定冷启动",
            },
            "top_opportunities": sorted(predictions, key=lambda item: item["score"], reverse=True)[:5],
            "category_summary": sorted(category_summary.values(), key=lambda item: item["avg_score"], reverse=True),
            "lanes": {key: [self._lane_item(item) for item in value[:6]] for key, value in lanes.items()},
        }

    def simulate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        base = dict(self.records[0])
        base.update(
            {
                "asin": payload.get("asin") or "SIM-NEW-ASIN",
                "product_name": payload.get("product_name") or "模拟 ASIN",
                "category": payload.get("category") or "Simulation",
                "stage": payload.get("stage") or "策略模拟",
            }
        )
        for field in FEATURE_FIELDS:
            if field in payload:
                base[field] = payload[field]
        return self.predict(base)

    def _public_features(self, record: Dict[str, Any]) -> Dict[str, Any]:
        keys = [
            "price",
            "rating",
            "reviews",
            "inventory_days",
            "organic_rank",
            "acos",
            "conversion_rate",
            "margin",
            "content_score",
            "keyword_gap",
        ]
        return {key: record.get(key) for key in keys}

    def _fit_scaler(self, records: List[Dict[str, Any]], fields: Iterable[str]) -> Dict[str, Tuple[float, float]]:
        scaler: Dict[str, Tuple[float, float]] = {}
        for field in fields:
            values = [self._transform_raw_value(field, float(record.get(field, 0) or 0)) for record in records]
            positive = [value for value in values if value > 0]
            low = min(positive) if positive else 0.0
            high = quantile(positive, 0.995) if len(positive) > 2 else (max(positive) if positive else 1.0)
            scaler[field] = (low, max(high, low + 1e-6))
        return scaler

    def _scale_value(self, field: str, value: float, scaler: Dict[str, Tuple[float, float]]) -> float:
        transformed = self._transform_raw_value(field, value)
        if transformed <= 0:
            return 0.0
        low, high = scaler[field]
        clipped = min(transformed, high)
        return clamp(2.5 * (clipped - low) / (high - low), 0.0, 2.5)

    def _transform_raw_value(self, field: str, value: float) -> float:
        if field in {"reviews", "organic_rank", "ad_spend_7d", *HISTORY_FIELDS}:
            return log1p(max(0.0, value))
        if field == "content_score":
            return value / 100.0
        return value

    def _vector(self, record: Dict[str, Any], fields: List[str], scaler: Dict[str, Tuple[float, float]]) -> List[float]:
        return [self._scale_value(field, float(record.get(field, 0) or 0), scaler) for field in fields]

    def _model_member(self, record: Dict[str, Any], member: int) -> ModelOutput:
        x = self._vector(record, FEATURE_FIELDS, self.scaler)
        feature = dict(zip(FEATURE_FIELDS, x))
        jitter = (member - (self.M - 1) / 2) / self.M
        cold_penalty = 0.18 if self.is_cold_start(record) else 0.0

        demand = 0.24 * feature["category_demand"] + 0.18 * feature["conversion_rate"] + 0.16 * feature["keyword_gap"]
        trust = 0.2 * feature["rating"] + 0.12 * feature["reviews"] + 0.1 * feature["content_score"]
        economics = 0.22 * feature["margin"] + 0.1 * feature["buybox_share"] - 0.14 * feature["acos"]
        operations = 0.1 * feature["inventory_days"] - 0.08 * feature["bsr_percentile"] - 0.08 * feature["organic_rank"]
        history = 0.05 * sum(feature[field] for field in HISTORY_FIELDS) / len(HISTORY_FIELDS)

        propensity_raw = -1.25 + 0.42 * demand + 0.28 * trust + 0.24 * economics + 0.18 * history - 0.15 * cold_penalty
        propensity = clamp(sigmoid(propensity_raw + jitter * 0.24), 0.025, 0.975)

        base = 36 + 18 * demand + 14 * trust + 16 * economics + 9 * operations + 8 * history
        base = max(0.0, base * (1 - cold_penalty * 0.55) + jitter * 2.4)

        uplift_signal = (
            18 * feature["keyword_gap"]
            + 12 * feature["category_demand"]
            + 10 * feature["coupon_rate"]
            + 9 * feature["content_score"]
            + 7 * feature["margin"]
            - 8 * feature["acos"]
            - 5 * feature["bsr_percentile"]
            - 6 * max(0.0, 0.7 - feature["inventory_days"])
        )
        causal_correction = 1 + (0.5 - abs(propensity - 0.5)) * 0.18
        uplift = max(-8.0, (uplift_signal - 12.5) * causal_correction + jitter * 1.8)

        mu0 = max(0.0, base)
        mu1 = max(0.0, base + uplift)
        return ModelOutput(member=member, mu0=mu0, mu1=mu1, propensity=propensity, tau=mu1 - mu0)

    def _observed_outcome_proxy(self, record: Dict[str, Any], variant: int) -> float:
        demand = float(record.get("category_demand", 0))
        conversion = float(record.get("conversion_rate", 0))
        margin = float(record.get("margin", 0))
        content = float(record.get("content_score", 0)) / 100.0
        inventory = min(float(record.get("inventory_days", 0)) / 45.0, 1.4)
        price = float(record.get("price", 0))
        reviews = log1p(float(record.get("reviews", 0))) / 7
        seasonal = 1 + ((variant % 5) - 2) * 0.045
        outcome = (price * 0.42 + 54 * demand + 26 * conversion + 18 * margin + 12 * content + 9 * reviews)
        return max(4.0, outcome * max(0.35, inventory) * seasonal)

    def _build_reference(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        reference: List[Dict[str, Any]] = []
        for index, record in enumerate(records):
            for variant in range(8):
                synthetic = dict(record)
                factor = 1 + ((variant % 4) - 1.5) * 0.055
                synthetic["price"] = max(6.99, float(record["price"]) * factor)
                synthetic["rating"] = clamp(float(record["rating"]) + ((variant % 3) - 1) * 0.08, 3.4, 4.9)
                synthetic["reviews"] = max(0, float(record["reviews"]) * (1 + ((variant % 5) - 2) * 0.12))
                synthetic["inventory_days"] = max(3, float(record["inventory_days"]) + (variant - 3) * 3)
                synthetic["organic_rank"] = max(1, float(record["organic_rank"]) + (variant - 4) * 5)
                synthetic["acos"] = clamp(float(record["acos"]) + ((variant % 4) - 1.5) * 0.035, 0.08, 0.85)
                synthetic["conversion_rate"] = clamp(float(record["conversion_rate"]) * (1 + ((variant % 3) - 1) * 0.08), 0.015, 0.22)
                vector = self._vector(synthetic, COLD_CLUSTER_FIELDS, self.cluster_scaler)
                reference.append(
                    {
                        "asin": record["asin"],
                        "vector": vector,
                        "unit": l2_normalize(vector),
                        "outcome": self._observed_outcome_proxy(synthetic, index + variant),
                    }
                )
        return reference

    def _fit_clusters(self, reference: List[Dict[str, Any]]) -> Tuple[List[List[float]], Dict[int, List[Dict[str, Any]]]]:
        if not reference:
            return [], {}
        k = min(self.K, len(reference))
        centers = [list(reference[int(i * len(reference) / k)]["vector"]) for i in range(k)]
        assignments = [0 for _ in reference]
        for _ in range(18):
            for idx, item in enumerate(reference):
                assignments[idx] = min(range(k), key=lambda cluster: self._distance(item["vector"], centers[cluster]))
            for cluster in range(k):
                members = [reference[idx]["vector"] for idx, assigned in enumerate(assignments) if assigned == cluster]
                if not members:
                    continue
                centers[cluster] = [sum(values) / len(values) for values in zip(*members)]
        clusters: Dict[int, List[Dict[str, Any]]] = {cluster: [] for cluster in range(k)}
        for idx, item in enumerate(reference):
            clusters[assignments[idx]].append(item)
        return centers, clusters

    def _distance(self, a: List[float], b: List[float]) -> float:
        return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def _cluster_enhance(self, record: Dict[str, Any]) -> Dict[str, Any]:
        vector = self._vector(record, COLD_CLUSTER_FIELDS, self.cluster_scaler)
        nearest_cluster = min(range(len(self.cluster_centers)), key=lambda idx: self._distance(vector, self.cluster_centers[idx]))
        query = l2_normalize(vector)
        candidates = self.clusters.get(nearest_cluster, [])
        ranked = sorted(candidates, key=lambda item: cosine(query, item["unit"]), reverse=True)
        neighbors = ranked[: self.NEIGHBORS] or ranked
        outcomes = [item["outcome"] for item in neighbors]
        return {
            "cluster_id": nearest_cluster + 1,
            "neighbors": len(neighbors),
            "q45_neighbor_outcome": round(quantile(outcomes, self.Q), 2),
            "avg_similarity": round(sum(cosine(query, item["unit"]) for item in neighbors) / max(1, len(neighbors)), 3),
            "reference_asins": list(dict.fromkeys(item["asin"] for item in neighbors))[:4],
        }

    def _confidence(
        self,
        record: Dict[str, Any],
        propensity: float,
        spread: float,
        cluster_info: Dict[str, Any] | None,
    ) -> float:
        completeness = 1 - sum(1 for field in HISTORY_FIELDS if float(record.get(field, 0) or 0) <= 0) / len(HISTORY_FIELDS)
        overlap = 1 - abs(propensity - 0.5) * 2
        cluster_quality = cluster_info["avg_similarity"] if cluster_info else 0.86
        spread_penalty = min(spread / 20, 0.45)
        score = 38 + 22 * overlap + 18 * cluster_quality + 14 * completeness - 18 * spread_penalty
        if self.is_cold_start(record):
            score -= 4
        return clamp(score, 28, 96)

    def _opportunity_score(self, record: Dict[str, Any], cate: float, confidence: float) -> float:
        demand = float(record.get("category_demand", 0))
        margin = float(record.get("margin", 0))
        inventory = clamp(float(record.get("inventory_days", 0)) / 45.0, 0, 1.3)
        content = float(record.get("content_score", 0)) / 100.0
        risk_drag = max(0, float(record.get("acos", 0)) - 0.45) * 42
        score = 42 + cate * 1.7 + demand * 12 + margin * 10 + inventory * 6 + content * 7 + confidence * 0.12 - risk_drag
        return clamp(score, 0, 100)

    def _risk_flags(self, record: Dict[str, Any], confidence: float, cate: float) -> List[str]:
        risks: List[str] = []
        if float(record.get("inventory_days", 0)) < 18:
            risks.append("库存覆盖不足")
        if float(record.get("acos", 0)) > 0.55:
            risks.append("广告 ACOS 偏高")
        if float(record.get("rating", 0)) < 4.1:
            risks.append("评分低于安全线")
        if float(record.get("content_score", 0)) < 70:
            risks.append("Listing 内容薄弱")
        if confidence < 55:
            risks.append("模型置信度偏低")
        if cate < 0:
            risks.append("处理效应为负")
        return risks

    def _recommended_action(
        self,
        record: Dict[str, Any],
        score: float,
        confidence: float,
        cate: float,
        risks: List[str],
    ) -> str:
        if "库存覆盖不足" in risks:
            return "先补库存，再放量"
        if "处理效应为负" in risks:
            return "暂停加预算，做Listing修复"
        if score >= 82 and confidence >= 66:
            return "进攻：优惠券 + 精准广告冷启动"
        if score >= 68:
            return "验证：小预算关键词测试"
        if float(record.get("acos", 0)) > 0.55:
            return "止损：收缩高花费词"
        return "修复：补内容、评测与转化"

    def _playbook(
        self,
        record: Dict[str, Any],
        score: float,
        confidence: float,
        cate: float,
        risks: List[str],
    ) -> List[Dict[str, str]]:
        if "处理效应为负" in risks:
            return [
                {"step": "冻结放量", "owner": "广告", "detail": "关闭高 ACOS 词，保留品牌防守。"},
                {"step": "补齐信号", "owner": "运营", "detail": "先补主图、A+、评价结构，再复测。"},
                {"step": "7 天复盘", "owner": "数据", "detail": "观察转化率和自然排名是否回到安全线。"},
            ]
        if score >= 80:
            return [
                {"step": "24 小时", "owner": "广告", "detail": "启动精准词和竞品 ASIN 小预算验证。"},
                {"step": "3 天", "owner": "运营", "detail": "设置 5%-10% 优惠券，监控转化和库存。"},
                {"step": "7 天", "owner": "负责人", "detail": "若 CATE 与置信度稳定，扩大预算 30%。"},
            ]
        if confidence < 58:
            return [
                {"step": "补数据", "owner": "运营", "detail": "优先补历史销量、评价和关键词表现信号。"},
                {"step": "小样本测试", "owner": "广告", "detail": "用 3-5 个核心词做低预算实验。"},
                {"step": "再评分", "owner": "数据", "detail": "48 小时后重新计算 ColdNet 机会分。"},
            ]
        return [
            {"step": "关键词", "owner": "广告", "detail": "扩展转化词，减少泛流量。"},
            {"step": "转化", "owner": "运营", "detail": "优化首图、价格锚点和优惠券强度。"},
            {"step": "监控", "owner": "负责人", "detail": "跟踪 CATE、ACOS、库存天数三条线。"},
        ]

    def _lane_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "asin": item["asin"],
            "name": item["product_name"],
            "score": item["score"],
            "cate": item["prediction"]["cate"],
            "action": item["recommended_action"],
        }
