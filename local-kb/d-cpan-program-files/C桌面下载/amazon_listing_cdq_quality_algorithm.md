# 亚马逊官方 Listing 质量评分因素与 CDQ 算法系统

> 版本：V1.0  
> 适用对象：Amazon Seller Central / Vendor Central 目录数据质量、Listing 质量自查、ASIN 批量诊断、账号目录健康监控  
> 核心变化：从 IDQ / Listing 完整度检查，升级为 CDQ（Catalog Data Quality）目录数据质量评估。评分不再只看“有没有填”，而是同时看“是否完整、是否正确、是否一致、是否规范化”，并新增“变体质量”等维度，借助 AI / LLM 对整体目录健康进行更全面判断。

---

## 1. 背景：从 IDQ 到 CDQ 的变化

### 1.1 旧逻辑：IDQ / Listing 完整度

旧版 Listing 完整度或 IDQ 更偏向“字段是否存在”的检查，典型关注点包括：

- 是否有分类叶节点；
- 是否填写搜索关键词；
- 是否有 A+ 页面；
- 是否有品牌名称；
- 是否有商品描述；
- 是否有商品要点 / Bullet Points；
- 是否填写关键属性；
- 标题长度是否合规；
- 标题是否以品牌名开头；
- 图片数量、图片信息完整度、主图缩放功能。

这类评分适合做 Listing 基础完整度检查，但它的问题是：**只知道字段有没有，不一定知道字段对不对、前后是否一致、是否符合类目规范、变体是否健康。**

### 1.2 新逻辑：CDQ / Catalog Data Quality

CDQ 的目标是全面评估单个商品目录数据质量对客户完整购买流程的影响。CDQv3 由亚马逊精选与目录系统团队（ASCS）在 2025 年 3 月推出，重点检测目录数据的：

1. **完整性 Completeness**：关键字段、关键属性是否完整填写；
2. **准确性 / 正确性 Accuracy / Correctness**：填写的信息是否与真实产品一致；
3. **一致性 Consistency**：标题、五点、描述、图片、变体、后台属性、多站点数据之间是否一致；
4. **规范化 Normalization**：属性值、单位、格式、枚举值、语言本地化是否符合平台标准；
5. **变体质量 Variation Quality**：父子体关系、变体主题、子体属性值是否正确且不重复；
6. **客户体验影响 Customer Journey Impact**：信息质量是否影响搜索、筛选、对比、理解、转化和退货风险。

> 简单理解：IDQ 更像“字段打勾表”，CDQ 更像“目录数据健康评分系统”。

---

## 2. CDQ 指标分级

根据官方 CDQ 培训资料，CDQv2 / CDQv3 的分级可按下表理解：

| 等级 | 评分范围 | 质量含义 | 运营含义 |
|---|---:|---|---|
| A | 85%+ | 高质量 | Listing 数据质量较好，可进入精修和转化优化阶段 |
| B | 70% - 85% | 中等质量 | 基础可售，但仍有明显优化空间 |
| C | 0 - 70% | 低质量 - 非严重缺陷 | 会影响曝光、筛选、转化和客户理解，需要排期优化 |
| D | 0 | 低质量 - 严重缺陷 | 存在严重目录缺陷，需要立即修复 |
| U | N/A | 低质量 - 政策违规 | 存在政策违规或抑制风险，优先级最高 |

### 2.1 评分先后顺序

CDQ 不是简单加分模型，而是“**先判定红线，再计算分数**”：

```text
Step 1：政策违规 / 抑制判断
    如果存在索引抑制、网站抑制、标题政策违规等问题：Grade = U，Score = N/A

Step 2：严重缺陷判断
    如果存在严重目录缺陷或严重变体缺陷：Grade = D，Score = 0

Step 3：组件评分
    如果未触发 U / D，再按标题、结构化属性、变体、图片、五点、A+ 等组件加权评分

Step 4：等级映射
    Score >= 85 -> A
    70 <= Score < 85 -> B
    0 < Score < 70 -> C
```

---

## 3. 官方 CDQ v3 核心评分因素总表

| 模块 | CDQ 是否核心评分 | 官方变化点 | 主要检查因素 | 运营优先级 |
|---|---|---|---|---|
| 政策违规 / 抑制 | 是，红线项 | 索引 / 网站抑制、标题政策违规纳入红线 | 标题不完整、冗余、受限关键词、长度或大小写错误、被搜索或详情页抑制 | P0 |
| 严重缺陷 | 是，红线项 | 从“字段缺失”升级到“属性错误 / 完整性严重不足” | 多数 PT 中 Top 6 相关属性错误，或 Top 10 相关属性完整性低于 50% | P0 |
| 标题质量 | 是 | 从标题长度 / 品牌开头，升级为 TQS 逻辑 | 完整性、准确性、长度、大小写、关键词标注、关键词冗余、特殊字符、限制性短语 | P0 / P1 |
| 结构化属性 | 是 | 从前 4 / 10 相关属性完整度，升级为完整性 + 正确性 | Top 6 RAI 属性、Band A / B 属性、属性完整、属性正确、可筛选 / 可对比 | P0 / P1 |
| 变体质量 | 是，新增 | CDQ 新增重要维度 | 变体主题一致性、属性正确、单位一致、无冗余、无子体重复、本地化正确 | P0 / P1 |
| 五点 / 描述性总结 | 是 | 保留 Bullet 数量逻辑；商品描述在 CDQ 版本中已移除 | Bullet Points 数量，是否至少 3 条 | P1 |
| 图片质量 | 是 | 保留图片数量与 IAI 指标 | 图片数量 ≥4、IAI ≥0.4、图片信息完整、主图合规、可缩放 | P1 |
| A+ 内容 | 是 | A+ 存在性保留 | 是否存在 A+ / A+ 型内容 | P2 |
| 可发现性 | 即将推出 / 当前不计入核心分 | 叶节点、搜索关键词在 CDQ 当前版本中被移除；Search Keyword Gap Ratio 计划后续推出 | 搜索关键词覆盖、搜索量关键词缺口、类目节点 | P2 / 未来项 |

---

## 4. CDQ v3 系统化算法模型

### 4.1 总分公式

基于官方 CDQ 培训资料可直接确认的组件权重包括：

- 标题质量：25%
- 结构化属性：30%
- 变体质量：20%
- 描述性总结 / Bullet：5%
- A+ 内容：5%

以上合计 85%。官方资料同时明确 CDQ 对图像与 A+ 仍保留“图像数量 ≥4、IAI ≥0.4、A+ 型”等检查项。为了形成可执行的 100 分系统，本算法将剩余 15% 作为图片质量评分项。

> 注意：图片质量 15% 是为了工程化落地的“系统保留权重”。如果后台官方 CDQ 报表未来披露更精确的图片权重，应以后台官方权重为准。

```text
CDQ_Score =
  Title_Quality_Score * 25%
+ Structured_Attribute_Score * 30%
+ Variation_Quality_Score * 20%
+ Image_Quality_Score * 15%
+ Bullet_Summary_Score * 5%
+ Aplus_Content_Score * 5%
```

其中所有组件分都用 0 - 100 表示。

---

## 5. 组件一：标题质量 Title Quality，权重 25%

### 5.1 标题质量检查因素

CDQv3 使用 TQS 逻辑评估标题质量，重点看：

| 检查项 | 官方逻辑 | 系统判断方式 |
|---|---|---|
| 标题完整性 | 标题中应标注足够的关键属性 | 提取标题中的品牌、品类、核心属性、型号、规格、数量、适配信息等 |
| 标题准确性 | 标题信息应与实际商品一致 | 与后台属性、图片、五点、说明书、包装信息交叉验证 |
| 标题长度 | 标题长度 ≤ 200 字符 | 超过 200 触发违规 / 高风险 |
| 大小写规范 | 大小写评分 > 0 | 检查全大写、异常大小写、乱码 |
| 关键词标注 | 标题应覆盖清晰商品识别信息 | 是否能让客户无需猜测理解商品是什么 |
| 关键词冗余 | 不应重复堆砌同一词 / 短语 | 同一语境下重复词组超过阈值则扣分 |
| 特殊字符 | 不应含不可读或装饰性特殊字符 | 检查 `! $ ? _ { } ^ ¬ ¦ ~ # < > *` 等不合规使用 |
| 限制性短语 | 不应包含促销或受限表述 | 如 free shipping、100% quality guaranteed 等 |
| 品牌开头 | 旧版完整度要求标题以品牌字段开头 | CDQ 核心更强调完整性、规范性；内部仍建议监控 |

### 5.2 标题等级算法

```text
如果 title_completeness < 0.4
    或 title_redundancy <= 0.6
    或 title_length > 200
    或 restricted_phrase_score < 1：
        Title_Quality_Score = 0
        CDQ_Grade = U 或触发高风险复核

如果 title_completeness >= 0.6
    且 title_redundancy = 1
    且 title_length <= 200
    且 case_score > 0
    且 special_character_score = 1
    且 restricted_phrase_score = 1：
        Title_Quality_Score = 100

否则：
        Title_Quality_Score = 50 - 99，根据缺陷数量和严重度扣分
```

### 5.3 标题内部评分建议

| 子项 | 分值 | 判断方式 |
|---|---:|---|
| 标题完整性 | 30 | 标题中识别到 ≥3 个关键属性得满分；2 个部分得分；<2 个高风险 |
| 标题准确性 | 20 | 标题与属性、图片、五点是否冲突 |
| 长度合规 | 15 | 10 < 标题长度 ≤ 200 |
| 冗余控制 | 15 | 无重复堆砌得满分 |
| 特殊字符 / 乱码 | 10 | 无不可读字符得满分 |
| 限制性短语 | 10 | 无促销词、承诺词、违规词得满分 |

---

## 6. 组件二：结构化属性 Structured Attributes，权重 30%

### 6.1 CDQ 的核心变化

旧 IDQ 主要看“前 4 / 10 个相关属性是否填写”。CDQv3 改为看：

- 相关属性是否完整填写；
- 相关属性是否正确；
- 属性是否与详情页、标题、图片、变体、类目逻辑一致；
- Top 6 RAI 属性是否健康；
- Band A / Band B 属性是否支撑详情页客户关键信息；
- 属性值是否标准化、单位是否统一、枚举值是否符合规范。

### 6.2 属性分层

建议把属性按重要度分成 4 层：

| 层级 | 属性类型 | 示例 | 权重建议 |
|---|---|---|---:|
| P0 | 必填身份属性 Product Identity | brand、item_name、product_type、external_product_id、model_number | 高 |
| P1 | Top 6 RAI 关键属性 | 材质、尺寸、容量、颜色、数量、适配型号、功率等 | 最高 |
| P2 | Band A 属性 | 客户在详情页、搜索筛选、对比中高频使用的属性 | 高 |
| P3 | Band B 属性 | 补充型、场景型、功能型属性 | 中 |

### 6.3 结构化属性评分公式

```text
对每个关键属性 attr_i：
    attr_i_score = completeness_i * correctness_i * consistency_i * normalization_i

Structured_Attribute_Score = Σ(attr_i_score * attr_i_weight) / Σ(attr_i_weight) * 100
```

其中：

| 变量 | 含义 | 取值方式 |
|---|---|---|
| completeness_i | 是否填写 | 填写 = 1；未填写 = 0；部分填写 = 0.5 |
| correctness_i | 是否正确 | 与商品事实一致 = 1；明显错误 = 0；待确认 = 0.5 |
| consistency_i | 是否一致 | 与标题、五点、图片、变体、站点信息一致 = 1；冲突 = 0 |
| normalization_i | 是否规范化 | 单位、格式、枚举值、语言符合规范 = 1；不规范 = 0.5 或 0 |
| attr_i_weight | 属性权重 | P0/P1 高，P2 中高，P3 中 |

### 6.4 正确性、一致性、规范化的判定案例

| 质量概念 | 错误例子 | 正确做法 |
|---|---|---|
| 正确性 | 后台功率填 1400W，标题写 1800W | 以真实产品规格为准，所有字段统一 |
| 一致性 | 图片展示 2 件套，标题写 1 件套 | 标题、主图、副图、变体、属性统一 |
| 规范化 | 尺寸有的写 inch，有的写 cm；颜色写 Blue、blu、蓝色混用 | 使用站点语言和类目认可枚举值，单位统一 |
| 本地化 | 德国站仍保留英文材质 / 场景词 | 按站点语言本地化，且不改变事实 |

---

## 7. 组件三：变体质量 Variation Quality，权重 20%

### 7.1 CDQ 新增重点

变体质量是 CDQ 相比 IDQ 的重要新增维度。它不只看是否有父子体，还要看变体主题、子体属性、重复子体、本地化、单位和格式是否正确。

### 7.2 变体严重缺陷

以下问题属于严重缺陷，需要立即处理：

- 错误属性值；
- 单位制混用；
- 变体信息冗余；
- 本地化错误；
- 子项重复；
- 父子体不应合并却被合并；
- 不同产品类型被错误放入同一变体族；
- 子体缺少变体主题属性值；
- 变体主题属性与实际差异不匹配。

### 7.3 非严重缺陷

以下问题可排期优化：

- 未标准化值；
- 格式不匹配；
- 变体主题错误但暂未造成严重客户误导；
- 颜色、尺寸、数量等值命名不统一；
- 多站点翻译不一致。

### 7.4 变体质量评分算法

```text
如果没有变体：
    Variation_Quality_Score = 100

如果存在严重变体缺陷：
    Variation_Quality_Score = 0
    CDQ_Grade = D 或触发 P0 修复

否则：
    Variation_Quality_Score = 100
        - 25 * variation_theme_error_count
        - 20 * duplicate_child_count
        - 15 * inconsistent_unit_count
        - 10 * unnormalized_value_count
        - 10 * localization_error_count
    最低不低于 0
```

### 7.5 变体健康检查规则

| 检查项 | 通过标准 |
|---|---|
| 父体主题 | 变体主题与客户真实选择维度一致，如 Size、Color、Style、Pattern |
| 子体唯一性 | 同一父体下不能有重复子体 |
| 属性一致性 | 子体均填写同一变体主题属性 |
| 属性正确性 | 子体变体值与图片、标题、包装、后台属性一致 |
| 单位一致性 | 同一变体族使用同一单位体系 |
| 本地化一致 | 不同站点翻译准确，不能改变规格事实 |

---

## 8. 组件四：图片质量 Image Quality，系统权重 15%

### 8.1 官方保留检查项

官方 CDQ 对比资料保留了以下图片相关检查：

- 图片数量 ≥ 4；
- IAI ≥ 0.4；
- 图片与 A+ 型内容检查；
- 主图及附图符合类目合规要求。

### 8.2 图片评分算法

```text
Image_Quality_Score =
  image_count_score * 35%
+ image_information_score * 35%
+ main_image_compliance_score * 20%
+ zoom_score * 10%
```

| 子项 | 满分条件 |
|---|---|
| image_count_score | 图片数量 ≥4 |
| image_information_score | 从产品本身、多角度、使用场景、尺寸、细节、对比、配件等角度表达清晰 |
| main_image_compliance_score | 主图白底、真实商品、无文字水印、商品占比足够、无未售配件误导 |
| zoom_score | 图片最长边 ≥1600px，可触发缩放功能 |

### 8.3 主图基础合规要求

- 主图需采用纯白色背景，RGB 值 255 / 255 / 255；
- 主图必须是实际商品的专业照片，不得是图形、插图或实物模型；
- 单一正面角度展示商品本身，不得展示不出售的配件、标志、水印、色块、文字等；
- 商品应占主图 85% 以上；
- 图片最长边不低于 1600 像素，以满足网站缩放功能；
- 图片最长边不得超过 10000 像素；
- 亚马逊接受 JPEG、TIFF、GIF 文件格式，但首选 JPEG，不支持 `.gif` 动画；
- 女装和男装主图应采用模特照；
- 所有儿童和婴儿服装图片应采用平放拍摄，不借助模特。

---

## 9. 组件五：描述性总结 / Bullet Points，权重 5%

CDQ 中描述性总结主要按 Bullet Points 数量评分：

| Bullet 数量 | Bullet_Summary_Score |
|---:|---:|
| ≥3 条 | 100 |
| ≥1 条 | 50 |
| 0 条 | 0 |

> 实操建议：虽然官方最低逻辑是 ≥3 条，但运营上建议写满 5 条，并将核心功能、使用场景、参数、差异化卖点、售后 / 安全信息分层表达。

---

## 10. 组件六：A+ 内容，权重 5%

| A+ 状态 | Aplus_Content_Score |
|---|---:|
| 存在 A+ | 100 |
| 不存在 A+ | 0 |

A+ 在 CDQ 中是基础存在性检查，但在实际转化中建议进一步检查：

- A+ 是否覆盖客户疑问；
- A+ 是否与标题、五点、后台属性一致；
- A+ 是否展示尺寸、使用场景、对比表、安装方式、维护方式；
- A+ 是否有夸大、绝对化、违规或无法证实的表述。

---

## 11. 当前 CDQ 中被移除或即将推出的项目

| 项目 | IDQ / 旧版情况 | CDQ 当前情况 | 是否仍建议监控 |
|---|---|---|---|
| 分类叶节点 | 旧版完整度计分 | CDQ 中已移除 | 是，影响流量入口和类目相关性 |
| 搜索关键词 | 旧版完整度计分 | CDQ 中已移除 | 是，影响搜索覆盖 |
| 商品描述 | 旧版完整度计分 | CDQ 版本中已移除 | 是，尤其欧洲站仍常见失分项 |
| Search Keyword Gap Ratio | 旧版未系统化 | 计划 2026 年推出 | 是，适合做前置监控 |

---

## 12. 2024 新版亚马逊 Listing 完整度打分表（旧版 / 基础完整度）

该表适合做“基础 Listing 完整度”自查，可作为 CDQ 的前置数据采集层。

| 分类 | Listing 要素 | 家居生活用品 | 时尚 | 消费电子品 | 消费品 |
|---|---|---:|---:|---:|---:|
| 流量 | 有分类叶节点 | 10 | 10 | 20 | 10 |
| 流量 | 有搜索关键词 | 5 | 5 | 10 | 5 |
| 转化 | 有 A+ 页面 | 12.5 | 12.5 | 10 | 12.5 |
| 转化 | 有品牌名称 | 5 | 5 | 0 | 5 |
| 转化 | 有商品描述 | 5 | 5 | 10 | 5 |
| 转化 | 有 1 条商品要点 | 5 | 5 | 0 | 5 |
| 转化 | 有 3 条或以上商品要点 | 2.5 | 2.5 | 0 | 2.5 |
| 转化 | 关键属性全部填写 | 25 | 25 | 25 | 25 |
| 标题 | 10 字符 < 标题长度 < 200 字符 | 5 | 5 | 5 | 5 |
| 标题 | 标题以品牌名开头 | 5 | 5 | 0 | 5 |
| 图片 | 图片信息完整度 | 5 | 5 | 5 | 5 |
| 图片 | 有 4 张或以上图片 | 5 | 5 | 5 | 5 |
| 图片 | 主图有缩放功能 | 10 | 10 | 10 | 10 |
| 合计 | 满分 | 100 | 100 | 100 | 100 |

### 12.1 旧版完整度等级

| 等级 | 分数 | 解释 |
|---|---:|---|
| A | 80 - 100 | 具有所有要素或仅缺少一个 |
| B | 70 - 79 | 缺少 1 - 2 个要素，有改善空间 |
| C | 60 - 69 | 缺少 2 - 3 个要素，有改善空间 |
| D | 50 - 59 | 缺少 3 - 4 个要素，需要改善 |
| E | 10 - 49 | 缺少 4 - 5 个核心属性，曝光转化会受到严重影响 |
| F | 0 | 创建了 ASIN 但存在合规问题，或缺失所有要素，在搜索和浏览界面被禁止显示 |

---

## 13. IDQ / Listing 完整度 vs CDQv3 对照表

| 维度 | IDQ / 旧版完整度 | CDQv3 新指标 | 变化本质 |
|---|---|---|---|
| 策略违规 | 索引 / 网站抑制 | 索引 / 网站抑制 + 标题政策违规 | 红线更明确 |
| 严重缺陷 | 多数 PT 中前 6 相关属性错误或前 10 相关属性完整性 <50% | 保留并扩展 | 从缺失扩展到错误 |
| 结构化属性 | 前 4 / 10 相关属性完整性 | 相关属性完整性 + 正确性；Top 6 + Band A / B 属性分析 | 从完整度变成质量度 |
| 标题 | 标题长度、标题以品牌开头 | 标题完整性、大小写、长度、受限词、冗余关键词 | 从形式合规变成语义质量 |
| 五点 / 说明 | Bullet 数量 ≥3，包含商品描述 | Bullet 数量 ≥3；商品描述从 CDQ 版本中移除 | 更聚焦可扫描摘要 |
| 变体 | 无 | 变体主题属性一致性、正确性、避免重复 | 新增核心指标 |
| 图像与 A+ | 图片数量 ≥4、IAI ≥0.4、A+ 型 | 保留图片数量、IAI、A+ 型 | 继续影响客户理解 |
| 可发现性 | 有叶节点、含关键词 | CDQ 当前移除，Search Keyword Gap Ratio 将于 2026 推出 | 未来会重新系统化 |

---

## 14. 账号级目录数据质量监控算法

CDQ 是 ASIN 级评分，但运营管理需要账号级监控。建议按以下方式聚合：

### 14.1 账号级核心指标

| 指标 | 公式 | 用途 |
|---|---|---|
| ASIN 平均 CDQ | 所有 ASIN CDQ 平均值 | 看整体质量 |
| 加权 CDQ | Σ(ASIN CDQ × 权重) / Σ权重 | 用销量、流量、库存价值加权，优先修复高价值 ASIN |
| A 级占比 | A级 ASIN 数 / 总 ASIN 数 | 看健康产品池 |
| C/D/U 占比 | C/D/U ASIN 数 / 总 ASIN 数 | 看风险池 |
| P0 缺陷数 | 政策违规、抑制、严重缺陷数量 | 每日必看 |
| 变体健康率 | 无严重变体缺陷父体数 / 父体总数 | 看变体目录质量 |
| 关键属性完整率 | 完整且正确的关键属性数 / 应填关键属性数 | 看结构化数据基础 |
| 图片健康率 | 图片达标 ASIN 数 / 总 ASIN 数 | 看视觉信息质量 |
| A+ 覆盖率 | 有 A+ ASIN 数 / 总 ASIN 数 | 看转化基础 |

### 14.2 ASIN 优先级排序

```text
Repair_Priority_Score =
  defect_severity_weight * 40%
+ traffic_or_sales_weight * 30%
+ conversion_impact_weight * 20%
+ ease_of_fix_weight * 10%
```

优先级建议：

1. U 级：政策违规、搜索 / 网站抑制、标题违规；
2. D 级：严重属性错误、严重变体缺陷；
3. 高流量 C 级：流量高但属性、图片、标题不完整；
4. 高库存 B 级：即将推广或库存压力大的 ASIN；
5. 新品：上架前必须达到 B 级以上，核心 ASIN 目标 A 级。

---

## 15. 数据表设计

### 15.1 ASIN 快照表 asin_catalog_snapshot

| 字段 | 类型 | 说明 |
|---|---|---|
| marketplace | string | 站点 |
| asin | string | 子 ASIN |
| parent_asin | string | 父 ASIN |
| sku | string | SKU |
| product_type | string | 产品类型 |
| category_leaf_node | string | 分类叶节点 |
| brand | string | 品牌 |
| title | string | 标题 |
| bullet_points | array | 五点 |
| product_description | string | 商品描述 |
| generic_keywords | string | 搜索关键词 |
| aplus_exists | boolean | 是否有 A+ |
| image_count | int | 图片数量 |
| image_metadata | json | 图片尺寸、格式、主图、缩放状态 |
| attributes | json | 后台属性 |
| variation_theme | string | 变体主题 |
| child_variation_values | json | 子体变体值 |
| suppression_status | string | 是否抑制 |
| policy_flags | json | 政策违规标记 |
| traffic_30d | float | 近 30 天流量 |
| sales_30d | float | 近 30 天销售额 |
| inventory_value | float | 库存价值 |
| updated_at | datetime | 抓取时间 |

### 15.2 属性主数据表 cdq_attribute_master

| 字段 | 类型 | 说明 |
|---|---|---|
| marketplace | string | 站点 |
| product_type | string | 产品类型 |
| attribute_name | string | 属性名 |
| attribute_band | string | P0 / Top6 / Band A / Band B |
| required_type | string | Required / Recommended |
| allowed_values | array | 允许值 |
| unit_standard | string | 标准单位 |
| weight | float | 属性权重 |
| locale_rule | string | 本地化规则 |

### 15.3 评分结果表 asin_cdq_score

| 字段 | 类型 | 说明 |
|---|---|---|
| asin | string | ASIN |
| marketplace | string | 站点 |
| cdq_score | float | 总分 |
| cdq_grade | string | A/B/C/D/U |
| title_score | float | 标题分 |
| structured_attribute_score | float | 结构化属性分 |
| variation_score | float | 变体分 |
| image_score | float | 图片分 |
| bullet_score | float | Bullet 分 |
| aplus_score | float | A+ 分 |
| policy_defects | json | 政策缺陷 |
| severe_defects | json | 严重缺陷 |
| non_severe_defects | json | 非严重缺陷 |
| recommended_actions | json | 修复建议 |
| created_at | datetime | 评分时间 |

---

## 16. AI / LLM 在 CDQ 中的作用

CDQ 的变化本质上适合引入 AI 和大型语言模型，因为很多问题不能靠简单字段规则判断。

### 16.1 AI 可做的判断

| 场景 | AI 任务 | 输出 |
|---|---|---|
| 标题质量 | 从标题中识别品牌、品类、规格、功能、适配、数量等属性 | 标题完整性分、冗余词、违规词 |
| 属性正确性 | 对比标题、五点、图片、后台属性 | 冲突字段清单 |
| 属性规范化 | 识别非标准单位、非本地语言、格式混乱 | 标准化建议 |
| 图片信息 | 识别图片是否展示尺寸、场景、细节、配件、对比 | 图片信息完整度 |
| 变体质量 | 检查子体是否重复、主题是否一致、单位是否混用 | 变体缺陷等级 |
| A+ 一致性 | 对比 A+ 与 Listing 字段是否冲突 | 风险提示 |
| 多站点同步 | 检查翻译是否改变事实 | 本地化错误清单 |

### 16.2 AI 使用边界

- AI 可以判断冲突、缺失、疑似错误，但不能编造商品事实；
- 涉及尺寸、材质、功率、认证、安全信息等事实属性，必须以产品规格书、包装、后台 V3 属性、供应链资料为准；
- AI 给出的标准化建议，需要运营人员确认后再批量上传；
- 对政策、合规、安全类字段，宁可人工复核，不可自动改写。

---

## 17. 评分伪代码

```python
def calculate_cdq(asin_snapshot, attribute_master):
    # 1. 政策红线
    if has_policy_violation(asin_snapshot):
        return {
            "score": None,
            "grade": "U",
            "reason": "Policy violation or index/site suppression"
        }

    # 2. 严重缺陷
    if has_severe_catalog_defect(asin_snapshot, attribute_master):
        return {
            "score": 0,
            "grade": "D",
            "reason": "Severe catalog defect"
        }

    if has_severe_variation_defect(asin_snapshot):
        return {
            "score": 0,
            "grade": "D",
            "reason": "Severe variation defect"
        }

    # 3. 组件分
    title_score = score_title_quality(asin_snapshot)
    attr_score = score_structured_attributes(asin_snapshot, attribute_master)
    variation_score = score_variation_quality(asin_snapshot)
    image_score = score_image_quality(asin_snapshot)
    bullet_score = score_bullet_summary(asin_snapshot)
    aplus_score = 100 if asin_snapshot.aplus_exists else 0

    # 4. 加权总分
    score = (
        title_score * 0.25
        + attr_score * 0.30
        + variation_score * 0.20
        + image_score * 0.15
        + bullet_score * 0.05
        + aplus_score * 0.05
    )

    # 5. 等级
    if score >= 85:
        grade = "A"
    elif score >= 70:
        grade = "B"
    else:
        grade = "C"

    return {
        "score": round(score, 2),
        "grade": grade,
        "component_scores": {
            "title": title_score,
            "structured_attributes": attr_score,
            "variation": variation_score,
            "image": image_score,
            "bullet": bullet_score,
            "aplus": aplus_score,
        },
        "actions": generate_repair_actions(asin_snapshot)
    }
```

---

## 18. 修复 SOP：三阶段落地

### Step 1：自测整体 ASIN 情况，制定更新计划

- 周期：1 - 2 周；
- 目标：找出 U / D / C 级 ASIN，建立修复优先级；
- 工具：新版打分表、增长机会、Fix Your Product、Listing Quality Dashboard。

### Step 2：补充商品信息、上传商品图片、批量更新

- 周期：4 - 6 周；
- 目标：补齐关键属性、图片、A+、Bullet、标题；
- 工具：生成商品内容、图片风格指南、BIL、LOSG、批量模板。

### Step 3：检查 Listing，同步各站点 ASIN

- 周期：2 周；
- 目标：消除站点间信息不一致、变体错误、本地化错误；
- 工具：FYP、LQD、BIL、LOSG。

---

## 19. 自动化监控规则

| 监控项 | 触发条件 | 告警等级 | 建议动作 |
|---|---|---|---|
| 政策违规 | U 级 / N/A | P0 | 立即修复标题、受限词、抑制问题 |
| 严重缺陷 | D 级 / 0 分 | P0 | 修复 Top 属性错误或严重变体缺陷 |
| 关键属性缺失 | Top 6 / Band A 属性缺失 | P1 | 补齐 Required 与高权重 Recommend 属性 |
| 属性冲突 | 标题、图片、五点、后台属性不一致 | P1 | 以产品事实为准统一所有字段 |
| 变体异常 | 子体重复、单位混用、主题错误 | P1 | 拆分或重建变体族 |
| 图片不足 | 图片少于 4 张 | P1 | 补齐主图、多角度、尺寸、场景、细节图 |
| 主图不可缩放 | 最长边 <1600px | P2 | 替换高清主图 |
| Bullet 不足 | Bullet <3 条 | P2 | 至少补齐 3 条，运营上建议 5 条 |
| A+ 缺失 | 无 A+ | P2 | 补充 A+，尤其主推 ASIN |
| 多站点不一致 | BIL 同步后字段冲突 | P2 | 检查翻译、本地化、单位、价格和库存关联 |

---

## 20. 输出报告模板

每个 ASIN 的最终报告建议包含：

```markdown
## ASIN：B0XXXXXXXX / US

### 1. CDQ 总览
- CDQ Score：82.5
- CDQ Grade：B
- 风险等级：P1
- 主要问题：结构化属性不完整、图片信息不足、变体值未标准化

### 2. 组件分
| 组件 | 权重 | 得分 | 问题 |
|---|---:|---:|---|
| 标题质量 | 25% | 90 | 标题合规，但核心参数未充分标注 |
| 结构化属性 | 30% | 70 | Top 6 属性缺失 2 个 |
| 变体质量 | 20% | 85 | 部分颜色值未标准化 |
| 图片质量 | 15% | 60 | 图片少于 4 张，缺少尺寸图 |
| Bullet | 5% | 100 | 已有 5 条 |
| A+ | 5% | 0 | 无 A+ |

### 3. P0 / P1 / P2 修复动作
- P0：无
- P1：补齐材质、尺寸、功率、适配型号等关键属性
- P1：补充尺寸图、场景图、细节图，图片数量达到 4 张以上
- P2：补充 A+ 内容
```

---

## 21. 实操结论

1. **CDQ 不是简单 Listing 文案分，而是目录数据质量分。** 以后评估 Listing，要从标题、属性、图片、变体、A+、Bullet、抑制风险、站点一致性一起看。
2. **关键属性是 CDQ 的核心。** 新版结构化属性权重高，而且引入正确性、一致性、规范化，不能只填空字段。
3. **变体质量是新增重点。** 对多颜色、多尺寸、多套装产品，父子体错误会显著影响 CDQ。
4. **标题从“长度合规”变成“语义质量合规”。** 不仅要 ≤200 字符，还要完整、准确、不冗余、无受限词、无异常字符。
5. **图片不只是数量。** 需要表达信息完整，至少 4 张，主图合规，可缩放，并能支持客户理解产品。
6. **AI / LLM 最适合做 CDQ 辅助诊断。** 它可以帮你识别字段冲突、属性缺失、标题冗余、变体异常、图片信息不足，但事实字段必须由运营或供应链确认。
7. **账号级监控要加权。** 高流量、高销售、高库存、高广告投入 ASIN 要优先修复，而不是平均用力。

---

## 22. 资料来源

- 《CDQ Training (1)官方.pptx》：CDQ 指标概述、CDQv3 对比 IDQv2、组件评分、标题质量、结构化属性、变体质量、Bullet 与 A+ 规则。
- 《CN_GS_Listing_Basics_1.4_Uploading.pdf》：上传商品 Listing 基础学习资料、Listing 质量自查工具、2024 新版 Listing 完整度打分表、标题、关键属性、图片信息完整度、三步优化流程。
