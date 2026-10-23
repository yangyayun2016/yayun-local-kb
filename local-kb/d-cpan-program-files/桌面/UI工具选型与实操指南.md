# 这个 UI 怎么做的？工具选择与实操指南

## 一、风格定性

这是一张典型的「中国 SaaS 移动端 Dashboard」截图，整体视觉语言如下：

- **平台**：移动端 H5 / 小程序风格
- **布局**：顶部状态栏 + 筛选条 + 双指标卡 + 折线图 + 业绩对比 + 利润统计 + 底部 6 Tab
- **色板**：主色 Antd 蓝（#1677FF）+ 白底卡片 + 涨跌绿红
- **字体**：系统字（PingFang SC / Microsoft YaHei）+ 数字大字号加粗
- **图表**：ECharts / AntV / Recharts 风格折线图
- **既视感参考**：店小秘、蝉妈妈、抖查查、飞书多维表格、Antd Mobile、Vant

---

## 二、工具选型对比

| 工具 | 适合场景 | 还原度 | 推荐指数 |
|---|---|---|---|
| v0.dev（Vercel） | 卡片 + 数据展示类 UI 之王，吐 React + Tailwind + shadcn | ⭐⭐⭐⭐⭐ | 强烈推荐 |
| same.new | 输描述 / 截图 → React + Tailwind 代码 | ⭐⭐⭐⭐ | 推荐 |
| Bolt.new | 全栈 + 部署一体 | ⭐⭐⭐ | 备选 |
| Lovable / Relume | 营销页 / 落地页为主 | ⭐⭐ | 不推荐 |
| Pencil Project | 画线框图 / 原型 | ⭐⭐ | 不推荐 |
| Galileo / Uizard / Visily | AI 生成设计稿 / 线框 | ⭐⭐⭐ | 仅出原型 |
| Figma / 即时设计 / MasterGo | 专业 UI 稿，自由度最高 | ⭐⭐⭐⭐⭐ | 出设计稿首选 |
| antd-mobile 手搓 | 100% 还原控制 | ⭐⭐⭐⭐⭐ | 工程化首选 |

**结论：**

这类中国 SaaS 数据后台 UI，**首选 v0.dev**，原因是它默认就吐 Tailwind + shadcn/ui + lucide-react + Recharts 栈，对中国式蓝色调、卡片化、数据密度的还原度最高。

如果还要先出设计稿再写代码，选 Figma / 即时设计，但中间多一道翻译，效率反而低。

如果工程化要求高、要直接落地项目，用 antd-mobile 手搓最稳。

---

## 三、三套实操方案

### 方案 A：v0.dev（最快，推荐）

打开 v0.dev，粘贴以下 prompt：

```text
做一个移动端 H5 销售数据看板，参考中国 SaaS 风格（Antd Mobile 那种感觉）：

1. 顶部：状态栏 + 一行下拉筛选（国家/店铺/负责人/USD）+ 右侧 ··· 菜单
2. 指标卡 2 张并排：销量（购物袋 icon）今 202 / 昨 113；销售额($) 今 13,757 / 昨 7,806
3. 业绩走势卡：折线图，今日深蓝 / 昨日浅蓝，时间轴 02-23，下方三列：
   今日 202 / 上周同天 31 (+551.61% 绿) / 去年同天 115 (+75.65% 绿)
4. 利润统计：标题 + 前7天下拉（部分可见即可）
5. 底部 Tab Bar 6 个：首页(选中蓝)/统计/订单/广告/应用/消息(红点)

技术栈：Next.js + Tailwind + shadcn/ui + lucide-react + Recharts。
中文界面，主色 #1677FF，绿色涨 #52C41A，白底卡片圆角 shadow-sm。
```

出来的代码直接 `npx create-next-app` 跑起来就能看。

---

### 方案 B：same.new 实操

打开 same.so → New project → 选 **React + Tailwind** 模板 → 把方案 A 的 prompt 贴进去 → 下载后 `pnpm install && pnpm dev`。

---

### 方案 C：手搓（最稳，能 100% 还原）

**脚手架命令：**

```bash
pnpm create vite my-dashboard -- --template react-ts
cd my-dashboard
pnpm add antd-mobile echarts lucide-react
```

**技术选型：**

- **框架**：React + Vite
- **UI 库**：antd-mobile（天生的中国 SaaS 味，比 shadcn 更贴这张图）
- **图标**：lucide-react 或 @ant-design/icons
- **图表**：ECharts for React（echarts-for-react）
- **数字大字号**：`font-variant-numeric: tabular-nums`

---

## 四、字体与系统既视感的关键细节

这种既视感是几个细节堆出来的，单独列出：

```css
/* 1. 数字必须 tabular-nums，等宽对齐，看着就专业 */
.num {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
}

/* 2. 主色用 Antd 默认蓝，比 Tailwind 的 blue-500 更"中国 SaaS" */
:root {
  --primary: #1677FF;
  --up: #52C41A;
  --down: #FF4D4F;
}

/* 3. 卡片：1px 边 + 极轻阴影，不要大圆角 */
.card {
  @apply bg-white rounded-lg border border-gray-100 shadow-sm;
}

/* 4. 字体栈 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* 5. 状态栏占位（移动端 H5 必备） */
.status-bar { height: env(safe-area-inset-top, 24px); }

/* 6. 底部安全区 */
.safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
```

---

## 五、组件拆分建议

按这张图拆出 7 个组件最合适：

| 序号 | 组件 | 职责 |
|---|---|---|
| 1 | `<StatusBar />` | 顶部状态栏 |
| 2 | `<FilterBar />` | 国家/店铺/负责人/USD 筛选条 |
| 3 | `<MetricCards />` | 销量 + 销售额双卡 |
| 4 | `<TrendChart />` | 业绩走势折线图 |
| 5 | `<ComparisonTable />` | 今日/上周/去年对比三列 |
| 6 | `<ProfitSection />` | 利润统计 |
| 7 | `<TabBar />` | 底部 6 Tab |

这样拆分后，每个组件不超过 80 行，可维护性强。

---

## 六、推荐路径总结

| 目标 | 工具 | 耗时 |
|---|---|---|
| 最快出图 | v0.dev | 10 分钟 |
| 工程化落地 | antd-mobile 手搓 | 30 分钟 |
| 设计稿先行 | Figma / 即时设计 | 60 分钟 |

> **对中国 SaaS 风格来说，v0.dev 是性价比最高的工具。**

---

## 附：v0.dev Prompt 备查（可直接复制使用）

```text
做一个移动端 H5 销售数据看板，参考中国 SaaS 风格（Antd Mobile 那种感觉）：

1. 顶部：状态栏 + 一行下拉筛选（国家/店铺/负责人/USD）+ 右侧 ··· 菜单
2. 指标卡 2 张并排：销量（购物袋 icon）今 202 / 昨 113；销售额($) 今 13,757 / 昨 7,806
3. 业绩走势卡：折线图，今日深蓝 / 昨日浅蓝，时间轴 02-23，下方三列：
   今日 202 / 上周同天 31 (+551.61% 绿) / 去年同天 115 (+75.65% 绿)
4. 利润统计：标题 + 前7天下拉（部分可见即可）
5. 底部 Tab Bar 6 个：首页(选中蓝)/统计/订单/广告/应用/消息(红点)

技术栈：Next.js + Tailwind + shadcn/ui + lucide-react + Recharts。
中文界面，主色 #1677FF，绿色涨 #52C41A，白底卡片圆角 shadow-sm。
```

---

**文档结束**
