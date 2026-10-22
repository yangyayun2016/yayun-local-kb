---
name: amazon-ppc-profit-diagnosis
description: |
  亚马逊广告专业分析与利润诊断系统。交互式采集产品客单价、类目平均转化率/CPC、毛利率、广告预算、目标ACOS及其上调/下调阈值等参数，建立「广告前毛利率＝盈亏平衡ACOS」的盈亏分析架构，把每个搜索词/Target/词根/Campaign 分入五档健康分区，同时输出「止损（否词/降bid/关停）」与「待投放（提价/扩量/新建精准Campaign）」两个方向的建议，并生成每日诊断单（昨日 vs 近7日/30日均值，UP/DOWN趋势）、词根聚合表、异常问题清单。
  Use when: (1) 用户上传亚马逊广告后台报表（Search Term / Targeting / Campaign Report）并希望做专业分析而不只是简单止损, (2) 用户想设定目标ACOS、测算能承受多少CPC/CPA、算清楚"愿意用多少毛利做广告", (3) 用户需要每日/每周广告诊断复盘、看昨日数据相对近期趋势的变化, (4) 用户想知道除了否词止损，哪些词/词根值得加大投放, (5) 用户提到"广告止损"、"待投放"、"广告诊断"、"目标ACOS阈值"、"盈亏平衡ACOS"、"词根聚合"等术语。即使用户只说"帮我看看这份广告报表该怎么调"，也应触发本 Skill。

---

## Purpose

这是一个**决策型**广告分析 Skill，不是简单的"关广告工具"。核心价值：

- 用「广告前毛利率＝盈亏平衡 ACOS」把 ACOS 判断从模糊的经验值，变成可计算的利润公式
- 目标 ACOS 不是一条线，而是「优质区 / 健康区 / 预警区 / 承压区 / 亏损区」五档分区，
  每一档对应明确动作，而不是只有"关"或"不关"
- 止损（收）与待投放（放）是同一套分区逻辑的两个方向，本 Skill 同时输出两者，
  避免只会防守、不会进攻
- 从搜索词、词根、Target、Campaign 四个颗粒度分层判断，避免误杀/误放
- 每日诊断单把"今天广告是否异常"和"这个词该不该动"分成宏观/中观/微观三层，逻辑独立
- 所有高风险动作强制标记人工复核，低风险动作（观察、降/提10-20%）可直接生成执行清单

详细公式、诊断规则、待投放规则分别在：
`references/formulas.md`、`references/diagnosis-rules.md`、`references/scale-up-and-root-clustering.md`。
本文件只讲流程，判断细节以三份文档为准，Instructions 中会指明何时该读哪一份。

---

## Instructions

### Step 0：判断这次是"配置"还是"分析"

- 如果用户是第一次使用，或明确要"设置规则/配置参数" → 走 Step 1 完整交互式配置
- 如果用户已经提供过参数（本次对话前面出现过，或直接甩报表说"按上次的算"）
  → 跳过 Step 1，直接复用已有参数进入 Step 2，但仍要口头确认一次关键数字（客单价、目标ACOS、毛利率），避免用错版本
- 如果用户只想问一个孤立的公式问题（比如"CPC上限怎么算"）→ 直接用 `references/formulas.md` 里的公式回答，不必启动完整流程

---

### Step 1：交互式规则配置

分四组提问，每组尽量一次问完（避免变成审讯式逐条提问），允许用户跳过、给区间估算值、
或者说"不知道，用默认值"——所有参数都要有合理默认值兜底，缺参数不是卡流程的理由。

**A. 产品与市场基准**
```
1. 客单价 Selling Price（$）
2. 目标类目平均转化率 CVR（%）——没有就用自己产品近30天实际CVR代替
3. 目标类目平均 CPC（$）——可选，用于判断类目整体能不能打平，没有就跳过
```

**B. 利润参数**
```
4. 产品单位毛利（广告前，即已扣 COGS/头程/FBA费/佣金，但不扣广告费）$
   —— 或者给毛利率(%)，脚本用「毛利率 × 客单价」反推
5.（可选）该产品历史广告前毛利率区间，如"19%–29%，月均24%"
   —— 没有就用第4项算出的毛利率作为 Break-even ACOS
```

**C. ACOS 目标与阈值（五档分区参数，见 formulas.md 第六节）**
```
6. 目标 ACOS（%）
7. 上调阈值系数（默认 20%，即预警区上限 = 目标ACOS × 1.2）
8. 下调阈值系数（默认 20%，即优质区上限 = 目标ACOS × 0.8）
9. 毛利牺牲比例 sacrifice_ratio：
   - 保守（如 70%，广告后仍留部分毛利）
   - 盈亏平衡（100%，默认）
   - 激进（如 130%，新品冲排名/大促蓄流量，愿意用毛利以外的钱换份额）
```

**D. 预算与投放阶段**
```
10. 日预算（$）或目标广告占比 TACOS（%），二选一即可
11. 该产品是否处于新品保护期（上线≤14天 / Review<5 / 广告订单<5，满足任一即算新品）
12. 分析周期：默认最近 7 天（微观止损/待投放判断窗口），诊断单固定用近30天趋势
```

配置完成后，**先把计算出的关键阈值念给用户确认**，再进入 Step 2：
```
Break-even ACOS（盈亏平衡）= XX%
目标 ACOS = XX%（优质区 ≤XX% ｜ 健康区 XX–XX% ｜ 预警区 XX–XX% ｜ 承压区 XX–XX% ｜ 亏损区 >XX%）
Max CPA = $X.XX　可承受 CPC = $X.XX　出单临界点击数 = X 次
```

---

### Step 2：解析上传文件

调用 `scripts/diagnose.py`，支持以下文件类型，可一次传多个，脚本自动识别：

| 文件类型 | 用途 | 识别依据 |
|---------|------|---------|
| Search Term Report | 微观止损/待投放 + 词根聚合 | 含 `Customer Search Term` 列 |
| Targeting Report | Target 层止损/待投放 | 含 `Targeting`+`Match Type`，无 `Customer Search Term` |
| Campaign Report | Campaign 层止损/待投放 + 预算打满率 | 含 `Daily Budget` |
| 每日趋势报表 | 宏观每日诊断单 | 含 `Date` 列且覆盖 ≥7 行不同日期 |
| 产品利润表 | 补充/覆盖 Step 1 的利润参数 | 含 `Gross Margin` 或 `Break-even ACOS` |

支持 `.csv` / `.xlsx` / `.tsv`。如果用户没有"每日趋势报表"，Step 4 的诊断单跳过，
不影响 Step 5/6 的词根聚合与止损/待投放判断（那两步只需要窗口聚合数据）。

---

### Step 3：计算五档分区阈值

按 `references/formulas.md` 第六节公式，用 Step 1 参数算出：
```
floor（优质区上限）= target_acos × (1 − 下调阈值系数)
ceiling（预警区上限）= target_acos × (1 + 上调阈值系数)
breakeven = 广告前毛利率
```
这四个数字（floor / target / ceiling / breakeven）贯穿 Step 4–6 的所有判断，先算出来再往下走。

---

### Step 4：每日诊断单（若有每日趋势报表）

按 `references/diagnosis-rules.md` 生成：
1. 顶部一句话结论（按该文档第四节优先级规则）
2. 指标对比表：昨日 / 近7日均值 / 近30日均值 / 涨跌幅 / 趋势符号（▲▼→），
   覆盖 Spend、Sales、ACOS、TACOS（如有自然销量数据）、ROI、Orders、CVR、CPC、预算打满率
3. 异常问题清单（该文档第五节），全部标记为人工复核

---

### Step 5：词根聚合分析（若有 Search Term Report）

按 `references/scale-up-and-root-clustering.md` 第五节做词根提取与聚合，
输出词根层级表（词根 / 覆盖搜索词数 / 汇总指标 / 词根ACOS / 分区 / 建议操作）。

词根层的分区判断复用 Step 3 算出的 floor/target/ceiling/breakeven，
但样本阈值放宽（词根 Orders≥5 才判优质，Orders=0 才判止损候选）。

---

### Step 6：止损与待投放建议（微观：搜索词 / Target / Campaign 三层）

对每个对象（搜索词 / Keyword Target / ASIN Target / Campaign）：
1. 先看有没有订单——**有订单一律优先降/提 bid，不直接否定，也不用一次性大幅提价**
2. 落入 Step 3 的哪个分区，映射到对应方向的动作：

```
① 优质区 + 样本足够   → 待投放：PROMOTE_TO_EXACT / RAISE_BID_10~20 / RAISE_BUDGET
② 健康区              → 维持，NO_ACTION
③ 预警区              → OBSERVE，小幅降 bid 10%
④ 承压区              → LOWER_BID_20~30 / REDUCE_BUDGET
⑤ 亏损区 + 无订单+点击超止损阈值 → NEGATIVE_EXACT / PAUSE_TARGET / PAUSE_CAMPAIGN
⑤ 亏损区 + 有订单     → 先 LOWER_BID_30~50，订单≥3且ACOS>目标ACOS×2 才升级为暂停候选
```

3. 明显不相关词（低意图词根，如 free/used/repair/pdf 等，见脚本内清单）→ 无视分区，
   ≥5 clicks 且 0 订单直接标记 `NEGATIVE_PHRASE*`，人工复核
4. 新品保护期内，除明显不相关词外，其余止损动作一律降级为 `OBSERVE`
5. 待投放动作的幅度上限：常规模式 ≤20%，激进模式（sacrifice_ratio>100%）另行标注

---

### Step 7：输出模块化报告

按以下模块顺序输出（没有对应数据的模块跳过，不要输出空表）：

1. **规则配置回顾**（Step 1 确认的参数 + Step 3 算出的四个分区阈值）
2. **每日诊断单**（Step 4）
3. **词根聚合表**（Step 5）
4. **止损执行表**：`Campaign | Ad Group | Object Type | Object | Clicks | Spend | Orders | ACOS | 分区 | Action | Reason | Review Required`
5. **待投放清单**：`Object Type | Object | 当前匹配方式 | ACOS | Orders | 分区 | Action | 建议幅度 | Review Required`
6. **人工复核表**：`Priority | Object | Suggested Action | Why Review`
7. **Bulk Sheet 草稿**：`Record Type | Operation | Campaign | Ad Group | Keyword/Product Targeting | Match Type | State | Bid | Reason`
8. **可视化图表**（如运行环境支持图表/可视化组件）：ACOS 五档分区柱状/散点图、
   花费与ACOS近30日趋势折线图、词根聚合气泡图（点击量×ACOS×订单数）

---

## Examples

**输入：**
- 客单价 $28，目标类目CVR 9%，毛利（广告前）$9，目标ACOS 28%，上/下调阈值系数均20%，
  历史广告前毛利率 34%，日预算 $15，非新品
- 上传：Search Term Report（近7天）、Campaign Report（含Date，近30天）

**输出：**
- 阈值确认：floor 22.4% / target 28% / ceiling 33.6% / breakeven 34%
- 诊断单：昨日 ACOS 41% 相对7日均值 ▲35%，触发"已进入亏损区，建议立即止损"结论
- 词根聚合：识别出 3 个亏损词根（建议整体否定）、1 个优质词根（建议新建 Exact Campaign）
- 止损执行表：6 条动作（3 个 Negative Exact，2 个降 bid，1 个 Pause Target 候选）
- 待投放清单：4 条动作（2 个 Promote to Exact，1 个提 bid，1 个提预算）
- Bulk Sheet 草稿：可直接导入 Amazon 后台

---

## Guardrails

- 有订单的对象不自动否定，只降 bid；待投放同理，不给零样本的词直接大幅提价
- 点击未达最少观察点击数（默认20）的对象不自动止损，除非是明显不相关词
- 以下动作强制 `Review Required`：Negative Phrase、Negative Product、Pause Campaign、
  品牌词/竞品词否定、激进模式（sacrifice_ratio>100%）下的所有待投放动作
- 新品保护期、大促期间（Prime Day/黑五/网一）、断货期间、Listing 刚被修改期间、
  价格刚变动期间：止损/待投放动作一律降级为 `OBSERVE`，只做记录不做执行建议
- 不替用户编造利润数据；Step 1 缺失的关键参数（客单价、目标ACOS）必须问清楚，不能瞎猜
- 词根聚合是启发式分词，不是精确 NLP，输出的词根分组请用户过一遍再执行否定类动作
- 本 Skill 仅支持 Sponsored Products；Sponsored Brands / Sponsored Display 的数据结构不同，暂不支持
- TACOS 计算依赖自然销量数据，用户未提供时不要编数字，明确说"缺数据，暂不可算"
