#!/usr/bin/env python3
"""
Amazon PPC Profit Diagnosis Engine
用法示例：
python diagnose.py --files search_term.csv campaign_daily.csv \
  --price 28 --category-cvr 0.09 --category-cpc 0.35 \
  --unit-profit 9 --historical-margin 0.34 \
  --target-acos 0.28 --floor-factor 0.20 --ceiling-factor 0.20 \
  --sacrifice-ratio 1.0 --daily-budget 15 --window-days 7
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "缺少依赖：pandas。请运行 pip install pandas openpyxl"}, ensure_ascii=False))
    sys.exit(1)


# ── 低购买意图词根（中英文场景通用清单，可自行扩展）─────────────────────────────
LOW_INTENT_ROOTS = [
    "free", "used", "second hand", "secondhand", "replacement part",
    "manual", "repair", "diy", "pdf", "instruction", "how to",
    "tutorial", "review", "vs ", " vs", "wholesale", "template",
    "download", "cracked", "broken",
]

# ── 词根提取用停用词（英文简化版）────────────────────────────────────────────
STOPWORDS = {
    "for", "with", "the", "a", "an", "of", "and", "or", "set", "pack",
    "size", "color", "colour", "small", "large", "new", "best", "top",
    "in", "on", "to", "your", "my", "kit", "piece", "pcs", "inch", "cm",
}


# ── 工具函数 ──────────────────────────────────────────────────────────────
def safe_float(val, default=0.0):
    try:
        if isinstance(val, str):
            val = val.replace("$", "").replace(",", "").replace("%", "").strip()
        if val is None or val == "":
            return default
        return float(val)
    except (ValueError, TypeError):
        return default


def load_file(path: str) -> pd.DataFrame:
    p = Path(path)
    ext = p.suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif ext == ".tsv":
        return pd.read_csv(path, sep="\t", thousands=",")
    try:
        return pd.read_csv(path, thousands=",")
    except Exception:
        return pd.read_csv(path, sep="\t", thousands=",")


def detect_file_type(df: pd.DataFrame) -> str:
    cols = {c.lower().strip() for c in df.columns}
    if "customer search term" in cols:
        return "search_term"
    if "gross margin" in cols or "break-even acos" in cols:
        return "profit"
    if "daily budget" in cols and "date" not in cols:
        return "campaign"
    if "date" in cols and ({"spend"} <= cols or {"cost"} <= cols):
        return "daily_trend"
    if "targeting" in cols or "match type" in cols:
        return "targeting"
    return "unknown"


def build_col_map(df: pd.DataFrame) -> dict:
    return {c.lower().strip(): c for c in df.columns}


def has_low_intent(term: str) -> str:
    t = term.lower()
    for root in LOW_INTENT_ROOTS:
        if root in t:
            return root
    return ""


def extract_root(term: str) -> str:
    """极简词根提取：去停用词，取剩余词的核心组合"""
    tokens = re.findall(r"[a-zA-Z]+", term.lower())
    core = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    if not core:
        return term.lower().strip()
    # 简单复数归一
    core = [t[:-1] if t.endswith("s") and len(t) > 3 else t for t in core]
    return " ".join(core[:3])  # 最多取前3个核心词作为词根


# ── 主引擎 ────────────────────────────────────────────────────────────────
class ProfitDiagnosisEngine:
    def __init__(self, price, category_cvr, category_cpc, unit_profit,
                 historical_margin, target_acos, floor_factor, ceiling_factor,
                 sacrifice_ratio, daily_budget, tacos_target, new_product,
                 window_days, min_clicks=20, stop_clicks=35):
        self.price = price
        self.category_cvr = category_cvr
        self.category_cpc = category_cpc
        self.unit_profit = unit_profit
        self.pre_ad_margin = (unit_profit / price) if (unit_profit and price) else None
        self.breakeven_acos = historical_margin if historical_margin else self.pre_ad_margin
        self.target_acos = target_acos
        self.floor = round(target_acos * (1 - floor_factor), 4)
        self.ceiling = round(target_acos * (1 + ceiling_factor), 4)
        self.sacrifice_ratio = sacrifice_ratio
        # 利润口径 Max CPA（核心，用于止损判定）
        self.max_cpa = (unit_profit * sacrifice_ratio) if unit_profit else (price * target_acos)
        # 销售额口径 Max CPA（辅助参考）
        self.max_cpa_sales_based = price * target_acos
        self.affordable_cpc = (self.max_cpa * category_cvr) if category_cvr else None
        self.breakeven_clicks = (1 / category_cvr) if category_cvr else None
        self.daily_budget = daily_budget
        self.tacos_target = tacos_target
        self.new_product = new_product
        self.window_days = window_days
        self.min_clicks = min_clicks
        self.stop_clicks = stop_clicks

        self.action_rows = []      # 止损执行表
        self.scale_up_rows = []    # 待投放清单
        self.review_rows = []      # 人工复核表
        self.bulk_rows = []        # Bulk Sheet 草稿
        self.root_rows = []        # 词根聚合表
        self.diagnosis_rows = []   # 每日诊断指标表
        self.anomaly_rows = []     # 异常问题清单
        self.conclusion = []       # 诊断结论

    # ── 五档分区 ──────────────────────────────────────────────────────────
    def classify_zone(self, acos):
        if acos is None or self.breakeven_acos is None:
            return None
        if acos <= self.floor:
            return "①优质区"
        elif acos <= self.target_acos:
            return "②健康区"
        elif acos <= self.ceiling:
            return "③预警区"
        elif acos <= self.breakeven_acos:
            return "④承压区"
        else:
            return "⑤亏损区"

    # ── 通用：单个对象（搜索词/Target/Campaign）判断 ─────────────────────────
    def _judge_object(self, ctx, is_asin=False, stop_threshold=None):
        clicks, spend, orders, sales = ctx["clicks"], ctx["spend"], ctx["orders"], ctx["sales"]
        term = ctx.get("obj", "")
        stop_threshold = stop_threshold or self.stop_clicks

        # 新品保护
        if self.new_product and clicks < 50 and spend < 2 * self.max_cpa:
            low_root = has_low_intent(term) if term else ""
            if not low_root:
                self._add_action(ctx, "OBSERVE", "新品保护期，数据不足", None, review=False)
                return

        # 明显不相关词（仅搜索词/关键词场景适用）
        if term and orders == 0 and clicks >= 5:
            low_root = has_low_intent(term)
            if low_root:
                self._add_action(ctx, "NEGATIVE_PHRASE*", f"明显低意图词根: {low_root}", "⑤亏损区", review=True)
                self._add_review("High", term, "Negative Phrase", f"词根 '{low_root}' 可能低意图，需人工确认产品匹配性")
                self._add_bulk(ctx, "Negative Keyword", "negativePhrase", "enabled", "", f"低意图词根: {low_root}")
                return

        # 无订单：走点击/花费阈值判断（ACOS 未定义，落入亏损区判断逻辑）
        if orders == 0:
            if clicks >= stop_threshold and spend >= self.max_cpa:
                action = "NEGATIVE_PRODUCT*" if is_asin else ("NEGATIVE_EXACT" if ctx["obj_type"] == "Search Term" else "PAUSE_TARGET")
                review = is_asin or action == "NEGATIVE_EXACT"
                self._add_action(ctx, action, f"{int(clicks)} clicks 0 订单，花费 ${spend:.2f} ≥ 利润口径 Max CPA ${self.max_cpa:.2f}",
                                  "⑤亏损区(0单)", review=review)
                self._add_review("High" if review else "Medium", term or ctx["obj"],
                                  action.replace("*", ""), f"{int(clicks)} clicks 0 订单，超过 Max CPA")
                if action == "NEGATIVE_EXACT":
                    self._add_bulk(ctx, "Negative Keyword", "negativeExact", "enabled", "", f"0 订单花费超 Max CPA")
                elif action == "PAUSE_TARGET":
                    self._add_bulk(ctx, "Keyword", ctx.get("match_type", ""), "paused", "", "0 订单花费超 Max CPA")
                elif action == "NEGATIVE_PRODUCT*":
                    self._add_bulk(ctx, "Product Targeting", "", "paused", "", "ASIN 0 订单花费超 Max CPA")
            elif clicks >= self.min_clicks:
                self._add_action(ctx, "OBSERVE", f"点击 {int(clicks)}，花费未超 Max CPA，未达止损线", "观察区(未达止损线)", review=False)
            else:
                self._add_action(ctx, "OBSERVE", "样本量不足，继续观察", "—", review=False)
            return

        # 有订单：ACOS 五档分区
        acos = spend / sales if sales > 0 else None
        zone = self.classify_zone(acos)
        ctx["acos_val"] = acos

        # 严重亏损优先级最高
        if orders >= 3 and acos is not None and acos > self.target_acos * 2:
            self._add_action(ctx, "PAUSE_TARGET*", f"ACOS {acos*100:.0f}% 超 Target×2，订单≥3", zone, review=True)
            self._add_review("High", term or ctx["obj"], "Pause Target", f"ACOS {acos*100:.0f}% 严重超标")
            return

        if zone == "①优质区":
            self._add_scale_up(ctx, "候选：提bid/转Exact/提预算", zone)
        elif zone == "②健康区":
            self._add_action(ctx, "NO_ACTION", "ACOS 处于健康区，维持现状", zone, review=False)
        elif zone == "③预警区":
            self._add_action(ctx, "OBSERVE+LOWER_BID_10", "ACOS 进入预警区，小幅降 bid 观察", zone, review=False)
        elif zone == "④承压区":
            bid_down = 20 if orders < 3 else 30
            self._add_action(ctx, f"LOWER_BID_{bid_down}", f"ACOS {acos*100:.0f}% 超上调阈值但未破盈亏平衡", zone, review=False)
            self._add_bulk(ctx, "Keyword", ctx.get("match_type", ""), "enabled", "", f"承压区降 bid {bid_down}%")
        elif zone == "⑤亏损区":
            bid_down = 30 if orders < 3 else 50
            self._add_action(ctx, f"LOWER_BID_{bid_down}", f"ACOS {acos*100:.0f}% 超盈亏平衡 {self.breakeven_acos*100:.0f}%，先降价不否定", zone, review=False)
            self._add_bulk(ctx, "Keyword", ctx.get("match_type", ""), "enabled", "", f"亏损区降 bid {bid_down}%")

    # ── 搜索词分析 ────────────────────────────────────────────────────────
    def analyze_search_terms(self, df: pd.DataFrame):
        col_map = build_col_map(df)
        root_agg = {}

        for _, row in df.iterrows():
            term = str(row.get(col_map.get("customer search term", ""), "")).strip()
            campaign = str(row.get(col_map.get("campaign name", ""), ""))
            adgroup = str(row.get(col_map.get("ad group name", ""), ""))
            match_type = str(row.get(col_map.get("match type", ""), ""))
            clicks = safe_float(row.get(col_map.get("clicks", ""), 0))
            spend = safe_float(row.get(col_map.get("spend", ""), 0))
            orders = safe_float(row.get(col_map.get("orders", ""), 0))
            sales = safe_float(row.get(col_map.get("sales", ""), 0))

            if not term or clicks == 0:
                continue

            ctx = dict(campaign=campaign, adgroup=adgroup, obj_type="Search Term",
                       obj=term, match_type=match_type, clicks=clicks, spend=spend,
                       orders=orders, sales=sales)
            self._judge_object(ctx)

            root = extract_root(term)
            r = root_agg.setdefault(root, {"terms": set(), "clicks": 0, "spend": 0, "orders": 0, "sales": 0})
            r["terms"].add(term)
            r["clicks"] += clicks
            r["spend"] += spend
            r["orders"] += orders
            r["sales"] += sales

        for root, agg in root_agg.items():
            acos = agg["spend"] / agg["sales"] if agg["sales"] > 0 else None
            zone = self.classify_zone(acos) if acos is not None else ("⑤亏损区(0单)" if agg["orders"] == 0 and agg["spend"] >= self.max_cpa else "观察区")
            if acos is None:
                suggestion = "整体否定候选" if (agg["orders"] == 0 and agg["spend"] >= self.max_cpa and agg["clicks"] >= self.stop_clicks) else "继续观察"
            elif zone == "①优质区" and agg["orders"] >= 5:
                suggestion = "待投放：新建 Exact/Phrase Campaign 承接"
            elif zone in ("④承压区", "⑤亏损区") and agg["orders"] == 0:
                suggestion = "整体否定候选"
            elif zone in ("④承压区", "⑤亏损区") and agg["orders"] > 0:
                suggestion = "整体降价观察（有转化但超阈值）"
            else:
                suggestion = "维持"
            self.root_rows.append({
                "词根": root, "覆盖搜索词数": len(agg["terms"]),
                "汇总Clicks": int(agg["clicks"]), "汇总Spend": f"${agg['spend']:.2f}",
                "汇总Orders": int(agg["orders"]), "汇总Sales": f"${agg['sales']:.2f}",
                "词根ACOS": f"{acos*100:.0f}%" if acos is not None else "—",
                "分区": zone, "建议操作": suggestion
            })

    # ── Target 分析 ───────────────────────────────────────────────────────
    def analyze_targets(self, df: pd.DataFrame):
        col_map = build_col_map(df)
        for _, row in df.iterrows():
            targeting = str(row.get(col_map.get("targeting", ""), "")).strip()
            campaign = str(row.get(col_map.get("campaign name", ""), ""))
            adgroup = str(row.get(col_map.get("ad group name", ""), ""))
            match_type = str(row.get(col_map.get("match type", ""), ""))
            clicks = safe_float(row.get(col_map.get("clicks", ""), 0))
            spend = safe_float(row.get(col_map.get("spend", ""), 0))
            orders = safe_float(row.get(col_map.get("orders", ""), 0))
            sales = safe_float(row.get(col_map.get("sales", ""), 0))

            if not targeting or clicks == 0:
                continue

            is_asin = targeting.lower().startswith("asin=") or re.match(r"^b0[a-z0-9]{8}$", targeting, re.IGNORECASE)
            ctx = dict(campaign=campaign, adgroup=adgroup,
                       obj_type="ASIN Target" if is_asin else "Keyword Target",
                       obj=targeting, match_type=match_type, clicks=clicks, spend=spend,
                       orders=orders, sales=sales)
            stop_threshold = 30 if is_asin else self.stop_clicks
            self._judge_object(ctx, is_asin=is_asin, stop_threshold=stop_threshold)

    # ── Campaign 分析 ─────────────────────────────────────────────────────
    def analyze_campaigns(self, df: pd.DataFrame):
        col_map = build_col_map(df)
        for _, row in df.iterrows():
            campaign = str(row.get(col_map.get("campaign name", ""), "")).strip()
            budget = safe_float(row.get(col_map.get("daily budget", ""), 0))
            spend = safe_float(row.get(col_map.get("spend", ""), 0))
            orders = safe_float(row.get(col_map.get("orders", ""), 0))
            sales = safe_float(row.get(col_map.get("sales", ""), 0))

            if not campaign or budget == 0:
                continue

            window_budget = budget * self.window_days
            utilization = spend / window_budget if window_budget else 0
            acos = spend / sales if sales > 0 else None
            zone = self.classify_zone(acos)

            ctx = dict(campaign=campaign, adgroup="—", obj_type="Campaign", obj=campaign,
                       match_type="", clicks="—", spend=spend, orders=orders, sales=sales,
                       acos_val=acos)

            if orders == 0 and utilization >= 0.8:
                self._add_action(ctx, "PAUSE_CAMPAIGN*",
                                  f"{self.window_days}天预算 ${window_budget:.0f} 已花 ${spend:.2f}，0 订单", "⑤亏损区", review=True)
                self._add_review("High", campaign, "Pause Campaign", "先检查是否只是少数 Target 在烧钱，避免误关整个 Campaign")
                continue

            if utilization >= 1.0 and zone in ("①优质区", "②健康区"):
                self._add_scale_up(ctx, "预算连续打满且 ACOS 健康，建议提高日预算 20%-50%", zone)
                continue

            if orders >= 2 and acos is not None and acos > self.breakeven_acos:
                self._add_action(ctx, "REDUCE_BUDGET", f"ACOS {acos*100:.0f}% 超盈亏平衡，但有 {int(orders)} 单，先降预算不关停", zone, review=False)
                self._add_bulk(ctx, "Campaign", "", "enabled", f"${budget*0.6:.2f}", "整体亏损降预算 40%")

    # ── 每日趋势诊断 ──────────────────────────────────────────────────────
    def diagnose_daily_trend(self, df: pd.DataFrame, total_sales_col=None):
        col_map = build_col_map(df)
        date_col = col_map.get("date")
        spend_col = col_map.get("spend") or col_map.get("cost")
        sales_col = col_map.get("sales")
        orders_col = col_map.get("orders")
        clicks_col = col_map.get("clicks")
        budget_col = col_map.get("daily budget")

        df = df.copy()
        df["_date"] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=["_date"])
        daily = df.groupby("_date").agg(
            spend=(spend_col, "sum") if spend_col else ("_date", "size"),
            sales=(sales_col, "sum") if sales_col else ("_date", "size"),
            orders=(orders_col, "sum") if orders_col else ("_date", "size"),
            clicks=(clicks_col, "sum") if clicks_col else ("_date", "size"),
        ).sort_index()

        if daily.empty:
            return

        yesterday = daily.index.max()
        window7 = daily[(daily.index < yesterday) & (daily.index >= yesterday - pd.Timedelta(days=7))]
        window30 = daily[(daily.index < yesterday) & (daily.index >= yesterday - pd.Timedelta(days=30))]

        y = daily.loc[yesterday]

        def avg_metrics(w):
            if w.empty:
                return None
            spend = w["spend"].mean()
            sales = w["sales"].mean()
            orders = w["orders"].mean()
            clicks = w["clicks"].mean()
            return dict(spend=spend, sales=sales, orders=orders, clicks=clicks,
                        acos=(spend / sales) if sales else None,
                        cvr=(orders / clicks) if clicks else None,
                        cpc=(spend / clicks) if clicks else None)

        y_metrics = dict(spend=y["spend"], sales=y["sales"], orders=y["orders"], clicks=y["clicks"],
                          acos=(y["spend"] / y["sales"]) if y["sales"] else None,
                          cvr=(y["orders"] / y["clicks"]) if y["clicks"] else None,
                          cpc=(y["spend"] / y["clicks"]) if y["clicks"] else None)
        m7 = avg_metrics(window7)
        m30 = avg_metrics(window30)

        def pct_change(a, b):
            if a is None or b in (None, 0):
                return None
            return (a - b) / b

        def trend_symbol(pct):
            if pct is None:
                return "—"
            if pct >= 0.10:
                return "▲"
            if pct <= -0.10:
                return "▼"
            return "→"

        metric_labels = {"spend": "广告花费", "sales": "广告销售额", "orders": "广告订单",
                          "clicks": "点击量", "acos": "ACOS", "cvr": "CVR", "cpc": "CPC"}
        for key, label in metric_labels.items():
            yv = y_metrics.get(key)
            v7 = m7.get(key) if m7 else None
            v30 = m30.get(key) if m30 else None
            chg7 = pct_change(yv, v7)
            chg30 = pct_change(yv, v30)
            self.diagnosis_rows.append({
                "指标": label,
                "昨日": self._fmt_metric(key, yv),
                "近7日均值": self._fmt_metric(key, v7),
                "近30日均值": self._fmt_metric(key, v30),
                "较7日涨跌": f"{chg7*100:+.0f}%" if chg7 is not None else "—",
                "较30日涨跌": f"{chg30*100:+.0f}%" if chg30 is not None else "—",
                "趋势(vs7日)": trend_symbol(chg7),
            })

        # 结论生成
        spend_chg7 = pct_change(y_metrics["spend"], m7["spend"] if m7 else None)
        orders_chg7 = pct_change(y_metrics["orders"], m7["orders"] if m7 else None)
        acos_chg7 = pct_change(y_metrics["acos"], m7["acos"] if m7 else None)

        if spend_chg7 is not None and spend_chg7 >= 0.30 and (orders_chg7 is None or orders_chg7 < 0.10):
            self.conclusion.append("花费异常放大但订单未跟上，疑似误触发竞价或新词抢量，需要立即核查")
            self.anomaly_rows.append({"异常类型": "花费骤增无转化", "说明": f"昨日花费较7日均值 {spend_chg7*100:+.0f}%，订单未同步上升"})
        if y_metrics["acos"] is not None and self.breakeven_acos is not None and y_metrics["acos"] > self.breakeven_acos and acos_chg7 is not None and acos_chg7 >= 0.20:
            self.conclusion.append("昨日广告已进入亏损区，建议立即执行止损模块")
        if orders_chg7 is not None and orders_chg7 <= -0.30 and (spend_chg7 is None or spend_chg7 > -0.10):
            self.conclusion.append("花费不变但转化骤降，优先检查 Listing / 库存 / 差评 / 竞对动作，而非直接砍广告")
            self.anomaly_rows.append({"异常类型": "转化率骤降", "说明": f"昨日订单较7日均值 {orders_chg7*100:+.0f}%，花费未同步下降"})

        if budget_col and self.daily_budget:
            util = y_metrics["spend"] / self.daily_budget if self.daily_budget else 0
            if util >= 1.0 and y_metrics["acos"] is not None and self.target_acos and y_metrics["acos"] <= self.target_acos:
                self.conclusion.append("预算是当前的增长瓶颈，建议提高日预算或转入待投放模块评估提价")

        if not self.conclusion:
            if y_metrics["acos"] is not None and self.floor is not None and self.target_acos is not None and self.floor < y_metrics["acos"] <= self.target_acos:
                self.conclusion.append("广告运行健康，无需干预")
            else:
                self.conclusion.append("各项指标无显著异常波动，建议结合词根聚合与止损/待投放清单做进一步判断")

    def _fmt_metric(self, key, val):
        if val is None:
            return "—"
        if key in ("acos", "cvr"):
            return f"{val*100:.1f}%"
        if key in ("spend", "sales", "cpc"):
            return f"${val:,.2f}"
        return f"{val:,.1f}"

    # ── 内部：写入各表 ────────────────────────────────────────────────────
    def _add_action(self, ctx, action, reason, zone, review=False):
        acos_val = ctx.get("acos_val")
        self.action_rows.append({
            "Campaign": ctx["campaign"], "Ad Group": ctx["adgroup"],
            "Object Type": ctx["obj_type"], "Object": ctx["obj"],
            "Clicks": ctx["clicks"] if isinstance(ctx["clicks"], str) else int(ctx["clicks"]),
            "Spend": f"${ctx['spend']:.2f}", "Orders": int(ctx["orders"]) if not isinstance(ctx["orders"], str) else ctx["orders"],
            "ACOS": f"{acos_val*100:.0f}%" if acos_val is not None else "—",
            "分区": zone or "—", "Action": action, "Reason": reason,
            "Review Required": "⚠️ Yes" if review else "No",
        })

    def _add_scale_up(self, ctx, action, zone):
        acos_val = ctx.get("acos_val")
        self.scale_up_rows.append({
            "Object Type": ctx["obj_type"], "Object": ctx["obj"],
            "当前匹配方式": ctx.get("match_type", "—") or "—",
            "ACOS": f"{acos_val*100:.0f}%" if acos_val is not None else "—",
            "Orders": int(ctx["orders"]) if not isinstance(ctx["orders"], str) else ctx["orders"],
            "分区": zone, "Action": action,
            "建议幅度": "≤20%（激进模式另行标注）" if self.sacrifice_ratio <= 1.0 else "≤30%（激进模式）",
            "Review Required": "No" if self.sacrifice_ratio <= 1.0 else "⚠️ Yes",
        })

    def _add_review(self, priority, obj, action, reason):
        self.review_rows.append({"Priority": priority, "Object": obj, "Suggested Action": action, "Why Review": reason})

    def _add_bulk(self, ctx, record_type, match_type, state, bid, reason):
        self.bulk_rows.append({
            "Record Type": record_type, "Operation": "Update" if state else "Create",
            "Campaign": ctx["campaign"], "Ad Group": ctx["adgroup"],
            "Keyword/Product Targeting": ctx["obj"], "Match Type": match_type,
            "State": state, "Bid": bid, "Reason": reason,
        })

    # ── 汇总输出 ──────────────────────────────────────────────────────────
    def get_summary(self):
        return {
            "params": {
                "selling_price": self.price,
                "category_cvr": f"{self.category_cvr*100:.1f}%" if self.category_cvr else None,
                "category_cpc": f"${self.category_cpc:.2f}" if self.category_cpc else None,
                "unit_profit_pre_ad": self.unit_profit,
                "breakeven_acos_pct": f"{self.breakeven_acos*100:.1f}%" if self.breakeven_acos else None,
                "target_acos_pct": f"{self.target_acos*100:.1f}%",
                "floor_pct": f"{self.floor*100:.1f}%",
                "ceiling_pct": f"{self.ceiling*100:.1f}%",
                "sacrifice_ratio": f"{self.sacrifice_ratio*100:.0f}%",
                "max_cpa_profit_based": f"${self.max_cpa:.2f}",
                "max_cpa_sales_based": f"${self.max_cpa_sales_based:.2f}",
                "affordable_cpc": f"${self.affordable_cpc:.2f}" if self.affordable_cpc else None,
                "breakeven_clicks": f"{self.breakeven_clicks:.1f}" if self.breakeven_clicks else None,
                "new_product_mode": self.new_product,
            },
            "conclusion": self.conclusion,
            "table_daily_diagnosis": self.diagnosis_rows,
            "table_anomaly": self.anomaly_rows,
            "table_root_clustering": self.root_rows,
            "table1_stop_loss": self.action_rows,
            "table2_scale_up": self.scale_up_rows,
            "table3_review": self.review_rows,
            "table4_bulk_sheet": self.bulk_rows,
        }


def main():
    parser = argparse.ArgumentParser(description="Amazon PPC Profit Diagnosis Engine")
    parser.add_argument("--files", nargs="+", required=True)
    parser.add_argument("--price", type=float, required=True)
    parser.add_argument("--category-cvr", type=float, default=0.0)
    parser.add_argument("--category-cpc", type=float, default=0.0)
    parser.add_argument("--unit-profit", type=float, default=0.0, help="单位毛利（广告前，$）")
    parser.add_argument("--margin", type=float, default=0.0, help="毛利率，未提供 unit-profit 时用它反推")
    parser.add_argument("--historical-margin", type=float, default=0.0, help="历史广告前毛利率，作为 breakeven acos")
    parser.add_argument("--target-acos", type=float, required=True)
    parser.add_argument("--floor-factor", type=float, default=0.20)
    parser.add_argument("--ceiling-factor", type=float, default=0.20)
    parser.add_argument("--sacrifice-ratio", type=float, default=1.0)
    parser.add_argument("--daily-budget", type=float, default=0.0)
    parser.add_argument("--tacos-target", type=float, default=0.0)
    parser.add_argument("--new-product", action="store_true")
    parser.add_argument("--window-days", type=int, default=7)
    parser.add_argument("--min-clicks", type=int, default=20)
    parser.add_argument("--stop-clicks", type=int, default=35)
    args = parser.parse_args()

    errors = []
    if args.price <= 0:
        errors.append("--price 必须大于 0")
    if not (0 < args.target_acos < 3):
        errors.append("--target-acos 必须在合理区间（如 0.25 表示 25%）")
    unit_profit = args.unit_profit if args.unit_profit > 0 else (args.price * args.margin if args.margin > 0 else 0)
    if unit_profit <= 0 and args.historical_margin <= 0:
        errors.append("必须提供 --unit-profit 或 --margin 或 --historical-margin 中至少一项，用于计算盈亏平衡 ACOS")
    if errors:
        print(json.dumps({"error": "参数错误", "details": errors}, ensure_ascii=False, indent=2))
        sys.exit(1)

    engine = ProfitDiagnosisEngine(
        price=args.price, category_cvr=args.category_cvr or None,
        category_cpc=args.category_cpc or None, unit_profit=unit_profit or None,
        historical_margin=args.historical_margin or None, target_acos=args.target_acos,
        floor_factor=args.floor_factor, ceiling_factor=args.ceiling_factor,
        sacrifice_ratio=args.sacrifice_ratio, daily_budget=args.daily_budget or None,
        tacos_target=args.tacos_target or None, new_product=args.new_product,
        window_days=args.window_days, min_clicks=args.min_clicks, stop_clicks=args.stop_clicks,
    )

    loaded = {"search_term": [], "targeting": [], "campaign": [], "daily_trend": [], "profit": [], "unknown": []}
    for fpath in args.files:
        try:
            df = load_file(fpath)
            ftype = detect_file_type(df)
            loaded[ftype].append((fpath, df))
            print(f"✅ 已识别 [{ftype}]：{fpath}", file=sys.stderr)
        except Exception as e:
            print(json.dumps({"error": f"文件读取失败：{fpath}", "detail": str(e)}, ensure_ascii=False))
            sys.exit(1)

    if loaded["unknown"]:
        names = [p for p, _ in loaded["unknown"]]
        print(json.dumps({"warning": f"无法识别文件类型，已跳过：{names}"}, ensure_ascii=False), file=sys.stderr)

    for _, df in loaded["search_term"]:
        engine.analyze_search_terms(df)
    for _, df in loaded["targeting"]:
        engine.analyze_targets(df)
    for _, df in loaded["campaign"]:
        engine.analyze_campaigns(df)
    for _, df in loaded["daily_trend"]:
        engine.diagnose_daily_trend(df)

    print(json.dumps(engine.get_summary(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
