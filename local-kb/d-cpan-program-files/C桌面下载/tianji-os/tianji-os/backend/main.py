"""
天机智能决策OS - FastAPI 主程序
启动：
  cd backend && python seed.py && uvicorn main:app --host 0.0.0.0 --port 8000
打开：http://localhost:8000
"""
from datetime import date, timedelta, datetime
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db, engine, Base
import models as m
from services import ai_agent, mcp_client, rpa, feishu, scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="天机智能决策OS", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


@app.on_event("startup")
def _startup():
    scheduler.start()


# ====================== 工作台 / 销售中心 ======================

@app.get("/api/dashboard/summary")
def dashboard_summary(days: int = 30, db: Session = Depends(get_db)):
    """近N天驾驶舱核心指标（对齐截图5个KPI卡）"""
    since = date.today() - timedelta(days=days)
    prev_since = since - timedelta(days=days)

    def agg(start, end):
        r = db.query(func.sum(m.SalesDaily.sales_amount), func.sum(m.SalesDaily.orders),
                     func.sum(m.SalesDaily.units), func.sum(m.SalesDaily.gross_profit)
                     ).filter(m.SalesDaily.date >= start, m.SalesDaily.date < end).first()
        return [round(x or 0, 2) for x in r]

    cur = agg(since, date.today())
    prev = agg(prev_since, since)

    def pct(a, b):
        return round((a - b) / b * 100, 1) if b else 0

    return {
        "range": {"start": str(since), "end": str(date.today() - timedelta(days=1))},
        "sales_amount": cur[0], "sales_amount_pct": pct(cur[0], prev[0]),
        "orders": int(cur[1]), "orders_pct": pct(cur[1], prev[1]),
        "daily_avg_sales": round(cur[0] / days, 2),
        "period_units": int(cur[2]),
        "gross_profit": cur[3], "gross_profit_pct": pct(cur[3], prev[3]),
    }


@app.get("/api/dashboard/trend")
def dashboard_trend(days: int = 30, db: Session = Depends(get_db)):
    """销售额 + 毛利润 双线趋势"""
    since = date.today() - timedelta(days=days)
    rows = (db.query(m.SalesDaily.date,
                     func.sum(m.SalesDaily.sales_amount).label("sales"),
                     func.sum(m.SalesDaily.gross_profit).label("profit"))
            .filter(m.SalesDaily.date >= since)
            .group_by(m.SalesDaily.date).order_by(m.SalesDaily.date).all())
    return {"dates": [r.date.strftime("%m-%d") for r in rows],
            "sales": [round(r.sales, 0) for r in rows],
            "profit": [round(r.profit, 0) for r in rows]}


@app.get("/api/sales/products")
def sales_by_product(days: int = 30, db: Session = Depends(get_db)):
    since = date.today() - timedelta(days=days)
    rows = (db.query(m.SalesDaily.asin, m.SalesDaily.sku,
                     func.sum(m.SalesDaily.units).label("units"),
                     func.sum(m.SalesDaily.sales_amount).label("sales"),
                     func.sum(m.SalesDaily.gross_profit).label("profit"),
                     func.avg(m.SalesDaily.conversion_rate).label("cvr"))
            .filter(m.SalesDaily.date >= since)
            .group_by(m.SalesDaily.asin, m.SalesDaily.sku)
            .order_by(func.sum(m.SalesDaily.sales_amount).desc()).all())
    titles = {p.asin: p.title for p in db.query(m.Product).all()}
    return [{"asin": r.asin, "sku": r.sku, "title": titles.get(r.asin, ""),
             "units": int(r.units), "sales": round(r.sales, 2),
             "profit": round(r.profit, 2), "cvr": round(r.cvr, 2)} for r in rows]


# ====================== 广告中心 ======================

@app.get("/api/ads/campaigns")
def ads_campaigns(days: int = 7, db: Session = Depends(get_db)):
    since = date.today() - timedelta(days=days)
    rows = (db.query(m.AdsDaily.campaign_id, m.AdsDaily.campaign_name,
                     func.sum(m.AdsDaily.impressions).label("imp"),
                     func.sum(m.AdsDaily.clicks).label("clicks"),
                     func.sum(m.AdsDaily.spend).label("spend"),
                     func.sum(m.AdsDaily.sales).label("sales"),
                     func.sum(m.AdsDaily.orders).label("orders"))
            .filter(m.AdsDaily.date >= since)
            .group_by(m.AdsDaily.campaign_id, m.AdsDaily.campaign_name).all())
    out = []
    for r in rows:
        spend, sales = round(r.spend or 0, 2), round(r.sales or 0, 2)
        out.append({"campaign_id": r.campaign_id, "campaign": r.campaign_name,
                    "impressions": int(r.imp), "clicks": int(r.clicks),
                    "spend": spend, "sales": sales, "orders": int(r.orders),
                    "acos": round(spend / sales * 100, 1) if sales else None,
                    "roas": round(sales / spend, 2) if spend else 0})
    return sorted(out, key=lambda x: -x["spend"])


@app.post("/api/ads/diagnose")
def ads_diagnose(db: Session = Depends(get_db)):
    """手动触发广告诊断（闭环2）：规则引擎识别 → 生成待确认任务"""
    findings = ai_agent.diagnose_ads(db)
    created = 0
    for f in findings:
        exists = db.query(m.AITask).filter(
            m.AITask.task_type == "ads_diagnosis",
            m.AITask.title.contains(f["campaign_id"]),
            m.AITask.human_decision == "pending").first()
        if not exists:
            db.add(m.AITask(task_type="ads_diagnosis",
                            title=f"[{f['rule']}] {f['campaign']} ({f['campaign_id']})",
                            ai_result=str(f), suggested_action=f["action"],
                            human_decision="pending", owner="广告组-小王", input_data=f))
            created += 1
    db.commit()
    return {"findings": findings, "tasks_created": created}


# ====================== 库存中心 ======================

@app.get("/api/inventory")
def inventory(db: Session = Depends(get_db)):
    rows = db.query(m.InventoryDaily).order_by(m.InventoryDaily.sellable_days).all()
    return [{"sku": r.sku, "asin": r.asin, "available": r.available_qty,
             "inbound": r.inbound_qty, "daily_avg": r.daily_sales_avg,
             "sellable_days": r.sellable_days, "risk": r.risk_level} for r in rows]


# ====================== 异常事件 / 主动提醒卡片 ======================

@app.get("/api/alerts")
def alerts(status: str = "open", db: Session = Depends(get_db)):
    q = db.query(m.Alert).order_by(m.Alert.created_at.desc())
    if status != "all":
        q = q.filter(m.Alert.status == status)
    return [{"id": a.id, "type": a.alert_type, "level": a.alert_level, "title": a.title,
             "description": a.description, "action": a.suggested_action,
             "owner": a.owner, "status": a.status,
             "created_at": a.created_at.isoformat()} for a in q.all()]


@app.post("/api/alerts/{alert_id}/ack")
def ack_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.query(m.Alert).get(alert_id)
    if not a:
        raise HTTPException(404)
    a.status = "acknowledged"
    db.commit()
    return {"ok": True}


# ====================== AI 任务 / 人机协同 ======================

class Decision(BaseModel):
    decision: str           # approved / rejected
    approver: str = "admin"
    comment: str = ""


@app.get("/api/tasks")
def tasks(db: Session = Depends(get_db)):
    rows = db.query(m.AITask).order_by(m.AITask.created_at.desc()).limit(50).all()
    return [{"id": t.id, "type": t.task_type, "title": t.title,
             "result": t.ai_result, "action": t.suggested_action,
             "decision": t.human_decision, "status": t.execution_status,
             "owner": t.owner, "created_at": t.created_at.isoformat()} for t in rows]


@app.post("/api/tasks/{task_id}/decide")
def decide_task(task_id: int, body: Decision, db: Session = Depends(get_db)):
    """人机协同核心：人确认 → 写审批记录 → RPA 执行 → 回写状态"""
    t = db.query(m.AITask).get(task_id)
    if not t:
        raise HTTPException(404)
    t.human_decision = body.decision
    db.add(m.HumanApproval(task_id=t.id, approver=body.approver,
                           decision=body.decision, comment=body.comment))
    exec_result = None
    if body.decision == "approved" and t.task_type == "ads_diagnosis":
        data = t.input_data or {}
        cid = data.get("campaign_id", "")
        if "暂停" in (t.suggested_action or ""):
            exec_result = rpa.pause_campaign(cid, body.approver)
        elif "否定" in (t.suggested_action or "") or "否词" in (t.suggested_action or ""):
            exec_result = rpa.negate_keyword(cid, data.get("keyword", ""), body.approver)
        elif "出价" in (t.suggested_action or "") or "降价" in (t.suggested_action or ""):
            exec_result = rpa.adjust_bid(cid, data.get("keyword", ""), 0.96, body.approver)
        t.execution_status = "done" if exec_result else "pending"
        t.completed_at = datetime.utcnow()
    elif body.decision == "rejected":
        t.execution_status = "done"
        t.completed_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "rpa": exec_result}


# ====================== 闭环1：老板日报 ======================

@app.post("/api/report/daily")
def daily_report(push: bool = False, db: Session = Depends(get_db)):
    result = ai_agent.generate_daily_report(db)
    if push:
        result["feishu"] = feishu.push_card("📊 老板日报", result["report"].split("\n"), "blue")
    return result


# ====================== Skill / Workflow 中心 ======================

@app.get("/api/skills")
def skills(db: Session = Depends(get_db)):
    return [{"id": s.id, "name": s.skill_name, "type": s.skill_type,
             "description": s.description, "status": s.status}
            for s in db.query(m.Skill).all()]


@app.get("/api/workflows")
def workflows(db: Session = Depends(get_db)):
    return [{"id": w.id, "name": w.workflow_name, "trigger": w.trigger_type,
             "config": w.trigger_config, "steps": w.steps, "status": w.status}
            for w in db.query(m.Workflow).all()]


# ====================== MCP 工具透传 ======================

@app.get("/api/mcp/keyword")
def mcp_keyword(keyword: str):
    return mcp_client.keyword_research(keyword)


@app.get("/api/mcp/competitor")
def mcp_competitor(asin: str):
    return mcp_client.competitor_snapshot(asin)


@app.get("/api/mcp/traffic")
def mcp_traffic(asin: str):
    return mcp_client.asin_traffic_keywords(asin)


# ====================== 前端 ======================

@app.get("/")
def index():
    return FileResponse(FRONTEND / "index.html")


app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")
