"""
天机智能决策OS - 定时任务（6大自动化闭环的触发器）
APScheduler，跟随 FastAPI 启动。
"""
from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
import models as m
from services import ai_agent, feishu

scheduler = BackgroundScheduler(timezone="America/Los_Angeles")


def job_daily_report():
    """闭环1：老板日报自动化（每天8:00）"""
    db = SessionLocal()
    try:
        result = ai_agent.generate_daily_report(db)
        task = m.AITask(task_type="daily_report", title=f"自动生成老板日报",
                        ai_result=result["report"], suggested_action="推送飞书",
                        execution_status="done", human_decision="approved", owner="系统",
                        input_data=result["facts"])
        db.add(task)
        db.commit()
        feishu.push_card("📊 老板日报", result["report"].split("\n"), "blue")
    finally:
        db.close()


def job_ads_anomaly():
    """闭环2：广告异常自动化（每天8:30）"""
    db = SessionLocal()
    try:
        findings = ai_agent.diagnose_ads(db)
        for f in findings:
            exists = db.query(m.AITask).filter(
                m.AITask.task_type == "ads_diagnosis",
                m.AITask.title.contains(f["campaign_id"]),
                m.AITask.human_decision == "pending").first()
            if not exists:
                db.add(m.AITask(task_type="ads_diagnosis",
                                title=f"[{f['rule']}] {f['campaign']} ({f['campaign_id']})",
                                ai_result=str(f), suggested_action=f["action"],
                                execution_status="pending", human_decision="pending",
                                owner="广告组-小王", input_data=f))
        db.commit()
        if findings:
            feishu.push_card("⚠️ 广告异常提醒",
                             [f"**{x['campaign']}**：{x['rule']}，建议{x['action']}" for x in findings],
                             "warning")
    finally:
        db.close()


def job_inventory_check():
    """闭环3：库存预警自动化（每天9:00）"""
    db = SessionLocal()
    try:
        risks = db.query(m.InventoryDaily).filter(
            m.InventoryDaily.risk_level.in_(["warning", "danger"])).all()
        danger = [r for r in risks if r.risk_level == "danger"]
        if danger:
            feishu.push_card("🚨 库存预警",
                             [f"**{r.sku}** 可售 {r.sellable_days} 天，建议立即补货" for r in danger],
                             "danger")
    finally:
        db.close()


def start():
    scheduler.add_job(job_daily_report, "cron", hour=8, minute=0, id="daily_report")
    scheduler.add_job(job_ads_anomaly, "cron", hour=8, minute=30, id="ads_anomaly")
    scheduler.add_job(job_inventory_check, "cron", hour=9, minute=0, id="inventory_check")
    scheduler.start()
