# 亚马逊 CDQ Listing 质量打分系统算法架构设计稿

> 版本：v1.0  
> 用途：作为「亚马逊运营智能体 / CDQ 打分系统 / Listing 质量诊断系统」的算法架构底稿  
> 适用对象：亚马逊精品运营团队、广告运营团队、Listing 优化团队、AI 产品研发团队、SaaS 系统开发团队  
> 资料底座：你上传的 `CDQ Training 官方.pptx`、`CN_GS_Listing_Basics_1.4_Uploading.pdf`、`CDQ打分系统skills.md`  
> 核心判断：CDQ 不是旧版 IDQ 的简单升级，而是从“信息是否填了”升级为“目录数据是否完整、正确、一致、规范，并能支撑客户完整购买决策”的系统工程。

---

## 0. 一句话结论

亚马逊 Listing 质量评分已经从 **IDQ：字段完整度检查**，升级为 **CDQ：Catalog Data Quality 目录数据质量评估**。

过去 IDQ 更像是：

> “该填的字段有没有填？”

现在 CDQ 更像是：

> “买家、搜索系统、推荐系统、广告系统、Rufus / Alexa for Shopping / LLM 是否能从这条 Listing 中获得完整、正确、一致、规范、可理解、可转化的商品事实？”

所以，我们开发系统时，不能只做一个“标题字数 + 图片数量 + Bullet 数量”的静态打分器，而应该做一个 **商品事实质量引擎**：

```text
商品事实层
  ↓
字段完整性判断
  ↓
字段正确性判断
  ↓
跨模块一致性判断
  ↓
类目规范化判断
  ↓
变体家族一致性判断
  ↓
AI 语义理解与风险判断
  ↓
CDQ 分数 / 缺陷等级 / 修复建议 / 批量任务
```

---

## 1. IDQ 到 CDQ 的本质变化

### 1.1 旧 IDQ 的底层逻辑

IDQ 更偏向 **Integrity / Completeness 完整性**。

典型检查项：

| 旧 IDQ 检查项 | 逻辑 |
|---|---|
| 有无分类叶节点 | 商品是否放入某个细分类目 |
| 有无搜索关键词 | 后台 Search Terms 是否填写 |
| 有无品牌名 | Brand 是否存在 |
| 标题是否以品牌开头 | 标题结构是否满足基本规范 |
| 标题长度是否合理 | 主要看字符数 |
| 有无 Bullet | 是否至少有 1 条 / 3 条要点 |
| 有无 Description | 是否有商品描述 |
| 有无 A+ | 是否创建 A+ |
| 图片数量是否 ≥ 4 | 是否满足图片数量 |
| 主图是否可缩放 | 是否满足像素与缩放要求 |
| RAC Top4 / Top10 属性完整度 | 相关属性是否填写 |

这套逻辑的优势是简单、容易批量跑；问题是它容易被“形式化填充”绕过。

例如：

```text
Material 字段填了 “Plastic”
但图片、标题、五点都显示是 Stainless Steel
旧 IDQ 可能认为字段已填
CDQ 应该认为：错误、不一致、误导买家
```

---

### 1.2 新 CDQ 的底层逻辑

CDQ 的判断核心从 **有没有** 变成 **有没有 + 对不对 + 是否一致 + 是否规范 + 是否影响客户购买路径**。

| 维度 | IDQ 时代 | CDQ 时代 |
|---|---|---|
| 完整性 | 字段是否填写 | 关键属性是否完整覆盖购买决策 |
| 正确性 | 很弱 | 属性值是否真实、可信、符合实物 |
| 一致性 | 很弱 | 标题、图片、五点、A+、后台属性、变体是否互相一致 |
| 规范化 | 基础格式 | 单位、枚举值、本地化表达、类目规范是否标准化 |
| 变体质量 | 基本不管 | 单独成为重要质量组件 |
| AI 判断 | 无或弱 | LLM / 视觉模型 / 语义模型参与判断 |
| 目标 | 信息完整 | 目录健康、搜索匹配、转化决策、风险控制 |

---

### 1.3 系统设计上的关键转变

如果我们做系统，不能只复制亚马逊后台分数，而要做两层分数：

```text
A. 官方 CDQ Core Score：尽量贴近亚马逊官方目录质量逻辑，100 分制
B. 业务增强 Quality Opportunity Score：结合流量、转化、广告、竞品、关键词，做运营优先级判断
```

也就是说：

> 官方 CDQ 告诉你：“哪里有目录质量缺陷。”  
> 我们的系统要进一步告诉你：“先修哪个、怎么修、修完预计影响什么、是否值得修。”

---

## 2. 官方 CDQ 与用户自定义 Skill 的冲突校准

你之前整理的 `CDQ打分系统skills.md` 中提出了一个 **120 分模型**：

| 模块 | 权重 |
|---|---:|
| 结构化属性质量 | 30 |
| 标题质量 | 25 |
| 描述性摘要 / Bullet | 5 |
| 图片质量 | 15 |
| A+ 页面质量 | 5 |
| 变体质量 | 20 |
| 产品类型分类 / 可发现性 | 20 |
| 合计 | 120 |

这个模型非常适合做你自己的商业化系统，因为它把 **Product Type Classification / Leaf Node / Discoverability** 也纳入了商业诊断。

但从官方 CDQ 培训资料看，应该做一个重要区分：

### 2.1 官方核心 CDQ：100 分

```text
CDQ Core 100 =
结构化属性 30
+ 标题质量 25
+ 变体质量 20
+ 图片质量 15
+ Bullet 5
+ A+ 5
```

合计 100 分。

### 2.2 业务增强分：额外 20 分

```text
Business Discoverability 20 =
产品类型分类正确性
+ Leaf Node 准确性
+ Search Keyword Gap
+ 后台关键词覆盖
+ 类目筛选属性覆盖
```

这部分不应与官方 CDQ 混在一起，而应作为 **CDQ+ / Business Quality Score / Discoverability Score** 独立展示。

### 2.3 推荐系统中的分数结构

```text
最终系统输出三个分数：

1. CDQ Core Score / 100
   贴近官方目录质量分

2. Discoverability Opportunity Score / 20
   流量可发现性与类目机会分

3. Commercial Listing Quality Score / 120
   用于运营团队排序、修复和 KPI 管理
```

这样做的好处：

- 不混淆官方 CDQ 与你自己的运营增强模型；
- 方便向客户解释：“官方 CDQ 分是 82，但我们的商业机会分只有 9/20，所以这个 ASIN 仍然有很大流量修复空间”；
- 系统未来可以兼容亚马逊 2026 年可能推出的可发现性指标。

---

## 3. 系统总架构

### 3.1 总体架构图

```text
┌──────────────────────────────────────────────┐
│  数据接入层 Data Ingestion                    │
│  Seller Central / SP-API / Flat File / LQD     │
│  前台页面 / Apify / 图片 / A+ / 竞品 / 广告数据 │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  数据标准化层 Data Normalization              │
│  ASIN-SKU-PT-Marketplace 映射                 │
│  单位规范 / 枚举值规范 / 本地语言规范 / 去重     │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  商品事实层 Product Fact Graph                │
│  标题事实 / 图片事实 / 五点事实 / 后台属性事实   │
│  A+事实 / 变体事实 / 竞品事实 / 类目事实         │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  规则引擎 Rule Engine                         │
│  标题规则 / 图片规则 / 变体规则 / 类目规则       │
│  违禁词 / 受限声明 / 格式校验 / 严重缺陷判断     │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  AI 语义判断层 AI Quality Judge               │
│  正确性 / 一致性 / 规范化 / 本地化 / 冲突识别    │
│  LLM + 视觉模型 + OCR + RAG 规则库             │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  CDQ 打分引擎 Scoring Engine                  │
│  Gate → Component Score → Severity → Grade    │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  修复建议与任务系统 Action Engine             │
│  缺陷解释 / 修复字段 / 推荐值 / 批量模板 / SOP   │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  监控与闭环 Monitoring                        │
│  账号质量看板 / ASIN 优先级 / 修复 SLA / 复检    │
└──────────────────────────────────────────────┘
```

---

## 4. 数据输入设计

### 4.1 必须输入的数据

| 数据源 | 用途 | 获取方式 |
|---|---|---|
| ASIN / SKU / Marketplace | 主键 | 用户输入 / Seller Central |
| Product Type | 决定类目字段与属性权重 | SP-API / Flat File |
| Listing 标题 | 标题质量评分 | 前台抓取 / Catalog API |
| Bullet Points | 描述摘要评分 | 前台抓取 / Catalog API |
| Product Description | 非 CDQ 核心，但用于一致性判断 | 前台抓取 / Catalog API |
| A+ 是否存在 | A+ 质量评分 | 前台抓取 / A+ Content Manager |
| 图片数量与图片 URL | 图片质量评分 | 前台抓取 / Catalog API |
| 主图尺寸与像素 | 缩放与图片合规 | 图片解析 |
| 后台结构化属性 | 结构化属性评分 | Flat File / Catalog API |
| Parent-Child 变体关系 | 变体质量评分 | Flat File / Catalog API |
| 类目节点 Leaf Node | Discoverability 扩展分 | Browse Tree / Product Type |
| Search Terms | 可发现性机会分 | Flat File / 后台导出 |
| LQD / 商品信息质量报告 | 官方推荐修复项 | Seller Central 导出 |
| 30 天页面浏览量 / 销售额 | 修复优先级 | Business Reports |
| 广告消耗 / ACOS / CVR | 商业机会判断 | Ads API / 报表 |
| 竞品标题 / 属性 / 图片 / A+ | 标杆判断 | Apify / 前台抓取 |

---

### 4.2 商品事实图谱 Product Fact Graph

CDQ 的核心不是字段，而是 **事实**。

例如一个空气净化器 ASIN：

```json
{
  "asin": "B0XXXXXXX",
  "marketplace": "US",
  "product_type": "AIR_PURIFIER",
  "facts": {
    "brand": {
      "backend": "HYCHIKA",
      "title": "HYCHIKA",
      "image_ocr": null,
      "status": "consistent"
    },
    "coverage_area": {
      "backend": "1076 sq ft",
      "title": "1076 Sq Ft",
      "bullet": "Covers up to 1076 ft²",
      "image_ocr": "1076 sq ft",
      "status": "consistent"
    },
    "filter_type": {
      "backend": "HEPA",
      "title": "HEPA",
      "bullet": "H13 True HEPA",
      "image_vision": "filter cartridge",
      "status": "partially_consistent"
    }
  }
}
```

系统最终不是简单判断 “coverage_area 是否填写”，而是判断：

```text
coverage_area 是否存在？
coverage_area 是否真实？
coverage_area 单位是否标准？
coverage_area 在标题、五点、图片、A+ 中是否一致？
coverage_area 是否符合类目枚举与消费者理解？
coverage_area 是否存在夸大或违规风险？
```

---

## 5. 评分总模型

### 5.1 官方 CDQ Core Score

```text
CDQ_Core_100 =
0.30 * Structured_Attributes_Quality
+ 0.25 * Title_Quality
+ 0.20 * Variation_Quality
+ 0.15 * Image_Quality
+ 0.05 * Descriptive_Summary_Quality
+ 0.05 * APlus_Content_Quality
```

每个组件分数范围为 0-100。

### 5.2 业务增强分

```text
Discoverability_Opportunity_20 =
20 * (
  0.35 * Product_Type_Correctness
+ 0.25 * Leaf_Node_Correctness
+ 0.20 * Search_Term_Coverage
+ 0.10 * Filter_Attribute_Coverage
+ 0.10 * Keyword_Gap_Opportunity
)
```

### 5.3 商业化系统总分

```text
Commercial_CDQ_120 =
CDQ_Core_100 + Discoverability_Opportunity_20
```

### 5.4 官方等级映射

官方 CDQ 推荐用以下等级逻辑：

| 等级 | 分数 | 含义 | 系统动作 |
|---|---:|---|---|
| A | ≥85 | 高质量 | 保持监控 |
| B | 70-85 | 中等质量 / 有优化空间 | 建议优化 |
| C | 0-70 | 低质量 - 非严重缺陷 | 进入修复队列 |
| D | 0 | 低质量 - 严重缺陷 | 立即处理 |
| U | N/A | 低质量 - 政策违规 | 合规优先，暂停优化 |

### 5.5 商业增强等级

| 等级 | Commercial Score / 120 | 含义 |
|---|---:|---|
| A++ | 105-120 | 目录质量与可发现性极强 |
| A+ | 95-104 | 高质量 |
| A | 85-94 | 可销售，但仍有结构优化空间 |
| B | 70-84 | 明显优化空间 |
| C | 40-69 | 低质量，应排期修复 |
| D | 1-39 | 严重缺陷 |
| U | N/A | 政策违规或被抑制 |

---

## 6. Gate 机制：先判生死，再算分数

CDQ 系统必须先做 Gate 判断。

### 6.1 Policy Gate：政策违规

触发任一项，直接进入 U 级或合规修复队列：

| Gate | 示例 |
|---|---|
| Quarantined | 商品被隔离 |
| Is Not Search Indexed | 商品不被搜索索引 |
| Is Not Website Active | 前台不可售 / 不显示 |
| Title Policy Violation | 标题长度超限、冗余、受限词、特殊字符 |
| Restricted Claims | 医疗、杀菌、除螨、抗菌、杀虫等敏感声明 |
| Trademark Risk | 竞品品牌词、商标侵权词 |
| Misclassification | 故意错误分类规避限制 |
| Duplicate Detail Page | 重复创建详情页 |
| Main Image Violation | 主图水印、促销、非白底、文字、虚假配件 |

伪代码：

```python
def policy_gate(listing):
    if listing.quarantined:
        return "U", "ASIN is quarantined"
    if not listing.is_search_indexed:
        return "D", "ASIN is not search indexed"
    if not listing.is_website_active:
        return "D", "ASIN is not website active"
    if has_restricted_claims(listing.title, listing.bullets, listing.images_ocr):
        return "U", "Restricted claims detected"
    if title_policy_violation(listing.title):
        return "U", "Title policy violation"
    return "PASS", None
```

---

### 6.2 Critical Defect Gate：严重缺陷

不是所有低分都是同等级问题。严重缺陷应该优先处理。

官方 CDQ 逻辑中，严重缺陷包括：

| 严重缺陷 | 系统解释 |
|---|---|
| 大多数 Product Type 中前 6 项相关属性错误 | 核心事实错误 |
| Top 10 相关属性完整性 < 50% | 关键购买信息不足 |
| 变体严重缺陷 | 变体主题错误、子项重复、单位混用、变体误导 |
| 属性值与图片/标题冲突 | 可能误导买家 |
| 类目或 PT 明显错误 | 错误流量入口，广告与搜索匹配失真 |

伪代码：

```python
def critical_defect_gate(fact_graph, pt_schema):
    top6 = get_top_relevant_attributes(pt_schema, n=6)
    top10 = get_top_relevant_attributes(pt_schema, n=10)

    top6_wrong_ratio = count_wrong(fact_graph, top6) / len(top6)
    top10_complete_ratio = count_complete(fact_graph, top10) / len(top10)

    if top6_wrong_ratio >= 0.5:
        return "D", "Most Top 6 relevant attributes are incorrect"

    if top10_complete_ratio < 0.5:
        return "D", "Top 10 relevant attributes completeness < 50%"

    if has_critical_variation_defect(fact_graph):
        return "D", "Critical variation defect"

    return "PASS", None
```

---

## 7. 组件一：结构化属性质量 SAQ / 30%

### 7.1 结构化属性的核心思想

结构化属性不再只是后台字段，而是亚马逊用于以下系统的“商品事实燃料”：

- 搜索索引；
- 筛选栏；
- 推荐系统；
- 广告匹配；
- Rufus / Alexa for Shopping 问答；
- 详情页产品概述；
- Band A / Band B 深度信息组件；
- 退货和客户投诉风险判断。

### 7.2 评分对象

| 属性层级 | 含义 | 权重建议 |
|---|---|---:|
| Top 6 Relevant Attributes | 最核心购买决策属性 | 45% |
| Top 7-10 Relevant Attributes | 次核心属性 | 25% |
| Band A Attributes | 显性转化驱动属性 | 20% |
| Band B Attributes | 筛选、推荐、体验增强属性 | 10% |

### 7.3 单个属性评分公式

```text
Attribute_Score_i =
Weight_i
* Completeness_i
* Correctness_i
* Consistency_i
* Normalization_i
* Confidence_i
```

各因子：

| 因子 | 范围 | 说明 |
|---|---:|---|
| Completeness | 0 / 0.5 / 1 | 是否填写；是否填了有效信息 |
| Correctness | 0-1 | 是否真实、符合实物、符合类目 |
| Consistency | 0-1 | 与标题、图片、五点、A+、变体是否一致 |
| Normalization | 0-1 | 单位、枚举、大小写、本地语言是否规范 |
| Confidence | 0.6-1 | AI 判断置信度，低置信度进入人工审核 |

最终：

```text
SAQ = 100 * Σ(Attribute_Score_i) / Σ(Attribute_Weight_i)
```

### 7.4 完整性判断

| 状态 | 分值 | 判断 |
|---|---:|---|
| 有明确有效值 | 1 | `material = Stainless Steel` |
| 有值但弱有效 | 0.5 | `material = Other` |
| 空值 / 无意义空格 / N/A 不允许 | 0 | `material = " "` |
| 字段不适用于该 PT | 不计入分母 | Battery 属性对非电池商品 |

> 重要判断：你之前 Skill 中提到“空值填空格”在旧 IDQ 时代可能有提高完整度的经验价值，但 CDQ 时代必须谨慎。  
> 系统不能默认推荐“填空格”作为修复方式。  
> 正确策略是：  
> 1. 如果属性不适用，优先判断是否能合法标记 Not Applicable；  
> 2. 如果是可枚举字段，必须使用类目允许值；  
> 3. 如果是自由文本字段，必须填真实且相关的信息；  
> 4. 无意义空格只作为“历史兼容观察项”，不能作为 CDQ 正式修复建议。

### 7.5 正确性判断

正确性优先级高于完整性。

| 错误类型 | 示例 | 严重程度 |
|---|---|---|
| 实物错误 | backend 写 Metal，图片显示 Plastic | 高 |
| 单位错误 | 10 inch 写成 10 cm | 高 |
| 枚举错误 | HEPA 填入 Color 字段 | 高 |
| 本地化错误 | 德国站属性值用英文且非标准枚举 | 中 |
| 夸大属性 | 覆盖面积、功率、认证夸大 | 高 |
| 与变体冲突 | 子体颜色是 Red，标题写 Blue | 高 |

### 7.6 一致性判断矩阵

| 字段 | 标题 | 五点 | 图片 OCR | 图片视觉 | A+ | 后台属性 | 变体属性 |
|---|---|---|---|---|---|---|---|
| Brand | ✓ | 可选 | 可选 | - | 可选 | ✓ | ✓ |
| Color | ✓ | 可选 | 可选 | ✓ | 可选 | ✓ | ✓ |
| Size | ✓ | ✓ | ✓ | 可选 | ✓ | ✓ | ✓ |
| Material | ✓ | ✓ | 可选 | 可选 | ✓ | ✓ | 可选 |
| Capacity | ✓ | ✓ | ✓ | - | ✓ | ✓ | ✓ |
| Voltage | 可选 | ✓ | ✓ | - | ✓ | ✓ | 可选 |
| Compatible Model | ✓ | ✓ | 可选 | - | ✓ | ✓ | ✓ |

一致性得分：

```text
Consistency_i =
1 - Conflict_Count_i / Evidence_Source_Count_i
```

但如果冲突发生在核心属性上，例如尺寸、材质、容量、电压，则应提高惩罚。

---

## 8. 组件二：标题质量 TQ / 25%

### 8.1 标题评分逻辑

标题质量采用 TQS 思路：

```text
Title_Quality =
Policy_Pass
* (
  0.25 * Title_Completeness
+ 0.20 * Title_Correctness
+ 0.15 * Length_Score
+ 0.10 * Casing_Score
+ 0.10 * Redundancy_Score
+ 0.10 * Keyword_Tagging_Score
+ 0.10 * Readability_Score
)
```

如果 Policy_Pass = 0，则 Title Quality = 0，甚至触发 U 级。

### 8.2 标题 A / B / C 三级判断

| 等级 | 条件 | 分数 |
|---|---|---:|
| A | 完整性 ≥0.6；无冗余；≤200 字符；大小写合规；无不可读字符；无限制短语 | 100 |
| B | 未违规，但至少一个维度未达高质量 | 50-99 |
| C | 标题完整性 <0.4；冗余严重；>200；存在受限短语 | 0 / U |

### 8.3 标题规则库

| 规则 | 说明 |
|---|---|
| 长度 | 不超过 200 字符；移动端建议 80-160 字符 |
| 品牌 | 建议以品牌名开头，且与 Brand 字段一致 |
| 结构 | 品牌 + 核心产品名 + 核心属性 + 场景 / 规格 |
| 大小写 | 不要全大写；英文每个主要单词首字母大写 |
| 数字 | 使用阿拉伯数字 |
| 特殊字符 | 避免 `! $ ? _ { } ^ ¬ ¦` 等 |
| 促销语 | 不写 Free Shipping、Best Seller、100% Quality Guaranteed |
| 重复词 | 同一语境下不要重复超过 2 次 |
| 主观词 | 避免 Hot Item、Best、Cheapest |
| 侵权词 | 不使用竞品品牌、商标、平台词 |
| 受限声明 | 谨慎使用 sanitize、antibacterial、anti-mites、sterilize、pesticide 等 |

### 8.4 标题语义完整性

标题不是越长越好，而是必须覆盖 “买家快速判断购买所需的核心事实”。

不同类目标题事实不同：

| 类目 | 必须覆盖的标题事实 |
|---|---|
| 空气净化器 | 品牌、产品词、覆盖面积、过滤类型、适用场景 |
| 布艺清洗机 | 品牌、产品词、功率、吸力、功能模式、适用对象 |
| 发夹 | 品牌、产品词、数量、材质、颜色、适用人群 |
| 电子产品 | 品牌、型号、规格、兼容性、容量 / 尺寸 |
| 服装 | 品牌、品类、性别、材质、款式、颜色 / 尺码 |

标题完整性公式：

```text
Title_Completeness =
Matched_Title_Facts / Required_Title_Facts_By_PT
```

例如布艺清洗机：

```text
Required_Title_Facts = [
  brand,
  product_type,
  power,
  suction,
  cleaning_mode,
  target_surface
]
```

如果标题只包含品牌、产品词、功率，则：

```text
Title_Completeness = 3/6 = 0.5
```

---

## 9. 组件三：变体质量 VQ / 20%

### 9.1 变体为什么重要

变体质量是 CDQ 相比 IDQ 的重要新增方向。

变体错误会直接造成：

- 买家选错规格；
- 评论聚合污染；
- 颜色 / 尺寸 / 套装误导；
- 父体下不同商品混挂；
- 广告和搜索权重错误合并；
- 退货率上升；
- ASIN 被拆分或抑制。

### 9.2 变体评分对象

| 对象 | 检查内容 |
|---|---|
| Parent ASIN | 是否存在合理父体 |
| Child ASIN | 子体是否真实属于同一商品族 |
| Variation Theme | 主题是否正确，如 Color、Size、Style |
| Theme Attributes | 子体主题属性是否完整、正确、一致 |
| Duplicate Child | 是否存在重复子体 |
| Localized Value | 不同站点属性值是否本地化 |
| Unit System | 是否存在 inch/cm、oz/ml 混用 |
| Redundant Info | 子体标题是否堆砌无关变体信息 |

### 9.3 变体严重缺陷

| 严重缺陷 | 示例 | 动作 |
|---|---|---|
| 错误属性值 | 子体 color_name=Blue，图片为 Red | 立即修复 |
| 单位制混用 | 同一变体家族中 cm 与 inch 无标准化 | 立即修复 |
| 变体信息冗余 | 标题重复堆砌所有颜色 | 修复 |
| 本地化错误 | 德国站 Color 填 “Dark Gray” 而非规范值 | 修复 |
| 子项重复 | 两个子体实际同款同色同尺寸 | 合并 / 删除 |
| 主题错误 | 应该用 Size，却用 Color | 重建变体 |

### 9.4 变体评分公式

```text
Variation_Quality =
100
- Critical_Defect_Penalty
- NonCritical_Defect_Penalty
```

建议惩罚：

| 缺陷 | 惩罚 |
|---|---:|
| 错误主题 | -40 |
| 子体重复 | -30 |
| 核心主题属性错误 | -30 |
| 单位混用 | -20 |
| 本地化错误 | -15 |
| 未标准化值 | -10 |
| 格式不匹配 | -5 |

如果出现多个严重缺陷，最低可归零，并触发 D 级。

---

## 10. 组件四：图片质量 IQ / 15%

### 10.1 图片评分公式

```text
Image_Quality =
0.25 * Image_Count_Score
+ 0.25 * Main_Image_Compliance
+ 0.20 * Zoom_and_Technical_Score
+ 0.15 * Image_Information_Completeness
+ 0.10 * Image_Attribute_Consistency
+ 0.05 * Image_Alt_Tag_Score
```

### 10.2 图片核心规则

| 检查项 | 满分要求 |
|---|---|
| 图片数量 | ≥4 张 |
| 主图背景 | 纯白背景 RGB 255,255,255 |
| 主图产品占比 | 约 85% 以上 |
| 主图内容 | 只展示销售商品，不加文字、水印、促销、边框 |
| 缩放 | 最长边建议 ≥1600 px，且不超过 10000 px |
| 格式 | JPEG 优先；TIFF / GIF 等按平台要求 |
| 清晰度 | 不模糊、不像素化 |
| 一致性 | 图片中的颜色、尺寸、套装、配件与标题/属性一致 |
| 信息完整 | 主图、场景图、功能图、尺寸图、卖点图、对比图覆盖购买决策 |

### 10.3 AI 视觉判断

系统需要做图片解析：

```text
图片 → CV 模型 → 识别商品主体、颜色、材质、配件、场景
图片 → OCR → 识别图中文字、参数、认证、违禁词
图片 → 质量模型 → 判断白底、占比、清晰度、像素、是否水印
图片 → 属性一致性模型 → 与后台属性、标题、五点对比
```

输出示例：

```json
{
  "image_id": "MAIN",
  "defects": [
    {
      "type": "main_image_text_overlay",
      "severity": "critical",
      "evidence": "OCR detected '50% OFF'"
    },
    {
      "type": "color_inconsistency",
      "severity": "major",
      "evidence": "Backend color=Black, visual color=White"
    }
  ],
  "score": 62
}
```

---

## 11. 组件五：Bullet / 描述性摘要 DSQ / 5%

### 11.1 官方核心规则

```text
≥3 个 Bullet = 100
≥1 个 Bullet = 50
0 个 Bullet = 0
```

### 11.2 系统增强判断

虽然官方 CDQ 对 Bullet 的打分较简单，但你的系统应该额外判断：

| 维度 | 判断 |
|---|---|
| 数量 | 是否 ≥3，建议 5 条 |
| 禁词 | 是否包含受限声明或违规词 |
| 事实完整 | 是否覆盖核心功能、规格、场景、差异点 |
| 0-1-3 原则 | 0 个基础功能遗漏；1 个主卖点；3 个魅力卖点 |
| 可读性 | 是否过长、堆砌、翻译腔 |
| 一致性 | 是否与后台属性、图片、A+ 冲突 |
| 关键词覆盖 | 是否自然覆盖核心词根 |

### 11.3 Bullet 质量增强分

不改变官方 5 分，但可以做 “Content Optimization Score”。

```text
Bullet_Optimization_Score =
0.25 * Coverage
+ 0.20 * Clarity
+ 0.20 * Conversion_Power
+ 0.15 * Keyword_Naturalness
+ 0.10 * Compliance
+ 0.10 * Consistency
```

---

## 12. 组件六：A+ 内容 APQ / 5%

### 12.1 官方核心规则

```text
Has A+ Content = 100
No A+ Content = 0
```

### 12.2 系统增强判断

A+ 不只是有无，而是商品事实补充层。

| 维度 | 判断 |
|---|---|
| 是否存在 | 是否有 A+ |
| 是否覆盖关键属性 | 参数、尺寸、功能、场景 |
| 是否与标题/五点一致 | 不冲突 |
| 是否补充详情页缺失信息 | 产品概述、深度信息 |
| 图片 alt 是否埋词 | 关键词、属性、场景 |
| 是否有对比表 | 适合多 SKU / 多型号 |
| 是否存在禁词 | 医疗、绝对化、促销、保修等风险 |

A+ 质量增强分可作为运营建议，不直接覆盖官方 5 分。

---

## 13. 扩展组件：产品类型与可发现性 DTS / 20%

> 这是你系统的商业增强模块，不建议称为“官方 CDQ 权重”。

### 13.1 为什么要保留这 20 分

即使官方 CDQ 当前将 Leaf Node / Keywords 从核心计分中移除，类目和关键词仍然决定：

- 是否进入正确 BSR 赛道；
- 是否触发正确属性模板；
- 是否出现在筛选栏；
- 广告相关性是否正常；
- Search Query Performance 机会是否能承接；
- Rufus / Alexa 能否理解商品身份。

### 13.2 评分公式

```text
Discoverability_20 =
20 * (
  0.35 * Product_Type_Correctness
+ 0.25 * Leaf_Node_Correctness
+ 0.20 * Backend_Search_Term_Coverage
+ 0.10 * Filter_Attribute_Coverage
+ 0.10 * Search_Keyword_Gap_Opportunity
)
```

### 13.3 关键判断

| 项目 | 判断 |
|---|---|
| Product Type | 是否与商品本质一致 |
| Leaf Node | 是否是最细、最相关、竞争合理的节点 |
| Browse Path | 是否进入正确类目流量 |
| Search Terms | 是否覆盖核心词根、同义词、场景词 |
| Filter Attributes | 是否覆盖买家筛选条件 |
| Keyword Gap | 高搜索量相关词是否未被标题/属性/图片/A+承接 |

---

## 14. AI / LLM 在 CDQ 中的角色

### 14.1 AI 不应该替代规则，而应该增强判断

系统应采用：

```text
确定性规则引擎 + LLM 语义判断 + 视觉模型 + RAG 规则库
```

分工：

| 能力 | 最适合的技术 |
|---|---|
| 字符数、图片数量、字段缺失 | 规则引擎 |
| 违禁词、特殊字符 | 规则引擎 + 词库 |
| 标题是否自然 | LLM |
| 属性是否矛盾 | LLM + 商品事实图谱 |
| 图片是否白底 / 占比 | CV 模型 |
| 图片文字是否违规 | OCR + 规则 |
| 本地化表达是否自然 | LLM |
| 变体是否合理 | 图结构规则 + LLM |
| 类目是否正确 | PT 规则 + 竞品聚类 + LLM |

### 14.2 LLM 判断必须带证据

LLM 输出不能直接给分，必须输出证据：

```json
{
  "attribute": "material",
  "backend_value": "Plastic",
  "evidence": {
    "title": "Stainless Steel Coffee Grinder",
    "bullet": "Made of stainless steel",
    "image_vision": "metallic surface"
  },
  "judgement": "inconsistent",
  "confidence": 0.87,
  "recommended_action": "Change material to Stainless Steel if product facts are verified."
}
```

### 14.3 置信度策略

| 置信度 | 动作 |
|---:|---|
| ≥0.85 | 自动生成修复建议 |
| 0.65-0.85 | 标记人工确认 |
| <0.65 | 不扣重分，进入待验证 |
| 规则命中违规 | 不受置信度影响，直接触发风险 |

---

## 15. 缺陷分类体系

### 15.1 缺陷等级

| 等级 | 含义 | 示例 | SLA |
|---|---|---|---|
| P0 | 政策违规 / 被抑制 | 标题违规、禁词、前台不可见 | 当天 |
| P1 | 严重目录缺陷 | Top6 属性错误、变体严重缺陷 | 1-2 天 |
| P2 | 中度质量缺陷 | 图片不足、A+缺失、Top10属性缺失 | 3-7 天 |
| P3 | 优化机会 | 标题可读性、关键词覆盖不足 | 7-14 天 |
| P4 | 观察项 | 低流量 ASIN 小问题 | 月度 |

### 15.2 缺陷对象

| 对象 | 缺陷示例 |
|---|---|
| ASIN | 标题过长、图片不足、A+缺失 |
| SKU | 后台属性缺失 |
| Parent | 变体主题错误 |
| Child | 子体属性错误 |
| Marketplace | 本地化错误 |
| Product Type | PT 不匹配 |
| Brand | 品牌不一致 |
| Image | 主图违规 |
| Attribute | 值缺失 / 错误 / 不规范 |

---

## 16. 修复优先级算法

CDQ 系统不能只按分数排序。一个低销量 ASIN 的 50 分，不一定比主推 ASIN 的 78 分更紧急。

### 16.1 影响优先级公式

```text
Repair_Priority =
Severity_Weight
* Traffic_Weight
* Revenue_Weight
* Conversion_Impact
* Confidence
* Fix_Ease
```

建议：

```text
Severity_Weight:
P0 = 10
P1 = 7
P2 = 4
P3 = 2
P4 = 1

Traffic_Weight = log(30_day_pageviews + 1)
Revenue_Weight = log(30_day_sales + 1)
Fix_Ease:
一键修复 = 1.2
需素材 = 0.8
需改变体 = 0.6
需合规审核 = 0.4
```

### 16.2 修复排序示例

| ASIN | CDQ | 缺陷 | 30天PV | 30天销售额 | 优先级 |
|---|---:|---|---:|---:|---:|
| A | 78 | A+ 缺失 | 30,000 | 80,000 | 高 |
| B | 55 | 图片不足 | 500 | 900 | 中 |
| C | 82 | 标题违规风险 | 15,000 | 50,000 | 最高 |
| D | 40 | 属性缺失 | 100 | 0 | 低 |

---

## 17. 数据库设计

### 17.1 核心表

```sql
-- ASIN 主表
CREATE TABLE asin_master (
  id BIGSERIAL PRIMARY KEY,
  asin VARCHAR(20),
  sku VARCHAR(100),
  marketplace VARCHAR(20),
  brand VARCHAR(255),
  product_type VARCHAR(255),
  leaf_node_id VARCHAR(100),
  parent_asin VARCHAR(20),
  status VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Listing 文本快照
CREATE TABLE listing_text_snapshot (
  id BIGSERIAL PRIMARY KEY,
  asin VARCHAR(20),
  marketplace VARCHAR(20),
  title TEXT,
  bullets JSONB,
  description TEXT,
  search_terms TEXT,
  snapshot_at TIMESTAMP
);

-- 后台属性表
CREATE TABLE backend_attributes (
  id BIGSERIAL PRIMARY KEY,
  asin VARCHAR(20),
  marketplace VARCHAR(20),
  attribute_name VARCHAR(255),
  attribute_value TEXT,
  unit VARCHAR(50),
  source VARCHAR(50),
  normalized_value TEXT,
  is_applicable BOOLEAN,
  snapshot_at TIMESTAMP
);

-- PT 属性规则表
CREATE TABLE pt_attribute_schema (
  id BIGSERIAL PRIMARY KEY,
  marketplace VARCHAR(20),
  product_type VARCHAR(255),
  attribute_name VARCHAR(255),
  required_level VARCHAR(50), -- required/recommended/optional
  relevance_rank INT,
  band VARCHAR(20), -- top6/top10/band_a/band_b
  allowed_values JSONB,
  unit_rules JSONB,
  weight NUMERIC
);

-- 图片表
CREATE TABLE listing_images (
  id BIGSERIAL PRIMARY KEY,
  asin VARCHAR(20),
  marketplace VARCHAR(20),
  image_url TEXT,
  image_type VARCHAR(50), -- main/secondary/a_plus
  width INT,
  height INT,
  format VARCHAR(20),
  has_zoom BOOLEAN,
  ocr_text TEXT,
  vision_tags JSONB,
  defects JSONB,
  snapshot_at TIMESTAMP
);

-- 变体关系表
CREATE TABLE variation_family (
  id BIGSERIAL PRIMARY KEY,
  parent_asin VARCHAR(20),
  child_asin VARCHAR(20),
  marketplace VARCHAR(20),
  variation_theme VARCHAR(100),
  theme_attributes JSONB,
  normalized_theme_attributes JSONB,
  defects JSONB,
  snapshot_at TIMESTAMP
);

-- CDQ 分数快照
CREATE TABLE cdq_score_snapshot (
  id BIGSERIAL PRIMARY KEY,
  asin VARCHAR(20),
  marketplace VARCHAR(20),
  cdq_core_score NUMERIC,
  discoverability_score NUMERIC,
  commercial_score NUMERIC,
  grade VARCHAR(10),
  title_score NUMERIC,
  structured_attribute_score NUMERIC,
  variation_score NUMERIC,
  image_score NUMERIC,
  bullet_score NUMERIC,
  aplus_score NUMERIC,
  policy_gate_status VARCHAR(50),
  critical_gate_status VARCHAR(50),
  confidence NUMERIC,
  scored_at TIMESTAMP
);

-- 缺陷表
CREATE TABLE catalog_defects (
  id BIGSERIAL PRIMARY KEY,
  asin VARCHAR(20),
  sku VARCHAR(100),
  marketplace VARCHAR(20),
  component VARCHAR(100),
  defect_type VARCHAR(100),
  severity VARCHAR(20),
  evidence JSONB,
  merchant_action TEXT,
  recommended_value TEXT,
  status VARCHAR(50), -- pending/done/no_action/benchmark
  priority_score NUMERIC,
  created_at TIMESTAMP,
  resolved_at TIMESTAMP
);
```

---

## 18. 打分引擎伪代码

```python
def score_asin(asin, marketplace):
    listing = load_listing(asin, marketplace)
    pt_schema = load_pt_schema(listing.product_type, marketplace)
    fact_graph = build_fact_graph(listing)

    # Step 1: Policy Gate
    gate_status, gate_reason = policy_gate(listing)
    if gate_status == "U":
        return ScoreResult(
            asin=asin,
            grade="U",
            cdq_core_score=None,
            reason=gate_reason
        )

    # Step 2: Critical Defect Gate
    critical_status, critical_reason = critical_defect_gate(fact_graph, pt_schema)

    # Step 3: Component Scores
    saq = score_structured_attributes(fact_graph, pt_schema)
    tq = score_title(listing.title, fact_graph, pt_schema)
    vq = score_variation_quality(listing.variation_family, fact_graph)
    iq = score_image_quality(listing.images, fact_graph)
    dsq = score_bullets(listing.bullets)
    apq = score_aplus(listing.aplus)

    cdq_core = (
        0.30 * saq
        + 0.25 * tq
        + 0.20 * vq
        + 0.15 * iq
        + 0.05 * dsq
        + 0.05 * apq
    )

    discoverability = score_discoverability(listing, pt_schema, fact_graph)
    commercial = cdq_core + discoverability

    # Step 4: Grade
    if critical_status == "D":
        grade = "D"
        cdq_core = min(cdq_core, 49)
    elif cdq_core >= 85:
        grade = "A"
    elif cdq_core >= 70:
        grade = "B"
    else:
        grade = "C"

    # Step 5: Defects and Actions
    defects = detect_defects(
        listing=listing,
        fact_graph=fact_graph,
        pt_schema=pt_schema,
        component_scores={
            "SAQ": saq,
            "TQ": tq,
            "VQ": vq,
            "IQ": iq,
            "DSQ": dsq,
            "APQ": apq
        }
    )

    actions = generate_merchant_actions(defects)

    return ScoreResult(
        asin=asin,
        grade=grade,
        cdq_core_score=cdq_core,
        discoverability_score=discoverability,
        commercial_score=commercial,
        component_scores={
            "structured_attributes": saq,
            "title": tq,
            "variation": vq,
            "image": iq,
            "bullets": dsq,
            "aplus": apq
        },
        defects=defects,
        actions=actions
    )
```

---

## 19. LLM Prompt 设计

### 19.1 属性正确性判断 Prompt

```text
你是亚马逊 CDQ 目录数据质量审核专家。
请判断给定 ASIN 的属性值是否完整、正确、一致、规范。

输入：
- marketplace
- product_type
- attribute_name
- backend_attribute_value
- title
- bullet_points
- description
- image_ocr_text
- image_vision_tags
- aplus_text
- variation_theme
- allowed_values
- unit_rules

输出 JSON：
{
  "attribute_name": "",
  "completeness": 0-1,
  "correctness": 0-1,
  "consistency": 0-1,
  "normalization": 0-1,
  "confidence": 0-1,
  "judgement": "pass / warning / defect / critical_defect",
  "evidence": [],
  "recommended_value": "",
  "merchant_action": ""
}

要求：
1. 只能基于输入证据判断，不得编造商品事实。
2. 如果证据不足，输出 need_human_review。
3. 如果发现医疗、杀菌、除螨、抗菌、杀虫、绝对化宣传等风险，需要标记 policy_risk。
4. 需要说明具体冲突来源。
```

### 19.2 标题质量判断 Prompt

```text
请按亚马逊 CDQ / TQS 逻辑审核标题质量。

检查：
1. 是否超过 200 字符
2. 是否以品牌开头
3. 是否包含至少 3 个关键商品属性
4. 是否有重复词堆砌
5. 是否包含受限短语
6. 是否有不可读特殊字符
7. 大小写是否规范
8. 是否准确表达商品，不误导买家
9. 移动端可读性如何

输出：
{
  "title_quality_score": 0-100,
  "title_grade": "A/B/C",
  "policy_violation": true/false,
  "defects": [],
  "rewrite_suggestion": "",
  "confidence": 0-1
}
```

---

## 20. 账号级质量监控

### 20.1 账号质量不是平均分

不能只看所有 ASIN 的平均 CDQ。

应该看：

```text
账号 CDQ Health =
销售额加权 CDQ
+ 页面浏览量加权 CDQ
+ 严重缺陷数量
+ U/D ASIN 占比
+ 主推 ASIN 修复完成率
+ 缺陷老化时间
```

### 20.2 账号看板指标

| 指标 | 含义 |
|---|---|
| CDQ Core Avg | 全账号平均 CDQ |
| Weighted CDQ by Sales | 按销售额加权 |
| Weighted CDQ by PV | 按页面浏览量加权 |
| A 级 ASIN 占比 | 高质量商品比例 |
| U/D ASIN 数量 | 合规与严重缺陷 |
| Top10 属性完整率 | 核心属性覆盖情况 |
| Top6 属性错误率 | 核心事实错误率 |
| 变体缺陷率 | Parent-Child 健康度 |
| 图片合规率 | 主图、数量、缩放、质量 |
| A+ 覆盖率 | A+ 内容覆盖 |
| Bullet ≥3 覆盖率 | 描述摘要基础质量 |
| 缺陷修复 SLA | P0/P1/P2 处理时效 |
| 修复后复检通过率 | 闭环效果 |

### 20.3 账号风险分

```text
Account_Risk =
0.30 * U_D_ASIN_Ratio
+ 0.20 * Weighted_Core_Defect_Ratio
+ 0.20 * Variation_Defect_Ratio
+ 0.15 * Policy_Risk_Ratio
+ 0.15 * Defect_Aging_Ratio
```

---

## 21. 修复建议生成逻辑

### 21.1 缺陷到动作映射

| Catalog Defect | Merchant Action |
|---|---|
| Missing A+ | Add A+ |
| Website images <4 | Upload at least 4 website images |
| Main image no zoom | Upload image ≥1600 px on longest side |
| Title length >200 | Rewrite title under 200 characters |
| Title redundancy | Remove repeated terms |
| Restricted phrase in title | Remove restricted phrase |
| Relevant attributes ranked 5-10 incomplete | Fill missing relevant attributes |
| Top 10 relevant attributes not identified | Assign eligible PT and fill relevant attributes 1-10 |
| Variation theme incorrect | Rebuild variation family |
| Duplicate child ASIN | Remove or merge duplicate child |
| Unit mismatch | Normalize unit |
| Localized value incorrect | Replace with marketplace-native allowed value |

### 21.2 输出格式

每个 ASIN 输出：

```markdown
## ASIN: B0XXXXXXX

### 总分
- CDQ Core: 76 / 100
- Discoverability: 12 / 20
- Commercial Score: 88 / 120
- Grade: B

### 主要缺陷
1. 结构化属性 Top10 缺失：maximum_current, item_weight
2. 图片数量不足：当前 3 张，建议 ≥4 张
3. A+ 缺失
4. 标题存在重复词：air purifier 出现 4 次

### 修复优先级
P1：补齐 Top10 属性  
P2：上传第 4 张图片并满足缩放  
P2：创建 A+  
P3：优化标题可读性

### 推荐动作
- 在后台 Product Detail 字段补齐 item_weight、maximum_current
- 上传 1600px 以上尺寸图
- 创建 A+ 模块：场景、功能、参数、对比表
- 标题改写为：...
```

---

## 22. 从系统产品角度拆成 6 个模块

### 22.1 模块一：ASIN 数据采集器

能力：

- 输入 ASIN / SKU / Marketplace；
- 拉取前台 Listing；
- 拉取后台属性；
- 拉取图片；
- 拉取 A+；
- 拉取变体关系；
- 拉取 LQD 报告；
- 拉取业务数据。

### 22.2 模块二：CDQ 规则库

规则类型：

| 规则类型 | 示例 |
|---|---|
| Global Rule | 标题不超过 200 字符 |
| Marketplace Rule | 德国站本地化表达 |
| PT Rule | AIR_PURIFIER 必须有 filter_type |
| Image Rule | 主图白底、85% 占比 |
| Claim Rule | 消毒、抗菌、杀虫敏感声明 |
| Variation Rule | 颜色变体必须 color_name 一致 |
| Unit Rule | inch / cm / oz / ml 规范 |
| Brand Rule | 标题品牌与品牌字段一致 |

### 22.3 模块三：商品事实图谱

核心是把分散内容统一成可判断事实：

```text
Title Fact
Bullet Fact
Image Fact
A+ Fact
Backend Attribute Fact
Variation Fact
Competitor Fact
```

### 22.4 模块四：AI 审核器

包括：

- 标题质量审核；
- 属性正确性审核；
- 变体合理性审核；
- 图片文字风险审核；
- A+ 内容一致性审核；
- 本地化表达审核；
- 竞品标杆对比。

### 22.5 模块五：评分与任务引擎

输出：

- 分数；
- 等级；
- 缺陷；
- 优先级；
- 负责人；
- 截止时间；
- 修复建议；
- 批量模板。

### 22.6 模块六：复检闭环

流程：

```text
生成修复建议
  ↓
运营确认
  ↓
批量修改 / 上传
  ↓
等待亚马逊处理
  ↓
再次抓取
  ↓
重新评分
  ↓
记录前后变化
```

---

## 23. MVP 开发范围

### 23.1 第一阶段：7 天可做 MVP

只做最核心的 6 个组件：

| 功能 | 是否做 |
|---|---|
| 标题评分 | 做 |
| Bullet 数量 | 做 |
| 图片数量 / 主图像素 | 做 |
| A+ 有无 | 做 |
| 后台属性 Top10 完整性 | 做 |
| 变体基础检查 | 做 |
| LLM 正确性判断 | 简版 |
| 账号看板 | 简版 |
| 批量修复模板 | 简版 |

输入：Excel / Flat File / 前台抓取数据  
输出：HTML + Markdown + Excel 修复表

### 23.2 第二阶段：30 天产品化

新增：

- PT schema 自动匹配；
- Top6 / Top10 / Band A/B 属性库；
- 图片 OCR + Vision；
- 变体图谱；
- LLM 语义一致性；
- 缺陷任务系统；
- 修复优先级；
- 多站点本地化；
- 竞品标杆库。

### 23.3 第三阶段：SaaS 化

新增：

- SP-API 接入；
- Ads API 接入；
- 定时任务；
- 多账号管理；
- 用户权限；
- 团队协作；
- 一键导出 Flat File 修复模板；
- 复检与效果归因；
- 商业机会预测。

---

## 24. 系统输出文件设计

### 24.1 账号总览报告

```markdown
# CDQ Account Health Report

## 账号概览
- ASIN 数量：
- A 级 ASIN：
- U/D 风险 ASIN：
- 销售额加权 CDQ：
- 最高优先级修复项：

## 组件健康度
| 组件 | 平均分 | 风险 ASIN 数 | 主要问题 |
|---|---:|---:|---|
| 标题 | 82 | 10 | 冗余、长度、品牌不一致 |
| 属性 | 69 | 38 | Top10 缺失、单位不规范 |
| 图片 | 74 | 22 | 图片不足、无缩放 |
| 变体 | 88 | 5 | 主题属性不一致 |
```

### 24.2 ASIN 明细报告

```markdown
# ASIN CDQ Detail

## 基础信息
- ASIN:
- SKU:
- Marketplace:
- Product Type:
- Parent ASIN:
- Leaf Node:

## 分数
| 组件 | 分数 | 权重 | 加权得分 |
|---|---:|---:|---:|
| 结构化属性 | 72 | 30% | 21.6 |
| 标题 | 90 | 25% | 22.5 |
| 变体 | 100 | 20% | 20 |
| 图片 | 60 | 15% | 9 |
| Bullet | 100 | 5% | 5 |
| A+ | 0 | 5% | 0 |

## 缺陷清单
| 优先级 | 组件 | 缺陷 | 证据 | 修复动作 |
|---|---|---|---|---|
```

### 24.3 批量修复 Excel 字段

| 字段 | 说明 |
|---|---|
| status | 商品状态 |
| sku | SKU |
| asin | ASIN |
| marketplace | 站点 |
| product_type | PT |
| component | 组件 |
| catalog_defect | 缺陷 |
| missing_or_invalid_attribute | 缺失 / 错误字段 |
| current_value | 当前值 |
| recommended_value | 推荐值 |
| evidence | 证据 |
| merchant_action | 操作建议 |
| priority | 优先级 |
| owner | 负责人 |
| todo_status | Pending / Done / Benchmark / No Action |
| reviewed_by_human | 是否人工确认 |

---

## 25. 高度思考：CDQ 系统的真正价值

### 25.1 CDQ 不是 Listing 美化工具，而是商品数据基础设施

过去运营优化 Listing，通常关注：

- 标题有没有埋词；
- 图片好不好看；
- 五点有没有卖点；
- A+ 是否漂亮。

但 CDQ 的底层逻辑更像：

> 商品事实是否可被亚马逊机器系统信任。

一个高 CDQ 的 Listing，本质上是在同时服务四类对象：

| 对象 | 它需要什么 |
|---|---|
| 买家 | 看得懂、相信、能决策 |
| 亚马逊搜索 | 能识别产品是什么 |
| 亚马逊推荐 / AI | 能建立商品语义画像 |
| 亚马逊风控 | 不违规、不误导、不制造差体验 |

### 25.2 正确性将压过完整性

你之前 Skill 中有一个非常重要的经验：“属性尽量填全”。

但 CDQ 时代必须升级为：

```text
第一优先级：正确
第二优先级：一致
第三优先级：规范
第四优先级：完整
第五优先级：关键词覆盖
```

原因是：

- 错误属性会伤害转化率；
- 冲突属性会降低系统信任；
- 不规范属性无法进入筛选 / 推荐；
- 虚假完整可能触发更大风险。

### 25.3 变体质量会成为精品运营的隐形分水岭

精品团队常见问题：

- 把不同功能产品合并成变体；
- 颜色 / 尺寸字段随便填；
- 子体标题不规范；
- 父体下混入配件或套装；
- 德国、法国、西班牙站点翻译不一致。

这些问题旧 IDQ 很难发现，但 CDQ 会越来越重视。

### 25.4 AI 会让“伪优化”越来越失效

传统 SEO 式堆词可能短期有效，但 LLM 参与后，系统更看重语义一致性。

例如：

```text
标题：Portable Steam Cleaner
五点：hot water cleaner
后台属性：vacuum cleaner
图片：carpet extractor
A+：upholstery cleaner
```

过去可能只是关键词多。  
现在 AI 可能判断：商品身份混乱。

所以未来 Listing 优化不是“把词塞满”，而是：

> 构建一个稳定、清晰、一致、可验证的商品语义画像。

---

## 26. 开发优先级建议

### P0：必须先做

1. CDQ Core 100 打分；
2. 标题 TQS 规则；
3. Top10 属性完整性；
4. A+ / Bullet / 图片数量；
5. 主图尺寸与缩放；
6. 变体基础一致性；
7. 缺陷清单；
8. 修复建议；
9. Markdown / Excel 输出。

### P1：增强竞争力

1. 商品事实图谱；
2. LLM 正确性判断；
3. 图片 OCR / Vision；
4. 属性冲突检测；
5. Product Type / Leaf Node 机会分；
6. 修复优先级；
7. 账号健康看板；
8. 多站点本地化。

### P2：商业化壁垒

1. 竞品标杆对比；
2. 关键词 Gap；
3. 广告浪费与 CDQ 关联；
4. Rufus / Alexa 问答可回答性；
5. Listing 修改后效果归因；
6. 批量 Feed 自动生成；
7. SOP 任务流；
8. SaaS 多账号权限。

---

## 27. 最终推荐算法版本

### 27.1 系统主公式

```text
CDQ_Core_100 =
0.30 * SAQ
+ 0.25 * TQ
+ 0.20 * VQ
+ 0.15 * IQ
+ 0.05 * DSQ
+ 0.05 * APQ

Commercial_CDQ_120 =
CDQ_Core_100
+ Discoverability_Opportunity_20
```

### 27.2 SAQ 属性公式

```text
SAQ =
100 * Σ(
  Attribute_Weight
  * Completeness
  * Correctness
  * Consistency
  * Normalization
  * Confidence
) / Σ(Attribute_Weight)
```

### 27.3 缺陷优先级公式

```text
Repair_Priority =
Severity_Weight
* log(PageViews_30d + 1)
* log(Sales_30d + 1)
* Conversion_Impact
* Confidence
* Fix_Ease
```

### 27.4 Gate 逻辑

```text
如果 Policy Violation → U
否则如果 Critical Defect → D
否则按 CDQ Core Score 分 A/B/C
```

---

## 28. 你可以直接用于开发的 JSON 输出协议

```json
{
  "asin": "B0XXXXXXX",
  "marketplace": "US",
  "sku": "SKU-001",
  "product_type": "AIR_PURIFIER",
  "scores": {
    "cdq_core_100": 82.4,
    "discoverability_20": 13.5,
    "commercial_120": 95.9,
    "grade": "A"
  },
  "component_scores": {
    "structured_attributes": 76,
    "title": 92,
    "variation": 100,
    "image": 68,
    "bullets": 100,
    "aplus": 100
  },
  "gates": {
    "policy_gate": "PASS",
    "critical_defect_gate": "PASS"
  },
  "defects": [
    {
      "component": "structured_attributes",
      "defect_type": "missing_relevant_attribute",
      "severity": "P2",
      "attribute": "item_weight",
      "current_value": null,
      "recommended_value": "Need human input",
      "evidence": "Top 10 relevant attribute missing",
      "merchant_action": "Fill item_weight in Product Detail",
      "priority_score": 74.5
    }
  ],
  "action_plan": [
    {
      "priority": "P1",
      "action": "补齐 Top10 相关属性",
      "owner": "Listing Operator",
      "expected_impact": "提升结构化属性分和筛选覆盖"
    }
  ],
  "confidence": 0.88,
  "need_human_review": true
}
```

---

## 29. 最终落地 SOP

### Step 1：全量扫描

- 每周扫描全账号 ASIN；
- 新品上架前必须跑一次；
- Listing 修改后 48 小时复检；
- 大促前 14 天扫描主推 SKU。

### Step 2：分层处理

```text
U / D：合规与严重缺陷，当天处理
C：进入本周修复
B：进入优化池
A：只监控，不动核心结构
```

### Step 3：修复顺序

```text
1. 前台不可见 / 不索引 / 合规
2. 标题违规
3. Top6 / Top10 属性错误
4. 变体严重缺陷
5. 图片不足 / 主图不合规
6. A+ 缺失
7. Bullet 缺失
8. 类目 / 关键词机会
9. 转化表达优化
```

### Step 4：复检

每次修复后记录：

| 字段 | 说明 |
|---|---|
| before_score | 修复前分数 |
| after_score | 修复后分数 |
| score_delta | 分数变化 |
| pv_delta | 页面浏览变化 |
| cvr_delta | 转化变化 |
| acos_delta | 广告效率变化 |
| organic_rank_delta | 自然排名变化 |
| defect_resolved | 是否解决 |

---

## 30. 结尾：这套系统的定位

这套 CDQ 算法系统不应该只是一个“亚马逊官方分数复刻器”。

它应该成为：

```text
亚马逊商品目录数据质量操作系统
```

它连接：

- Listing 基础质量；
- 商品事实一致性；
- 类目与属性规范；
- 图片与 A+ 语义；
- 变体家族健康；
- 搜索可发现性；
- 广告相关性；
- AI 购物助手可理解性；
- 运营修复 SOP；
- 账号级质量监控。

最终系统要回答三个问题：

```text
1. 我的 Listing 是否符合亚马逊 CDQ 的质量要求？
2. 哪些目录数据缺陷正在影响搜索、转化、广告和 AI 理解？
3. 我应该先修什么、怎么修、修完如何复检？
```

这才是从 IDQ 到 CDQ 后，真正值得开发成产品的算法架构。
