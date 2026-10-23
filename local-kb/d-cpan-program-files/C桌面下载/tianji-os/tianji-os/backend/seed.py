"""
天机智能决策OS - 演示数据生成
生成近30天的销售/广告/库存数据 + 异常事件 + AI任务 + Skill + Workflow
"""
import random
from datetime import date, timedelta, datetime
from database import engine, SessionLocal, Base
import models as m

random.seed(42)

ASINS = [
    ("B0CX1A2B3C", "TJ-LED-001", "LED Strip Lights 50ft Smart RGB", "TianjiHome", 9.8, 25.99),
    ("B0DY4E5F6G", "TJ-KIT-002", "Kitchen Scale Digital Stainless", "TianjiHome", 5.2, 16.99),
    ("B0EZ7H8I9J", "TJ-PET-003", "Pet Hair Remover Roller Reusable", "TianjiPet", 3.1, 12.99),
    ("B0FA0K1L2M", "TJ-CAR-004", "Car Trunk Organizer Collapsible", "TianjiAuto", 7.5, 23.99),
    ("B0GB3N4O5P", "TJ-OFF-005", "Desk Cable Management Tray", "TianjiOffice", 4.4, 18.99),
    ("B0HC6Q7R8S", "TJ-OUT-006", "Camping Lantern Rechargeable 4-Pack", "TianjiOutdoor", 11.2, 32.99),
    ("B0ID9T0U1V", "TJ-BAB-007", "Baby Silicone Bibs 3-Pack", "TianjiBaby", 2.8, 13.99),
    ("B0JE2W3X4Y", "TJ-GYM-008", "Resistance Bands Set with Handles", "TianjiFit", 6.6, 21.99),
]

CAMPAIGNS = [
    ("CMP-001", "SP-精准-LED主推", "led strip lights", "exact"),
    ("CMP-002", "SP-广泛-厨房秤", "kitchen scale", "broad"),
    ("CMP-003", "SP-自动-宠物毛刷", "auto", "auto"),
    ("CMP-004", "SB-品牌-车载收纳", "trunk organizer", "phrase"),
    ("CMP-005", "SP-精准-露营灯", "camping lantern rechargeable", "exact"),
    ("CMP-006", "SP-捡漏-长尾词", "cable tray under desk", "exact"),
]


def run():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    store = m.Store(store_name="Tianji-US-Main", marketplace="US", seller_id="A1TIANJI88")
    db.add(store)
    db.flush()

    for asin, sku, title, brand, cost, price in ASINS:
        db.add(m.Product(store_id=store.id, sku=sku, asin=asin, title=title, brand=brand,
                         category="Home & Kitchen", cost=cost, price=price,
                         fba_fee=round(price * 0.18, 2), referral_fee=round(price * 0.15, 2)))

    today = date.today()
    # —— 销售数据：整体上升趋势 + 周末波动，对齐截图 $89,546 / 762单 量级 ——
    for d in range(30, 0, -1):
        day = today - timedelta(days=d)
        weekend = 1.25 if day.weekday() >= 5 else 1.0
        growth = 1 + (30 - d) * 0.018
        for i, (asin, sku, title, brand, cost, price) in enumerate(ASINS):
            base_units = [22, 14, 18, 9, 11, 8, 16, 12][i]
            units = max(0, int(base_units * weekend * growth * random.uniform(0.7, 1.3)))
            orders = max(0, units - random.randint(0, 2))
            sessions = int(units / random.uniform(0.06, 0.14)) if units else random.randint(30, 80)
            sales = round(units * price, 2)
            gp = round(sales - units * (cost + price * 0.33), 2)
            db.add(m.SalesDaily(store_id=store.id, asin=asin, sku=sku, date=day,
                                sessions=sessions, orders=orders, units=units,
                                sales_amount=sales,
                                conversion_rate=round(units / sessions * 100, 2) if sessions else 0,
                                buy_box_rate=round(random.uniform(92, 99), 1),
                                bsr=random.randint(800, 15000),
                                gross_profit=gp, net_profit=round(gp * 0.82, 2)))

    # —— 广告数据：埋入异常（高ACOS / 高点击零转化）供闭环识别 ——
    for d in range(30, 0, -1):
        day = today - timedelta(days=d)
        for cid, cname, kw, mt in CAMPAIGNS:
            imp = random.randint(2000, 18000)
            clicks = int(imp * random.uniform(0.004, 0.02))
            cpc = round(random.uniform(0.45, 1.6), 2)
            spend = round(clicks * cpc, 2)
            if cid == "CMP-006":          # 异常1：持续花钱无单
                orders, sales = 0, 0.0
            elif cid == "CMP-002" and d < 10:   # 异常2：近期ACOS飙升
                orders = max(1, int(clicks * 0.02))
                sales = round(orders * 16.99, 2)
            else:
                orders = int(clicks * random.uniform(0.06, 0.15))
                sales = round(orders * random.uniform(15, 30), 2)
            acos = round(spend / sales * 100, 1) if sales else 999.0
            db.add(m.AdsDaily(store_id=store.id, campaign_id=cid, campaign_name=cname,
                              ad_group_id=f"AG-{cid}", keyword=kw, match_type=mt, date=day,
                              impressions=imp, clicks=clicks, spend=spend, sales=sales,
                              orders=orders, cpc=cpc,
                              ctr=round(clicks / imp * 100, 2) if imp else 0,
                              cvr=round(orders / clicks * 100, 2) if clicks else 0,
                              acos=acos, roas=round(sales / spend, 2) if spend else 0))

    # —— 库存：含断货风险 SKU ——
    risk_map = {"TJ-LED-001": (95, "warning"), "TJ-PET-003": (28, "danger"),
                "TJ-BAB-007": (40, "danger"), "TJ-GYM-008": (160, "warning")}
    for asin, sku, *_ in [(a[0], a[1]) + tuple(a[2:]) for a in ASINS]:
        qty, risk = risk_map.get(sku, (random.randint(400, 900), "normal"))
        avg = round(random.uniform(8, 25), 1)
        db.add(m.InventoryDaily(store_id=store.id, sku=sku, asin=asin, date=today,
                                available_qty=qty, inbound_qty=random.choice([0, 0, 200, 500]),
                                reserved_qty=random.randint(5, 40), daily_sales_avg=avg,
                                sellable_days=round(qty / avg, 1), risk_level=risk))

    # —— 异常事件 ——
    alerts = [
        ("ads_anomaly", "danger", "广告活动 SP-捡漏-长尾词 7天花费$86无订单",
         "CMP-006 近7天点击41次、花费$86.4、0订单，ACOS无限大。", None, "SP-捡漏-长尾词",
         "建议立即暂停该活动，并将关键词加入否定精准。", "广告组-小王"),
        ("ads_anomaly", "warning", "3个广告活动 ACOS 高于目标 30%",
         "CMP-002 近7天ACOS 87%（目标35%）；CMP-004 ACOS 52%；CMP-005 ACOS 48%。", None, "SP-广泛-厨房秤",
         "建议降低 CMP-002 出价20%，对高ACOS搜索词做否词。", "广告组-小王"),
        ("inventory_risk", "danger", "2个SKU预计10天内断货",
         "TJ-PET-003 可售天数1.6天；TJ-BAB-007 可售天数2.4天。", "B0EZ7H8I9J", None,
         "立即创建补货计划（建议海运+空运组合），同时下调对应广告预算30%。", "供应链-小李"),
        ("inventory_risk", "warning", "12个SKU库存低于安全库存",
         "其中4个SKU可售天数低于15天，详见库存中心。", None, None,
         "按可售天数排序逐个确认补货量。", "供应链-小李"),
        ("competitor", "warning", "竞品 B0COMP888 疑似进入放量阶段",
         "近7天Review增长86条，价格下降12%，开启20% Coupon。", "B0CX1A2B3C", None,
         "建议监控其广告坑位与自然排名，必要时跟进Coupon。", "运营-小张"),
        ("listing", "info", "Listing CDQ 巡检：3个ASIN图片得分低于70",
         "B0FA0K1L2M 主图无场景；B0GB3N4O5P 缺少尺寸图；B0ID9T0U1V A+未启用。", "B0FA0K1L2M", None,
         "已生成整改建议稿，待美工排期。", "美工-小陈"),
    ]
    for t, lv, title, desc, asin, cmp_, act, owner in alerts:
        db.add(m.Alert(store_id=store.id, alert_type=t, alert_level=lv, title=title,
                       description=desc, related_asin=asin, related_campaign=cmp_,
                       suggested_action=act, owner=owner))

    # —— AI 任务（人机协同） ——
    tasks = [
        ("daily_report", "生成6月12日老板日报", "done", "approved",
         "今日销售额 $3,386（环比+8.2%），毛利 $812。广告花费 $402，ACOS 31.8%。2个SKU断货风险，已生成补货建议。"),
        ("ads_diagnosis", "暂停 CMP-006 广告活动", "pending", "pending",
         "建议：暂停活动并否定关键词 cable tray under desk（41次点击无转化）。预计每周节省 $86。"),
        ("ads_diagnosis", "CMP-002 出价下调 20%", "pending", "pending",
         "建议：将 kitchen scale 广泛匹配出价由 $1.20 下调至 $0.96，并否定3个高花费搜索词。"),
        ("inventory_check", "TJ-PET-003 紧急补货 800件", "pending", "pending",
         "建议：空运300件（7天到仓）+ 海运500件（25天到仓），断货期间广告预算下调30%。"),
        ("competitor_watch", "竞品 B0COMP888 周度快照", "running", "approved",
         "正在抓取竞品价格/Review/BSR/Coupon数据，预计10分钟后产出对比报告。"),
    ]
    for tt, title, st, hd, result in tasks:
        db.add(m.AITask(task_type=tt, title=title, execution_status=st, human_decision=hd,
                        ai_result=result, suggested_action=result, owner="系统",
                        input_data={"store_id": store.id}))

    # —— Skills ——
    skills = [
        ("广告止损 Skill", "ads", "按公司止损规则（7天35点击无单/ACOS>100%等）输出暂停/否词/降价建议"),
        ("Listing CDQ 打分 Skill", "listing", "按 CDQ 模型对标题/五点/图片/A+/Review 打分并输出修改稿"),
        ("竞品分析 Skill", "competitor", "拆解竞品推广节奏：价格/Review/BSR/Coupon/广告坑位变化"),
        ("关键词打标 Skill", "keyword", "按流量层级/意图/竞争度对关键词自动打标分组"),
        ("选品判断 Skill", "sourcing", "需求/竞争/利润/供应链/风险五维评分，输出进入/观察/放弃结论"),
        ("老板日报 Skill", "report", "汇总销售/毛利/广告/库存/异常，生成结构化日报并推送飞书"),
    ]
    for name, t, desc in skills:
        db.add(m.Skill(skill_name=name, skill_type=t, description=desc,
                       prompt_template=f"你是{name}。严格按公司方法论输出，禁止编造数据。",
                       rule_config={}))

    # —— Workflows（6大自动化闭环） ——
    wfs = [
        ("老板日报自动化", "cron", {"cron": "0 8 * * *"},
         ["拉取昨日数据", "计算核心指标", "识别异常", "AI生成日报", "推送飞书", "等待查看"]),
        ("广告异常自动化", "cron", {"cron": "30 8 * * *"},
         ["拉取广告报表", "计算7/14/30天指标", "匹配止损规则", "AI生成建议", "推送负责人", "人工确认", "RPA执行", "追踪效果"]),
        ("库存预警自动化", "cron", {"cron": "0 9 * * *"},
         ["读取库存+在途", "计算可售天数", "判断断货风险", "生成补货建议", "推送采购"]),
        ("Listing质量巡检", "cron", {"cron": "0 10 * * 1"},
         ["抓取前台Listing", "CDQ模型打分", "找缺失项", "AI生成整改稿", "分配任务"]),
        ("竞品变化监控", "cron", {"cron": "0 11 * * *"},
         ["定时抓竞品", "对比价格/Review/BSR/Coupon", "判断竞品动作", "生成提醒", "推送运营"]),
        ("选品机会发现", "cron", {"cron": "0 14 * * 3"},
         ["抓趋势+关键词", "抓竞品+Review痛点", "供应链匹配", "利润模型", "输出选品评分"]),
    ]
    for name, tt, cfg, steps in wfs:
        db.add(m.Workflow(workflow_name=name, trigger_type=tt, trigger_config=cfg, steps=steps))

    db.commit()
    db.close()
    print("✅ 演示数据已生成")


if __name__ == "__main__":
    run()
