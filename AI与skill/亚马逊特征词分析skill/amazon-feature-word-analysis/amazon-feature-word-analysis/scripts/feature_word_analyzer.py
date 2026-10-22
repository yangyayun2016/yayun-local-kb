#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
亚马逊特征词分析工具（Feature Word Analyzer）
天机OS · TRACE 技能配套脚本

输入：亚马逊广告后台搜索词报告（CSV / XLSX）
输出：Excel 多 Sheet（清洗数据 / 单词结果 / 双词结果 / 出价建议），可选 HTML 报告

口径：
  CPC=Spend/Clicks  CTR=Clicks/Impr  CVR=Orders/Clicks
  ACOS=Spend/Sales  CPA=Spend/Orders
  CPC上限 = 目标ACOS × 客单价 × CVR   (engineering: 词根级目标BID)
"""

import argparse
import re
import sys
from collections import defaultdict

import pandas as pd

# ---------- 列名模糊匹配 ----------
COLUMN_ALIASES = {
    "search_term": ["customer search term", "customer search terms", "消费者搜索词", "客户搜索词", "搜索词"],
    "impressions": ["impressions", "曝光量", "展示量"],
    "clicks": ["clicks", "点击量", "点击"],
    "spend": ["spend", "cost", "广告花费", "花费"],
    "sales": ["7 day total sales", "14 day total sales", "total sales", "7天总销售额", "总销售额", "销售额"],
    "orders": ["7 day total orders (#)", "7 day total orders", "14 day total orders (#)",
               "total orders", "7天总订单量", "总订单量", "订单量", "订单"],
}

ASIN_PATTERN = re.compile(r"^b0[0-9a-z]{8}$")
ENGINEERING_CLICK_THRESHOLD = 15  # engineering_assumption: 15个点击出一单


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip().lower()


def map_columns(df: pd.DataFrame) -> dict:
    mapping = {}
    norm_cols = {normalize(c): c for c in df.columns}
    for std, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in norm_cols:
                mapping[std] = norm_cols[alias]
                break
        else:
            # 宽松包含匹配
            for nc, orig in norm_cols.items():
                if any(alias in nc for alias in aliases):
                    mapping[std] = orig
                    break
    missing = [k for k in COLUMN_ALIASES if k not in mapping]
    if missing:
        sys.exit(f"[错误] 找不到必需字段: {missing}\n报告实际列名: {list(df.columns)}\n"
                 f"请确认导出的是搜索词报告，或手动重命名列后重试。")
    return mapping


def to_number(x):
    if pd.isna(x):
        return 0.0
    s = re.sub(r"[^\d.\-]", "", str(x))
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def derive_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["CPC"] = (df["Spend"] / df["Clicks"]).where(df["Clicks"] > 0)
    df["CTR"] = (df["Clicks"] / df["Impressions"]).where(df["Impressions"] > 0)
    df["CVR"] = (df["Orders"] / df["Clicks"]).where(df["Clicks"] > 0)
    df["ACOS"] = (df["Spend"] / df["Sales"]).where(df["Sales"] > 0)
    df["CPA"] = (df["Spend"] / df["Orders"]).where(df["Orders"] > 0)
    return df


def load_report(path: str) -> pd.DataFrame:
    if path.lower().endswith((".xlsx", ".xls")):
        raw = pd.read_excel(path)
    else:
        raw = pd.read_csv(path)
    m = map_columns(raw)
    df = pd.DataFrame({
        "Customer Search Term": raw[m["search_term"]].astype(str).map(normalize),
        "Impressions": raw[m["impressions"]].map(to_number),
        "Clicks": raw[m["clicks"]].map(to_number),
        "Spend": raw[m["spend"]].map(to_number),
        "Sales": raw[m["sales"]].map(to_number),
        "Orders": raw[m["orders"]].map(to_number),
    })
    df = df[df["Customer Search Term"] != ""]
    # 同一搜索词跨活动聚合
    df = df.groupby("Customer Search Term", as_index=False).sum(numeric_only=True)
    return df


def split_asin_rows(df: pd.DataFrame):
    is_asin = df["Customer Search Term"].map(lambda t: bool(ASIN_PATTERN.match(t.replace(" ", ""))))
    return df[~is_asin].reset_index(drop=True), df[is_asin].reset_index(drop=True)


def ngram_aggregate(df: pd.DataFrame, n: int) -> pd.DataFrame:
    agg = defaultdict(lambda: {"Impressions": 0.0, "Clicks": 0.0, "Spend": 0.0,
                               "Sales": 0.0, "Orders": 0.0, "TermCount": 0})
    for _, row in df.iterrows():
        tokens = row["Customer Search Term"].split()
        grams = set(" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1))
        for g in grams:
            a = agg[g]
            for f in ("Impressions", "Clicks", "Spend", "Sales", "Orders"):
                a[f] += row[f]
            a["TermCount"] += 1
    out = pd.DataFrame([{"词根" if n == 1 else "双词组合": k, **v} for k, v in agg.items()])
    if out.empty:
        return out
    out = derive_metrics(out.rename(columns=str))
    return out.sort_values("Spend", ascending=False).reset_index(drop=True)


def attach_unigram_context(bigram_df: pd.DataFrame, unigram_df: pd.DataFrame) -> pd.DataFrame:
    """双词结果并列展示组合内两个单词各自的 CVR/ACOS/CPA"""
    if bigram_df.empty:
        return bigram_df
    uni = unigram_df.set_index("词根")
    rows = []
    for _, r in bigram_df.iterrows():
        w1, w2 = r["双词组合"].split(" ", 1)
        d = r.to_dict()
        for tag, w in (("单词1", w1), ("单词2", w2)):
            d[tag] = w
            for metric in ("CVR", "ACOS", "CPA"):
                d[f"{tag}_{metric}"] = uni.at[w, metric] if w in uni.index else None
        rows.append(d)
    return pd.DataFrame(rows)


def bid_suggestions(unigram_df: pd.DataFrame, price: float, target_acos: float,
                    min_clicks: int) -> pd.DataFrame:
    df = unigram_df.copy()
    df["CPC上限(目标BID)"] = target_acos * price * df["CVR"].fillna(0)
    df["目标CPA"] = target_acos * price

    avg_cvr = df.loc[df["Clicks"] >= min_clicks, "CVR"].mean()

    def tag(r):
        if r["Clicks"] >= ENGINEERING_CLICK_THRESHOLD and r["Orders"] == 0:
            return "候选否定（烧钱不出单）"
        if r["Clicks"] < min_clicks:
            return "数据不足（继续观察）"
        if pd.isna(r["CPC"]):
            return "无点击"
        cap = r["CPC上限(目标BID)"]
        if cap == 0:
            return "候选否定（无转化）"
        if r["CPC"] > cap * 1.2:
            return "降价（CPC超上限20%+）"
        if r["CPC"] < cap * 0.8 and avg_cvr and r["CVR"] >= avg_cvr:
            return "可加价（有空间且CVR达标）"
        return "维持"

    df["建议动作"] = df.apply(tag, axis=1)
    return df.sort_values("Spend", ascending=False).reset_index(drop=True)


def fmt_sheet(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        if df[c].dtype == float:
            df[c] = df[c].round(4)
    return df


def write_excel(path, cleaned, uni, bi, bids, asin_rows):
    with pd.ExcelWriter(path, engine="openpyxl") as w:
        fmt_sheet(cleaned).to_excel(w, sheet_name="原始数据(清洗后)", index=False)
        fmt_sheet(uni).to_excel(w, sheet_name="单词结果(1-gram)", index=False)
        fmt_sheet(bi).to_excel(w, sheet_name="双词结果(2-gram)", index=False)
        if bids is not None:
            fmt_sheet(bids).to_excel(w, sheet_name="出价建议", index=False)
        if not asin_rows.empty:
            fmt_sheet(asin_rows).to_excel(w, sheet_name="ASIN定向(不拆词)", index=False)


def write_html(path, cleaned, uni, bi, bids, price, target_acos):
    def table(df, n=30):
        return fmt_sheet(df.head(n)).to_html(index=False, border=0, classes="tbl")
    total_spend, total_sales = cleaned["Spend"].sum(), cleaned["Sales"].sum()
    acos = total_spend / total_sales if total_sales else float("nan")
    params = (f"客单价 {price} · 目标ACOS {target_acos:.0%}" if price else "未提供客单价/目标ACOS")
    sections = [
        f"<h2>总览</h2><p>搜索词 {len(cleaned)} 个 · 总花费 {total_spend:,.2f} · "
        f"总销售额 {total_sales:,.2f} · 整体ACOS {acos:.1%} · {params}</p>",
        "<h2>单词结果 Top30（按花费）</h2>" + table(uni),
        "<h2>双词结果 Top30（按花费）</h2>" + table(bi),
    ]
    if bids is not None:
        neg = bids[bids["建议动作"].str.startswith("候选否定")]
        sections.append("<h2>候选否定词根</h2>" + table(neg, 50))
        sections.append("<h2>出价建议 Top30</h2>" + table(bids))
    html = f"""<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">
<title>亚马逊特征词分析报告</title><style>
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;margin:2rem;color:#222}}
h1{{border-bottom:3px solid #ff4d4f;padding-bottom:.4rem}}
.tbl{{border-collapse:collapse;font-size:12px;width:100%}}
.tbl th{{background:#1f2937;color:#fff;padding:6px 8px;text-align:left}}
.tbl td{{padding:5px 8px;border-bottom:1px solid #eee}}
.tbl tr:nth-child(even){{background:#fafafa}}
</style></head><body><h1>亚马逊特征词分析报告 · 天机OS</h1>{''.join(sections)}
<p style="color:#999">口径：CPC上限=目标ACOS×客单价×CVR · 出单临界值15点击/单为 engineering_assumption</p>
</body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser(description="亚马逊特征词分析（1-gram / 2-gram 词根聚合）")
    ap.add_argument("report", help="搜索词报告路径（CSV/XLSX）")
    ap.add_argument("-o", "--output", default="特征词分析结果.xlsx")
    ap.add_argument("--html", default=None, help="可选：HTML 报告输出路径")
    ap.add_argument("--price", type=float, default=None, help="客单价")
    ap.add_argument("--target-acos", type=float, default=None, help="目标ACOS，如 0.30")
    ap.add_argument("--min-clicks", type=int, default=5, help="出价建议最低点击门槛（默认5）")
    args = ap.parse_args()

    df = load_report(args.report)
    df, asin_rows = split_asin_rows(df)
    cleaned = derive_metrics(df).sort_values("Spend", ascending=False).reset_index(drop=True)

    uni = ngram_aggregate(df, 1)
    bi = attach_unigram_context(ngram_aggregate(df, 2), uni)

    bids = None
    if args.price and args.target_acos:
        bids = bid_suggestions(uni, args.price, args.target_acos, args.min_clicks)

    write_excel(args.output, cleaned, uni, bi, bids, asin_rows)
    print(f"[OK] Excel 已输出: {args.output}")
    if args.html:
        write_html(args.html, cleaned, uni, bi, bids, args.price, args.target_acos)
        print(f"[OK] HTML 已输出: {args.html}")

    print(f"搜索词 {len(cleaned)} 个 | 单词词根 {len(uni)} 个 | 双词组合 {len(bi)} 个"
          + (f" | ASIN定向 {len(asin_rows)} 个" if len(asin_rows) else ""))
    if bids is not None:
        neg = (bids["建议动作"].str.startswith("候选否定")).sum()
        print(f"候选否定词根 {neg} 个（点击≥{ENGINEERING_CLICK_THRESHOLD}零转化，engineering_assumption）")


if __name__ == "__main__":
    main()
