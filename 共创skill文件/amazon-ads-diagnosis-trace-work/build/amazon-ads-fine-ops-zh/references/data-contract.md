# 数据接入与字段口径

使用本参考处理 TJ OS、Amazon Ads、ABA、SIF、卖家精灵、利润、库存和竞品数据。

## 数据优先级

1. 用户上传的原始报表和 TJ OS 明细表。
2. Amazon Ads 搜索词报告、广告活动报告、广告商品报告、广告位报告、预算与操作日志。
3. 利润表、库存表、价格与促销记录、Listing 质量、评分评论。
4. ABA 搜索词绩效、SIF 关键词时机、卖家精灵竞品与类目数据。
5. 用户文字描述和截图。

如果数据源冲突，优先使用时间范围清楚、字段口径明确、可追溯到具体对象的明细数据。

## 必需字段

店铺维度最低需要：

- 站点、账号、日期范围
- ASIN/SKU 级销售额、订单、广告花费、广告销售额、广告订单
- ACOS 或可计算 ACOS 的 spend/sales
- 广告后毛利或广告前毛利率/盈亏平衡 ACOS

ASIN/SKU 维度最低需要：

- ASIN 或 SKU
- 近 7/14/30 天广告花费、广告销售额、订单、点击、CVR、ACOS
- 盈亏平衡 ACOS 或广告前毛利率
- Campaign 或搜索词数据；没有时只能做止损与补数建议

完整诊断建议补充：

- Campaign、Ad Group、Targeting、Search Term、Placement
- CPC、CTR、CVR、ROAS、TACOS
- 日预算、预算打满次数、分时花费
- 评分、评论数、价格、Coupon、库存、可销月、Listing 质量
- BSR、竞品 BSR、ABA 点击份额/购买份额、SIF 词时机

## 字段归一

| 标准字段 | 常见名称 |
|---|---|
| `account` | 店铺、销售账号、账号 |
| `marketplace` | 站点、国家、US、北美站 |
| `asin` | ASIN、父ASIN、子ASIN |
| `sku` | SKU、MSKU、Seller SKU |
| `campaign` | Campaign、广告活动 |
| `ad_group` | Ad Group、广告组 |
| `keyword` | Keyword、关键词、投放词 |
| `search_term` | Customer Search Term、搜索词、客户搜索词 |
| `placement` | 广告位、搜索首位、详情页、其他搜索位 |
| `spend` | Spend、Cost、广告费、花费 |
| `ad_sales` | Ad Sales、广告销售额 |
| `orders` | Orders、广告订单、购买 |
| `clicks` | Clicks、点击 |
| `impressions` | Impressions、曝光、展示 |
| `acos` | ACOS、广告ACOS |
| `tacos` | TACOS |
| `cvr` | CVR、转化率、广告转化 |
| `cpc` | CPC |
| `gross_profit` | 毛利润、广告后净利润 |
| `pre_ad_margin` | 广告前毛利率、盈亏平衡ACOS |

## 计算规则

- ACOS = 广告花费 / 广告销售额。
- ROAS = 广告销售额 / 广告花费。
- CVR = 广告订单 / 点击。
- CPC = 广告花费 / 点击。
- CTR = 点击 / 展示。
- 广告后毛利率 = gross_profit / 总销售额。
- 盈亏平衡 ACOS = 广告前毛利率 = (gross_profit + 广告费) / 总销售额。
- 广告亏损金额可估算为：广告花费 - 广告销售额 * 盈亏平衡 ACOS。

只在字段存在时计算；不要用缺失字段推导精确结论。

## 数据不足时的标准说法

缺搜索词报告：

```text
缺少搜索词报告，无法定位具体高花费低转化词；需要补充近7天或30天搜索词报告，至少包含搜索词、Campaign、Ad Group、花费、点击、订单、销售额、ACOS、CVR。
```

缺广告活动数据：

```text
缺少广告活动层级数据，无法判断是全账户预算问题、单 Campaign 烧钱，还是某个 ASIN/SKU 承接异常；需要补充 Campaign 近7/14/30天花费、订单、ACOS、日预算和状态。
```

缺利润口径：

```text
缺少广告前毛利率或盈亏平衡 ACOS，无法判断广告是否真实亏损；当前只能按 ACOS/CVR 异常做效率诊断。
```
