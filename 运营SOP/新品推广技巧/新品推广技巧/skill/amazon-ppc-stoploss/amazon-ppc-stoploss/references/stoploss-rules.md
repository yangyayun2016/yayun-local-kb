# Amazon PPC 止损规则库 v1.0

## 核心参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| analysis_window | 主分析周期 | 7 天 |
| support_window | 辅助参考周期 | 14 / 30 天 |
| min_clicks_observe | 最少观察点击数（达到才判断） | 20 |
| default_no_order_stop | 无订单止损点击阈值 | 35 |
| max_cpa | 售价 × Target ACOS | 按产品计算 |
| break_even_cpa | 售价 × Break-even ACOS | 按产品计算 |

---

## 计算字段

```
CTR = Clicks / Impressions
CVR = Orders / Clicks
CPC = Spend / Clicks
CPA = Spend / Orders （Orders=0 时标记 INFINITE）
ACOS = Spend / Sales （Sales=0 时标记 INFINITE）
ROAS = Sales / Spend
Max CPA = Selling Price × Target ACOS
Break-even CPA = Selling Price × Break-even ACOS
Target CPC = Target ACOS × Selling Price × CVR
```

> ⚠️ Spend > 0 且 Orders = 0 → 潜在浪费，不因 ACOS 为空而忽略

---

## 止损层级顺序

```
搜索词层（Search Term）
    ↓
关键词/ASIN Target 层（Targeting）
    ↓
广告组层（Ad Group）
    ↓
Campaign 层
```

一个 Campaign 亏损，可能只是里面 1 个词在烧钱。从细到粗止损，避免误杀有效流量。

---

## 规则 1：搜索词无订单止损

**触发条件：**
```
Customer Search Term clicks >= max(20, 35)
AND Orders = 0
AND Spend >= Max CPA
```

**动作：** `NEGATIVE_EXACT`
**Review Required：** Yes（建议人工确认后执行）

**示例：**
- 售价 $25，Target ACOS 25%，Max CPA = $6.25
- 搜索词 "pink lunch box for kids"：38 clicks，$9.20 花费，0 订单
- → Negative Exact

---

## 规则 2：搜索词明显不相关止损

**触发条件：**
```
Search Term 包含明显低购买意图词根
AND Clicks >= 5
AND Orders = 0
```

**低意图词根参考（需人工确认）：**
```
free / used / second hand / replacement parts / manual
repair / cheap / DIY / pdf / instructions / wholesale
template / how to / tutorial / review / vs
```

> ⚠️ 注意：cheap / used 等词需结合产品判断，不可盲目否定
> 如果选取的是低价产品，则 cheap 不一定是低意图词

**动作：** `NEGATIVE_PHRASE` 候选
**Review Required：** 是，必须人工复核

---

## 规则 3：搜索词有订单但亏损

**触发条件（轻度亏损）：**
```
Orders >= 1
AND ACOS > Break-even ACOS
AND Orders < 3
```
**动作：** 降 bid 20%–30%，继续观察，不否定

**触发条件（严重亏损）：**
```
Orders >= 3
AND ACOS > Target ACOS × 2
```
**动作：** 暂停 target 候选（`PAUSE_TARGET`），人工复核
**Review Required：** 是

**核心原则：有订单 = 有相关性，优先降 bid，不轻易否定**

---

## 规则 4：Keyword Target 止损

Target 层看整体表现（汇总该 Target 下所有搜索词）。

**无订单止损：**
```
Target Clicks >= 35
AND Orders = 0
AND Spend >= Max CPA
```
**动作：** `PAUSE_TARGET`

**有订单但亏损：**
```
Orders >= 2
AND ACOS > Break-even ACOS
```
**动作：** `LOWER_BID_20` 至 `LOWER_BID_40`

**严重亏损：**
```
Orders >= 3
AND ACOS > Target ACOS × 2
```
**动作：** `PAUSE_TARGET` 候选，人工复核

---

## 规则 5：ASIN Product Target 止损

```
Target ASIN Clicks >= 30
AND Orders = 0
AND Spend >= Max CPA
```
**动作：** `NEGATIVE_PRODUCT`（否定该竞品 ASIN）
**Review Required：** 是，需确认竞品关系

**有订单但亏损：**
```
Orders >= 2
AND ACOS > Break-even ACOS
```
**动作：** 降 bid 20%–40%

---

## 规则 6：Campaign 整体无订单止损

```
Campaign Spend >= Daily Budget × 7 × 80%
AND Campaign Orders = 0
```

**执行顺序（避免误关）：**
1. 先检查：是否只有少数 Target 在烧钱？
   - 是 → 暂停该 Target，不关 Campaign
   - 否 → `PAUSE_CAMPAIGN` 候选，人工复核

2. 如整个 Campaign 全无有效 Target：
   - `PAUSE_CAMPAIGN` 或 Daily Budget 降至 $1–$3

**Review Required：** 是

---

## 规则 7：Campaign 亏损但有有效词

```
Campaign ACOS > Break-even ACOS
AND Campaign Orders >= 2
AND 存在部分有效 Target
```

**动作：**
- 不关 Campaign
- 把浪费的搜索词否定掉（执行规则 1/2）
- 把高转化词转移到 Exact Campaign
- Campaign 整体降预算 30%–50%

---

## 规则 8：新品保护期

**新品判定（满足任一）：**
- 上线 ≤ 14 天
- Review 数量 < 5
- 总广告订单 < 5

**逻辑：**
```
IF 新品 = Yes
AND Clicks < 50
AND Spend < 2 × Max CPA
THEN OBSERVE（不自动止损）
```

**例外：** 明显不相关词仍可人工复核后否定

---

## 动作类型对照表

| 动作代码 | 含义 | 是否需人工确认 |
|----------|------|---------------|
| `NO_ACTION` | 不操作 | — |
| `OBSERVE` | 继续观察 | — |
| `LOWER_BID_10` | 降 bid 10% | 否 |
| `LOWER_BID_20` | 降 bid 20% | 否 |
| `LOWER_BID_30` | 降 bid 30% | 否 |
| `LOWER_BID_50` | 降 bid 50% | 否 |
| `NEGATIVE_EXACT` | 精确否定词 | 建议确认 |
| `NEGATIVE_PHRASE` | 词组否定 | **必须确认** |
| `NEGATIVE_PRODUCT` | 否定 ASIN | **必须确认** |
| `PAUSE_TARGET` | 暂停关键词/Target | 建议确认 |
| `PAUSE_CAMPAIGN` | 暂停 Campaign | **必须确认** |
| `REDUCE_BUDGET` | 降低日预算 | 否 |
| `REVIEW_REQUIRED` | 仅标记，待人工处理 | **必须确认** |
| `LISTING_CHECK` | 提示检查 Listing | — |

---

## 安全机制：不自动止损的情形

以下情形自动降级为 `OBSERVE` 或 `REVIEW_REQUIRED`：

```
✗ 有订单（不管 ACOS 多高，先降 bid）
✗ 有加购数据但无订单（归因窗口未到）
✗ 样本量不足（点击 < 20 且非明显不相关）
✗ 新品保护期
✗ 促销期间（Prime Day / 黑五 / 网一）
✗ 库存断货期间
✗ Listing 被修改期间
✗ 价格突然上涨期间
```

品牌词、竞品词、类目词否定，一律人工复核。