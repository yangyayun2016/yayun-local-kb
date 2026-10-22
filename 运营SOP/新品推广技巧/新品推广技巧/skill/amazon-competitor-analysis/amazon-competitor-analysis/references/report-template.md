# HTML报告模板参考

## 完整HTML骨架

生成报告时，按以下骨架填充数据。所有样式内联，Chart.js通过CDN引入。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ASIN} 竞品推广节奏分析报告</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
  <style>
    /* ===== 全局变量 ===== */
    :root {
      --bg-primary: #0f1923;
      --bg-secondary: #1a2736;
      --bg-card: #1e3044;
      --bg-card-hover: #243b52;
      --text-primary: #e8edf2;
      --text-secondary: #8899aa;
      --text-muted: #5c7080;
      --accent-blue: #4fc3f7;
      --accent-green: #66bb6a;
      --accent-orange: #ffa726;
      --accent-red: #ef5350;
      --accent-purple: #ab47bc;
      --border-color: #2a3f54;
      --gradient-blue: linear-gradient(135deg, #1565c0, #42a5f5);
      --gradient-green: linear-gradient(135deg, #2e7d32, #66bb6a);
      --gradient-orange: linear-gradient(135deg, #e65100, #ffa726);
      --gradient-purple: linear-gradient(135deg, #6a1b9a, #ab47bc);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.6;
      padding: 20px;
    }

    .container { max-width: 1200px; margin: 0 auto; }

    /* ===== 报告头部 ===== */
    .report-header {
      text-align: center;
      padding: 40px 20px;
      margin-bottom: 30px;
      background: linear-gradient(135deg, #0d2137 0%, #1a3a5c 50%, #0d2137 100%);
      border-radius: 16px;
      border: 1px solid var(--border-color);
    }
    .report-header h1 {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 8px;
      background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .report-header .period {
      font-size: 14px;
      color: var(--text-secondary);
    }

    /* ===== 指标卡片 ===== */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin: 24px 0;
    }
    .metric-card {
      padding: 24px;
      border-radius: 12px;
      color: #fff;
      position: relative;
      overflow: hidden;
    }
    .metric-card::after {
      content: '';
      position: absolute;
      top: -50%;
      right: -50%;
      width: 100%;
      height: 100%;
      background: rgba(255,255,255,0.05);
      border-radius: 50%;
    }
    .metric-card .label {
      font-size: 13px;
      opacity: 0.85;
      margin-bottom: 8px;
    }
    .metric-card .value {
      font-size: 32px;
      font-weight: 700;
    }
    .metric-card .sub {
      font-size: 12px;
      opacity: 0.7;
      margin-top: 4px;
    }

    /* ===== 章节 ===== */
    .section {
      background: var(--bg-secondary);
      border-radius: 12px;
      border: 1px solid var(--border-color);
      padding: 28px;
      margin-bottom: 24px;
    }
    .section-title {
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--border-color);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    /* ===== 时间线 ===== */
    .timeline {
      position: relative;
      padding-left: 30px;
    }
    .timeline::before {
      content: '';
      position: absolute;
      left: 8px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: var(--border-color);
    }
    .timeline-item {
      position: relative;
      padding: 12px 0;
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .timeline-item::before {
      content: '';
      position: absolute;
      left: -26px;
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--accent-blue);
      border: 2px solid var(--bg-secondary);
    }
    .timeline-item .event-name {
      font-size: 14px;
      color: var(--text-secondary);
      min-width: 120px;
    }
    .timeline-item .event-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }

    /* ===== 图表容器 ===== */
    .chart-container {
      background: var(--bg-card);
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .chart-container canvas {
      max-height: 360px;
    }

    /* ===== 月度卡片 ===== */
    .month-card {
      background: var(--bg-card);
      border-radius: 10px;
      border: 1px solid var(--border-color);
      margin-bottom: 16px;
      overflow: hidden;
    }
    .month-header {
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      transition: background 0.2s;
    }
    .month-header:hover { background: var(--bg-card-hover); }
    .month-header h3 { font-size: 16px; font-weight: 600; }
    .month-tag {
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
    }
    .tag-entry { background: rgba(79,195,247,0.15); color: var(--accent-blue); }
    .tag-maintain { background: rgba(102,187,106,0.15); color: var(--accent-green); }
    .tag-sprint { background: rgba(255,167,38,0.15); color: var(--accent-orange); }
    .tag-risk { background: rgba(239,83,80,0.15); color: var(--accent-red); }

    .month-body {
      padding: 0 24px 24px;
      display: none;
    }
    .month-body.active { display: block; }

    .strategy-block {
      margin-bottom: 20px;
    }
    .strategy-block h4 {
      font-size: 14px;
      font-weight: 600;
      color: var(--accent-blue);
      margin-bottom: 8px;
    }
    .strategy-block p, .strategy-block li {
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.8;
    }

    /* ===== 风险标签 ===== */
    .risk-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
    }
    .risk-green { background: rgba(102,187,106,0.12); color: var(--accent-green); }
    .risk-yellow { background: rgba(255,167,38,0.12); color: var(--accent-orange); }
    .risk-red { background: rgba(239,83,80,0.12); color: var(--accent-red); }

    /* ===== 数据表格 ===== */
    .table-wrapper {
      overflow-x: auto;
      margin-top: 12px;
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      white-space: nowrap;
    }
    th {
      background: var(--bg-card);
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
      color: var(--text-secondary);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
    }
    td {
      padding: 8px 14px;
      border-bottom: 1px solid rgba(42,63,84,0.5);
      color: var(--text-primary);
    }
    tr:hover td { background: rgba(79,195,247,0.04); }

    /* ===== 汇总表 ===== */
    .summary-table th { background: #1a3a5c; }
    .summary-table td:first-child { font-weight: 600; }

    /* ===== 折叠组件 ===== */
    .collapsible-header {
      padding: 14px 20px;
      background: var(--bg-card);
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
      border: 1px solid var(--border-color);
      transition: background 0.2s;
    }
    .collapsible-header:hover { background: var(--bg-card-hover); }
    .collapsible-header .arrow {
      transition: transform 0.3s;
      font-size: 12px;
      color: var(--text-muted);
    }
    .collapsible-header.open .arrow { transform: rotate(180deg); }
    .collapsible-content {
      display: none;
      padding: 12px 0;
    }
    .collapsible-content.open { display: block; }

    /* ===== 效果总结 ===== */
    .result-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }
    .result-item {
      padding: 16px;
      background: var(--bg-card);
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }
    .result-item .label { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
    .result-item .value { font-size: 24px; font-weight: 700; color: var(--accent-blue); }
    .result-item .change {
      font-size: 12px;
      margin-top: 4px;
    }
    .change-up { color: var(--accent-green); }
    .change-down { color: var(--accent-red); }

    /* ===== 数据缺失提示 ===== */
    .data-notice {
      margin-top: 24px;
      padding: 16px;
      background: rgba(255,167,38,0.08);
      border: 1px solid rgba(255,167,38,0.2);
      border-radius: 8px;
      font-size: 13px;
      color: var(--accent-orange);
    }
  </style>
</head>
<body>
<div class="container">

  <!-- ===== 模块1：报告头部 ===== -->
  <div class="report-header">
    <h1>{{ASIN}} 竞品前4个月推广节奏分析报告</h1>
    <p class="period">分析周期：{{START_DATE}} ~ {{END_DATE}}</p>
  </div>

  <div class="metrics-grid">
    <div class="metric-card" style="background: var(--gradient-blue);">
      <div class="label">前4月总销量</div>
      <div class="value">{{TOTAL_SALES}}</div>
      <div class="sub">聚合表口径</div>
    </div>
    <div class="metric-card" style="background: var(--gradient-green);">
      <div class="label">前4月销售额</div>
      <div class="value">{{TOTAL_REVENUE}}</div>
      <div class="sub">{{CURRENCY}}</div>
    </div>
    <div class="metric-card" style="background: var(--gradient-orange);">
      <div class="label">累计评论增长</div>
      <div class="value">{{REVIEW_GROWTH}}</div>
      <div class="sub">前4月累计</div>
    </div>
    <div class="metric-card" style="background: var(--gradient-purple);">
      <div class="label">大类最佳排名 (BSR)</div>
      <div class="value">#{{BEST_BSR}}</div>
      <div class="sub">数值越低排名越好</div>
    </div>
  </div>

  <!-- ===== 模块2：关键时间节点 ===== -->
  <div class="section">
    <h2 class="section-title">📅 关键时间节点</h2>
    <div class="timeline">
      <!-- 用JS或直接硬编码每个时间节点 -->
      <div class="timeline-item">
        <span class="event-name">首次上架</span>
        <span class="event-value">{{FIRST_LIST_DATE}}</span>
      </div>
      <!-- ... 其他事件按同样格式 ... -->
    </div>
  </div>

  <!-- ===== 模块3：核心趋势图表 ===== -->
  <div class="section">
    <h2 class="section-title">📈 核心趋势</h2>
    <div class="chart-container">
      <h4 style="margin-bottom: 12px; color: var(--text-secondary); font-size: 14px;">排名 / 成交价 / 评论数 综合趋势</h4>
      <canvas id="trendChart"></canvas>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
      <div class="chart-container">
        <h4 style="margin-bottom: 12px; color: var(--text-secondary); font-size: 14px;">月度销量结构对比</h4>
        <canvas id="salesChart"></canvas>
      </div>
      <div class="chart-container">
        <h4 style="margin-bottom: 12px; color: var(--text-secondary); font-size: 14px;">月度新增评论数</h4>
        <canvas id="reviewChart"></canvas>
      </div>
    </div>
  </div>

  <!-- ===== 模块4：前4个月汇总表 ===== -->
  <div class="section">
    <h2 class="section-title">📊 前4个月汇总</h2>
    <div class="table-wrapper">
      <table class="summary-table">
        <thead>
          <tr>
            <th>月份</th><th>策略</th><th>销量</th><th>成交价</th>
            <th>大类BSR最佳</th><th>小类最佳</th><th>评论数</th>
            <th>留评率</th><th>广告占比</th><th>新增广告</th>
          </tr>
        </thead>
        <tbody>
          <!-- 每月一行 -->
        </tbody>
      </table>
    </div>
  </div>

  <!-- ===== 模块5：月度推广节奏拆解 ===== -->
  <div class="section">
    <h2 class="section-title">🔍 推广节奏拆解</h2>
    <!-- 每月一个 month-card -->
    <div class="month-card">
      <div class="month-header" onclick="toggleMonth(this)">
        <h3>MONTH 1 — 第1个月（起止日期）</h3>
        <span class="month-tag tag-entry">低价切入+评论拉升</span>
      </div>
      <div class="month-body active">
        <!-- 内容区域 -->
      </div>
    </div>
    <!-- MONTH 2, 3, 4 同理 -->
  </div>

  <!-- ===== 模块6：效果总结 ===== -->
  <div class="section">
    <h2 class="section-title">🎯 效果总结</h2>
    <div class="result-grid">
      <!-- 结果指标 -->
    </div>
  </div>

  <!-- ===== 模块7：明细数据表 ===== -->
  <div class="section">
    <h2 class="section-title">📋 明细数据</h2>
    <div class="collapsible-header" onclick="toggleCollapse(this)">
      <span>全量明细数据</span>
      <span class="arrow">▼</span>
    </div>
    <div class="collapsible-content">
      <div class="table-wrapper">
        <table><!-- 完整数据表 --></table>
      </div>
    </div>
    <!-- 其他维度的折叠表同理 -->
  </div>

  <!-- 数据缺失提示（如有需要） -->
  <div class="data-notice" id="dataNotice" style="display:none;">
    ⚠️ 以下数据未获取到，报告中用"—"表示：<span id="missingFields"></span>
  </div>

</div>

<script>
  // ===== 折叠交互 =====
  function toggleMonth(el) {
    const body = el.nextElementSibling;
    body.classList.toggle('active');
  }
  function toggleCollapse(el) {
    el.classList.toggle('open');
    el.nextElementSibling.classList.toggle('open');
  }

  // ===== Chart.js 图表初始化 =====
  // 综合趋势图
  const trendCtx = document.getElementById('trendChart').getContext('2d');
  new Chart(trendCtx, {
    type: 'line',
    data: {
      labels: [/* 日期数组 */],
      datasets: [
        {
          label: '大类排名(BSR)',
          data: [/* 排名数据 */],
          borderColor: '#4fc3f7',
          backgroundColor: 'transparent',
          yAxisID: 'y-rank',
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: '小类排名',
          data: [/* 排名数据 */],
          borderColor: '#ab47bc',
          backgroundColor: 'transparent',
          yAxisID: 'y-rank',
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: '成交价',
          data: [/* 价格数据 */],
          borderColor: '#66bb6a',
          backgroundColor: 'transparent',
          yAxisID: 'y-price',
          tension: 0.3,
          pointRadius: 0
        },
        {
          label: '评论数',
          data: [/* 评论数据 */],
          borderColor: '#ffa726',
          backgroundColor: 'rgba(255,167,38,0.1)',
          yAxisID: 'y-price',
          fill: true,
          tension: 0.3,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { labels: { color: '#8899aa', font: { size: 12 } } }
      },
      scales: {
        x: { ticks: { color: '#5c7080', maxTicksLimit: 15 }, grid: { color: 'rgba(42,63,84,0.3)' } },
        'y-rank': {
          position: 'left',
          reverse: true,  // 排名越低越好，反转轴
          ticks: { color: '#4fc3f7' },
          grid: { color: 'rgba(42,63,84,0.3)' },
          title: { display: true, text: '排名', color: '#4fc3f7' }
        },
        'y-price': {
          position: 'right',
          ticks: { color: '#66bb6a' },
          grid: { display: false },
          title: { display: true, text: '价格 / 评论数', color: '#66bb6a' }
        }
      }
    }
  });

  // 月度销量柱状图
  const salesCtx = document.getElementById('salesChart').getContext('2d');
  new Chart(salesCtx, {
    type: 'bar',
    data: {
      labels: [/* 月份标签 */],
      datasets: [
        { label: '全部销量', data: [/* */], backgroundColor: '#4fc3f7' },
        { label: '自然流量销量', data: [/* */], backgroundColor: '#66bb6a' },
        { label: '广告流量销量', data: [/* */], backgroundColor: '#ffa726' }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: '#8899aa', font: { size: 11 } } } },
      scales: {
        x: { ticks: { color: '#5c7080' }, grid: { display: false } },
        y: { ticks: { color: '#5c7080' }, grid: { color: 'rgba(42,63,84,0.3)' } }
      }
    }
  });

  // 月度新增评论柱状图
  const reviewCtx = document.getElementById('reviewChart').getContext('2d');
  new Chart(reviewCtx, {
    type: 'bar',
    data: {
      labels: [/* 月份标签 */],
      datasets: [
        { label: '新增评论', data: [/* */], backgroundColor: '#ab47bc', borderRadius: 6 }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#5c7080' }, grid: { display: false } },
        y: { ticks: { color: '#5c7080' }, grid: { color: 'rgba(42,63,84,0.3)' } }
      }
    }
  });
</script>
</body>
</html>
```

## 数据填充说明

生成报告时，用实际数据替换所有 `{{PLACEHOLDER}}`。对于Chart.js图表，将数据直接写入JS的data数组中。

## 风险判断逻辑

```javascript
function judgeRisk(reviewRate, adRatio, monthlyReviewGrowth) {
  const risks = [];
  if (reviewRate > 0.03) {
    risks.push({ level: 'red', text: `留评率${(reviewRate*100).toFixed(1)}%，超过3%，需警惕刷单风险` });
  } else if (reviewRate > 0.01) {
    risks.push({ level: 'yellow', text: `留评率${(reviewRate*100).toFixed(1)}%，略高于1%，需观察` });
  }
  if (adRatio < 0.05 && monthlyReviewGrowth > 50) {
    risks.push({ level: 'yellow', text: '广告占比低但评论增长快，排名来源需关注' });
  }
  if (monthlyReviewGrowth > 100 && reviewRate > 0.05) {
    risks.push({ level: 'red', text: '评论增速异常，高度疑似刷单' });
  }
  if (risks.length === 0) {
    risks.push({ level: 'green', text: '未触发明显风险信号' });
  }
  return risks;
}
```

## 策略标签自动判断

```javascript
function getStrategyTag(monthIndex, data, allMonthsData) {
  if (monthIndex === 0) {
    const avgPriceLater = allMonthsData.slice(1).reduce((s,m) => s + m.avgPrice, 0) / (allMonthsData.length - 1);
    if (data.avgPrice < avgPriceLater * 0.85) return { tag: '低价切入+评论拉升', class: 'tag-entry' };
    return { tag: '常规起步', class: 'tag-maintain' };
  }
  if (monthIndex === 3) {
    if (data.adRatio > allMonthsData[monthIndex-1].adRatio) return { tag: '广告调整+排名冲刺', class: 'tag-sprint' };
  }
  // 中间月份
  const prevBSR = allMonthsData[monthIndex-1].bestBSR;
  const change = Math.abs(data.bestBSR - prevBSR) / prevBSR;
  if (change < 0.2) return { tag: '排名维持期', class: 'tag-maintain' };
  return { tag: '排名回落观察', class: 'tag-risk' };
}
```
