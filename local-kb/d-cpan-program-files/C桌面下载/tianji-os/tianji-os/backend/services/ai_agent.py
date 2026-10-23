"""
天机智能决策OS - AI Agent 层
- 老板日报 Agent
- 广告诊断 Agent（规则引擎 + AI 生成建议）
配置 ANTHROPIC_API_KEY 后启用真实大模型；未配置时走规则引擎本地输出。
"""
import os
from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
import models as m

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("TIANJI_MODEL", "claude-sonnet-4-6")


def _llm(system: str, user: str) -> str | None:
    if not ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(model=MODEL, max_tokens=1500, system=system,
                                     messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in msg.content if b.type == "text")
    except Exception:
        return None


# ---------- 广告止损规则引擎（公司方法论，防止模型自由发挥） ----------

STOP_LOSS_RULES = [
    {"name": "无单止损", "cond": lambda s: s["clicks"] >= 35 and s["orders"] == 0,
     "action": "暂停活动并否定关键词"},
    {"name": "高ACOS止损", "cond": lambda s: s["sales"] > 0 and s["acos"] > 100,
     "action": "出价下调30%，复查搜索词报告"},
    {"name": "ACOS超标", "cond": lambda s: s["sales"] > 0 and 35 < s["acos"] <= 100,
     "action": "出价下调15-20%，否定高花费低转化搜索词"},
    {"name": "高曝光低点击", "cond": lambda s: s["impressions"] > 8000 and s["ctr"] < 0.25,
     "action": "检查主图与价格竞争力，必要时更换广告素材"},
]


def diagnose_ads(db: Session, days: int = 7) -> list[dict]:
    since = date.today() - timedelta(days=days)
    rows = (db.query(m.AdsDaily.campaign_id, m.AdsDaily.campaign_name,
                     func.sum(m.AdsDaily.impressions).label("impressions"),
                     func.sum(m.AdsDaily.clicks).label("clicks"),
                     func.sum(m.AdsDaily.spend).label("spend"),
                     func.sum(m.AdsDaily.sales).label("sales"),
                     func.sum(m.AdsDaily.orders).label("orders"))
            .filter(m.AdsDaily.date >= since)
            .group_by(m.AdsDaily.campaign_id, m.AdsDaily.campaign_name).all())
    findings = []
    for r in rows:
        s = {"impressions": r.impressions or 0, "clicks": r.clicks or 0,
             "spend": round(r.spend or 0, 2), "sales": round(r.sales or 0, 2),
             "orders": r.orders or 0}
        s["acos"] = round(s["spend"] / s["sales"] * 100, 1) if s["sales"] else 999
        s["ctr"] = round(s["clicks"] / s["impressions"] * 100, 2) if s["impressions"] else 0
        for rule in STOP_LOSS_RULES:
            if rule["cond"](s):
                findings.append({"campaign_id": r.campaign_id, "campaign": r.campaign_name,
                                 "rule": rule["name"], "action": rule["action"], **s})
                break
    return findings


# ---------- 老板日报 Agent ----------

def generate_daily_report(db: Session) -> dict:
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)

    def day_sales(d):
        r = db.query(func.sum(m.SalesDaily.sales_amount), func.sum(m.SalesDaily.orders),
                     func.sum(m.SalesDaily.gross_profit)).filter(m.SalesDaily.date == d).first()
        return [round(x or 0, 2) for x in r]

    s1, o1, g1 = day_sales(yesterday)
    s0, o0, g0 = day_sales(day_before)
    ad = db.query(func.sum(m.AdsDaily.spend), func.sum(m.AdsDaily.sales)).filter(
        m.AdsDaily.date == yesterday).first()
    spend, ad_sales = round(ad[0] or 0, 2), round(ad[1] or 0, 2)
    acos = round(spend / ad_sales * 100, 1) if ad_sales else 0
    inv_risks = db.query(m.InventoryDaily).filter(m.InventoryDaily.risk_level == "danger").count()
    ad_findings = diagnose_ads(db)

    facts = {
        "date": str(yesterday),
        "sales": s1, "sales_dod": round((s1 - s0) / s0 * 100, 1) if s0 else 0,
        "orders": o1, "gross_profit": g1,
        "ad_spend": spend, "acos": acos,
        "inventory_danger_skus": inv_risks,
        "ads_anomalies": len(ad_findings),
    }

    system = "你是亚马逊企业的老板日报Agent。只基于给定数据写日报，禁止编造。结构：今日经营、异常风险、明日重点动作。中文，120字以内每段。"
    text = _llm(system, f"经营数据：{facts}；广告异常：{ad_findings[:3]}")
    if not text:
        text = (f"【老板日报 {yesterday}】\n"
                f"今日经营：销售额 ${s1:,.0f}（环比{'+' if facts['sales_dod'] >= 0 else ''}{facts['sales_dod']}%），"
                f"订单 {int(o1)} 单，毛利 ${g1:,.0f}。广告花费 ${spend:,.0f}，ACOS {acos}%。\n"
                f"异常风险：{inv_risks} 个SKU断货风险（danger）；{len(ad_findings)} 个广告活动触发止损规则。\n"
                f"明日重点：1) 确认广告止损建议 2) 处理紧急补货 3) 跟踪竞品Coupon动作。")
    return {"facts": facts, "report": text, "ads_findings": ad_findings}
