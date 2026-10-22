#!/usr/bin/env python3
"""
亚马逊广告诊断脚本
输入：用户提供的广告指标数据（ACOS、CTR、CVR、曝光量等）
输出：结构化诊断报告 + 优先操作清单
用法：python diagnose_ads.py --acos 0.45 --ctr 0.003 --cvr 0.08 --impressions 50000 --target-acos 0.25
"""

import argparse
import sys
import json

# ─── 健康范围定义 ─────────────────────────────────────
THRESHOLDS = {
    "acos":        {"healthy": (0.15, 0.35), "warning": 0.50},
    "tacos":       {"healthy": (0.08, 0.15), "warning": 0.20},
    "ctr":         {"healthy": (0.003, 0.005), "warning": 0.001},
    "cvr":         {"healthy": (0.10, 0.25), "warning": 0.05},
    "roas":        {"healthy": (3.0, None), "warning": 2.0},
    "ad_order_pct":{"healthy": (0.30, 0.50), "warning": 0.70},
}

DIAGNOSES = [
    # (曝光, CTR, CVR) → 诊断 + 建议
    ("high",  "low",  "low",  "关键词相关性差或主图吸引力弱",         ["优化主图与标题", "否定不相关词", "检查关键词与产品匹配度"]),
    ("high",  "high", "low",  "Listing承接能力差（详情页问题）",       ["优化价格竞争力", "补充评价数量", "优化A+内容与图片", "检查库存与配送"]),
    ("mid",   "high", "high", "最理想状态，扩大投放",                  ["提高竞价扩大曝光", "增加关键词覆盖", "扩展广告预算"]),
    ("low",   "high", "high", "竞价不足，争取更多曝光",                ["提高竞价 +20%~+30%", "检查预算是否提前耗尽"]),
    ("high",  "low",  "high", "主图/标题需优化，产品质量好",           ["A/B测试主图", "优化搜索页标题前15字", "添加促销标签"]),
    ("any",   "high", "zero", "Listing严重问题",                       ["检查价格竞争力", "检查评价状态", "检查库存/配送时效", "确认ASIN无抑制"]),
    ("low",   "low",  "low",  "竞价过低+关键词不精准",                 ["提高核心词竞价", "优化关键词相关性", "检查是否赢得购物车"]),
]


def classify_metric(value, low_threshold, high_threshold):
    """将指标分类为 low/mid/high"""
    if value < low_threshold:
        return "low"
    elif value > high_threshold:
        return "high"
    return "mid"


def check_status(value, healthy_range, warning):
    """返回状态标记"""
    lo, hi = healthy_range
    if hi is not None and value > hi:
        return "⚠️ 偏高"
    if value < lo:
        if value < warning:
            return "🔴 异常"
        return "⚠️ 偏低"
    return "✅ 正常"


def diagnose(args):
    results = {"metrics": {}, "diagnoses": [], "actions": [], "summary": ""}

    # ─── 1. 指标评估 ──────────────────────────────────
    if args.acos is not None:
        status = check_status(args.acos, THRESHOLDS["acos"]["healthy"], THRESHOLDS["acos"]["warning"])
        results["metrics"]["ACOS"] = {"value": f"{args.acos:.1%}", "status": status}

    if args.ctr is not None:
        status = check_status(args.ctr, THRESHOLDS["ctr"]["healthy"], THRESHOLDS["ctr"]["warning"])
        results["metrics"]["CTR"] = {"value": f"{args.ctr:.2%}", "status": status}

    if args.cvr is not None:
        status = check_status(args.cvr, THRESHOLDS["cvr"]["healthy"], THRESHOLDS["cvr"]["warning"])
        results["metrics"]["CVR"] = {"value": f"{args.cvr:.1%}", "status": status}

    if args.tacos is not None:
        status = check_status(args.tacos, THRESHOLDS["tacos"]["healthy"], THRESHOLDS["tacos"]["warning"])
        results["metrics"]["TACOS"] = {"value": f"{args.tacos:.1%}", "status": status}

    if args.roas is not None:
        status = check_status(args.roas, THRESHOLDS["roas"]["healthy"], THRESHOLDS["roas"]["warning"])
        results["metrics"]["ROAS"] = {"value": f"{args.roas:.1f}x", "status": status}

    # ─── 2. 组合诊断 ──────────────────────────────────
    if args.impressions is not None and args.ctr is not None and args.cvr is not None:
        imp_class = classify_metric(args.impressions, 5000, 50000)
        ctr_class = classify_metric(args.ctr, 0.002, 0.004)
        cvr_class = "zero" if args.cvr == 0 else classify_metric(args.cvr, 0.05, 0.15)

        matched = False
        for imp, ctr, cvr, diag, actions in DIAGNOSES:
            if (imp == "any" or imp == imp_class) and ctr == ctr_class and cvr == cvr_class:
                results["diagnoses"].append(diag)
                results["actions"].extend(actions)
                matched = True
                break

        if not matched:
            results["diagnoses"].append("数据组合未命中预设场景，请参考详细SOP手动诊断")

    # ─── 3. ACOS vs 目标值分析 ────────────────────────
    if args.acos is not None and args.target_acos is not None:
        ratio = args.acos / args.target_acos
        if ratio < 0.8:
            results["actions"].append(f"ACOS低于目标{ratio:.0%}，可考虑提高竞价 +10%~+20% 扩大曝光")
        elif ratio > 1.3:
            results["actions"].append(f"ACOS超目标{ratio:.0%}，建议降低竞价 -10%~-20% 或暂停高消耗无转化词")
        else:
            results["actions"].append("ACOS在目标区间内，保持现有策略，观察趋势")

    # ─── 4. 汇总 ──────────────────────────────────────
    red_count = sum(1 for m in results["metrics"].values() if "🔴" in m["status"])
    warn_count = sum(1 for m in results["metrics"].values() if "⚠️" in m["status"])

    if red_count > 0:
        results["summary"] = f"发现 {red_count} 个异常指标，需立即处理"
    elif warn_count > 0:
        results["summary"] = f"发现 {warn_count} 个指标偏离健康区间，建议本周内优化"
    else:
        results["summary"] = "各指标均在健康区间，保持现有策略并持续监控"

    return results


def format_output(data):
    lines = ["", "═" * 50, "  亚马逊广告诊断报告", "═" * 50, ""]

    if data["metrics"]:
        lines.append("【指标状态】")
        for name, info in data["metrics"].items():
            lines.append(f"  {info['status']}  {name}: {info['value']}")
        lines.append("")

    if data["diagnoses"]:
        lines.append("【诊断结论】")
        for d in data["diagnoses"]:
            lines.append(f"  → {d}")
        lines.append("")

    if data["actions"]:
        lines.append("【优先操作清单】")
        for i, a in enumerate(data["actions"], 1):
            lines.append(f"  {i}. {a}")
        lines.append("")

    lines.append(f"【总结】{data['summary']}")
    lines.append("═" * 50)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="亚马逊广告诊断工具")
    parser.add_argument("--acos",        type=float, help="当前ACOS（小数，如0.35）")
    parser.add_argument("--target-acos", type=float, help="目标ACOS（小数，如0.25）")
    parser.add_argument("--tacos",       type=float, help="当前TACOS（小数）")
    parser.add_argument("--ctr",         type=float, help="当前CTR（小数，如0.003）")
    parser.add_argument("--cvr",         type=float, help="当前CVR（小数，如0.12）")
    parser.add_argument("--roas",        type=float, help="当前ROAS（如3.5）")
    parser.add_argument("--impressions", type=int,   help="近7天曝光量")
    parser.add_argument("--json",        action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    # 至少需要一个指标
    if all(v is None for v in [args.acos, args.ctr, args.cvr, args.tacos, args.roas]):
        print("错误：请至少提供一个广告指标（--acos / --ctr / --cvr / --tacos / --roas）")
        parser.print_help()
        sys.exit(1)

    result = diagnose(args)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()