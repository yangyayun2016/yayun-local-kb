"""
权重与阈值回归校准工具
================================================
用途：用真实历史数据（各子指标原始得分 vs 实际观测结果）反推PQS/SCS体系中
标了⚙️的工程假设权重与阈值，输出 calibrated_weights.json，
pqs_scorer.py / scs_scorer.py 会在下次运行时自动读取并生效（见 weights_loader.py）。

不校准CDQ顶层权重——那是Amazon官方公开的精确值（30/25/5/15/5/20/0-20），
校准会破坏其准确性。

算法：
  - 权重组（多个子指标 -> 一个综合分）：约束最小二乘回归
    minimize  Σ(Σ w_i * x_i - y)^2
    subject to  w_i >= 0, Σ w_i = 1
    用投影梯度下降（Projected Gradient Descent + 单纯形投影）求解，纯Python实现，
    无需numpy/scipy，可直接在你现有环境运行。
  - 阈值组（如特色品牌达标门槛）：用标签样本（达标/未达标）中"已达标组"的
    分位数（默认10分位，留出安全边际）作为校准阈值，并给出可分性诊断。

用法：
    # 1. 生成训练数据模板
    python3 calibrate_weights.py --template calibration_template.json

    # 2. 填入真实历史数据后运行校准
    python3 calibrate_weights.py --data calibration_data.json --output calibrated_weights.json

    # 3. calibrated_weights.json 与 pqs_scorer.py / scs_scorer.py 放同目录即可自动生效
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# 约束最小二乘：非负 + 和为1（单纯形约束）投影梯度下降
# ---------------------------------------------------------------------------

def _project_to_simplex(v: list[float]) -> list[float]:
    """将向量投影到概率单纯形（非负、和为1）上，标准算法（Duchi et al. 2008）。"""
    n = len(v)
    u = sorted(v, reverse=True)
    cssv = []
    cum = 0.0
    for ui in u:
        cum += ui
        cssv.append(cum)
    theta = (cssv[-1] - 1) / n
    for i in range(n - 1, -1, -1):
        t = (cssv[i] - 1) / (i + 1)
        if u[i] - t > 0:
            theta = t
            break
    return [max(vi - theta, 0.0) for vi in v]


def fit_constrained_weights(
    X: list[list[float]],
    y: list[float],
    n_iter: int = 3000,
    lr: float = 0.3,
) -> tuple[list[float], dict]:
    """
    投影梯度下降求解 minimize ||Xw - y||^2  s.t. w>=0, sum(w)=1
    返回 (权重列表, 诊断信息字典)
    """
    n_samples = len(X)
    n_features = len(X[0])
    w = [1.0 / n_features] * n_features

    for _ in range(n_iter):
        grad = [0.0] * n_features
        for row, target in zip(X, y):
            pred = sum(wi * xi for wi, xi in zip(w, row))
            err = pred - target
            for j in range(n_features):
                grad[j] += 2 * err * row[j] / n_samples
        w = [wi - lr * g for wi, g in zip(w, grad)]
        w = _project_to_simplex(w)

    # 诊断：R^2 与 MAE
    preds = [sum(wi * xi for wi, xi in zip(w, row)) for row in X]
    mean_y = sum(y) / n_samples
    ss_res = sum((yt - yp) ** 2 for yt, yp in zip(y, preds))
    ss_tot = sum((yt - mean_y) ** 2 for yt in y) or 1e-9
    r_squared = 1 - ss_res / ss_tot
    mae = sum(abs(yt - yp) for yt, yp in zip(y, preds)) / n_samples

    diagnostics = {
        "n_samples": n_samples,
        "r_squared": round(r_squared, 4),
        "mae": round(mae, 4),
        "reliable": n_samples >= 20,  # ⚙️经验阈值：样本量<20时校准结果仅供参考
    }
    return w, diagnostics


def calibrate_weight_group(group_key: str, group_data: dict) -> tuple[dict, dict]:
    features = group_data["features"]
    samples = group_data["samples"]
    X = [[s["features"][f] for f in features] for s in samples]
    y = [s["actual_outcome"] for s in samples]

    if len(samples) < 3:
        raise ValueError(f"[{group_key}] 样本数({len(samples)})过少，至少需要3条才能回归，已跳过")

    weights, diagnostics = fit_constrained_weights(X, y)
    calibrated = {f: round(w, 4) for f, w in zip(features, weights)}
    # 归一化修正浮点误差，确保和精确为1
    total = sum(calibrated.values())
    if total > 0:
        calibrated = {k: round(v / total, 4) for k, v in calibrated.items()}
    return calibrated, diagnostics


# ---------------------------------------------------------------------------
# 阈值校准（如特色品牌达标门槛）：基于已达标样本的分位数
# ---------------------------------------------------------------------------

def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * pct
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - f) * (k - f)


def calibrate_threshold_group(group_key: str, group_data: dict, margin_pct: float = 0.10) -> tuple[dict, dict]:
    metrics = group_data["metrics"]
    samples = group_data["samples"]
    achieved = [s["metrics"] for s in samples if s.get("achieved")]
    not_achieved = [s["metrics"] for s in samples if not s.get("achieved")]

    if len(achieved) < 3:
        raise ValueError(f"[{group_key}] '已达标'样本数({len(achieved)})过少，至少需要3条才能校准阈值，已跳过")

    thresholds = {}
    overlap_warnings = []
    for m in metrics:
        achieved_values = [a[m] for a in achieved]
        threshold = _percentile(achieved_values, margin_pct)  # 已达标组的10分位，留安全边际
        thresholds[m] = round(threshold, 4)

        if not_achieved:
            not_achieved_values = [na[m] for na in not_achieved]
            overlap = sum(1 for v in not_achieved_values if v >= threshold)
            if overlap > 0:
                overlap_warnings.append(
                    f"{m}: {overlap}/{len(not_achieved_values)}个'未达标'样本的值 >= 校准阈值，"
                    f"说明该指标单独判定的区分度有限"
                )

    diagnostics = {
        "n_achieved": len(achieved),
        "n_not_achieved": len(not_achieved),
        "overlap_warnings": overlap_warnings,
        "reliable": len(achieved) >= 20,
    }
    return thresholds, diagnostics


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def run_calibration(data_path: Path, output_path: Path) -> None:
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    calibrated_output: dict = {}
    report_lines = ["# 权重/阈值校准报告\n"]

    for group_key, group_data in data.get("weight_groups", {}).items():
        try:
            calibrated, diag = calibrate_weight_group(group_key, group_data)
        except ValueError as e:
            print(f"⚠️  {e}", file=sys.stderr)
            continue

        path_parts = group_key.split(".")
        node = calibrated_output
        for p in path_parts[:-1]:
            node = node.setdefault(p, {})
        node[path_parts[-1]] = calibrated

        reliability = "✅ 样本充足" if diag["reliable"] else "⚠️ 样本量偏少，结果仅供参考"
        report_lines.append(
            f"## [权重组] {group_key}\n"
            f"- 样本数：{diag['n_samples']}（{reliability}）\n"
            f"- R² 拟合优度：{diag['r_squared']}\n"
            f"- MAE 平均绝对误差：{diag['mae']}\n"
            f"- 校准结果：{json.dumps(calibrated, ensure_ascii=False)}\n"
        )

    for group_key, group_data in data.get("thresholds", {}).items():
        try:
            thresholds, diag = calibrate_threshold_group(group_key, group_data)
        except ValueError as e:
            print(f"⚠️  {e}", file=sys.stderr)
            continue

        path_parts = group_key.split(".")
        node = calibrated_output
        for p in path_parts[:-1]:
            node = node.setdefault(p, {})
        node[path_parts[-1]] = thresholds

        reliability = "✅ 样本充足" if diag["reliable"] else "⚠️ 样本量偏少，结果仅供参考"
        warn_text = "\n  - ".join(diag["overlap_warnings"]) if diag["overlap_warnings"] else "无"
        report_lines.append(
            f"## [阈值组] {group_key}\n"
            f"- 已达标样本数：{diag['n_achieved']}，未达标样本数：{diag['n_not_achieved']}（{reliability}）\n"
            f"- 校准结果：{json.dumps(thresholds, ensure_ascii=False)}\n"
            f"- 区分度警告：\n  - {warn_text}\n"
        )

    # 与已有校准文件做深合并，允许分批次、分组校准
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        calibrated_output = deep_merge(existing, calibrated_output)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(calibrated_output, f, ensure_ascii=False, indent=2)

    report_path = output_path.with_suffix(".report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"校准完成，权重文件已写入：{output_path}")
    print(f"校准报告已写入：{report_path}")
    print("将 calibrated_weights.json 与 pqs_scorer.py / scs_scorer.py 放同目录即可自动生效。")


# ---------------------------------------------------------------------------
# 训练数据模板
# ---------------------------------------------------------------------------

def build_template() -> dict:
    return {
        "weight_groups": {
            "pqs.sub_weights.listing_quality": {
                "features": ["idq", "glance_views", "reviews_ratings", "sales_trend"],
                "samples": [
                    {"features": {"idq": 0.8, "glance_views": 0.6, "reviews_ratings": 0.7, "sales_trend": 0.5}, "actual_outcome": 0.72},
                    {"features": {"idq": 0.5, "glance_views": 0.4, "reviews_ratings": 0.5, "sales_trend": 0.3}, "actual_outcome": 0.45},
                    {"features": {"idq": 0.9, "glance_views": 0.8, "reviews_ratings": 0.85, "sales_trend": 0.7}, "actual_outcome": 0.88},
                ],
                "_说明": "actual_outcome 建议填：该ASIN真实的Listing Quality相对表现（0-1归一化），"
                        "可用后台展示的排名/CTR/转化率等指标做归一化代理",
            },
            "scs.weights": {
                "features": ["ranking_badges", "platform_badges", "category_structure", "recommendation_signals"],
                "samples": [
                    {"features": {"ranking_badges": 0.6, "platform_badges": 0.5, "category_structure": 0.9, "recommendation_signals": 0.4}, "actual_outcome": 0.65},
                    {"features": {"ranking_badges": 0.2, "platform_badges": 0.3, "category_structure": 0.8, "recommendation_signals": 0.2}, "actual_outcome": 0.30},
                    {"features": {"ranking_badges": 0.9, "platform_badges": 0.8, "category_structure": 1.0, "recommendation_signals": 0.7}, "actual_outcome": 0.90},
                ],
                "_说明": "actual_outcome 建议填：该ASIN在叶节点内的真实曝光/流量份额（0-1归一化）",
            },
        },
        "thresholds": {
            "scs.featured_brand_thresholds": {
                "metrics": ["brand_review_count", "brand_positive_review_pct", "brand_recent_orders"],
                "samples": [
                    {"metrics": {"brand_review_count": 5200, "brand_positive_review_pct": 0.93, "brand_recent_orders": 11000}, "achieved": True},
                    {"metrics": {"brand_review_count": 6000, "brand_positive_review_pct": 0.94, "brand_recent_orders": 15000}, "achieved": True},
                    {"metrics": {"brand_review_count": 3000, "brand_positive_review_pct": 0.90, "brand_recent_orders": 8000}, "achieved": False},
                ],
                "_说明": "achieved=True 表示该品牌已被亚马逊官方授予Featured Brand标签的真实样本",
            }
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="PQS/SCS 权重与阈值回归校准工具")
    parser.add_argument("--data", type=str, help="训练数据JSON路径")
    parser.add_argument("--output", type=str, default="calibrated_weights.json", help="输出校准权重文件路径")
    parser.add_argument("--template", type=str, help="生成训练数据模板到指定路径，不执行校准")
    args = parser.parse_args()

    if args.template:
        template_path = Path(args.template)
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(build_template(), f, ensure_ascii=False, indent=2)
        print(f"训练数据模板已生成：{template_path}")
        return

    if not args.data:
        print("请指定 --data 训练数据路径，或使用 --template 先生成模板", file=sys.stderr)
        sys.exit(1)

    run_calibration(Path(args.data), Path(args.output))


if __name__ == "__main__":
    main()
