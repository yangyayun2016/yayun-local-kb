#!/usr/bin/env python3
"""
亚马逊竞品 ASIN 推广节奏分析报告生成器
用法: python generate_report.py <data_file> <ASIN> [--output <output_dir>]
"""

import sys
import os
import re
import json
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

# ─── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="生成亚马逊竞品推广节奏分析 HTML 报告")
    p.add_argument("data_file", help="卖家精灵导出的数据文件（TXT/CSV）")
    p.add_argument("asin", help="目标 ASIN")
    p.add_argument("--output", default="/mnt/user-data/outputs", help="输出目录")
    return p.parse_args()

# ─── 数据解析 ─────────────────────────────────────────────────────────────────

SECTION_PATTERNS = [
    r"全量明细", r"前\d+月明细", r"前\d+周明细",
    r"近\d+月聚合", r"前\d+月聚合", r"第\d+月聚合", r"第\d+周聚合",
    r"明细数据", r"聚合数据",
]

def detect_section(line):
    for pat in SECTION_PATTERNS:
        if re.search(pat, line):
            return line.strip()
    return None

def parse_file(filepath):
    """
    解析多表结构的 TXT/CSV 文件。
    返回 dict: { section_name: [{'col': val, ...}, ...] }
    """
    sections = {}
    current_section = "全量明细"
    current_headers = []
    current_rows = []
    delimiter = None

    def flush():
        if current_headers and current_rows:
            sections[current_section] = current_rows[:]

    with open(filepath, encoding="utf-8-sig", errors="replace") as f:
        lines = f.readlines()

    for line in lines:
        raw = line.rstrip("\n")
        stripped = raw.strip()
        if not stripped:
            continue

        sec = detect_section(stripped)
        if sec and not delimiter:
            # 还没检测到分隔符，但匹配到区段名
            flush()
            current_section = sec
            current_headers = []
            current_rows = []
            continue

        # 自动检测分隔符
        if delimiter is None:
            if "\t" in stripped:
                delimiter = "\t"
            elif "," in stripped:
                delimiter = ","
            else:
                delimiter = "\t"

        cells = [c.strip() for c in stripped.split(delimiter)]

        # 区段标题行（可能在同一行作为第一个 cell）
        if cells and detect_section(cells[0]):
            flush()
            current_section = cells[0]
            current_headers = []
            current_rows = []
            continue

        if not current_headers:
            current_headers = cells
        else:
            if len(cells) >= max(1, len(current_headers) - 3):
                row = {}
                for i, h in enumerate(current_headers):
                    row[h] = cells[i] if i < len(cells) else ""
                current_rows.append(row)

    flush()
    return sections

def normalize_key(k):
    """统一字段名别名"""
    aliases = {
        "bsr": "大类排名", "best seller rank": "大类排名",
        "sub bsr": "小类排名", "sale price": "成交价",
        "total traffic": "全部流量", "organic traffic": "自然流量",
        "ad traffic": "广告流量", "date": "日期",
    }
    return aliases.get(k.lower(), k)

def to_float(v, default=0.0):
    try:
        return float(str(v).replace(",", "").replace("%", "").strip())
    except:
        return default

def to_int(v, default=0):
    try:
        return int(float(str(v).replace(",", "").strip()))
    except:
        return default

# ─── 指标计算 ─────────────────────────────────────────────────────────────────

def get_primary_rows(sections):
    for key in ["前4月明细", "全量明细", "明细数据"]:
        for k, v in sections.items():
            if key in k:
                return v
    # fallback: 最长的表
    if sections:
        return max(sections.values(), key=len)
    return []

def extract_events(rows):
    events = {}
    for row in rows:
        date = row.get("日期", "")
        if not date:
            continue
        if "首次上架" not in events and to_int(row.get("销量", 0)) > 0:
            events["首次上架"] = date
        if "最早出单" not in events and to_int(row.get("销量", 0)) > 0:
            events["最早出单"] = date
        if "首条评论" not in events and to_int(row.get("新增评论", 0)) > 0:
            events["首条评论"] = date
        if "首次改价" not in events and row.get("修改标题", "0") not in ("0", "", "—"):
            events["首次改价"] = date
        if "首次DEAL" not in events and row.get("LD数", "0") not in ("0", "", "—"):
            ld_price = row.get("LD价", row.get("成交价", ""))
            events["首次DEAL"] = f"{date}，价格 {ld_price}"
        if "首次卖家增加" not in events:
            sellers = to_int(row.get("卖家数", 1))
            if sellers > 1:
                events["首次卖家增加"] = date
        if "首次修改标题" not in events and row.get("修改标题", "0") not in ("0", "", "—"):
            events["首次修改标题"] = date
        if "首次修改主图" not in events and row.get("修改主图", "0") not in ("0", "", "—"):
            events["首次修改主图"] = date
    return events

def monthly_summary(rows):
    months = defaultdict(lambda: {
        "sales": 0, "revenue": 0.0, "reviews": 0, "new_reviews": 0,
        "bsr_min": float("inf"), "sub_bsr_min": float("inf"),
        "prices": [], "ad_count": 0, "traffic_total": 0,
        "traffic_organic": 0, "traffic_ad": 0, "dates": [],
    })
    for row in rows:
        date = row.get("日期", "")
        if not date:
            continue
        try:
            m = date[:7]  # YYYY-MM
        except:
            continue
        d = months[m]
        d["dates"].append(date)
        d["sales"] += to_int(row.get("销量", 0))
        price = to_float(row.get("成交价", 0))
        d["revenue"] += to_float(row.get("成交额", price * to_int(row.get("销量", 0))))
        d["reviews"] = max(d["reviews"], to_int(row.get("评论数", 0)))
        d["new_reviews"] += to_int(row.get("新增评论", 0))
        bsr = to_int(row.get("大类排名", 999999))
        if bsr > 0:
            d["bsr_min"] = min(d["bsr_min"], bsr)
        sub_bsr = to_int(row.get("小类排名", 99999))
        if sub_bsr > 0:
            d["sub_bsr_min"] = min(d["sub_bsr_min"], sub_bsr)
        if price > 0:
            d["prices"].append(price)
        d["ad_count"] += to_int(row.get("新增广告", 0))
        d["traffic_total"] += to_int(row.get("全部流量", 0))
        d["traffic_organic"] += to_int(row.get("自然流量", 0))
        d["traffic_ad"] += to_int(row.get("广告流量", 0))
    # clean up
    result = {}
    for m, d in sorted(months.items()):
        d["bsr_min"] = d["bsr_min"] if d["bsr_min"] != float("inf") else 0
        d["sub_bsr_min"] = d["sub_bsr_min"] if d["sub_bsr_min"] != float("inf") else 0
        d["avg_price"] = round(sum(d["prices"]) / len(d["prices"]), 2) if d["prices"] else 0
        d["review_rate"] = round(d["new_reviews"] / d["sales"] * 100, 2) if d["sales"] > 0 else 0
        d["ad_pct"] = round(d["traffic_ad"] / d["traffic_total"] * 100, 1) if d["traffic_total"] > 0 else 0
        d["organic_pct"] = round(d["traffic_organic"] / d["traffic_total"] * 100, 1) if d["traffic_total"] > 0 else 0
        result[m] = d
    return result

def strategy_label(idx, total_months, d, all_prices):
    other_prices = [v["avg_price"] for k, v in all_prices.items() if k != idx and v["avg_price"] > 0]
    avg_other = sum(other_prices) / len(other_prices) if other_prices else d["avg_price"]
    if idx == 0:
        return "低价切入+评论拉升" if d["avg_price"] < avg_other * 0.95 else "正常价格切入"
    if idx in (1, 2):
        bsr_vals = [v["bsr_min"] for v in all_prices.values() if v["bsr_min"] > 0]
        if len(bsr_vals) >= 2:
            variance = max(bsr_vals) / (min(bsr_vals) + 1)
            return "排名维持期" if variance < 1.2 else "排名回落观察"
        return "排名维持期"
    if idx >= 3:
        return "广告调整+排名冲刺" if d["ad_pct"] > 30 else "稳定增长期"
    return "—"

def risk_level(d):
    flags = []
    if d["review_rate"] > 3:
        flags.append(("🔴", "留评率超3%，需警惕刷单风险"))
    elif d["review_rate"] > 1:
        flags.append(("🟡", "留评率1~3%，略高，需观察"))
    if d["ad_pct"] < 5 and d["bsr_min"] > 0 and d["bsr_min"] < 5000:
        flags.append(("🟡", "广告占比<5%但排名较好，来源需关注"))
    if d["new_reviews"] > 100 and d["review_rate"] > 5:
        flags.append(("🔴", "月增评论>100且留评率>5%，高度疑似刷单"))
    if not flags:
        flags.append(("🟢", "正常"))
    return flags

# ─── HTML 生成 ────────────────────────────────────────────────────────────────

def build_html(asin, rows, sections, events, monthly, today_str):
    months_list = sorted(monthly.keys())[:4]  # 前4个月

    total_sales = sum(monthly[m]["sales"] for m in months_list)
    total_revenue = sum(monthly[m]["revenue"] for m in months_list)
    total_new_reviews = sum(monthly[m]["new_reviews"] for m in months_list)
    best_bsr = min((monthly[m]["bsr_min"] for m in months_list if monthly[m]["bsr_min"] > 0), default=0)

    period_start = rows[0].get("日期", "—") if rows else "—"
    period_end = rows[-1].get("日期", "—") if rows else "—"

    # chart data
    chart_dates = [r.get("日期", "") for r in rows[:120]]
    chart_bsr = [to_int(r.get("大类排名", 0)) for r in rows[:120]]
    chart_price = [to_float(r.get("成交价", 0)) for r in rows[:120]]
    chart_reviews = [to_int(r.get("评论数", 0)) for r in rows[:120]]

    chart_months = months_list
    chart_sales_total = [monthly[m]["sales"] for m in months_list]
    chart_sales_organic = [int(monthly[m]["sales"] * monthly[m]["organic_pct"] / 100) for m in months_list]
    chart_sales_ad = [int(monthly[m]["sales"] * monthly[m]["ad_pct"] / 100) for m in months_list]
    chart_new_reviews = [monthly[m]["new_reviews"] for m in months_list]

    # monthly cards
    monthly_cards_html = ""
    for i, m in enumerate(months_list):
        d = monthly[m]
        label = strategy_label(i, len(months_list), d, monthly)
        risks = risk_level(d)
        risk_html = "".join(f'<span class="risk-badge">{em} {txt}</span>' for em, txt in risks)
        price_start = d["prices"][0] if d["prices"] else 0
        price_end = d["prices"][-1] if d["prices"] else 0
        open_attr = "open" if i == 0 else ""
        monthly_cards_html += f"""
        <details class="month-card" {open_attr}>
          <summary>MONTH {i+1} — 第{i+1}个月（{m}）<span class="tag">{label}</span></summary>
          <div class="month-body">
            <div class="sub-section">■ 销量与排名<br>
              销量 <b>{d['sales']:,}</b>，成交额 <b>${d['revenue']:,.2f}</b>，
              大类排名最佳 <b>{d['bsr_min']:,}</b>，小类排名最佳 <b>{d['sub_bsr_min']:,}</b>
            </div>
            <div class="sub-section">■ 价格策略<br>
              月初成交价 <b>${price_start}</b> → 月末 <b>${price_end}</b>，月均 <b>${d['avg_price']}</b>
            </div>
            <div class="sub-section">■ 评论策略<br>
              月新增评论 <b>{d['new_reviews']}</b>，留评率 <b>{d['review_rate']}%</b>
            </div>
            <div class="sub-section">■ 流量策略<br>
              全部流量 <b>{d['traffic_total']:,}</b>，
              自然 <b>{d['organic_pct']}%</b> / 广告 <b>{d['ad_pct']}%</b>，
              新增广告 <b>{d['ad_count']}</b> 次
            </div>
            <div class="sub-section">■ 风险判断<br>{risk_html}</div>
          </div>
        </details>"""

    # events timeline
    events_html = ""
    for k, v in events.items():
        events_html += f'<div class="timeline-item"><span class="tl-dot"></span><b>{k}</b>：{v}</div>'
    if not events_html:
        events_html = '<div class="timeline-item">暂无事件数据</div>'

    # summary table
    summary_rows_html = ""
    for i, m in enumerate(months_list):
        d = monthly[m]
        label = strategy_label(i, len(months_list), d, monthly)
        summary_rows_html += f"""<tr>
          <td>{m}</td><td><span class="tag">{label}</span></td>
          <td>{d['sales']:,}</td><td>${d['avg_price']}</td>
          <td>{d['bsr_min']:,}</td><td>{d['sub_bsr_min']:,}</td>
          <td>{d['reviews']:,}</td><td>{d['review_rate']}%</td>
          <td>{d['ad_pct']}%</td><td>{d['ad_count']}</td>
        </tr>"""

    # detail tables
    detail_tables_html = ""
    for sec_name, sec_rows in sections.items():
        if not sec_rows:
            continue
        headers = list(sec_rows[0].keys())
        thead = "".join(f"<th>{h}</th>" for h in headers)
        tbody = ""
        for row in sec_rows:
            tbody += "<tr>" + "".join(f"<td>{row.get(h,'')}</td>" for h in headers) + "</tr>"
        detail_tables_html += f"""
        <details class="data-table-wrap">
          <summary>{sec_name}（{len(sec_rows)} 行）</summary>
          <div class="table-scroll">
            <table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>
          </div>
        </details>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{asin} 竞品推广节奏分析</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0f1923;color:#d4dde8;font-family:'Segoe UI',Arial,sans-serif;font-size:14px;padding:24px}}
  h1{{color:#7ec8e3;font-size:22px;margin-bottom:4px}}
  .subtitle{{color:#8a9bb0;margin-bottom:24px}}
  .kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:32px}}
  @media(max-width:800px){{.kpi-grid{{grid-template-columns:repeat(2,1fr)}}}}
  .kpi{{background:linear-gradient(135deg,#1a2f45,#1e3a52);border-radius:10px;padding:20px;text-align:center}}
  .kpi .val{{font-size:28px;font-weight:700;color:#7ec8e3}}
  .kpi .lbl{{color:#8a9bb0;font-size:12px;margin-top:6px}}
  .section-title{{color:#7ec8e3;font-size:16px;border-left:3px solid #7ec8e3;padding-left:10px;margin:28px 0 14px}}
  .timeline-item{{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #1c2e40}}
  .tl-dot{{width:10px;height:10px;border-radius:50%;background:#7ec8e3;flex-shrink:0}}
  .chart-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:28px}}
  @media(max-width:900px){{.chart-grid{{grid-template-columns:1fr}}}}
  .chart-box{{background:#142030;border-radius:10px;padding:16px}}
  .chart-box canvas{{max-height:260px}}
  .chart-full{{background:#142030;border-radius:10px;padding:16px;margin-bottom:20px}}
  .chart-full canvas{{max-height:300px}}
  table{{width:100%;border-collapse:collapse;font-size:12px}}
  th{{background:#1a2f45;color:#7ec8e3;padding:8px 10px;text-align:left;white-space:nowrap}}
  td{{padding:7px 10px;border-bottom:1px solid #1c2e40;white-space:nowrap}}
  tr:hover td{{background:#142030}}
  .tag{{background:#1e4a6e;color:#7ec8e3;border-radius:4px;padding:2px 8px;font-size:11px}}
  .month-card{{background:#142030;border-radius:10px;margin-bottom:12px;overflow:hidden}}
  .month-card summary{{padding:14px 18px;cursor:pointer;color:#7ec8e3;font-weight:600;display:flex;align-items:center;gap:10px}}
  .month-card summary::-webkit-details-marker{{display:none}}
  .month-body{{padding:0 18px 16px;line-height:2}}
  .sub-section{{margin-top:12px;padding:10px 14px;background:#0f1923;border-radius:6px}}
  .risk-badge{{display:inline-block;margin:2px 4px;padding:2px 8px;border-radius:4px;background:#1a2f45}}
  .data-table-wrap{{background:#142030;border-radius:8px;margin-bottom:10px}}
  .data-table-wrap summary{{padding:12px 16px;cursor:pointer;color:#8a9bb0}}
  .table-scroll{{overflow-x:auto;padding:0 16px 12px}}
</style>
</head>
<body>

<h1>{asin} 竞品前4个月推广节奏分析报告</h1>
<div class="subtitle">分析周期：{period_start} ~ {period_end} &nbsp;|&nbsp; 生成时间：{today_str}</div>

<div class="kpi-grid">
  <div class="kpi"><div class="val">{total_sales:,}</div><div class="lbl">前4月总销量</div></div>
  <div class="kpi"><div class="val">${total_revenue:,.0f}</div><div class="lbl">前4月销售额</div></div>
  <div class="kpi"><div class="val">{total_new_reviews:,}</div><div class="lbl">累计评论增长</div></div>
  <div class="kpi"><div class="val">{best_bsr:,}</div><div class="lbl">大类最佳排名(BSR)</div></div>
</div>

<div class="section-title">关键时间节点</div>
<div style="margin-bottom:28px">{events_html}</div>

<div class="section-title">核心趋势图表</div>
<div class="chart-full">
  <canvas id="chartA"></canvas>
</div>
<div class="chart-grid">
  <div class="chart-box"><canvas id="chartB"></canvas></div>
  <div class="chart-box"><canvas id="chartC"></canvas></div>
</div>

<div class="section-title">前4个月汇总表</div>
<div style="overflow-x:auto;margin-bottom:28px">
<table>
  <thead><tr>
    <th>月份</th><th>策略标签</th><th>销量</th><th>月均成交价</th>
    <th>大类BSR最佳</th><th>小类最佳</th><th>评论数</th>
    <th>留评率</th><th>广告流量占比</th><th>新增广告</th>
  </tr></thead>
  <tbody>{summary_rows_html}</tbody>
</table>
</div>

<div class="section-title">月度推广节奏拆解</div>
{monthly_cards_html}

<div class="section-title">效果总结</div>
<div style="background:#142030;border-radius:10px;padding:18px;margin-bottom:28px;line-height:2">
  大类排名：最佳 <b>{best_bsr:,}</b><br>
  累计销量：<b>{total_sales:,}</b><br>
  累计成交额：<b>${total_revenue:,.2f}</b>
</div>

<div class="section-title">明细数据表（点击展开）</div>
{detail_tables_html}

<script>
const chartADates = {json.dumps(chart_dates, ensure_ascii=False)};
const chartABsr   = {json.dumps(chart_bsr)};
const chartAPrice = {json.dumps(chart_price)};
const chartAReview= {json.dumps(chart_reviews)};

new Chart(document.getElementById('chartA'), {{
  data: {{
    labels: chartADates,
    datasets: [
      {{type:'line',label:'大类排名(BSR)',data:chartABsr,yAxisID:'y',borderColor:'#7ec8e3',tension:0.3,pointRadius:0}},
      {{type:'line',label:'成交价',data:chartAPrice,yAxisID:'y2',borderColor:'#f0c040',tension:0.3,pointRadius:0}},
      {{type:'line',label:'评论数',data:chartAReview,yAxisID:'y3',borderColor:'#6fcf97',fill:true,backgroundColor:'rgba(111,207,151,0.1)',tension:0.3,pointRadius:0}},
    ]
  }},
  options:{{
    responsive:true,interaction:{{mode:'index',intersect:false}},
    plugins:{{legend:{{labels:{{color:'#d4dde8'}}}},title:{{display:true,text:'排名/成交价/评论数综合趋势',color:'#7ec8e3'}}}},
    scales:{{
      x:{{ticks:{{color:'#8a9bb0',maxTicksLimit:10}},grid:{{color:'#1c2e40'}}}},
      y:{{type:'linear',position:'left',reverse:true,ticks:{{color:'#7ec8e3'}},grid:{{color:'#1c2e40'}},title:{{display:true,text:'BSR排名',color:'#7ec8e3'}}}},
      y2:{{type:'linear',position:'right',ticks:{{color:'#f0c040'}},grid:{{drawOnChartArea:false}},title:{{display:true,text:'成交价',color:'#f0c040'}}}},
      y3:{{type:'linear',position:'right',ticks:{{color:'#6fcf97'}},grid:{{drawOnChartArea:false}},title:{{display:true,text:'评论数',color:'#6fcf97'}}}},
    }}
  }}
}});

new Chart(document.getElementById('chartB'), {{
  type:'bar',
  data:{{
    labels:{json.dumps(chart_months)},
    datasets:[
      {{label:'全部流量销量',data:{json.dumps(chart_sales_total)},backgroundColor:'rgba(126,200,227,0.7)'}},
      {{label:'自然流量销量',data:{json.dumps(chart_sales_organic)},backgroundColor:'rgba(111,207,151,0.7)'}},
      {{label:'广告流量销量',data:{json.dumps(chart_sales_ad)},backgroundColor:'rgba(240,192,64,0.7)'}},
    ]
  }},
  options:{{
    responsive:true,plugins:{{
      legend:{{labels:{{color:'#d4dde8'}}}},
      title:{{display:true,text:'月度销量结构对比',color:'#7ec8e3'}}
    }},
    scales:{{
      x:{{stacked:true,ticks:{{color:'#8a9bb0'}},grid:{{color:'#1c2e40'}}}},
      y:{{stacked:true,ticks:{{color:'#8a9bb0'}},grid:{{color:'#1c2e40'}}}}
    }}
  }}
}});

new Chart(document.getElementById('chartC'), {{
  type:'bar',
  data:{{
    labels:{json.dumps(chart_months)},
    datasets:[{{label:'月度新增评论数',data:{json.dumps(chart_new_reviews)},backgroundColor:'rgba(111,207,151,0.8)'}}]
  }},
  options:{{
    responsive:true,plugins:{{
      legend:{{labels:{{color:'#d4dde8'}}}},
      title:{{display:true,text:'月度新增评论数',color:'#7ec8e3'}}
    }},
    scales:{{
      x:{{ticks:{{color:'#8a9bb0'}},grid:{{color:'#1c2e40'}}}},
      y:{{ticks:{{color:'#8a9bb0'}},grid:{{color:'#1c2e40'}}}}
    }}
  }}
}});
</script>
</body>
</html>"""
    return html

# ─── 主函数 ───────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    if not os.path.exists(args.data_file):
        print(f"[ERROR] 文件不存在: {args.data_file}", file=sys.stderr)
        sys.exit(1)

    sections = parse_file(args.data_file)
    rows = get_primary_rows(sections)

    if not rows:
        print("[ERROR] 未能解析到有效数据行，请检查文件格式", file=sys.stderr)
        sys.exit(1)

    events = extract_events(rows)
    monthly = monthly_summary(rows)
    today_str = datetime.now().strftime("%Y-%m-%d")

    html = build_html(args.asin, rows, sections, events, monthly, today_str)

    os.makedirs(args.output, exist_ok=True)
    out_path = os.path.join(args.output, f"{args.asin}_竞品分析报告_{today_str}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] 报告已生成: {out_path}")
    print(f"REPORT_PATH={out_path}")

if __name__ == "__main__":
    main()