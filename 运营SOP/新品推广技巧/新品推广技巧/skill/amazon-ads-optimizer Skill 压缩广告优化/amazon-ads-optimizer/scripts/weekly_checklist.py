#!/usr/bin/env python3
"""
广告周度操作清单生成器
输入：当前 TACOS、广告订单占比、主推 ASIN 数量、是否大促季
输出：本周优先任务 + 操作时间表
用法：python weekly_checklist.py --tacos 0.18 --ad-order-pct 0.6 --asins 3
"""

import argparse
from datetime import datetime

WEEKDAY_TASKS = {
    "周一": [
        "下载过去7天搜索词报告（Search Term Report）",
        "筛选点击量≥5的词，分类处理（有转化达标/超标/无转化）",
        "添加否定关键词（点击≥15次，0转化的词）",
        "检查ACOS异常词，标记高消耗无转化关键词",
    ],
    "周三": [
        "检查关键词竞价表现报告",
        "对ACOS<目标×0.8的词提价 +10%~+20%",
        "对ACOS>目标×1.3的词降价 -10%~-20%",
        "检查主要关键词广告位排名变化",
    ],
    "周五": [
        "将高转化搜索词升级为手动精准关键词",
        "在自动广告组中否定已升级的词（否定精准）",
        "检查广告预算利用率（目标>80%）",
        "检查库存状态，确保核心ASIN≥15天安全库存",
    ],
    "每日": [
        "检查广告活动状态（是否有暂停/拒审）",
        "检查日预算是否在上午耗尽",
        "检查核心ASIN库存与Featured Offer状态",
    ],
}

MONTHLY_CHECKLIST = {
    "广告结构健康": [
        "广告活动命名规则统一（格式：品类_类型_匹配_日期）",
        "每个广告活动关键词数量 ≤200",
        "无重复关键词在多个手动精准组同时竞争",
        "自动广告组已设置高频否定词",
        "STR流程已执行（高转化自动词已转入手动精准）",
    ],
    "投放效率健康": [
        "TACOS 维持在目标范围内（健康：8%~15%）",
        "广告订单占总订单比例 ≤50%",
        "无长期亏损关键词（ACOS>100% 且点击>50次）",
        "预算利用率 >80%",
    ],
    "Listing承接健康": [
        "主图/标题/价格/库存/评价 无明显异常",
        "A+内容是否需要季度更新",
        "竞品对比：价格/评分/图片是否落后",
        "Brand Store是否按季节更新",
    ],
    "数据合规健康": [
        "所有广告素材符合亚马逊广告政策",
        "ASIN无被抑制（suppressed）状态",
        "账号健康状态保持绿色（ODR<1%）",
    ],
}


def generate_priority_tasks(tacos, ad_order_pct, asins, is_promo):
    """根据输入数据生成优先任务"""
    priority = []

    if tacos is not None and tacos > 0.20:
        priority.append({
            "level": "🔴 紧急",
            "task": f"TACOS={tacos:.1%}，超过警戒线20%",
            "actions": [
                "立即排查高消耗无转化关键词并暂停",
                "检查自动广告否词是否完整",
                "评估是否需要降低非核心词竞价",
            ]
        })
    elif tacos is not None and tacos > 0.15:
        priority.append({
            "level": "⚠️ 关注",
            "task": f"TACOS={tacos:.1%}，偏高，需优化广告结构",
            "actions": [
                "本周重点执行STR转移流程",
                "对低效关键词降价10%",
            ]
        })

    if ad_order_pct is not None and ad_order_pct > 0.70:
        priority.append({
            "level": "⚠️ 关注",
            "task": f"广告订单占比={ad_order_pct:.1%}，广告依赖度过高",
            "actions": [
                "积累关键词自然排名，减少对广告的依赖",
                "优化Listing质量，提升自然转化",
                "检查是否有低价值词占用预算",
            ]
        })

    if is_promo:
        priority.insert(0, {
            "level": "🎯 大促",
            "task": "大促季广告节奏调整",
            "actions": [
                "核心关键词竞价提高 30%~50%",
                "日预算提高至平时 2~3倍",
                "开启/检查 SB/SBV 广告",
                "确认 Lightning Deal/Coupon 已设置",
                "09:00 / 15:00 / 21:00 三次检查预算消耗",
            ]
        })

    if not priority:
        priority.append({
            "level": "✅ 正常",
            "task": "广告指标健康，按常规周期执行操作清单",
            "actions": ["按标准周度时间表操作即可"]
        })

    return priority


def format_checklist(args):
    now = datetime.now()
    lines = [
        "",
        "═" * 55,
        f"  亚马逊广告周度操作清单  {now.strftime('%Y-%m-%d')}",
        "═" * 55,
        "",
    ]

    # 优先任务
    priority = generate_priority_tasks(args.tacos, args.ad_order_pct, args.asins, args.promo)
    lines.append("【本周优先任务】")
    for item in priority:
        lines.append(f"\n  {item['level']}  {item['task']}")
        for a in item["actions"]:
            lines.append(f"    ▸ {a}")
    lines.append("")

    # 周度标准操作
    lines.append("【周度操作时间表】")
    for day, tasks in WEEKDAY_TASKS.items():
        lines.append(f"\n  {day}")
        for t in tasks:
            lines.append(f"    □ {t}")
    lines.append("")

    # 月度复盘提醒
    lines.append("【月度复盘 Checklist（本月末执行）】")
    for category, items in MONTHLY_CHECKLIST.items():
        lines.append(f"\n  ▶ {category}")
        for item in items:
            lines.append(f"    □ {item}")

    lines.append("")
    lines.append("═" * 55)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="亚马逊广告周度操作清单生成器")
    parser.add_argument("--tacos",        type=float, help="当前TACOS（小数，如0.12）")
    parser.add_argument("--ad-order-pct", type=float, help="广告订单占总订单比例（小数，如0.45）")
    parser.add_argument("--asins",        type=int,   default=1, help="主推ASIN数量")
    parser.add_argument("--promo",        action="store_true",   help="是否处于大促季")

    args = parser.parse_args()
    print(format_checklist(args))


if __name__ == "__main__":
    main()