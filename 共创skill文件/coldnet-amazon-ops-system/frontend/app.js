const state = {
  data: null,
  activeTab: "dashboard",
  keywordFilter: "all",
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    ...options,
  });
  if (!response.ok) throw new Error(`${path} ${response.status}`);
  return response.json();
}

async function loadSystem() {
  state.data = await api("/api/system");
  renderShell();
  renderDashboard();
  renderDiagnosis();
  renderTasks();
  renderReport();
  renderKeywords();
  renderAsinView();
  renderBlueprint();
  bindGlobalEvents();
}

function renderShell() {
  const { navigation, tabs } = state.data;
  $("#mainMenu").innerHTML = navigation
    .map((item) => {
      const active = item === "广告中心" ? "active" : "";
      const locked = item === "广告中心" ? "" : "locked";
      return `<button class="menu-item ${active} ${locked}" type="button"><span>${iconText(item)}</span>${escapeHtml(item)}</button>`;
    })
    .join("");

  $("#tabbar").innerHTML = tabs
    .map((tab) => `<button class="tab-button ${tab.id === state.activeTab ? "active" : ""}" data-tab="${tab.id}" type="button">${escapeHtml(tab.label)}</button>`)
    .join("");

  $$("#tabbar .tab-button").forEach((button) => {
    button.addEventListener("click", () => switchTab(button.dataset.tab));
  });
}

function renderDashboard() {
  const { dashboard } = state.data;
  $("#dashboardAsOf").textContent = dashboard.asOf;
  $("#dashboardAlerts").innerHTML = dashboard.alerts
    .map((alert) => `<div><span class="alert-dot"></span>${escapeHtml(alert)}</div>`)
    .join("");

  $("#dashboardMetrics").innerHTML = `
    <div class="metric-head">
      <span>指标</span><span>昨天</span><span>vs 7天均值</span><span>7天均值</span><span>vs 30天均值</span><span>30天均值</span><span>趋势</span>
    </div>
    ${dashboard.summary
      .map(
        (row) => `
          <div class="metric-row ${row.status}">
            <strong>${escapeHtml(row.name)}</strong>
            <span>${escapeHtml(row.yesterday)}</span>
            <span>${escapeHtml(row.vs7)}</span>
            <span>${escapeHtml(row.avg7)}</span>
            <span>${escapeHtml(row.vs30)}</span>
            <span>${escapeHtml(row.avg30)}</span>
            <span class="status-dot ${row.status}">${statusName(row.status)}</span>
          </div>
        `,
      )
      .join("")}
  `;

  $("#storeRows").innerHTML = dashboard.stores
    .map(
      (store) => `
        <tr data-go="asin">
          <td><button class="link-button" type="button" data-go="asin">${escapeHtml(store.store)}</button></td>
          <td>${store.spend}</td>
          <td>${store.sales}</td>
          <td><span class="value-good">${store.acos}</span></td>
          <td>${store.tacos}</td>
          <td>${store.orders}</td>
          <td>${store.adShare}</td>
          <td>${store.impressions}</td>
          <td>${store.clicks}</td>
          <td>${store.ctr}</td>
          <td>${store.cpc}</td>
          <td>${store.cvr}</td>
          <td>${store.budgetCaps}</td>
          <td><span class="status-dot ok">${store.health}</span></td>
        </tr>
      `,
    )
    .join("");
}

function renderDiagnosis() {
  const { diagnosis } = state.data;
  $("#pipelineList").innerHTML = diagnosis.pipeline
    .map((step, index) => `<li><span>${index + 1}</span>${escapeHtml(step)}</li>`)
    .join("");
  renderJobs();
}

function renderJobs() {
  const jobs = state.data.diagnosis.jobs;
  $("#jobCards").innerHTML = jobs
    .map(
      (job) => `
        <article class="job-card">
          <div>
            <strong>${escapeHtml(job.title)}</strong>
            <span>${escapeHtml(job.store)} · ${escapeHtml(job.createdAt)}</span>
          </div>
          <span class="status-dot ${job.status === "已完成" ? "ok" : "warn"}">${escapeHtml(job.status)}</span>
          <div class="button-row">
            <button class="ghost-button" data-go="report" type="button">查看报告</button>
            <button class="ghost-button" data-go="tasks" type="button">生成清单</button>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderTasks() {
  const tasks = state.data.tasks;
  $("#taskGrid").innerHTML = tasks
    .map(
      (task) => `
        <article class="task-card level-${levelClass(task.level)}" data-task-id="${escapeHtml(task.id)}">
          <div class="task-head">
            <span class="risk-badge">${escapeHtml(task.level)}</span>
            <span class="status-dot ${taskStatusClass(task.status)}">${escapeHtml(task.status)}</span>
          </div>
          <h3>${escapeHtml(task.title)}</h3>
          <p>${escapeHtml(task.summary)}</p>
          <dl>
            <div><dt>核心指标</dt><dd>${escapeHtml(task.metric)}</dd></div>
            <div><dt>建议动作</dt><dd>${escapeHtml(task.action)}</dd></div>
            <div><dt>负责人</dt><dd>${escapeHtml(task.owner)} · ${escapeHtml(task.due)}</dd></div>
          </dl>
          <textarea placeholder="部分采纳或忽略时填写原因"></textarea>
          <div class="button-row">
            <button class="primary-button compact" data-status="全部采纳" type="button">全部采纳</button>
            <button class="ghost-button" data-status="部分采纳" type="button">部分采纳</button>
            <button class="ghost-button" data-status="忽略" type="button">忽略</button>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderReport() {
  const report = state.data.report;
  const steps = [
    "产品基础信息",
    "基础面判断",
    "月度销售广告毛利",
    "盈亏平衡ACOS",
    "Campaign结构",
    "关键词表现",
    "广告位表现",
    "预算打满",
    "竞品BSR",
    "排名下滑根因",
    "立即动作",
    "ABA搜索词绩效",
    "外部机会词",
  ];
  $("#reportNav").innerHTML = steps
    .map((step, index) => `<a href="#report-step-${index + 1}"><span>${index + 1}</span>${escapeHtml(step)}</a>`)
    .join("");

  $("#reportDocument").innerHTML = `
    <header class="report-cover">
      <p class="eyebrow">${escapeHtml(report.store)}</p>
      <h2>${escapeHtml(report.title)}</h2>
      <div class="report-meta">
        <span>ASIN：${escapeHtml(report.asin)}</span>
        <span>生成时间：${escapeHtml(report.generatedAt)}</span>
        <span>数据来源：${escapeHtml(report.sources)}</span>
      </div>
      <p>${escapeHtml(report.coverage)}</p>
    </header>
    ${reportSection(1, steps[0], keyValueTable(report.product))}
    ${reportSection(2, steps[1], simpleCards(report.baseChecks))}
    ${reportSection(3, steps[2], dataTable(["月份", "销量", "销售额", "广告费", "ACOS", "TACOS", "毛利润", "广告后毛利率", "CPC"], report.monthly))}
    ${reportSection(4, steps[3], conclusionBox("盈亏平衡ACOS约31%。当前5月ACOS 37.7%，每投一次广告都在亏钱；历史最优期ACOS 16~21%，有10个百分点安全余量。"))}
    ${reportSection(5, steps[4], dataTable(["Campaign", "状态", "日预算", "近3月花费", "近3月订单", "ACOS", "上线时间"], report.campaigns))}
    ${reportSection(6, steps[5], keywordSummary(report.keywords))}
    ${reportSection(7, steps[6], dataTable(["Campaign", "广告位", "花费", "订单", "ACOS", "判断"], report.placements))}
    ${reportSection(8, steps[7], dataTable(["Campaign", "4月以来预算打满次数", "日预算", "问题"], report.budgetCaps))}
    ${reportSection(9, steps[8], dataTable(["时间段", "B0XX-01（我们）", "BOYY-A（竞品1）", "BOYY-D（竞品2）"], report.competitors))}
    ${reportSection(10, steps[9], timelineBlock(report.timeline))}
    ${reportSection(11, steps[10], actionList(report.actions))}
    ${reportSection(12, steps[11], dataTable(["搜索词", "月搜索量", "点击占比", "购买占比", "购买", "广告花费", "广告ACOS", "SIF时机", "综合判断"], report.aba))}
    ${reportSection(13, steps[12], dataTable(["搜索词", "月搜索量", "BA购买占比", "建议"], report.longTail))}
    <section class="report-section">
      <h3>截图依据</h3>
      <div class="evidence-strip">
        ${report.evidence.slice(0, 6).map((src, index) => `<img src="${src}" alt="报告截图依据 ${index + 1}" />`).join("")}
      </div>
    </section>
  `;
}

function renderKeywords() {
  const report = state.data.report;
  const items = report.keywords.filter((item) => state.keywordFilter === "all" || item.type === state.keywordFilter);
  $("#keywordRows").innerHTML = items
    .map(
      (item) => `
        <tr>
          <td><strong>${item.word}</strong></td>
          <td>${formatNumber(item.volume)}</td>
          <td>${item.spend}</td>
          <td>${item.orders}</td>
          <td>${item.sales}</td>
          <td>${item.acos}</td>
          <td>${item.clicks}</td>
          <td>${escapeHtml(item.judge)}</td>
          <td><span class="type-pill ${item.type}">${opportunityName(item.type)}</span></td>
        </tr>
      `,
    )
    .join("");

  $("#abaPanels").innerHTML = `
    <div>
      <h3>高量级词表现</h3>
      ${dataTable(["搜索词", "月搜索量", "点击占比", "购买占比", "购买", "广告花费", "广告ACOS", "SIF时机", "综合判断"], report.aba)}
    </div>
    <div>
      <h3>长尾高转化词</h3>
      ${dataTable(["搜索词", "月搜索量", "BA购买占比", "建议"], report.longTail)}
    </div>
  `;
}

function renderAsinView() {
  const report = state.data.report;
  $("#asinView").innerHTML = `
    <div class="profile-card">
      <div class="card-head">
        <h3>产品基础信息</h3>
        <span class="status-dot ok">LQS 95</span>
      </div>
      ${keyValueTable(report.product)}
    </div>
    <div class="profile-card">
      <div class="card-head">
        <h3>利润与广告风险</h3>
        <span class="status-dot warn">ACOS偏高</span>
      </div>
      <div class="mini-grid">
        <div><span>盈亏平衡ACOS</span><strong>31%</strong></div>
        <div><span>当前ACOS</span><strong>37.7%</strong></div>
        <div><span>历史安全区</span><strong>16~21%</strong></div>
        <div><span>优先动作</span><strong>停K01/K02</strong></div>
      </div>
    </div>
    <div class="profile-card wide">
      <div class="card-head">
        <h3>月度销售、广告与毛利</h3>
        <button class="ghost-button" data-go="report" type="button">进入报告</button>
      </div>
      ${dataTable(["月份", "销量", "销售额", "广告费", "ACOS", "TACOS", "毛利润", "广告后毛利率", "CPC"], report.monthly)}
    </div>
    <div class="profile-card wide">
      <div class="card-head">
        <h3>原型首页依据</h3>
        <span>来自天机OS WPS截图</span>
      </div>
      <img class="full-image" src="/assets/tianji-os-dashboard.jpg" alt="天机OS广告中心截图依据" />
    </div>
  `;
}

function renderBlueprint() {
  const { blueprint, rules } = state.data;
  $("#blueprintView").innerHTML = `
    <div class="blueprint-grid">
      <article class="blue-card">
        <span>1年</span>
        <h3>验证闭环</h3>
        <p>${escapeHtml(blueprint.oneYear)}</p>
      </article>
      <article class="blue-card">
        <span>3年</span>
        <h3>模块化平台</h3>
        <p>${escapeHtml(blueprint.threeYear)}</p>
      </article>
      <article class="blue-card">
        <span>5年</span>
        <h3>AI OS生态</h3>
        <p>${escapeHtml(blueprint.fiveYear)}</p>
      </article>
    </div>
    <div class="table-card">
      <div class="card-head">
        <h3>系统积木模块</h3>
        <span>售前可组合，技术可快速生成Demo</span>
      </div>
      <div class="module-grid">
        ${blueprint.modules.map((module) => `<button type="button">${escapeHtml(module)}</button>`).join("")}
      </div>
    </div>
    <div class="table-card">
      <div class="card-head">
        <h3>广告诊断规则引擎</h3>
        <span>规则先算事实，AI只负责解释和报告</span>
      </div>
      ${dataTable(["规则", "逻辑", "样例", "等级"], rules.map((rule) => [rule.name, rule.logic, rule.sample, rule.level]))}
    </div>
  `;
}

function bindGlobalEvents() {
  document.addEventListener("click", (event) => {
    const go = event.target.closest("[data-go]");
    if (go) switchTab(go.dataset.go);

    const taskButton = event.target.closest("[data-status]");
    if (taskButton) updateTask(taskButton);

    const keywordFilter = event.target.closest("[data-filter]");
    if (keywordFilter) {
      state.keywordFilter = keywordFilter.dataset.filter;
      $$("#view-keywords .seg").forEach((button) => button.classList.toggle("active", button === keywordFilter));
      renderKeywords();
    }
  });

  $("#diagnosisForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const result = await api("/api/diagnosis/jobs", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    state.data.diagnosis.jobs.unshift(result.job);
    renderJobs();
    renderMissingData(result.missingData);
  });

  $("#openEvidence").addEventListener("click", () => openEvidence());
  $("#closeEvidence").addEventListener("click", () => $("#evidenceDialog").close());
  $("#addReportTasks").addEventListener("click", () => {
    switchTab("tasks");
    $("#taskGrid").scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

async function updateTask(button) {
  const card = button.closest(".task-card");
  const id = card.dataset.taskId;
  const status = button.dataset.status;
  const note = $("textarea", card).value;
  const result = await api(`/api/tasks/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify({ status, note }),
  });
  const index = state.data.tasks.findIndex((task) => task.id === id);
  if (index >= 0) state.data.tasks[index] = result.task;
  renderTasks();
}

function renderMissingData(items) {
  const box = $("#missingBox");
  if (!items.length) {
    box.innerHTML = `<span class="status-dot ok">诊断已完成，可查看完整报告</span>`;
    return;
  }
  box.innerHTML = `
    <strong>需补充数据</strong>
    <ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
  `;
}

function openEvidence() {
  const report = state.data.report;
  $("#evidenceGrid").innerHTML = `
    <figure>
      <img src="/assets/tianji-os-dashboard.jpg" alt="天机OS广告中心总览截图" />
      <figcaption>广告中心看板依据</figcaption>
    </figure>
    ${report.evidence
      .map(
        (src, index) => `
          <figure>
            <img src="${src}" alt="诊断报告截图 ${index + 1}" />
            <figcaption>报告截图 ${index + 1}</figcaption>
          </figure>
        `,
      )
      .join("")}
  `;
  $("#evidenceDialog").showModal();
}

function switchTab(tab) {
  state.activeTab = tab;
  $$(".tab-button").forEach((button) => button.classList.toggle("active", button.dataset.tab === tab));
  $$(".view").forEach((view) => view.classList.toggle("active", view.id === `view-${tab}`));
  window.location.hash = tab;
}

function reportSection(index, title, content) {
  return `
    <section class="report-section" id="report-step-${index}">
      <h3><span>${index}</span>${escapeHtml(title)}</h3>
      ${content}
    </section>
  `;
}

function keyValueTable(rows) {
  return `
    <table class="kv-table">
      <tbody>${rows.map(([key, value]) => `<tr><th>${escapeHtml(key)}</th><td>${escapeHtml(value)}</td></tr>`).join("")}</tbody>
    </table>
  `;
}

function dataTable(headers, rows) {
  return `
    <div class="table-wrap">
      <table>
        <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join("")}</tr></thead>
        <tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${escapeHtml(cell)}</td>`).join("")}</tr>`).join("")}</tbody>
      </table>
    </div>
  `;
}

function simpleCards(items) {
  return `
    <div class="simple-grid">
      ${items
        .map(
          (item) => `
            <div>
              <span>${escapeHtml(item.name)}</span>
              <strong>${escapeHtml(item.value)}</strong>
              <p>${escapeHtml(item.judge)}</p>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function conclusionBox(text) {
  return `<div class="conclusion-box">${escapeHtml(text)}</div>`;
}

function keywordSummary(items) {
  const table = dataTable(
    ["关键词", "月搜索量", "花费", "订单", "销售额", "ACOS", "点击", "判断"],
    items.map((item) => [item.word, formatNumber(item.volume), item.spend, item.orders, item.sales, item.acos, item.clicks, item.judge]),
  );
  return `${table}<div class="conclusion-box">核心发现：K01/K02花费多但真实购买转化差；K10购买占比高但广告覆盖极少，应优先加投。</div>`;
}

function timelineBlock(rows) {
  return `
    <div class="cause-chain">
      <span>5月旺季到来</span><span>竞品加大广告投入</span><span>CPC上涨50%</span><span>低预算上午打满</span><span>广告断流</span><span>自然排名下滑</span>
    </div>
    ${dataTable(["日期", "广告花费", "总销量", "关键事件"], rows)}
  `;
}

function actionList(actions) {
  return `
    <div class="action-list">
      ${actions
        .map(
          (item) => `
            <div>
              <span>${escapeHtml(item.priority)}</span>
              <strong>${escapeHtml(item.action)}</strong>
              <p>${escapeHtml(item.impact)}</p>
            </div>
          `,
        )
        .join("")}
    </div>
  `;
}

function statusName(status) {
  return { up: "上升", ok: "正常", warn: "预警" }[status] || status;
}

function taskStatusClass(status) {
  if (status === "全部采纳" || status === "已完成") return "ok";
  if (status === "忽略") return "muted";
  return "warn";
}

function levelClass(level) {
  return { 极高: "critical", 高: "high", 中: "medium", 低: "low" }[level] || "medium";
}

function opportunityName(type) {
  return {
    stop: "立即停投",
    priority: "最优先加投",
    scale: "加投",
    reduce: "降价/否词",
    negative: "否定",
    layout: "自然排名布局",
  }[type] || "观察";
}

function iconText(item) {
  const map = {
    工作台: "▦",
    销售中心: "↗",
    广告中心: "AD",
    商品中心: "★",
    选品中心: "⌕",
    库存货件: "◈",
    物流中心: "▸",
    采购中心: "□",
    财务中心: "$",
    团队管理: "TM",
    Agent中心: "AI",
    数据助手: "◎",
    工具箱: "TL",
    系统设置: "ST",
  };
  return map[item] || "·";
}

function formatNumber(value) {
  return Number(value).toLocaleString("zh-CN");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadSystem().catch((error) => {
  document.body.innerHTML = `<main class="fatal"><h1>系统加载失败</h1><p>${escapeHtml(error.message)}</p></main>`;
});
