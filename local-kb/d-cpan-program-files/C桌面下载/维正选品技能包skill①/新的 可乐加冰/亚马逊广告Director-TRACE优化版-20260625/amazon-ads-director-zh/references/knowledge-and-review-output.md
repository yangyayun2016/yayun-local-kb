# 知识库与复盘输出参考

当用户提供 ASIN 知识库、关键词库、搜索词分类结果、SQLite 导出，或要求把广告诊断整理成汇报/PPT/复盘材料时使用。

## 知识库事实边界

知识库用于补充 ASIN 属性、品牌/竞品关系、词库沉淀和历史判断。它不能覆盖上传报表的事实，也不能替代用户确认。

如果用户只给数据库路径但当前环境无法访问，说明需要导出相关表或授权访问，不要假装已查询。

## 常见表/字段

`products` 可包含：

- asin、title、rating、ratings_count、reviews_count、status
- bsr、bsr_category、bsr_subcategory_rank、bsr_subcategory_name
- brand、dimensions、ownership、first_seen_at、last_updated_at

`keyword_library` 可包含：

- keyword、attribute_type、status、weight、asin、relationship_type、source、updated_at

`search_term_classified` 可包含：

- search_term、advertised_asin、campaign、ad_group、targeting、attribute_type
- impressions、clicks、spend、sales、orders、acos、roas

## Ownership 与关系判断

- 优先使用用户明确给出的自有品牌、自有 ASIN、竞品 ASIN 和排除词规则。
- 不要把“品牌词类型”和“某 ASIN 是否适合投放”混为一谈。
- 一个词可以是全局有价值词，但对某个 ASIN 是浪费流量；输出中分开写 `termType` 和 `relationshipType`。

## 关键词分类

推荐分类：

- 产品核心词
- 品牌(自有)
- 品牌(竞品)
- 类目
- 功能
- 规格参数
- 使用场景
- 适配对象
- 卖点/差异化
- ASIN
- 风险/限制
- 未分类

匹配优先级：

1. 用户确认规则
2. ASIN-specific 关系
3. 明确的 deterministic 规则
4. AI 建议
5. 人工确认

AI 建议不得自动变成人工确认。

## 可沉淀为关键词资产的信号

- 动作是 negative、exact-harvest、protect 或 bid-up。
- 风险高，需要进入否定/限制词库。
- orders > 0。
- spend >= 5 USD 且 orders = 0 且 clicks >= 5。
- 有点击或花费，并且不是普通泛类目词。

## 复盘/PPT输出

先完成广告诊断，再整理成汇报材料。不要用漂亮话替代证据。

默认结构：

1. **一句话结论**：本轮广告问题和优先动作。
2. **KPI变化**：Spend、Sales、Orders、ACOS、ROAS、CTR、CPC、CVR 的核心变化。
3. **根因链路**：流量层 -> 搜索词/定向 -> 转化/利润/库存 -> 动作。
4. **LT架构页**：用 LT 层级表展示缺失、混层、空壳和预算转移。
5. **动作台账页**：动作、对象、证据、负责人、确认状态、预计影响、复盘日期。
6. **风险页**：利润、库存、评分、评论、目标阈值和数据缺口。
7. **下轮计划**：本周执行、下周观察、需要用户确认的问题。

写作风格：

- 用“把 Auto 里的有效词转入 Exact 承接”这类机制句。
- 避免“赋能增长”“打造闭环”“智能化升级”等没有机制的表达。
- 每页只保留一个主结论；表格和图示服务结论。

如果需要生成 PPTX，先给 slide map；只有在用户明确要文件时再创建实际 PPTX。
