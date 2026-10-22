#!/usr/bin/env python3
"""
关键词评分与投放档位分类工具
输入：关键词列表（CSV格式：keyword,search_volume,relevance,competition,ctr,cvr）
输出：关键词评分表 + 投放优先级分类

评分公式：
  综合评分 = 商业价值(40%) + 广告效率(30%) + 竞争强度(20%) + 流量规模(10%)

用法：
  python keyword_scorer.py --input keywords.csv
  python keyword_scorer.py --demo   # 运行演示数据
"""

import argparse
import csv
import sys
import io


# ─── 投放档位配置 ─────────────────────────────────────
TIERS = [
    {"name": "核心投放",  "min": 80, "budget_pct": "25%~35%", "match": "精准匹配"},
    {"name": "重点投放",  "min": 65, "budget_pct": "15%~25%", "match": "精准+词组"},
    {"name": "正常投放",  "min": 50, "budget_pct": "10%~15%", "match": "词组匹配"},
    {"name": "值得测试",  "min": 35, "budget_pct": "5%~10%",  "match": "宽泛匹配"},
    {"name": "小额测试",  "min": 20, "budget_pct": "<5%",     "match": "宽泛低价"},
    {"name": "暂不投放",  "min":  0, "budget_pct": "0%",      "match": "加否定词"},
]


def get_tier(score):
    for tier in TIERS:
        if score >= tier["min"]:
            return tier
    return TIERS[-1]


def score_keyword(search_volume, relevance, competition_score, ctr, cvr):
    """
    计算综合评分（0-100）
    
    参数：
      search_volume    : 月搜索量（数字）
      relevance        : 相关性（1=弱相关, 2=中相关, 3=强相关）
      competition_score: 竞争强度（1=低, 2=中, 3=高）—— 越低越好，评分时倒置
      ctr              : 预期CTR（小数）
      cvr              : 预期CVR（小数）
    """
    try:
        sv = float(search_volume)
        rel = float(relevance)
        comp = float(competition_score)
        ctr_v = float(ctr)
        cvr_v = float(cvr)
    except (ValueError, TypeError):
        return 0

    # 商业价值（40%）= CVR × 相关性
    business_value = min(100, (cvr_v * 100 * 2.5) * (rel / 3)) * 0.40

    # 广告效率（30%）= CTR × CVR
    ad_efficiency = min(100, ctr_v * 100 * 10 + cvr_v * 100 * 2) * 0.30

    # 竞争强度（20%）= 越低越好，倒置评分
    competition_score_norm = min(100, (4 - comp) / 3 * 100) * 0.20

    # 流量规模（10%）= log10(搜索量) 归一化
    import math
    volume_score = min(100, math.log10(max(sv, 1)) / 5 * 100) * 0.10

    total = business_value + ad_efficiency + competition_score_norm + volume_score
    return round(min(100, total), 1)


DEMO_DATA = [
    {"keyword": "wireless earbuds",          "search_volume": 250000, "relevance": 3, "competition": 3, "ctr": 0.004, "cvr": 0.12},
    {"keyword": "wireless earbuds for gym",  "search_volume": 8000,  "relevance": 3, "competition": 2, "ctr": 0.005, "cvr": 0.18},
    {"keyword": "bluetooth headphones",      "search_volume": 180000,"relevance": 2, "competition": 3, "ctr": 0.003, "cvr": 0.09},
    {"keyword": "noise cancelling earbuds",  "search_volume": 45000, "relevance": 3, "competition": 2, "ctr": 0.005, "cvr": 0.15},
    {"keyword": "earbuds under $30",         "search_volume": 12000, "relevance": 2, "competition": 2, "ctr": 0.004, "cvr": 0.14},
    {"keyword": "best earbuds 2026",         "search_volume": 6000,  "relevance": 2, "competition": 1, "ctr": 0.003, "cvr": 0.10},
    {"keyword": "earbuds for small ears",    "search_volume": 3500,  "relevance": 3, "competition": 1, "ctr": 0.006, "cvr": 0.22},
    {"keyword": "gaming headset",            "search_volume": 95000, "relevance": 1, "competition": 3, "ctr": 0.002, "cvr": 0.05},
    {"keyword": "phone case",                "search_volume": 300000,"relevance": 1, "competition": 3, "ctr": 0.001, "cvr": 0.03},
]


def process_keywords(keywords):
    results = []
    for kw in keywords:
        score = score_keyword(
            kw.get("search_volume", 0),
            kw.get("relevance", 2),
            kw.get("competition", 2),
            kw.get("ctr", 0.003),
            kw.get("cvr", 0.10),
        )
        tier = get_tier(score)
        results.append({
            "keyword":       kw["keyword"],
            "search_volume": kw.get("search_volume", "-"),
            "score":         score,
            "tier":          tier["name"],
            "budget_pct":    tier["budget_pct"],
            "match_type":    tier["match"],
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def format_table(results):
    lines = [
        "",
        "═" * 80,
        "  关键词评分与投放档位分类",
        "═" * 80,
        f"  {'关键词':<30} {'搜索量':>8} {'评分':>6} {'档位':<10} {'预算占比':<10} {'匹配方式'}",
        "─" * 80,
    ]
    for r in results:
        sv = f"{r['search_volume']:,}" if isinstance(r["search_volume"], (int, float)) else str(r["search_volume"])
        lines.append(
            f"  {r['keyword']:<30} {sv:>8} {r['score']:>6.1f} {r['tier']:<10} {r['budget_pct']:<10} {r['match_type']}"
        )

    # 汇总
    tier_counts = {}
    for r in results:
        tier_counts[r["tier"]] = tier_counts.get(r["tier"], 0) + 1

    lines.append("═" * 80)
    lines.append("\n  【档位分布汇总】")
    for tier in TIERS:
        count = tier_counts.get(tier["name"], 0)
        if count > 0:
            lines.append(f"    {tier['name']}: {count} 个关键词  建议预算占比 {tier['budget_pct']}，{tier['match']}投放")

    lines.append("\n  💡 建议：优先保证「核心投放」和「重点投放」词的预算充足，「小额测试」词设置严格日预算上限。")
    lines.append("═" * 80)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="亚马逊广告关键词评分工具")
    parser.add_argument("--input", help="CSV文件路径（列：keyword,search_volume,relevance,competition,ctr,cvr）")
    parser.add_argument("--demo",  action="store_true", help="使用内置演示数据运行")

    args = parser.parse_args()

    if args.demo:
        keywords = DEMO_DATA
    elif args.input:
        keywords = []
        try:
            with open(args.input, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    keywords.append({
                        "keyword":       row.get("keyword", ""),
                        "search_volume": float(row.get("search_volume", 0)),
                        "relevance":     float(row.get("relevance", 2)),
                        "competition":   float(row.get("competition", 2)),
                        "ctr":           float(row.get("ctr", 0.003)),
                        "cvr":           float(row.get("cvr", 0.10)),
                    })
        except FileNotFoundError:
            print(f"错误：找不到文件 {args.input}")
            sys.exit(1)
    else:
        print("请指定 --input <csv文件> 或使用 --demo 运行演示")
        parser.print_help()
        sys.exit(1)

    results = process_keywords(keywords)
    print(format_table(results))


if __name__ == "__main__":
    main()