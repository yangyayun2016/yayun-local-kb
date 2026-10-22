---
name: amazon-ppc-stoploss
description: |
  Amazon Sponsored Products 广告止损分析系统。读取 Search Term Report、Targeting Report、Campaign Report 及产品利润表，按 8 条分层规则识别浪费，输出止损执行表、人工复核表、Bulk Sheet 草稿三张表。
  Use when: (1) 上传广告报告，判断哪些词/ASIN/Campaign 在烧钱, (2) 需要批量否定词、降 bid、暂停 target 的操作清单, (3) 定期广告复盘，生成可直接导入的 Bulk Sheet 草稿

---

## Purpose

帮助亚马逊卖家从 Search Term Report、Targeting Report、Campaign Report 中识别广告浪费，分层执行止损动作，同时避免误杀有转化潜力的关键词。

核心价值：
- 不粗暴关广告，而是按「搜索词 → target → 广告组 → Campaign」从细到粗逐层止损
- 有订单的词降 bid，无订单且花费超限的词才否定
- 所有高风险动作（否定 Phrase、暂停 Campaign、否定 ASIN）强制标记人工复核

---

## Instructions

### Step 1：读取产品参数

用户需提供（或从利润表中读取）：
- 售价（Selling Price）
- 毛利率（Gross Margin）或毛利（Gross Profit）
- 目标 ACOS（Target ACOS）
- 分析周期（默认 7 天）

计算：
```
Break-even ACOS = 毛利率
Max CPA = 售价 × Target ACOS
Break-even CPA = 售价 × Break-even ACOS
```

若用户未提供利润表，询问售价和毛利率后继续。

---

### Step 2：解析上传文件

调用 `scripts/analyze.py`，传入用户上传的文件路径和产品参数。

支持格式：`.csv` / `.xlsx` / `.tsv`

文件类型自动识别规则：
- 含 `Customer Search Term` 字段 → Search Term Report
- 含 `Targeting` + `Match Type` 但无 `Customer Search Term` → Targeting Report
- 含 `Daily Budget` → Campaign Report
- 含 `Gross Margin` 或 `Break-even ACOS` → 利润表

---

### Step 3：执行 8 条止损规则（详见 references/stoploss-rules.md）

判断优先级（同一对象同时命中多条规则时按此顺序）：
1. 明显不相关词 → Negative Phrase 候选
2. 无订单 + 点击超阈值 + 花费超 Max CPA → Negative Exact / Pause Target
3. 有订单但 ACOS > Break-even → 降 bid
4. 严重亏损（ACOS > Target×2，订单≥3）→ Pause Target 候选
5. ASIN target 无订单超限 → Negative Product 候选
6. Campaign 整体无订单花完预算 → Pause Campaign 候选
7. Campaign 亏损但有有效词 → 降预算，不关
8. 新品保护期 → 仅观察，不自动止损

---

### Step 4：输出三张表

**表 1 — 止损执行表**（可直接操作的动作）

| Campaign | Ad Group | Object Type | Object | Clicks | Spend | Orders | ACOS | Rule | Action | Reason |

**表 2 — 人工复核表**（需确认后操作）

| Priority | Object | Suggested Action | Why Review |

**表 3 — Bulk Sheet 草稿**（可下载后直接上传 Amazon 后台）

| Record Type | Operation | Campaign | Ad Group | Keyword/ASIN | Match Type | State | Bid | Reason |

---

## Examples

**输入：**
- 上传 Search Term Report（最近 7 天）
- 售价 $25，毛利率 36%，Target ACOS 25%

**输出：**
- 表 1：5 条止损动作（2 个 Negative Exact，1 个降 bid，2 个观察）
- 表 2：3 条人工复核（1 个 Negative Phrase，1 个 Pause Campaign，1 个 Negative ASIN）
- 表 3：Bulk Sheet 草稿，可直接上传

---

## Guardrails

- 有订单的词，不自动否定，只降 bid
- 点击未达 20 次的词，不自动否定（除非明显不相关）
- 以下动作必须标记 Review Required，不自动执行：
  - Negative Phrase
  - Negative Product（ASIN 否定）
  - Pause Campaign
  - 品牌词否定
  - 竞品词否定
- 新品上线 ≤ 14 天、Review < 5、总广告订单 < 5 时，优先 Observe
- 大促期间（Prime Day / 黑五 / 网一）数据异常，优先 Observe
- 不适用于 Sponsored Brands / Sponsored Display，仅支持 Sponsored Products