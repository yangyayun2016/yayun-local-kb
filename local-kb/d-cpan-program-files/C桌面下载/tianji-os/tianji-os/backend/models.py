"""
天机智能决策OS - 核心数据模型
对应文档《亚马逊企业AI系统拆解》第九节的 10 张核心表
"""
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Date, DateTime, Text, JSON)
from database import Base


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    store_name = Column(String(100), nullable=False)
    marketplace = Column(String(20), default="US")
    seller_id = Column(String(50))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, index=True)
    sku = Column(String(80), index=True)
    asin = Column(String(20), index=True)
    title = Column(String(500))
    brand = Column(String(100))
    category = Column(String(200))
    marketplace = Column(String(20), default="US")
    status = Column(String(20), default="active")
    cost = Column(Float, default=0)
    price = Column(Float, default=0)
    fba_fee = Column(Float, default=0)
    referral_fee = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SalesDaily(Base):
    __tablename__ = "sales_daily"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, index=True)
    asin = Column(String(20), index=True)
    sku = Column(String(80))
    date = Column(Date, index=True)
    sessions = Column(Integer, default=0)
    orders = Column(Integer, default=0)
    units = Column(Integer, default=0)
    sales_amount = Column(Float, default=0)
    conversion_rate = Column(Float, default=0)
    buy_box_rate = Column(Float, default=0)
    bsr = Column(Integer, default=0)
    gross_profit = Column(Float, default=0)
    net_profit = Column(Float, default=0)


class AdsDaily(Base):
    __tablename__ = "ads_daily"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, index=True)
    campaign_id = Column(String(50), index=True)
    campaign_name = Column(String(200))
    ad_group_id = Column(String(50))
    keyword = Column(String(200))
    match_type = Column(String(20))
    date = Column(Date, index=True)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0)
    sales = Column(Float, default=0)
    orders = Column(Integer, default=0)
    cpc = Column(Float, default=0)
    ctr = Column(Float, default=0)
    cvr = Column(Float, default=0)
    acos = Column(Float, default=0)
    roas = Column(Float, default=0)


class InventoryDaily(Base):
    __tablename__ = "inventory_daily"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, index=True)
    sku = Column(String(80), index=True)
    asin = Column(String(20))
    date = Column(Date, index=True)
    available_qty = Column(Integer, default=0)
    inbound_qty = Column(Integer, default=0)
    reserved_qty = Column(Integer, default=0)
    daily_sales_avg = Column(Float, default=0)
    sellable_days = Column(Float, default=0)
    risk_level = Column(String(20), default="normal")  # normal / warning / danger


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, index=True)
    alert_type = Column(String(50))    # ads_anomaly / inventory_risk / competitor / listing
    alert_level = Column(String(20))   # info / warning / danger
    title = Column(String(300))
    description = Column(Text)
    related_asin = Column(String(20))
    related_campaign = Column(String(200))
    suggested_action = Column(Text)
    owner = Column(String(50))
    status = Column(String(20), default="open")  # open / acknowledged / resolved
    created_at = Column(DateTime, default=datetime.utcnow)


class AITask(Base):
    __tablename__ = "ai_tasks"
    id = Column(Integer, primary_key=True)
    task_type = Column(String(50))     # daily_report / ads_diagnosis / inventory_check / competitor_watch
    title = Column(String(300))
    input_data = Column(JSON)
    ai_result = Column(Text)
    suggested_action = Column(Text)
    human_decision = Column(String(20))   # pending / approved / rejected / modified
    execution_status = Column(String(20), default="pending")  # pending / running / done / failed
    owner = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    skill_name = Column(String(100))
    skill_type = Column(String(50))
    description = Column(Text)
    input_schema = Column(JSON)
    output_schema = Column(JSON)
    prompt_template = Column(Text)
    rule_config = Column(JSON)
    status = Column(String(20), default="active")


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Integer, primary_key=True)
    workflow_name = Column(String(100))
    trigger_type = Column(String(20))   # cron / event / manual
    trigger_config = Column(JSON)
    steps = Column(JSON)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class HumanApproval(Base):
    __tablename__ = "human_approvals"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, index=True)
    approver = Column(String(50))
    decision = Column(String(20))    # approved / rejected / modified
    comment = Column(Text)
    approved_at = Column(DateTime, default=datetime.utcnow)
