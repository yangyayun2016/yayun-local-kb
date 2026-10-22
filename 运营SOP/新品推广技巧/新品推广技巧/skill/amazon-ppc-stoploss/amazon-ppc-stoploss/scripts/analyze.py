#!/usr/bin/env python3
"""
Amazon PPC Stop-Loss Analyzer
用法：python analyze.py --files file1.csv file2.csv ... [--price 25] [--margin 0.36] [--target-acos 0.25] [--new-product]
"""

import argparse
import sys
import json
import re
from pathlib import Path

# ── 依赖检查 ──────────────────────────────────────────────────────────────────
try:
    import pandas as pd
except ImportError:
    print(json.dumps({"error": "缺少依赖：pandas。请运行 pip install pandas openpyxl"}))
    sys.exit(1)

# ── 低购买意图词根 ────────────────────────────────────────────────────────────
LOW_INTENT_ROOTS = [
    "free", "used", "second hand", "secondhand", "replacement part",
    "manual", "repair", "diy", "pdf", "instruction", "how to",
    "tutorial", "review", "vs ", " vs", "wholesale", "template",
    "download", "cracked", "broken"
]

# ── 文件类型识别 ──────────────────────────────────────────────────────────────
def detect_file_type(df: pd.DataFrame) -> str:
    cols = {c.lower().strip() for c in df.columns}
    if "customer search term" in cols:
        return "search_term"
    if "daily budget" in cols:
        return "campaign"
    if "targeting" in cols or "match type" in cols:
        return "targeting"
    if "gross margin" in cols or "break-even acos" in cols:
        return "profit"
    return "unknown"


def load_file(path: str) -> pd.DataFrame:
    p = Path(path)
    ext = p.suffix.lower()
    if ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif ext == ".tsv":
        return pd.read_csv(path, sep="\t", thousands=",")
    else:
        # 尝试逗号分隔，失败则制表符
        try:
            return pd.read_csv(path, thousands=",")
        except Exception:
            return pd.read_csv(path, sep="\t", thousands=",")


def safe_float(val, default=0.0):
    try:
        if isinstance(val, str):
            val = val.replace("$", "").replace(",", "").replace("%", "").strip()
        return float(val)
    except (ValueError, TypeError):
        return default


# ── 规则引擎 ──────────────────────────────────────────────────────────────────
class StopLossEngine:
    def __init__(self, price: float, margin: float, target_acos: float,
                 new_product: bool = False, min_clicks: int = 20, stop_clicks: int = 35):
        self.price = price
        self.margin = margin
        self.break_even_acos = margin
        self.target_acos = target_acos
        self.max_cpa = price * target_acos
        self.break_even_cpa = price * margin
        self.new_product = new_product
        self.min_clicks = min_clicks
        self.stop_clicks = stop_clicks

        self.action_rows = []   # 止损执行表
        self.review_rows = []   # 人工复核表
        self.bulk_rows = []     # Bulk Sheet 草稿

    # ── 搜索词分析 ────────────────────────────────────────────────────────────
    def analyze_search_terms(self, df: pd.DataFrame):
        col_map = self._build_col_map(df)

        for _, row in df.iterrows():
            term    = str(row.get(col_map.get("customer search term", ""), "")).strip()
            campaign= str(row.get(col_map.get("campaign name", ""), ""))
            adgroup = str(row.get(col_map.get("ad group name", ""), ""))
            clicks  = safe_float(row.get(col_map.get("clicks", ""), 0))
            spend   = safe_float(row.get(col_map.get("spend", ""), 0))
            orders  = safe_float(row.get(col_map.get("orders", ""), 0))
            sales   = safe_float(row.get(col_map.get("sales", ""), 0))
            impressions = safe_float(row.get(col_map.get("impressions", ""), 1))

            if not term or clicks == 0:
                continue

            acos = (spend / sales * 100) if sales > 0 else None
            acos_str = f"{acos:.0f}%" if acos is not None else "—"

            ctx = dict(campaign=campaign, adgroup=adgroup, obj_type="Search Term",
                       obj=term, clicks=int(clicks), spend=spend,
                       orders=int(orders), sales=sales, acos_str=acos_str)

            # 新品保护
            if self.new_product and clicks < 50 and spend < 2 * self.max_cpa:
                if not self._has_low_intent(term):
                    self._add_action(ctx, "OBSERVE", "新品保护期，数据不足", "1.新品")
                    continue

            # 规则 2：明显不相关词
            if orders == 0 and clicks >= 5:
                low_root = self._has_low_intent(term)
                if low_root:
                    self._add_action(ctx, "NEGATIVE_PHRASE*", f"明显低意图词根: {low_root}", "2.不相关",
                                     review=True)
                    self._add_bulk(campaign, adgroup, "Negative Keyword",
                                   "Create", term, "negativePhrase", "enabled", "",
                                   f"低意图词根: {low_root}")
                    self._add_review("High", term, "Negative Phrase",
                                     f"词根 '{low_root}' 可能低意图，需确认产品匹配性")
                    continue

            # 规则 1：无订单止损
            if orders == 0 and clicks >= self.stop_clicks and spend >= self.max_cpa:
                self._add_action(ctx, "NEGATIVE_EXACT", "无订单，点击超阈值，花费超 Max CPA", "1.无订单超限",
                                 review=True)
                self._add_bulk(campaign, adgroup, "Negative Keyword",
                               "Create", term, "negativeExact", "enabled", "",
                               f"{int(clicks)} clicks 0 订单，花费 ${spend:.2f}")
                self._add_review("High", term, "Negative Exact",
                                 f"{int(clicks)} clicks 0 订单，花费超 Max CPA ${self.max_cpa:.2f}")
                continue

            # 无订单但未达阈值
            if orders == 0 and clicks >= self.min_clicks:
                if spend >= self.max_cpa:
                    self._add_action(ctx, "OBSERVE→即将止损", "点击达到观察线，花费超限，待复核", "观察")
                else:
                    self._add_action(ctx, "OBSERVE", f"点击 {int(clicks)}，花费未超 Max CPA", "5.数据不足")
                continue

            # 规则 3：有订单但亏损
            if orders >= 1 and acos is not None:
                if orders >= 3 and acos > self.target_acos * 200:
                    self._add_action(ctx, "PAUSE_TARGET*", f"ACOS {acos:.0f}% 严重超 Target×2，订单≥3", "3.严重亏损",
                                     review=True)
                    self._add_review("High", term, "Pause Target",
                                     f"ACOS {acos:.0f}% > Target ACOS {self.target_acos*100:.0f}% × 2")
                elif acos > self.break_even_acos * 100:
                    # 降 bid
                    bid_down = 30 if orders < 3 else 50
                    self._add_action(ctx, f"LOWER_BID_{bid_down}", f"有转化但 ACOS {acos:.0f}% 超盈亏线", "3.有单亏损")
                    # 不加 Bulk，bid 调整需按实际数值
                continue

    # ── Target 分析 ───────────────────────────────────────────────────────────
    def analyze_targets(self, df: pd.DataFrame):
        col_map = self._build_col_map(df)

        for _, row in df.iterrows():
            targeting = str(row.get(col_map.get("targeting", ""), "")).strip()
            campaign  = str(row.get(col_map.get("campaign name", ""), ""))
            adgroup   = str(row.get(col_map.get("ad group name", ""), ""))
            match_type= str(row.get(col_map.get("match type", ""), "")).lower()
            clicks    = safe_float(row.get(col_map.get("clicks", ""), 0))
            spend     = safe_float(row.get(col_map.get("spend", ""), 0))
            orders    = safe_float(row.get(col_map.get("orders", ""), 0))
            sales     = safe_float(row.get(col_map.get("sales", ""), 0))
            bid       = safe_float(row.get(col_map.get("bid", ""), 0))

            if not targeting or clicks == 0:
                continue

            acos = (spend / sales * 100) if sales > 0 else None
            acos_str = f"{acos:.0f}%" if acos is not None else "—"
            is_asin = targeting.lower().startswith("asin=") or re.match(r"^b0[a-z0-9]{8}$", targeting, re.IGNORECASE)

            ctx = dict(campaign=campaign, adgroup=adgroup,
                       obj_type="ASIN Target" if is_asin else "Keyword Target",
                       obj=targeting, clicks=int(clicks), spend=spend,
                       orders=int(orders), sales=sales, acos_str=acos_str)

            stop_threshold = 30 if is_asin else self.stop_clicks

            # 规则 5 / 4：无订单超限
            if orders == 0 and clicks >= stop_threshold and spend >= self.max_cpa:
                if is_asin:
                    self._add_action(ctx, "NEGATIVE_PRODUCT*", f"ASIN target {int(clicks)} clicks 0 订单超 Max CPA", "5.ASIN无订单",
                                     review=True)
                    self._add_bulk(campaign, adgroup, "Product Targeting",
                                   "Update", targeting, "", "paused", "",
                                   f"0 订单 ${spend:.2f} 超 Max CPA")
                    self._add_review("High", targeting, "Negative Product",
                                     f"ASIN {int(clicks)} clicks 0 订单，需确认竞品关系")
                else:
                    self._add_action(ctx, "PAUSE_TARGET", f"{int(clicks)} clicks 0 订单超 Max CPA", "4.Target无订单")
                    self._add_bulk(campaign, adgroup, "Keyword",
                                   "Update", targeting, match_type, "paused", "",
                                   f"0 订单 ${spend:.2f} 超 Max CPA")
                continue

            # 有订单但亏损
            if orders >= 1 and acos is not None:
                if orders >= 3 and acos > self.target_acos * 200:
                    self._add_action(ctx, "PAUSE_TARGET*", f"ACOS {acos:.0f}% 严重亏损", "4.Target严重亏损",
                                     review=True)
                    self._add_review("Medium", targeting, "Pause Target",
                                     f"ACOS {acos:.0f}% 持续超 Target×2，已有 {int(orders)} 单")
                elif acos > self.break_even_acos * 100:
                    bid_down = 30 if orders < 3 else 40
                    new_bid = f"${bid * (1 - bid_down/100):.2f}" if bid > 0 else "—"
                    self._add_action(ctx, f"LOWER_BID_{bid_down}", f"ACOS {acos:.0f}% 超盈亏线", "4.Target亏损")
                    self._add_bulk(campaign, adgroup, "Keyword",
                                   "Update", targeting, match_type, "enabled", new_bid,
                                   f"ACOS {acos:.0f}% 降 bid {bid_down}%")

    # ── Campaign 分析 ─────────────────────────────────────────────────────────
    def analyze_campaigns(self, df: pd.DataFrame):
        col_map = self._build_col_map(df)

        for _, row in df.iterrows():
            campaign = str(row.get(col_map.get("campaign name", ""), "")).strip()
            budget   = safe_float(row.get(col_map.get("daily budget", ""), 0))
            spend    = safe_float(row.get(col_map.get("spend", ""), 0))
            orders   = safe_float(row.get(col_map.get("orders", ""), 0))
            sales    = safe_float(row.get(col_map.get("sales", ""), 0))
            status   = str(row.get(col_map.get("status", ""), "")).lower()

            if not campaign or budget == 0:
                continue

            acos = (spend / sales * 100) if sales > 0 else None
            acos_str = f"{acos:.0f}%" if acos is not None else "—"
            seven_day_budget = budget * 7

            ctx = dict(campaign=campaign, adgroup="—", obj_type="Campaign",
                       obj=campaign, clicks="—", spend=spend,
                       orders=int(orders), sales=sales, acos_str=acos_str)

            # 规则 6：整体无订单花完预算
            if orders == 0 and spend >= seven_day_budget * 0.8:
                self._add_action(ctx, "PAUSE_CAMPAIGN*", f"7 天预算 ${seven_day_budget:.0f} 已花 ${spend:.2f}，0 订单", "6.Campaign无订单",
                                 review=True)
                self._add_review("High", campaign, "Pause Campaign",
                                 f"7 天预算 ${seven_day_budget:.0f} 已花 ${spend:.2f} 且 0 订单，建议暂停或先查 Target 层")
                continue

            # 规则 7：亏损但有部分有效词
            if orders >= 2 and acos is not None and acos > self.break_even_acos * 100:
                self._add_action(ctx, "REDUCE_BUDGET", f"ACOS {acos_str} 超盈亏线，但有 {int(orders)} 单", "7.降预算")
                new_budget = f"${budget * 0.6:.2f}"
                self._add_bulk(campaign, "—", "Campaign",
                               "Update", "—", "—", "enabled", new_budget,
                               f"整体亏损降预算 40%")

    # ── 内部工具 ──────────────────────────────────────────────────────────────
    def _has_low_intent(self, term: str) -> str:
        t = term.lower()
        for root in LOW_INTENT_ROOTS:
            if root in t:
                return root
        return ""

    def _build_col_map(self, df: pd.DataFrame) -> dict:
        """构建小写列名映射"""
        return {c.lower().strip(): c for c in df.columns}

    def _add_action(self, ctx: dict, action: str, reason: str, rule: str, review: bool = False):
        self.action_rows.append({
            "Campaign": ctx["campaign"],
            "Ad Group": ctx["adgroup"],
            "Object Type": ctx["obj_type"],
            "Object": ctx["obj"],
            "Clicks": ctx["clicks"],
            "Spend": f"${ctx['spend']:.2f}",
            "Orders": ctx["orders"],
            "Sales": f"${ctx['sales']:.2f}" if isinstance(ctx['sales'], float) else ctx['sales'],
            "ACOS": ctx["acos_str"],
            "Rule": rule,
            "Recommended Action": action,
            "Reason": reason,
            "Review Required": "⚠️ Yes" if review else "No"
        })

    def _add_review(self, priority: str, obj: str, action: str, reason: str):
        self.review_rows.append({
            "Priority": priority,
            "Object": obj,
            "Suggested Action": action,
            "Why Review": reason
        })

    def _add_bulk(self, campaign, adgroup, record_type, operation,
                  keyword, match_type, state, bid, reason):
        self.bulk_rows.append({
            "Record Type": record_type,
            "Operation": operation,
            "Campaign": campaign,
            "Ad Group": adgroup,
            "Keyword / Product Targeting": keyword,
            "Match Type": match_type,
            "State": state,
            "Bid": bid,
            "Reason": reason
        })

    # ── 输出 ──────────────────────────────────────────────────────────────────
    def get_summary(self) -> dict:
        return {
            "params": {
                "selling_price": self.price,
                "gross_margin_pct": f"{self.margin*100:.1f}%",
                "target_acos_pct": f"{self.target_acos*100:.1f}%",
                "break_even_acos_pct": f"{self.break_even_acos*100:.1f}%",
                "max_cpa": f"${self.max_cpa:.2f}",
                "break_even_cpa": f"${self.break_even_cpa:.2f}",
                "new_product_mode": self.new_product
            },
            "table1_stop_loss": self.action_rows,
            "table2_review": self.review_rows,
            "table3_bulk_sheet": self.bulk_rows
        }


# ── 主程序 ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Amazon PPC Stop-Loss Analyzer")
    parser.add_argument("--files", nargs="+", required=True, help="上传的报告文件路径（支持 csv/xlsx/tsv）")
    parser.add_argument("--price", type=float, default=0.0, help="产品售价（美元）")
    parser.add_argument("--margin", type=float, default=0.0, help="毛利率，如 0.36 = 36%")
    parser.add_argument("--target-acos", type=float, default=0.0, help="目标 ACOS，如 0.25 = 25%")
    parser.add_argument("--new-product", action="store_true", help="是否为新品保护模式")
    parser.add_argument("--min-clicks", type=int, default=20, help="最少观察点击数（默认 20）")
    parser.add_argument("--stop-clicks", type=int, default=35, help="无订单止损点击阈值（默认 35）")
    args = parser.parse_args()

    # 参数校验
    errors = []
    if args.price <= 0:
        errors.append("--price 必须大于 0（例如：--price 25）")
    if not (0 < args.margin < 1):
        errors.append("--margin 必须在 0 到 1 之间（例如：--margin 0.36）")
    if not (0 < args.target_acos < 1):
        errors.append("--target-acos 必须在 0 到 1 之间（例如：--target-acos 0.25）")
    if errors:
        print(json.dumps({"error": "参数错误", "details": errors}, ensure_ascii=False, indent=2))
        sys.exit(1)

    engine = StopLossEngine(
        price=args.price,
        margin=args.margin,
        target_acos=args.target_acos,
        new_product=args.new_product,
        min_clicks=args.min_clicks,
        stop_clicks=args.stop_clicks
    )

    loaded = {"search_term": [], "targeting": [], "campaign": [], "profit": [], "unknown": []}

    for fpath in args.files:
        try:
            df = load_file(fpath)
            ftype = detect_file_type(df)
            loaded[ftype].append((fpath, df))
            print(f"✅ 已识别 [{ftype}]：{fpath}", file=sys.stderr)
        except Exception as e:
            print(json.dumps({"error": f"文件读取失败：{fpath}", "detail": str(e)},
                             ensure_ascii=False))
            sys.exit(1)

    if loaded["unknown"]:
        names = [p for p, _ in loaded["unknown"]]
        print(json.dumps({"warning": f"无法识别文件类型，已跳过：{names}"}, ensure_ascii=False))

    for _, df in loaded["search_term"]:
        engine.analyze_search_terms(df)

    for _, df in loaded["targeting"]:
        engine.analyze_targets(df)

    for _, df in loaded["campaign"]:
        engine.analyze_campaigns(df)

    result = engine.get_summary()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()