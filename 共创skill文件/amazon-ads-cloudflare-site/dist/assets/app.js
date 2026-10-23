const fixedUrl = "https://amazon-ads-ai-optimizer-20260626.pages.dev";

const iconPaths = {
  copy: [
    '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect>',
    '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>'
  ],
  workflow: [
    '<rect width="8" height="8" x="3" y="3" rx="2"></rect>',
    '<rect width="8" height="8" x="13" y="13" rx="2"></rect>',
    '<path d="M7 11v4a2 2 0 0 0 2 2h4"></path>'
  ],
  "cloud-upload": [
    '<path d="M12 13v8"></path>',
    '<path d="m8 17 4-4 4 4"></path>',
    '<path d="M20.4 17.4A5.5 5.5 0 0 0 16 8h-1.3A7 7 0 1 0 5 16.3"></path>'
  ],
  clipboard: [
    '<rect width="8" height="4" x="8" y="2" rx="1"></rect>',
    '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>'
  ],
  link: [
    '<path d="M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1"></path>',
    '<path d="M14 11a5 5 0 0 0-7.1 0l-2 2a5 5 0 0 0 7.1 7.1l1.1-1.1"></path>'
  ],
  "search-check": [
    '<path d="m8 11 2 2 4-4"></path>',
    '<circle cx="11" cy="11" r="8"></circle>',
    '<path d="m21 21-4.3-4.3"></path>'
  ],
  target: [
    '<circle cx="12" cy="12" r="10"></circle>',
    '<circle cx="12" cy="12" r="6"></circle>',
    '<circle cx="12" cy="12" r="2"></circle>'
  ],
  "trending-up": [
    '<path d="m22 7-8.5 8.5-5-5L2 17"></path>',
    '<path d="M16 7h6v6"></path>'
  ],
  route: [
    '<circle cx="6" cy="19" r="3"></circle>',
    '<path d="M9 19h8.5a3.5 3.5 0 0 0 0-7H6.5a3.5 3.5 0 0 1 0-7H15"></path>',
    '<circle cx="18" cy="5" r="3"></circle>'
  ],
  check: ['<path d="M20 6 9 17l-5-5"></path>']
};

function createIcons() {
  document.querySelectorAll("i[data-lucide]").forEach((icon) => {
    const name = icon.dataset.lucide;
    const paths = iconPaths[name];
    if (!paths) return;

    icon.outerHTML = [
      `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"`,
      ` fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">`,
      paths.join(""),
      `</svg>`
    ].join("");
  });
}

const stageDetails = {
  reports: {
    kicker: "Search Term / Campaign",
    title: "广告报表归因",
    summary: "先统一读取广告活动、搜索词、展示位置、商品利润和自然排名，避免只看 ACOS 做单点判断。",
    signal: "花费集中、点击异常、转化不足、自然位未被撬动。",
    action: "建立日报表字段，按 ASIN、Campaign、Ad Group、Keyword 四层聚合。",
    output: "广告诊断总表、利润红线、关键词候选池。"
  },
  sku: {
    kicker: "ASIN / SKU",
    title: "商品利润底线",
    summary: "广告调价必须先知道每个 SKU 能承受的点击成本和目标 ACOS。",
    signal: "售价、FBA、优惠券、毛利率变化导致目标 ACOS 变化。",
    action: "给每个 ASIN 设置目标 ACOS、最低可接受利润和冲排名预算上限。",
    output: "SKU 利润红线表、可承受 CPC 区间。"
  },
  acos: {
    kicker: "Guardrail",
    title: "ACOS 利润红线",
    summary: "把高 ACOS 拆成三类：词不准、价太高、页面转化差。",
    signal: "同一词有点击无单、CPC 高于承受区间、CVR 低于类目基准。",
    action: "错配词否掉，成交词保留并回推出价，低转化词进入 Listing 承接检查。",
    output: "降价清单、否词清单、转化优化清单。"
  },
  leak: {
    kicker: "Leakage",
    title: "流量浪费定位",
    summary: "先止损，再放量。浪费词不处理，预算会持续被低质量流量吃掉。",
    signal: "高点击低转化、曝光高 CTR 低、花费高订单少、竞品词错配。",
    action: "按浪费等级设置暂停、降价、否定精准、否定词组四类动作。",
    output: "浪费流量处置表。"
  },
  structure: {
    kicker: "SP / SB / SD",
    title: "广告结构重建",
    summary: "让每个广告活动只有一个明确任务，避免采词、转化、冲排名混在一起。",
    signal: "预算被自动广告吞掉，精准词拿不到展示，竞品词和类目词混跑。",
    action: "按自动采词、手动精准、词组扩展、竞品防守、再营销分层建组。",
    output: "Campaign 架构图、预算分配表。"
  },
  keyword: {
    kicker: "Harvest",
    title: "关键词采收与否词",
    summary: "自动广告负责发现搜索词，精准广告负责承接有效词。",
    signal: "搜索词有订单但还停留在自动广告，或重复消耗在多个广告组。",
    action: "成交词迁移到精准广告，原广告组加否定精准，避免重复竞价。",
    output: "采词表、否词表、精准词池。"
  },
  bid: {
    kicker: "Bid / Budget",
    title: "出价预算调度",
    summary: "出价决定流量质量，预算决定测试速度。两者必须跟目标阶段匹配。",
    signal: "预算过早耗尽、转化词拿不到展示、低转化词持续消耗。",
    action: "按利润词、冲排名词、测试词设置不同 CPC 区间和预算节奏。",
    output: "出价调整表、预算迁移清单。"
  },
  review: {
    kicker: "Weekly Review",
    title: "周复盘动作清单",
    summary: "每周固定看一组问题：钱花到哪里、哪些词带单、哪些动作改变了自然位。",
    signal: "7 天花费、订单、CVR、自然排名、广告排名与上周对比。",
    action: "输出保留、放量、降价、暂停、否词、补预算六类动作。",
    output: "周复盘报告、下周操作看板。"
  },
  cloudflare: {
    kicker: "Cloudflare",
    title: "固定页面发布",
    summary: "Codex 每次更新 HTML 后，都发布到同一个 Cloudflare Pages 项目。",
    signal: "本地文件不方便分享，临时链接不方便持续更新。",
    action: "项目名固定为 amazon-ads-ai-optimizer-20260626，后续只覆盖部署。",
    output: fixedUrl
  }
};

const detailKicker = document.querySelector("#detailKicker");
const detailTitle = document.querySelector("#detailTitle");
const detailSummary = document.querySelector("#detailSummary");
const detailSignal = document.querySelector("#detailSignal");
const detailAction = document.querySelector("#detailAction");
const detailOutput = document.querySelector("#detailOutput");

document.querySelectorAll(".process-card").forEach((card) => {
  card.addEventListener("click", () => {
    const detail = stageDetails[card.dataset.stage];
    if (!detail) return;

    document.querySelectorAll(".process-card").forEach((item) => item.classList.remove("active"));
    card.classList.add("active");

    detailKicker.textContent = detail.kicker;
    detailTitle.textContent = detail.title;
    detailSummary.textContent = detail.summary;
    detailSignal.textContent = detail.signal;
    detailAction.textContent = detail.action;
    detailOutput.textContent = detail.output;
  });
});

async function copyText(text, trigger) {
  await navigator.clipboard.writeText(text);
  const original = trigger.innerHTML;
  trigger.innerHTML = '<i data-lucide="check"></i><span>已复制</span>';
  createIcons();
  setTimeout(() => {
    trigger.innerHTML = original;
    createIcons();
  }, 1400);
}

document.querySelector("#copyUrl")?.addEventListener("click", (event) => {
  copyText(fixedUrl, event.currentTarget);
});

document.querySelectorAll(".copy-command").forEach((button) => {
  button.addEventListener("click", () => copyText(button.dataset.copy, button));
});

createIcons();
