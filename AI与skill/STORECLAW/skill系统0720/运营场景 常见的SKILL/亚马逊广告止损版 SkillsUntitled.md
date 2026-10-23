 **“亚马逊广告止损版 Skills / SOP”** 的研究框架。我建议把它分成两条主线：**止血** 和 **扩量**。

## 1. 核心目标

你的系统目标可以定义为：

**用数据规则减少广告浪费，同时把高转化关键词和 ASIN 自动沉淀成可批量创建的新广告资产。**

Amazon Sponsored Products 本身支持自动投放、手动关键词投放、商品/ASIN 投放和否定投放；否定投放可以排除低效关键词、商品或品牌，帮助优化花费。Amazon 也明确建议：做否词前最好至少观察到约 **20 次点击**，并且否词运行两周以上再调整。([Amazon Ads][1])

---

## 2. 必须建立的指标公式

先不要直接用“35 个点击不出单就关”作为固定规则，而是把它变成一个可计算阈值。

### 基础指标

| 指标              |                     公式 | 用途     |
| --------------- | ---------------------: | ------ |
| CVR 转化率       |        Orders / Clicks | 判断点击质量 |
| CPC             |         Spend / Clicks | 判断流量成本 |
| CPA             |         Spend / Orders | 每单广告成本 |
| ACOS            |          Spend / Sales | 广告销售成本 |
| ROAS            |          Sales / Spend | 广告回报   |
| Break-even ACOS |               毛利 / 销售额 | 盈亏平衡线  |
| Target ACOS     | Break-even ACOS × 安全系数 | 目标广告成本 |

### 关键公式

**最大可接受 CPA：**

```text
Max CPA = 客单价 × Target ACOS
```

例如：
售价 $25，扣除平台费、FBA、产品成本后毛利率 35%。
如果你希望保留利润，Target ACOS 设为 25%。

```text
Max CPA = 25 × 25% = $6.25
```

也就是说，某个词或 ASIN 花到 **$6.25 还没有出单**，就已经进入止损观察区。

---

## 3. “多少点击不出单就关？”的科学设定

你提到的规则：

> 7 天内 35 个点击不出单，关闭
> 7 天预算 $70 不出单，关闭
> 7 天 ACOS > 100%，关闭

这个思路是对的，但建议改成 **动态阈值**。

### 点击止损阈值

如果你知道账号或类目的平均 CVR，可以用这个逻辑：

```text
无订单点击阈值 = ln(0.05) / ln(1 - 平均CVR)
```

意思是：如果这个词本来应该有 X% 转化率，但点击了这么多次还没出单，基本可以判定它大概率不行。

| 历史平均 CVR | 95% 置信下“不出单”点击阈值 | 建议操作                     |
| -------: | ---------------: | ------------------------ |
|       5% |          约 59 点击 | 高客单/低转化类目可用              |
|       8% |          约 36 点击 | 你的 35 点击规则接近这个水平         |
|      10% |          约 29 点击 | 常见类目适用                   |
|      15% |          约 19 点击 | 但建议仍参考 Amazon 的 20 点击观察线 |
|      20% |          约 14 点击 | 高转化产品可更快止损               |

所以，**35 点击不出单**适合平均 CVR 大约在 **8%–10%** 的产品。
如果你的产品历史 CVR 是 15%，35个 点击才止损就太慢；如果 CVR 只有 4%–5%，35个 点击可能又太早。

---

## 4. 止损规则引擎

建议分 5 层处理，不要所有情况都直接“关闭广告”。

### A. 搜索词 / Search Term 止损

Search Term Report 是核心数据源，可以用来发现高效目标，也可以找出不符合目标的搜索词并做否词。Amazon 的搜索词报告用于分析搜索词表现，并可辅助优化投放。([Amazon Ads][2])

| 条件                                           | 动作                  |
| -------------------------------------------- | ------------------- |
| 搜索词明显不相关                                     | 直接否定 phrase 或 exact |
| 点击 ≥ 20，0 单，Spend ≥ 0.8 × Max CPA            | 加入观察名单              |
| 点击 ≥ 动态点击阈值，0 单，Spend ≥ Max CPA              | 否定 exact            |
| 搜索词包含明显错误人群词，如 free、cheap、used、replacement 等 | 视产品情况否定 phrase      |
| 有订单但 ACOS > Target ACOS × 2，且订单数 ≥ 2         | 降 bid 20%–40%，先不否词  |
| 有订单但长期亏损，订单数 ≥ 3，ACOS > Break-even ACOS      | 降 bid 或暂停 target    |

**建议：**
否词优先用 **Negative Exact**，不要轻易用 Negative Phrase。
Phrase 会杀掉很多长尾词，容易误伤未来可能转化的搜索词。

---

### B. Keyword / Target 止损

| 条件                                 | 动作               |
| ---------------------------------- | ---------------- |
| Target 点击 ≥ 20，0 单，Spend ≥ Max CPA | 降 bid 或暂停 target |
| Target 点击 ≥ 动态点击阈值，0 单             | 暂停 target        |
| Target 有单，但 CPA > Max CPA × 1.5    | 降 bid            |
| Target 有单，但 ACOS > Break-even ACOS | 降 bid            |
| Target 有单，ACOS ≤ Target ACOS       | 保留或加价            |
| Target 有单，CVR ≥ 平均 CVR × 1.2       | 进入扩量池            |

---

### C. Campaign / Ad Group 止损

你说的：

> 广告预算一天 $10，7 天预算 $70 不出单关闭

可以做，但最好不要先关 campaign，应该先找内部浪费源。

| 条件                                       | 动作                       |
| ---------------------------------------- | ------------------------ |
| Campaign 7 天 Spend ≥ $70，0 单             | 暂停 campaign 或把预算降到 $1–$3 |
| Campaign 有订单但 ACOS > 100%                | 不一定直接关，先看毛利和目标           |
| Campaign ACOS > Break-even ACOS 且订单数 ≥ 3 | 降预算、降 bid、拆分结构           |
| Campaign 花费集中在 1–2 个无效 target            | 只暂停 target，不关整个 campaign |
| Campaign 是新品冷启动                          | 可给更长观察期，如 14 天           |

**重要：ACOS > 100% 不一定是唯一关闭标准。**
真正的标准应该是：

```text
ACOS > Break-even ACOS
```

如果你的毛利率是 30%，那 ACOS 40% 已经亏了；
如果毛利率是 70%，ACOS 50% 可能还可以接受。
所以 **100% ACOS** 只是严重流血信号，不是唯一决策线。

---

## 5. 否词规则

Amazon 官方建议低效关键词、低效 ASIN、不想展示的搜索词或商品都可以考虑做否定；否定关键词通常使用 phrase 或 exact。([Amazon Ads][1])

### 否词分级

| 类型                      | 适用场景               | 动作      |
| ----------------------- | ------------------ | ------- |
| Negative Exact          | 某个搜索词点击多、无单或亏损     | 首选      |
| Negative Phrase         | 某一类词根整体不相关         | 谨慎使用    |
| Negative Product / ASIN | 某个 ASIN 点击多、无单或亏损  | 商品投放止损  |
| Campaign-level Negative | 整个 campaign 都不希望出现 | 用于大范围排除 |
| Ad-group-level Negative | 只排除某个广告组           | 更精细，推荐  |

### 否词判断例子

```text
IF Search Term clicks >= 35
AND orders = 0
AND spend >= Max CPA
THEN add Negative Exact
```

```text
IF Search Term contains irrelevant root word
AND clicks >= 10
AND orders = 0
THEN add Negative Phrase after manual review
```

```text
IF ASIN clicks >= 30
AND orders = 0
AND spend >= Max CPA
THEN add Negative Product Target
```

---

## 6. 扩量规则：把高转化关键词做成新广告

Amazon Bulksheets 可以用表格批量创建、编辑和优化广告活动；适合你说的批量生成广告模板。([Amazon Ads][3])

### 关键词进入扩量池的条件

建议满足任意一组：

| 条件                              | 说明     |
| ------------------------------- | ------ |
| Orders ≥ 2 且 ACOS ≤ Target ACOS | 稳定可扩   |
| Orders ≥ 1 且 CVR ≥ 平均 CVR × 1.5 | 潜力词    |
| CPA ≤ Max CPA                   | 成本合格   |
| ROAS ≥ 目标 ROAS                  | 回报合格   |
| Search Term 与产品高度相关             | 人工确认后扩 |

### 扩量动作

| 来源                 | 生成目标                          |
| ------------------ | ----------------------------- |
| Auto Campaign 转化词  | Manual Exact                  |
| Broad / Phrase 转化词 | Manual Exact + Phrase         |
| Search Term 高转化词   | 单独 Exact Campaign             |
| 高转化 ASIN           | Product Targeting Campaign    |
| 类目广告中出单 ASIN       | 单独 ASIN 定投                    |
| 品牌词高转化             | Brand Defense Campaign        |
| 竞品 ASIN 出单         | Competitor Targeting Campaign |

### Bid 计算

```text
Max CPC = 客单价 × Target ACOS × CVR
```

例如：

```text
售价 = $25
Target ACOS = 25%
CVR = 10%

Max CPC = 25 × 25% × 10% = $0.625
```

这个词的合理 CPC 上限大约是 **$0.63**。
如果当前 CPC 是 $1.20，即使有订单，也可能是亏损流量。

---

## 7. ASIN 定投规则

Amazon 的商品投放可以定投具体商品、类目、品牌等；搜索词报告中也可能出现产生点击或转化的 ASIN，可以把它们加入商品投放广告。([Amazon Ads][1])

### ASIN 扩量池

| 条件                      | 动作                   |
| ----------------------- | -------------------- |
| ASIN Orders ≥ 2         | 加入 Product Targeting |
| ASIN ACOS ≤ Target ACOS | 提高 bid 或单独建 campaign |
| ASIN CVR ≥ 平均 CVR       | 加入 ASIN 精准定投         |
| ASIN 点击多无单              | 加 Negative Product   |
| ASIN 是竞品但价格/评分你明显弱      | 谨慎投放或降低 bid          |
| ASIN 是互补品               | 可做 cross-sell 测试     |

---

## 8. 建议的广告结构

为了方便止损和扩量，广告结构要拆开。

### Campaign 命名

```text
SP_AUTO_Discovery_ASIN_Date
SP_KW_Exact_Profit_ASIN_Date
SP_KW_Phrase_Discovery_ASIN_Date
SP_ASIN_Target_Competitor_ASIN_Date
SP_ASIN_Target_Defense_ASIN_Date
SP_Brand_Defense_ASIN_Date
```

### 结构建议

| 类型                     | 目的         | 预算   |
| ---------------------- | ---------- | ---- |
| Auto Discovery         | 挖词、挖 ASIN  | 低预算  |
| Broad/Phrase Discovery | 扩展搜索词      | 中低预算 |
| Exact Profit           | 承接高转化词     | 较高预算 |
| ASIN Targeting         | 定投高转化 ASIN | 中预算  |
| Brand Defense          | 防守品牌词      | 稳定预算 |
| Competitor Targeting   | 打竞品        | 测试预算 |

Amazon 也建议不要在同一个 campaign/ad group 中混合太多不同策略，结构应方便根据 KPI 监控表现。([Amazon Ads][1])

---

## 9. 7 天止损版规则模板

可以直接作为第一版 SOP：

### 规则 1：无订单止损

```text
IF 日期窗口 = 最近7天
AND clicks >= max(20, 动态点击阈值)
AND orders = 0
AND spend >= Max CPA
THEN 暂停 target 或添加 Negative Exact
```

### 规则 2：预算流血止损

```text
IF campaign daily budget = $10
AND 最近7天 spend >= $70
AND orders = 0
THEN 暂停 campaign
OR 将预算降到 $1
OR 暂停主要花费 target
```

### 规则 3：ACOS 流血止损

```text
IF orders >= 2
AND ACOS > Break-even ACOS
THEN 降 bid 20%–40%
```

```text
IF orders >= 3
AND ACOS > Target ACOS × 2
THEN 暂停 target
```

### 规则 4：优质词扩量

```text
IF orders >= 2
AND ACOS <= Target ACOS
AND CVR >= 平均CVR
THEN 创建 Manual Exact Campaign
```

### 规则 5：高潜力词加价

```text
IF orders >= 2
AND ACOS <= Target ACOS × 0.8
THEN bid 提高 10%–20%
```

### 规则 6：ASIN 扩量

```text
IF search term = ASIN
AND orders >= 2
AND ACOS <= Target ACOS
THEN 创建 Product Targeting Campaign
```

---

## 10. 最终可以做成的 Skill 模块

你这个研究可以包装成 5 个 Skills：

### Skill 1：止损诊断

输入：Search Term Report、Campaign Report、Targeting Report
输出：

```text
要否词的搜索词
要暂停的关键词
要暂停的 ASIN
要降价的 targets
要关闭的 campaign
```

### Skill 2：否词生成

输出字段：

```text
Campaign
Ad Group
Search Term
Negative Type
Negative Match Type
Reason
Clicks
Spend
Orders
ACOS
Action
```

### Skill 3：扩量关键词生成

输出：

```text
Search Term
Source Campaign
Orders
Sales
Spend
ACOS
CVR
Recommended Match Type
Recommended Bid
New Campaign Name
```

### Skill 4：ASIN 定投生成

输出：

```text
Target ASIN
Source Campaign
Clicks
Orders
Sales
Spend
ACOS
CVR
Recommended Bid
Campaign Type
Manual Review
```

### Skill 5：Bulk Sheet 生成

输出 Amazon 可上传的批量操作模板，用于：

```text
创建 campaign
创建 ad group
添加关键词
添加 ASIN targets
添加 negative keywords
添加 negative ASINs
调整 bids
暂停 targets
暂停 campaigns
```

---

## 11. 第一版推荐阈值

在没有历史数据时，可以先用这组：

| 项目           |                              初始阈值 |
| ------------ | --------------------------------: |
| 无订单最小观察点击    |                         20 clicks |
| 标准止损点击       |                         35 clicks |
| 高 CVR 产品止损点击 |                      20–25 clicks |
| 低 CVR 产品止损点击 |                      45–60 clicks |
| 无订单花费止损      |                         ≥ Max CPA |
| 强制止损花费       |                   ≥ 1.5 × Max CPA |
| ACOS 警戒线     |                     > Target ACOS |
| ACOS 严重线     |                 > Break-even ACOS |
| ACOS 强制止损    |    > Target ACOS × 2，且 orders ≥ 3 |
| 扩量最低订单       |                        ≥ 2 orders |
| 强扩量条件        | ACOS ≤ Target ACOS 且 CVR ≥ 平均 CVR |

---

## 12. 你的例子怎么改成更专业版本

你原来的规则：

> 7 天内广告 35 个点击不出单，关闭
> 预算一天 $10，7 天 $70 不出单关闭
> 7 天 ACOS > 100%，关闭

建议改成：

```text
最近7天内：
1. 如果 clicks ≥ 35 且 orders = 0 且 spend ≥ Max CPA：
   搜索词层级 → Negative Exact
   Keyword/Target 层级 → Pause
   Campaign 层级 → 只在无明显单个浪费源时暂停

2. 如果 campaign spend ≥ 7天预算 且 orders = 0：
   先暂停花费最高的 targets
   若无有效 target，暂停 campaign

3. 如果 ACOS > Break-even ACOS：
   有2单以内 → 降 bid
   有3单以上且仍亏损 → 暂停 target

4. 如果 ACOS > 100%：
   默认严重亏损
   除非是新品冲排名或明确测试期，否则暂停/降价
```

---

我建议你的研究名称可以叫：

**Amazon Ads PPC Guardrail System：止损、否词与扩量自动化规则研究**

核心不是简单“关广告”，而是建立一套规则：

```text
无效流量 → 否词 / 关 target
高成本流量 → 降 bid
高转化流量 → 单独建 exact
高转化 ASIN → 单独定投
亏损 campaign → 拆解后再止损
```

这样既能防止广告流血，也不会误杀未来可能赚钱的关键词。

[1]: https://advertising.amazon.com/library/guides/targeting-with-sponsored-products "A guide to targeting with Sponsored Products | Amazon Ads"
[2]: https://advertising.amazon.com/help/G3HEFZYWZF84NPS9?utm_source=chatgpt.com "Search term report for Sponsored Products"
[3]: https://advertising.amazon.com/API/docs/en-us/bulksheets/2-0/get-started-with-bulksheets-part1?utm_source=chatgpt.com "Get started with bulksheets: Part 1"
