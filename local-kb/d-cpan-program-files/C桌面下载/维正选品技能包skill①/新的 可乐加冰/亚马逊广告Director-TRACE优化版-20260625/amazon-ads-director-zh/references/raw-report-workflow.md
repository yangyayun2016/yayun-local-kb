# 原始 Amazon Ads 报表工作流

当用户上传搜索词报告、广告商品报告、投放商品报告、Product Targeting Report、CSV/XLSX 或复制出的表格时，使用本参考。

## 事实边界

原始广告报表能支持 campaign、ad group、targeting、search term、ASIN/SKU、bid、budget、否定词和预算建议。除非用户另外提供字段，不能证明库存、评分、生命周期、利润率、类目排名、L2/L3 或 Listing 根因。

缺失业务上下文时，在最终输出放入“无法判断/需补充数据”，不要补写默认值。

## 报表识别

最小推荐组合：

- Search Term Report / 搜索词报告
- Advertised Product Report / 广告商品报告 / 投放商品报告

可选补充：

- Product Targeting Report
- Targeting Report
- Campaign 报表
- 用户导出的 ASIN/SKU、库存、利润、目标 ACOS/CPA 表

如果只有一张报表，也可以分析，但要标明 join 和 ASIN 归因受限。

## 字段别名

| 标准字段 | 常见别名 |
|---|---|
| `campaign` | Campaign, Campaign Name, 广告活动 |
| `ad_group` | Ad Group, Ad Group Name, 广告组 |
| `search_term` | Customer Search Term, Search Term, 搜索词, 客户搜索词 |
| `targeting` | Targeting, Keyword, 关键词, 投放, 定向 |
| `match_type` | Match Type, 匹配类型 |
| `advertised_asin` | Advertised ASIN, ASIN, 广告商品, 投放商品 |
| `sku` | SKU, Advertised SKU |
| `impressions` | Impressions, 展示量 |
| `clicks` | Clicks, 点击量 |
| `spend` | Spend, Cost, 花费 |
| `sales` | Sales, 7 Day Total Sales, 销售额 |
| `orders` | Orders, 7 Day Total Orders, 订单 |
| `units` | Units, 7 Day Total Units, 件数 |

只归一化已存在的列；不要把缺失列“补成”标准字段。

## 指标计算

只在分子和分母都存在时计算：

- CTR = clicks / impressions
- CPC = spend / clicks
- CVR = orders / clicks
- ACOS = spend / sales
- ROAS = sales / spend
- CPA = spend / orders

如果目标 ACOS、目标 CPA、利润率或生命周期缺失，把预算放大类建议标为“暂缓/需目标确认”。

## Join 规则

1. 先统一日期范围、账号、站点、币种和报表粒度。
2. 搜索词报告按 campaign + ad_group + targeting + search_term + match_type 聚合；如果有 ASIN/SKU，也保留。
3. 广告商品/投放商品报告按 campaign + ad_group + advertised_asin/SKU 聚合。
4. 双方都有 ASIN/SKU 时，优先用 campaign + ad_group + advertised_asin/SKU join。
5. 搜索词报告没有 ASIN/SKU 时，只能用 campaign + ad_group 间接归因，并在输出中说明。
6. campaign 或 ad group 名称不匹配时，不要模糊强行 join；列出未匹配项。

## 默认动作启发

这些是复核启发，不是硬规则。用户提供目标时以用户目标为准。

否定候选：

- orders = 0 且 clicks >= 10；
- orders = 0 且 spend >= max(5 USD, 临时目标 CPA)；
- 搜索词明显无关且已有点击/花费。

Exact 收割候选：

- 搜索词有订单且 ACOS/ROAS 可接受；
- 上传证据中未看到该词已作为 exact 承接；
- 搜索词与 ASIN 的关系明确，不是只靠泛类目词猜测。

降 bid / 暂停候选：

- 有订单但 ACOS 高于目标或 ROAS 低于目标；
- 高花费、低 CVR，且不是必须保护的品牌/核心词；
- 竞品或泛词与当前 ASIN 关系弱。

提 bid / 保护候选：

- 有订单，ACOS 不高于目标，且点击/订单量有意义；
- 品牌词、核心 exact 或高转化长尾词需要防守覆盖。

观察候选：

- 样本量低、缺目标阈值、缺 sales/orders、证据混合或无法判断 ASIN 归因。

## 输出要求

- 所有动作必须带指标证据。
- 否定候选和转精准候选分开输出，避免一个词同时被误解为“否定”和“加 exact”。
- 搜索词动作表中保留 campaign、ad group、targeting、match type，方便用户定位后台。
- 标注 `confidence`：高/中/低；高影响动作标注“需人工确认”。
- 输出 recommendations only，不要声称已经修改 Amazon Ads。
