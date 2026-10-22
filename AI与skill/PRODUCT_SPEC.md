# 天机 OS AI Ads 决策系统 · MVP 产品与技术交付说明

版本：UI 交互原型 V2.0（仅前端演示，不接生产 API）

## 一、参考截图及改造映射

| 上传原界面 | Demo 模块 | 本次改造重点 |
|---|---|---|
| 广告中心总看板 | 决策总览 | 店铺范围、日期、5 个 KPI、健康分、趋势、风险和机会分层 |
| 健康诊断任务列表 | 重新诊断 | 模拟任务扫描、分步骤进度、数据来源状态 |
| 健康诊断摘要 | 决策总览 / 报告摘要 | 健康分与证据可信度分离、行动进入审批流 |
| 商品基础信息 | 诊断报告 01 | 商品、售价、Coupon、Review、LQS、费用、标签状态 |
| CDQ/价格/库存 | 诊断报告 02 | 基本面证据，不以出单反推有货 |
| 月度广告、毛利 | 诊断报告 03 | 历史月度表、利润口径提示和不完整数据标识 |
| Campaign 与关键词 | 投放结构 / 关键词机会 | 结构、策略类型、Target 数据、ABA 匹配风险 |
| Placement | 投放结构 / 诊断报告 06 | Campaign × Placement 下钻；跨期不直接合计 |
| 预算打满 | 投放结构 / 诊断报告 07 | 预算约束与扩量价值分离 |
| 竞品 BSR | 竞品与排名 | BSR 同期对比，防止将排名倍数当销量倍数 |
| 5 月下滑根因 | 竞品与排名 / 诊断报告 09 | 时间线、支持和反证、缺失数据 |
| 优先级行动 | AI 行动中心 | Proposal→审批→模拟执行→审计 |
| ABA 搜索词绩效 | 关键词机会 / 诊断报告 10 | 购买份额/点击份额，校验口径 |
| 关键词空白 | 关键词机会 | K03、K04、K07、K10 机会分层 |

## 二、用户核心流程

1. 选择广告账户与期间，浏览 KPI 与主要风险。
2. 点击「健康诊断报告」，查看 12 章节诊断；展开每章并审阅指标。
3. 点击「关键词机会」选择风险或增长词，打开侧栏查看广告与 ABA 证据。
4. 在「投放结构」识别高 ACOS Placement、预算打满和策略分组。
5. 在「竞品与排名」查看同类商品 BSR 和历史事件链，明确因果假设级别。
6. 进入「AI 行动中心」调整 Bid、CVR、AOV、ACOS、Goal、单次变动上限。
7. 创建审批单、批准并模拟执行，在审计日志中查看全过程。
8. 导出诊断 CSV 或审计 CSV。所有内容在浏览器内存中运行，刷新即重置。

## 三、核心的后端实体

- `accounts`：tenant_id、profile_id、marketplace、currency、timezone。
- `ad_campaigns`：Campaign 的预算、状态、竞价策略、策略标签。
- `ad_groups`、`product_ads`、`targets`、`search_terms`。
- `placement_facts`：Campaign × Placement × 日期，带归因窗口。
- `sku_unit_economics`：净收入、成本、平台费、广告前/后贡献利润。
- `aba_query_facts`：Query × ASIN × 周或月 × 份额与数量。
- `rank_snapshots`：关键词、设备、邮编、采集时间、自然/广告位。
- `diagnostic_jobs`、`diagnostic_findings`、`evidence_records`。
- `action_proposals`、`approvals`、`execution_logs`、`evaluations`。

## 四、数据质量高优先级规则

1. 时间范围一致：不可将 7 天总额与 30 天日均并列直接比较。
2. 数据粒度一致：ABA Search Query 和 Target 不天然等价。
3. 店铺范围一致：所选账户的 KPI 不跨账户相加。
4. 金额币种一致：必须保存站点币种、汇率日期和货币转换方式。
5. 财务口径一致：广告前贡献利润 = 净销售 - 非广告变动成本；广告后再减广告费。
6. 空值/零值区别：无查询结果并不等于真实数据为 0。
7. 归因成熟度：订单与销售必须记录归因窗口和修订时间。
8. 数据来源保真：第三方估算不能表现成 Amazon 第一方真实数据。
9. 报告日期一致：2026-05 的 ABA、2026-04 的 Placement 和 2026-06 的店铺 KPI 不直接拼成一个总计。
10. 证据分级：A 事实、B 关联、C 合理假设、D 待补证。

## 五、算法与调价安全

价值出价演示公式：`Bid = PredictedAOV * PredictedCVR * TargetACOS * GoalModifier`。

单次安全出价：`max(current_bid*(1-maxChange), min(model_bid, current_bid*(1+maxChange)))`。

生产算法还需预测设置 Bid 对实际 CPC、Clicks、CVR 的影响，配合利润、库存、预算和 Placement 约束。请注意：当前设置 Bid 不是实际点击成本，不能直接拿它预测真实订单 CPA。

## 六、生产接入优先级

- P0：真实 Ads API、SP-API 授权、多租户 Profile 隔离、报告粒度与成本数据、数据质量规则。
- P1：关键词/Placement 诊断、审核流程、真实 Target 绑定、幂等写入、API 回读确认。
- P2：CVR / AOV 预测、Campaign 预算边际模拟、小时级数据（Stream）、操作效果回测。
- P3：Allyhub / SIF 竞争快照、自然排名增量实验、AI 工作流优化。

## 七、安全和使用边界

演示只在用户浏览器本地运行，无生产 Amazon OAuth/Ads Token、无远程请求。执行按钮只修改演示 UI 的本地状态，不能真实地暂停关键词或更改广告预算。
