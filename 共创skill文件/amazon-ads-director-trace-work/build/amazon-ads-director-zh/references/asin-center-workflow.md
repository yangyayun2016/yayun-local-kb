# ASIN Center 工作流

当输入包含 ASIN Center JSON、HAR、页面文本或这些字段时使用：`header`、`part1_review`、`part2_diagnosis`、`part4_adArchitecture`、`part5_operations`。

## 数据入口

常见 ASIN Center JSON 路径形态：

- `/json/{username}/asin-list.json`
- `/json/{username}/{ASIN}.json`
- `/json/_all/asin-list.json`
- `/json/_all/{ASIN}.json`

HAR 必须包含 ASIN 明细 JSON 才有诊断价值。如果只有 ASIN 列表，让用户进入某个 ASIN 明细页，等待报告加载完成，再导出包含内容的 HAR。

## 顶层结构

- `header`：ASIN 元数据和标题诊断。
- `part1_review`：数据对比、交叉验证、策略复核。
- `part2_diagnosis`：L2/L3 诊断链路和决策字段。
- `part3_changes`：变化解释。
- `part4_adArchitecture`：广告架构建议和归因。
- `part5_operations`：具体操作计划和广告树。
- `part6_decisionAttribution`：决策归因。
- `part7_expectedResults`：预期结果和监控计划。
- `part8_memo`：备忘。
- `part9_productOptimization`：产品优化建议。
- `part10_multiAsinPriority`：多 ASIN 优先级。

## 读取顺序

1. 读 `header`：`asin`、`productName`、`销售账号`、`负责人`、`L2`、`L3`、`库存模式`、`可销月`、`评分`、`生命周期`、`生成时间`。
2. 读 `part1_review.dataComparison`：访客、转化率、ACOS、广告点击、广告转化、订单、销售额、利润率、退款率、类目排名、可销月。
3. 使用 `part2_diagnosis` 作为权威诊断链：`l2Process`、`l2TypeReference`、`l3Details`、`rating`、`decisionFields`。除非用户要求审计，不要重新发明 L2/L3。
4. 读 `part4_adArchitecture`：预算层分配、策略匹配、流量分布、核心匹配效率、否定词控制、空壳率、覆盖检查、风险警告。
5. 读 `part5_operations`：`currentRisks`、`inventoryImpact`、`asinLevelOperations`、`priceCheck`、`moduleCoverage`、`reviewCheck`、`newActivities`、`operationStats`、`adTree`。
6. 需要补充时再看 `part6` 到 `part10`，用于解释预期结果、产品动作和多 ASIN 优先级。

## ASIN Center 输出重点

- 用 `header` 先交代 ASIN、生命周期、库存、评分和 L2/L3。
- 用 `part1_review` 抽取 3-6 个关键证据，不要堆满所有指标。
- 用 `part2_diagnosis` 串起根因链，而不是只复述指标涨跌。
- 用 `part4_adArchitecture` 转成 LT 层级表；不要只说“架构不合理”。
- 用 `part5_operations` 转成执行清单，保留模块、动作 ID、对象和触发原因。

## 动作语义

- Module A：站外流量和品牌内容。
- Module B：广告流量动作。
- Module C：转化、价格、Coupon、Promotion、Quantity Discount 检查。
- Module D：评论和评分动作。
- `B7-6`：否定关键词/流量清理。
- `B5-1`：Exact 承接/匹配收紧。
- `D16-1`：Review/Vine 相关动作。

## L2 = E流量质量差 时的默认优先级

1. 压缩过度分配的探索层预算。
2. 对无关或零订单高花费流量做否定/清理。
3. 把预算转向转化层和已验证 exact/phrase 目标。
4. 把 strong search terms 从 broad/auto 探索中拆出来单独 exact 承接。
5. 扩量前检查利润率、库存、评分和评论门槛。

## 风险处理

- 利润率低于 25%：默认预算收紧，不直接扩量。
- 可销月低或库存异常：抑制扩量，优先利润保护和库存安全。
- 评分低或评论不足：广告扩量前提示转化风险。
- ACOS 高且 CVR 低：优先清理流量质量，不建议 broad/auto 加预算。
- 分区结论冲突：展示冲突，并优先使用操作表、广告树和可追溯指标。
