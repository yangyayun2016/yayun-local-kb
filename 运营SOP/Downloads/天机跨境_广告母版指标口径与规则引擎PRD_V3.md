# 天机跨境 · 亚马逊广告母版 V3.0

**版本**：V3.0.0  | **案例**：德国站 SP 手动关键词广告，EUR | **工作目标**：给选品报告第7模块增加可信、可复算、可配置、可审批的广告母版

> 这是基于用户提供的亚马逊广告后台截图以及指定的 CPC €0.50、CVR 10% 做的模型。截图中 9 个投放目标里只有 8 个出价行可读。**不存在已获取的广告真实点击/花费/购买/销售额**，在用户授权提供报表之前绝不可把情景预测当成实绩。示例商品每笔广告归因销售额 €20 仅为演示，可在Excel参数页修改。

## 0. 交付及使用入口

- Excel：`天机跨境_亚马逊广告决策母版_CPC0.5_2026_V3.xlsx`，共17个工作表。
- 优先使用页：`00_经营看板` → `01_参数利润输入` → `02_后台竞价截图` → `03_投放关键词母版` → `04_广告实绩导入` → `10_利润保本分析` → `08_预算规模预测` → `09_81组敏感性` → `12_判定与止损规则` → `14_AI报告结论模板`。
- 说明：母版是**广告分析模块新增母版**，并不覆盖选品报告其余7个模块。广告结论依赖于同形态竞品池、价格利润与VOC、库存、广告实绩共同校验。

## 1. 截图真实可读的字段

截图为Amazon德语/欧元关键词投放设置界面，含关键词、广泛/词组/精确匹配、建议出价、建议区间与填写的Bid。

| 关键词 | 匹配类型 | 建议低价 | 建议中价 | 建议高价 | 当前填写Bid | 数据性质 |
|---|---|---:|---:|---:|---:|---|
| licht mit bewegungsmelder | 广泛 | €0.39 | €0.48 | €0.64 | €0.48 | 截图 |
| licht mit bewegungsmelder | 词组 | €0.34 | €0.44 | €0.52 | €0.44 | 截图 |
| licht mit bewegungsmelder | 精确 | €0.38 | €0.48 | €0.60 | €0.48 | 截图 |
| bewegungsmelder licht | 广泛 | €0.35 | €0.46 | €0.62 | €0.46 | 截图 |
| bewegungsmelder licht | 词组 | €0.35 | €0.44 | €0.55 | €0.44 | 截图 |
| bewegungsmelder licht | 精确 | €0.36 | €0.46 | €0.57 | €0.46 | 截图 |
| treppenlicht mit bewegungsmelder | 广泛 | €0.47 | €0.59 | €0.78 | €0.59 | 截图 |
| treppenlicht mit bewegungsmelder | 词组 | €0.46 | €0.58 | €0.77 | €0.58 | 截图 |
| 第9项截图未完整显示 | 待补 | — | — | — | — | 缺值 |

**风险说明**：截图里`IS / IR`标记及`IS: 0`不等于可以直接判定没有真实曝光；需要核实其界面和指标定义。8个投放项目是3条词根的多种匹配，不等于8条独立自然搜索词。`建议出价`、`填写Bid`和`实际CPC`三者必须独立存储；动态竞价与广告位加价可能改变最终调整后的竞价上限，而Ads CPC仍以真实`cost/clicks`确定。

## 2. 指标、计算公式与分母口径对齐

| 字段 | 英文名 | 单位/数据类型 | 最小粒度 | 定义及计算 | 真实来源/使用限制 |
|---|---|---|---|---|---|
| 站点 | marketplace | DE | Ads profile | 确认EUR、避免跨币种 | Ads profile |
| 投放目标词 | targetingText | 字符串 | target × match | 用户给后台设置的目标，不一定是用户实际搜索词 | Targeting report |
| 实际搜索词 | customerSearchTerm | 字符串 | target×searchTerm | 触发广告的用户搜索表达 | Search term report |
| 匹配类型 | matchType | 枚举 | target | broad/phrase/exact；自动广告另有close/loose/substitutes/complements | Targeting配置 |
| 建议低/中/高Bid | bidLow/recommended/high | €/click | target×match×快照 | 平台推荐或区间 | 截图、控制台可用数据；不是实际CPC |
| 当前设置Bid | enteredBid | €/click | target×快照 | 本次广告手动输入的基础竞价 | 截图/Targeting配置 |
| 广告位加价 | placementAdjustment | % | campaign×placement | 影响投放竞价策略的加价配置 | Campaign配置，不是实际CPC |
| 展示量 | impressions | 次 | 原始报告粒度 | 广告被展示次数，非全市场曝光 | Ads报表实绩 |
| 点击量 | clicks | 次 | 原始报告粒度 | 广告有效点击 | Ads报表实绩 |
| 广告花费 | cost/spend | € | 原始报告粒度 | 广告费用；注意币种和调整 | Ads报表实绩 |
| CTR | clickThroughRate | % | 同一报告粒度 | clicks/impressions | 不能混用ABA搜索点击率 |
| 实际CPC | actualCpc | €/click | 同一报告粒度 | cost/clicks；clicks=0则空值 | 不能用建议Bid替代 |
| 归因购买 | purchases | 笔 | 归因窗口×报表 | 被广告归因的购买行为；注意购买、订单、件数口径 | 真实广告报表 |
| 归因销量 | units | 件 | 归因窗口×报表 | 购买件数，不等同购买数 | Ads报告 |
| CVR | adsCVR | % | 同一报告粒度 | purchases/clicks；0 clicks→空值 | 样本少时仅作观察 |
| CPA | costPerPurchase | €/purchase | 同一报告粒度 | cost/purchases；purchases=0→空值 | 不可把0单CPA写成€0 |
| 广告归因销售额 | attributedSales | € | 归因窗口×报表 | Ads归因Sales，和Seller经营总Sales独立 | 注意VAT/优惠/归因口径 |
| 每笔归因销售额 | adSalesPerPurchase | €/purchase | 期间×SKU | attributedSales/purchases | 缺实绩可情景输入，必须标假设 |
| ACOS | acos | % | 同一报告粒度 | cost/attributedSales | 广告投放效率，不等于经营利润率 |
| ROAS | roas | 倍 | 同一报告粒度 | attributedSales/cost | 报告同币种 |
| 同期经营总销售额 | totalSkuSales | € | SKU×期间 | 财务/ERP商品经营销售 | 不能用Ads归因Sales顶替 |
| TACOS | tacos | % | SKU×期间 | 所属SKU广告费/对应经营总销售额 | 需要先界定跨SKU推广归属与时间窗口 |
| 商品展示售价 | listPrice | €/unit | SKU×快照 | 标价，促销、VAT需另外区分 | 当前€20仅演示 |
| 可确认无税销售净收入 | recognizedRevenue | €/unit | SKU×成本期 | 演示：`listPrice×(1-coupon)/(1+vatRate)` | VAT/退货核算要经财务审批 |
| 单位贡献利润（广告前） | unitContributionPreAds | €/unit | SKU×成本期 | 可确认净收入−货本−头程−佣金−FBA−退货损耗−其他变动成本 | 任一必填成本缺失返回null |
| 目标ACOS | targetAcos | % | 人工规则版本 | 默认25%经营目标，可版本化编辑 | **不是保本ACOS** |
| 保本ACOS | breakEvenAcos | % | SKU×成本期 | 单位贡献利润/每笔广告归因销售额（假设每笔1件） | 单位贡献<0须显示负数并阻断放量 |
| 目标允许CPA | targetAllowableCPA | €/purchase | 产品×利润窗 | 归因销售额/购买×目标ACOS | 仅经营目标 |
| 目标允许CPC | targetAllowableCPC | €/click | target×CVR假设 | 归因销售额/购买×目标ACOS×CVR | 每个关键词CVR不同会变 |
| 保本允许CPC | breakEvenAllowableCPC | €/click | target×CVR假设 | 单位贡献利润/每笔归因购买×CVR | 需真实成本与购买件数对齐 |
| 预测eCPM（广告费用） | effectiveSpendCPM | €/1000 impressions | 模拟 | 1000×CTR×CPC | **不声称为亚马逊自然排名算法** |
| 1000展示预期购买 | expectedPurchasesPerK | purchases/1000 imp | 模拟 | 1000×CTR×CVR | 是期望值，不是实绩 |
| 每千次展示的预计广告后贡献 | contributionPerK | €/1000 impressions | 模拟 | 1000×CTR×(CVR×unitContributionPreAds−CPC) | 需要单位成本齐全及统一1件/购买假设 |

### 2.1 主案例：€0.50 CPC + 10% CVR

```text
ExpectedClicksPerPurchase = 1 / 10% = 10 clicks
ExpectedCPA = €0.50 / 10% = €5.00 per purchase
100 Clicks ⇒ €50 Spend ⇒ 10 Expected Purchases

若 每笔广告归因销售额（仅演示）= €20：
ExpectedACOS = €5 / €20 = 25%
经营目标ACOS=25%时：TargetAllowableCPC = €20×25%×10% = €0.50
```

**按 €20演示客单价测算建议价**：
- €0.44 Bid作为假设CPC→CPA €4.40，ACOS 22.0%。
- €0.48 → CPA €4.80，ACOS 24.0%。
- €0.50 → CPA €5.00，ACOS 25.0%。
- €0.58 → CPA €5.80，ACOS 29.0%。
- €0.59 → CPA €5.90，ACOS 29.5%。

以上是**把建议Bid暂时当作模拟CPC的压力测试**，绝不等于真实扣费。未经广告实际报告验证，不宜直接称“关键词真实广告成本”。

### 2.2 日预算案例

`DailyBudget = €30`与`SpendUtilization=100%`均为演示假设；若每日花满：
- 点击数 = €30 / €0.5 = **60 clicks/day**。
- 购买期望 = 60 × 10% = **6 purchases/day**。
- 广告归因销售额期望 = 6 × €20 = **€120/day**。
- 预测 ACOS = €30/€120 = **25%**。
- 月按30天预算：**€900 spend、1800 clicks、180 expected purchases、€3600 attributed sales**。

若另外假设该SKU每天总订单15笔，每天总经营销售 €300，则广告订单比例 6/15=40%，预测TACOS €30/€300=10%。**这两个比率取自互相独立的演示条件，不是实际商品经营数据**。

### 2.3 24周与81组敏感性场景

- 81组：月订单`100、300、500` × 广告购买占比`20%、35%、50%` × CPC`€0.35、€0.50、€0.65` × CVR`5%、10%、15%`。
- 每组计算：`AdPurchases=Orders×AdPurchaseShare`，`Clicks=AdPurchases/CVR`，`Spend=Clicks×CPC`，`ACOS=Spend/(AdPurchases×SalesPerPurchase)`，`TACOS=Spend/(Orders×SalesPerPurchase)`。
- 对比月度预算额度：`ExpectedSpend≤DailyBudget×MonthDays`；展示“预算内/超预算”。
- 24周表按阶段分组但不虚构每周CVR改善；每周以人工输入预算系数，真实词和库存状态校准。
- 任何“月净利润”只有VAT与6项变动成本齐全才显示。

## 3. 广告母版的结构：可供开发团队做UI左侧导航

| 导航 / 页面 | 获取的数据 | 数据来源工具 | 判定标准 | 必须输出的结论 |
|---|---|---|---|---|
| 1. 经营广告总览 | CPC/CVR/CPA/ACOS/TACOS/ROAS、预算/库存 | Ads、ERP、SP-API | 目标/保本双ACOS，数据是否完整 | 费用压力、盈利约束、数据可靠度 |
| 2. 竞价快照 | keyword+match+推荐低中高+setBid | Amazon广告后台截图/配置 | `suggestedBid / targetCpc` ≤1，1~1.3，>1.3 | 可测词/谨慎词/高压力词 |
| 3. 关键词成本母版 | 输入Bid、假设/真实CPC、CVR、CPA/ACOS | 截图+Ads Targeting | 同match比较、实际与假设双列展示 | 每个词建议动作、预计单笔获客成本 |
| 4. Campaign / AdGroup | 状态、预算、出价策略、曝光、花费、销售 | Ads报告/Ads API | 有效数据、预算利用、利润门槛 | 该活动是控费/放量/收录/拓词 |
| 5. Search Term | 搜索词、点击、订单、花费、Sales | Ads Search Term | 20点击0单→人工复核，非硬停 | 否词/拓词/分拆匹配类型的审批候选 |
| 6. Placement | Top of Search/Rest/Product Pages表现 | Ads Placement | 按原生广告位粒度算CPC/CPA/ACOS | 是否值得竞价加成，需批准 |
| 7. SKU利润 | 货本、入仓、佣金、FBA、税务、退货 | ERP/财务 | 成本任一缺失不能算保本 | 目标CPC、保本CPC、总贡献 |
| 8. 预算与节奏 | 每日预算、广告订单目标、24周计划 | 手工规划+Ads实绩 | 实际预算/归因校准 | 预计点击、购买、CPA和月现金投入 |
| 9. 敏感性分析 | 81组CPC×CVR×广告订单占比×销量 | 公式引擎 | ACOS/预算/保本门槛 | 最差、中性、乐观的费用与盈利范围 |
| 10. 规则审批 | 规则ID、证据、建议操作、操作前后 | 内部权限/审计日志 | 人工审批红线 | 审批历史、可回滚、禁止未经同意写入 |

## 4. 五层数据关联与禁止的虚拟汇总

```text
Amazon Ads Profiles (accountId, marketplace, currency)
  └── Campaign (campaignId, date, biddingStrategy, dailyBudget)
        └── AdGroup (adGroupId)
              └── Targeting (targetId, matchType, keyword/ASIN)
                    └── SearchTerm (targetId, customerSearchTerm, report window)

Campaign ──────────► Placement Report (Campaign×Placement×日期)
AdGroup ───────────► Advertised Product Report (广告商品ASIN/SKU)
ERP / SP-API ──────► SKU 经营销售与成本/库存
```

不能未经可验证原生报告支持，将`Targeting`与`Placement`两张聚合表互相Join后乘比例，伪造“关键词×广告位真实点击、费用、出单”。如需多维交叉，必须使用同粒度的有效来源或标记为`MODELLED_ESTIMATE`。不同广告类型的归因窗以及`purchases / units`定义也必须分别管理。

## 5. 人工规则和动作边界

| 规则 | 触发条件 | 一级输出 | 二级动作 | 强制门控 |
|---|---|---|---|---|
| CPC压力低 | 预测或真实CPC≤目标允许CPC | 费用压力低 | 小预算验证或优化 | 预测/真实标识分开 |
| CPC压力中 | >1×且≤1.3×目标允许CPC | 费用压力中 | 检查匹配、搜索词、广告位 | 不能称必亏 |
| CPC压力高 | >1.3×目标允许CPC | 费用压力高 | 仅建议限价/先测长尾 | 修改前主管确认 |
| ACOS目标超限 | 真实ACOS>25% | 不达管理目标 | 查CPA、价格、CVR、自然订单 | 不等于广告必然亏损 |
| 高于保本ACOS | 真实ACOS>已核实保本ACOS | 单位广告贡献可能为负 | 重点审核止损 | 利润完整，成本模型与归因一致 |
| 3天0展示 | 至少三个完整日没有Impressions | 交付异常 | 检查广告资格/预算/Bid/Listing | 不能只靠0曝光暂停 |
| 7天0点击 | 7日 clicks=0且impressions≥500 | CTR或相关性异常 | 检查意图与主图 | 展示≥500是试行阈值 |
| 20点击0购买 | 完整窗口clicks≥20且purchases=0 | 观察+人工复核 | 词匹配、搜索词、BuyBox、价格 | 在10%CVR假设下0单概率约12.16% |
| 29点击0购买 | 完整窗口clicks≥29且purchases=0 | 高优先级复核 | 提交降Bid/否词**候选** | CVR=10%假设下约4.71%仍可能自然发生 |
| 放量候选 | 7天已归因购买≥5、ACOS≤目标、库存≥30天 | 可申请放量 | 人工批准后调整 | 利润、预算、库存、Listing状态完整 |

> 判断门槛可按类目/站点/阶段配置。硬性规则：**对外发送、公开发布、资金支出、承诺、删除、广告状态/预算/Bid/否词的修改必须事先得到指定审批人的同意。** 系统默认只读+建议，不应自动执行。

## 6. 数据合同（API/数据库开发参考）

```json
{
  "report_version": "tianji-ads-master/3.0.0",
  "scope": {"marketplace":"DE", "currency":"EUR", "account_id":null, "sku":null},
  "snapshot": {"type":"USER_SCREENSHOT", "captured_at":null, "visible_targets":8, "reported_targets":9},
  "manual_target_example": {
    "keyword":"licht mit bewegungsmelder", "match_type":"BROAD",
    "bid_low":0.39, "bid_recommended":0.48, "bid_high":0.64,
    "entered_bid":0.48, "actual_cpc":null, "status":"SCREENSHOT_ONLY"
  },
  "scenario": {"cpc_assumed":0.50, "cvr_assumed":0.10,
               "ad_sales_per_purchase_assumed":20.0, "target_acos":0.25,
               "forecast_cpa":5.0, "forecast_acos":0.25},
  "unit_economics": {"vat_rate":null, "cogs":null, "referral":null,
                      "fba":null, "inbound":null, "returns_reserve":null,
                      "other_variable_cost":null, "break_even_acos":null,
                      "break_even_cpc":null, "status":"NEEDS_COSTS"},
  "decisions": {"keyword_cost_pressure":"EVALUATE_BY_MATCH",
                "stop_keyword":"REQUIRES_HUMAN_APPROVAL",
                "increase_budget":"REQUIRES_HUMAN_APPROVAL"}
}
```

**建议后端表**：

- `ads_account_scope(profile_id, marketplace, currency, account_id, user_permission)`
- `ads_campaign_daily(date, profile_id, campaign_id, spend, clicks, sales, purchases, budget, bidding_strategy, ...)`
- `ads_adgroup_daily(date, campaign_id, ad_group_id, ...)`
- `ads_targeting_daily(date, target_id, match_type, keyword, impressions, clicks, spend, purchases, units, sales, attribution_window)`
- `ads_searchterm_daily(date, target_id, search_term, clicks, spend, purchases, sales, attribution_window)`
- `ads_placement_daily(date, campaign_id, placement_group, clicks, spend, purchases, sales, attribution_window)`
- `ads_bid_snapshot(snapshot_id, target_id?, keyword, match_type, low_bid, rec_bid, high_bid, entered_bid, source_type, captured_at)`
- `sku_unit_economics(sku, marketplace, effective_at, sales_price, vat, coupon, unit_cogs, inbound, referral, fba, returns_reserve, other, status)`
- `sku_owning_sales_daily(date, marketplace, sku, net_sales, purchases, units, returns)`
- `rule_set_version(version_id, scope_id, config_json, approved_by, approved_at)`
- `decision_run(run_id, rule_version, input_hash, outputs_json, quality_status)`
- `approval_log(change_id, actor, action, before_json, after_json, approval_id, timestamp, result)`

所有指标值必须伴随`source_ref`, `observed_or_estimated`, `report_window`, `currency`, `data_quality`, `transformation_version`。`break_even_acos`绝不依靠默认0填补缺失成本。

## 7. 研发验收测试（必须跑过）

1. 同一输入`CPC=0.50,CVR=0.10`得到`CPA=5.00`；CVR=0不得报€0 CPA，应返回空/无法计算。
2. `AdSalesPerPurchase=20,targetAcos=.25,CVR=.10`得到`targetCPC=0.50`；ACOS预测25%。
3. `dailyBudget=30,utilization=100%,CPC=.50,CVR=.10`得到日点击60、购买6、广告销售€120；按30天得到花费€900、购买180。
4. 输入8个完整截图建议价，另第9行保持缺失；统计显示8项，不虚构第9项。
5. 截图0.59 Bid在€20每笔归因销售额、CVR10%时推演ACOS29.5%，标高于25%目标，但不称“真实CPC超标”。
6. VAT或任意单位成本为空时：`beforeAdsContribution=null`,`breakEvenAcos=null`,`breakEvenCpc=null`,`profit=null`，不可计算为20€利润。
7. 一笔实际Ads数据：`spend=€40,clicks=100,purchases=8,sales=€160`，实际`CPC=€0.40,CVR=8%,CPA=€5,ACOS=25%`。
8. 搜索词20次点击0单时，仅`REVIEW`；在10%假设CVR下概率0.9^20≈12.16%，不得直接自动否词。
9. 两个不同账户/币种/归因窗不能被静默合并；Campaign与Placement不能靠多表Join创造目标词级广告位实际绩效。
10. 用户仅上传截图，无Ads报表：真实Spend/CPC/订单/ACOS保持空，系统只输出`SCENARIO`并显示待采。
11. 每一个外部写动作必须先预览、得到授权，并留下审计记录；未批准则动作API拒绝。
12. Excel可编辑参数后，目标CPC、CPA、预算和81组场景联动重算；单元格没有`#REF!/#DIV0!/#VALUE!`。

## 8. 补数优先级与负责人

**P0**：提供本商品德国站真实售价/每笔归因销售额、SKU、广告类型（SP）、确切广告活动名称与设置的竞价策略、Ads Targeting/SearchTerm/Placement报告（近7天与30天）、归因窗。

**P0（财务）**：VAT实际口径、采购、头程、平台佣金、FBA、退款退货损耗、其他变动费用。由此正式核算保本ACOS和保本CPC。

**P1**：广告运行7-30天后补充真实关键词CPC/CVR与广告位表现；从商品经营数据获取同SKU同期总销售额以计算TACOS。

**P1**：确认截图第9项、IS/IR字段定义、当期关键词建议出价是否更新；品牌/ASIN与报告的同形态竞品池联动。

**P2**：竞品SIF推断数据单独存放，作为竞争环境旁证而非竞品真实Ads花费。搭建日志与每日诊断工单自动执行，但写操作保留审批红线。

## 9. 官方指标资料（已核对）

- Amazon Ads - Sponsored Products best practices: https://advertising.amazon.com/library/guides/sponsored-products-best-practices
- Amazon Ads - Ads FAQ: https://advertising.amazon.com/resources/faq
- Amazon Ads - ACOS guide: https://advertising.amazon.com/library/guides/acos-advertising-cost-of-sales
- Amazon Ads - Performance metrics: https://advertising.amazon.com/help/GG44RFW942U9F6F5
- Amazon Ads - Attribution: https://advertising.amazon.com/help/GX7KDKHMWQYMJ385
- Amazon Ads - Dynamic bidding: https://advertising.amazon.com/library/guides/dynamic-bidding-sponsored-products

***
**交付状态**：可作为V2选品报告广告模块的V3开发参考，已经包含公式工作簿、规则、字段字典、示例与验收测试。真实广告数据与真实商品成本尚未接入，不能声称实盘投放成果或真实盈利。 
