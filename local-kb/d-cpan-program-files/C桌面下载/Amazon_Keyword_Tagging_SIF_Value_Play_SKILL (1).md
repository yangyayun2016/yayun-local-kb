---
name: amazon-keyword-tagging-sif-value-play
description: 使用 SIF 价值打法为亚马逊关键词词库进行打标、需求拆解、词频统计、供给匹配、机会评分、广告结构规划、Listing/视觉/选品输出。适用于 ABA 搜索词、广告 Search Term、竞品页面、评论、后台属性、站外趋势等数据，尤其适合亚马逊美国站类目词库分析。
version: 1.0.0
---

# Amazon Keyword Tagging Skill：SIF 价值打法版

## 1. Skill 定位

本 Skill 用于把亚马逊关键词词库，从“关键词列表”升级为“消费者需求地图 + 产品供给匹配 + 广告结构规划 + Listing/视觉/选品动作”。

核心思想：

> 关键词不是投放核心，消费者需求才是投放核心。关键词只是消费者需求的外显表达。

最终目标：

```text
关键词词库
→ 消费者需求拆解
→ 词频统计
→ 需求分类
→ 需求大小评估
→ 产品供给匹配
→ 价值点验证
→ 广告结构搭建
→ 投放词与匹配模式规划
→ 按搜索量集中度拆分广告活动
→ 数据回流
→ Listing / 视觉 / 产品 / 广告迭代
```

---

## 2. 适用场景

当用户提出以下需求时，使用本 Skill：

- 给亚马逊美国站关键词词库打标
- 分析 ABA 搜索词
- 整理某个类目的关键词标签体系
- 根据 SIF 价值打法搭建广告框架
- 做消费者需求分类
- 做词频统计、搜索量加权词频、需求强度分析
- 用自己产品卖点反向匹配市场需求
- 从关键词中提炼广告结构、Listing 卖点、视觉方向、选品机会
- 分析空气净化器、发夹、服装、家居、宠物、玩具、美妆、消费电子等非标品或半标品词库

---

## 3. 输入数据要求

优先使用用户上传的 Excel / CSV 文件。常见输入包括：

### 3.1 ABA 关键词数据

常见字段：

- 搜索词 / Keyword / Search Term
- ABA 排名 / Search Frequency Rank
- Top 1 Clicked ASIN
- Top 2 Clicked ASIN
- Top 3 Clicked ASIN
- Top 1 Click Share
- Top 2 Click Share
- Top 3 Click Share
- Top 1 Conversion Share
- Top 2 Conversion Share
- Top 3 Conversion Share
- Top 1 Brand
- Top 2 Brand
- Top 3 Brand
- Top 1 Category
- Top 2 Category
- Top 3 Category

### 3.2 广告 Search Term 数据

常见字段：

- Customer Search Term
- Match Type
- Campaign
- Ad Group
- Impressions
- Clicks
- CTR
- CPC
- Spend
- Sales
- Orders
- CVR
- ACOS
- ROAS

### 3.3 竞品与评论数据

常见字段：

- ASIN
- Title
- Bullet Points
- A+ Content
- Backend Attributes
- Review Title
- Review Body
- Rating
- Review Date
- Q&A

### 3.4 自己产品供给数据

用户可提供，也可以从 Listing / 产品描述中提取：

- 产品品类
- 材质
- 功能
- 尺寸
- 颜色
- 容量
- 参数
- 适用人群
- 使用场景
- 风格款式
- 差异化卖点
- 价格带
- 包装/套装
- 供应链优势
- 合规限制

---

## 4. 处理原则

### 4.1 关键词不是终点

不要只输出“关键词分类”。必须输出：

- 消费者需求分类
- 需求大小
- 供给匹配度
- 机会等级
- 广告打法
- Listing 用途
- 视觉内容建议
- 选品/产品建议

### 4.2 以消费者需求为中心

广告结构不按关键词机械拆分，而是按需求点拆分：

```text
需求点 → 广告活动 Campaign → 广告组 Ad Group → 关键词 → 匹配模式
```

### 4.3 供给必须反向匹配需求

不是市场有什么词就全部打，而是判断：

```text
这个需求大不大？
我的产品能不能满足？
满足得强不强？
竞争是否过强？
是否值得投放？
是否能迁移到 Listing、视觉、选品？
```

### 4.4 0-1-3 颗粒度法则

用于标签置信度和供给匹配分：

| 分值 | 含义 | 示例 |
|---|---|---|
| 0 | 不命中 / 不匹配 / 无证据 | 用户搜 metal clip，但产品是塑料 |
| 1 | 弱命中 / 弱匹配 / 单一证据 | 产品可用于 thick hair，但没有强抓力设计 |
| 3 | 强命中 / 强匹配 / 多源证据 | 产品主打 strong hold for thick hair，且评论验证 |

---

## 5. 标准工作流

## Step 1：搭建词库，收集消费者需求

目标：从多个来源收集目标市场中的真实消费者需求表达。

### 数据来源优先级

| 来源 | 作用 |
|---|---|
| ABA 搜索词 | 市场真实搜索需求 |
| 广告 Search Term | 真实点击和转化需求 |
| 竞品标题/五点/A+ | 竞品正在表达的供给 |
| 竞品评论 | 用户真实痛点、期待、满意点 |
| 竞品 Q&A | 购买前顾虑 |
| 类目属性 | 平台标准需求维度 |
| 站外趋势 | 审美、风格、情绪、流行元素 |
| 自己产品卖点 | 供给匹配和价值验证 |

### 原始词库表字段

| 字段 | 说明 |
|---|---|
| raw_keyword | 原始关键词 |
| normalized_keyword | 清洗后关键词 |
| 中文翻译 | 中文理解 |
| 数据来源 | ABA / 广告 / 竞品 / 评论 / 站外 |
| ABA 排名 | Search Frequency Rank |
| 搜索量 | 若有第三方搜索量则填 |
| 搜索量权重 | 没有搜索量时用 ABA 排名换算 |
| 点击份额 | ABA Top Clicked Product 相关数据 |
| 转化份额 | ABA Top Purchased Product 相关数据 |
| 相关 ASIN | 对应竞品 |
| 类目 | 主类目 / 细分类目 |
| 品牌词标记 | 是否品牌词 |
| IP/侵权风险 | 是否涉及授权/IP |
| 是否有效词 | 有效 / 低相关 / 剔除 |

---

## Step 2：关键词清洗与标准化

执行：

```text
小写化
去符号
去多余空格
单复数归一
同义词归一
单位标准化
品牌词识别
IP/授权词识别
低相关词识别
无效词过滤
```

示例：

| 原词 | 标准化 |
|---|---|
| leak proof | leakproof |
| kids / kid / children | kids |
| 32oz / 32 oz | 32 oz |
| bpa-free / BPA Free | BPA free |
| purifier for bedroom | air purifier bedroom |

---

## Step 3：通过词频统计整理消费者需求分类

### 3.1 TF 定义

TF = Term Frequency = 词频。

在本 Skill 中，TF 表示某个词根、元素、属性、需求点，在整个关键词词库中出现的频率。

### 3.2 出现次数词频

```text
TF_count(t) = 包含某个词 / 标签 t 的关键词数量
```

它回答：

> 这个需求在词库里被提到了多少次？

### 3.3 搜索量加权词频

如果有搜索量：

```text
TF_weighted(t) = Σ 关键词搜索量 × 是否包含标签 t
```

如果只有 ABA 排名：

```text
ABA_weight = 1 / ln(ABA_rank + 1)
```

```text
TF_weighted(t) = Σ ABA_weight × 是否包含标签 t
```

它回答：

> 这个需求背后有多大的真实搜索需求？

### 3.4 需求词频统计表字段

| 字段 | 说明 |
|---|---|
| 词根/元素 | thick hair / claw / flower / black |
| 中文翻译 | 厚发 / 抓夹 / 花朵 / 黑色 |
| 搜索需求分类 | 目标受众 / 功能特征 / 风格款式 / 颜色 |
| 出现次数词频 | TF_count |
| 出现次数占比 | TF_count / 总关键词数 |
| 搜索量加权词频 | TF_weighted |
| 搜索需求占比 | 该词加权搜索量 / 总加权搜索量 |
| 代表关键词 | 典型关键词 |
| 相关产品卖点 | 自己产品是否能承接 |
| 是否适合投放 | 是 / 否 / 待验证 |
| 备注 | 侵权、低相关、季节性等 |

---

## 6. 搜索需求分类体系

固定使用以下一级需求分类：

| 一级分类 | 解释 | 示例 |
|---|---|---|
| 品类名称 | 产品本体词 | air purifier, hair clips, lunch box |
| 目标受众 | 谁用 / 谁买 | women, girls, baby, pets, kids |
| 使用场景 | 在哪里用 / 什么时候用 | bedroom, office, school, wedding |
| 功能特征 | 解决什么功能问题 | HEPA, strong hold, leakproof, quiet |
| 风格款式 | 审美和造型 | y2k, vintage, cute, minimalist |
| 颜色 | 颜色需求 | black, brown, gold, pink |
| 材质材料 | 材质需求 | metal, acrylic, plastic, stainless steel |
| 尺寸大小 | 大小规格 | large, small, mini, jumbo |
| 容量 | 容量型产品适用 | 32 oz, large capacity |
| 参数 | 技术/规格参数 | CADR, voltage, count, length |
| 主题元素 | 图案、造型、元素 | flower, butterfly, star, bow |
| 品牌 | 品牌或竞品词 | Levoit, Shark, Winix, Scunci |
| 季节 | 季节性需求 | summer, winter, allergy season |
| 节日 | 节日礼品需求 | Christmas, Halloween, Valentine |
| 兼容搭配 | 和什么搭配 / 适配谁 | for thick hair, for pets, for bedroom |
| 配件 | 附属件 / 耗材 | replacement filter, refill, organizer |
| 其他需求 | 无法归入主类的需求 | bulk, wholesale, aesthetic |
| 风险词 | IP、低相关、侵权、敏感词 | Disney, Barbie, trademark terms |

---

## 7. 第三步：用自己产品卖点反向匹配市场需求

目标：判断“市场需求”与“自己产品供给”之间是否匹配。

### 7.1 建立供给卖点表

| 自己产品卖点 | 对应需求分类 | 可承接关键词 |
|---|---|---|
| HEPA 滤网 | 功能特征 | HEPA air purifier |
| 适合卧室 | 使用场景 | air purifier for bedroom |
| 宠物毛发净化 | 目标受众/痛点 | air purifier for pet hair |
| 大空间适用 | 尺寸/场景 | large room air purifier |
| 静音 | 功能/情绪 | quiet air purifier |
| 替换滤芯 | 配件/耗材 | replacement filter |
| 大号抓夹 | 尺寸大小 | large claw clips |
| 强抓力 | 功能特征 | strong hold hair clips |
| 适合厚发 | 目标受众/发质 | claw clips for thick hair |

### 7.2 供给匹配分

| 分值 | 含义 | 动作 |
|---|---|---|
| 3 | 强匹配，是产品核心卖点 | 主推，适合 Exact/Phrase |
| 1 | 弱匹配，产品可承接但不是核心优势 | 小预算测试 |
| 0 | 不匹配，产品无法满足 | 不主推 / 否定 / 仅观察 |

---

## 8. 评论分析与需求验证

评论不是单独分析，而是要与关键词需求打通。

### 8.1 评论打标维度

| 评论内容 | 标签类型 | 作用 |
|---|---|---|
| doesn’t hold thick hair | 痛点 | 厚发抓力不足 |
| too small | 尺寸痛点 | 需要 large/jumbo |
| cute design | 风格/情绪 | 可爱外观被认可 |
| breaks easily | 质量痛点 | 耐用性机会 |
| great for bedroom | 场景 | 卧室使用场景 |
| helps with allergies | 功能/痛点 | 过敏需求验证 |
| removes pet odor | 痛点/人群 | 宠物家庭需求验证 |

### 8.2 评论输出结果

```text
已验证价值：用户明确满意的点
未满足需求：用户抱怨但竞品没解决的点
情绪需求：用户为什么喜欢或讨厌
```

### 8.3 评论与关键词合并示例

```text
关键词：air purifier for pets
评论痛点：pet odor / pet hair / dog smell
自己卖点：HEPA + odor filter
最终判断：高价值需求词，适合主推
```

---

## 9. 需求强度与价值机会评分

### 9.1 需求分

```text
Demand Score =
标准化搜索量加权词频 × 0.6
+ 标准化出现次数词频 × 0.25
+ 转化信号 × 0.15
```

转化信号可来自：

- ABA 购买份额
- 广告 CVR
- 广告订单数
- 评论正向提及
- Top Purchased ASIN 集中度

### 9.2 价值机会分

```text
Value Opportunity Score =
Demand Score × 0.4
+ Supply Fit × 0.3
+ Review Pain Gap × 0.15
+ Competition Advantage × 0.1
+ Profit Feasibility × 0.05
```

### 9.3 机会等级

| 等级 | 条件 | 推荐动作 |
|---|---|---|
| S-核心必打 | 高需求 + 强供给匹配 + 明确转化/痛点 | Exact + Phrase，独立预算 |
| A-高机会长尾 | 中高需求 + 强匹配 + 竞争可控 | Phrase + Exact 测试 |
| B-中机会测试 | 有需求但匹配或转化不确定 | 小预算测试 |
| C-低优先级 | 需求弱或不够聚焦 | Listing 收录 / 低预算探索 |
| R-风险词 | 品牌/IP/授权/低相关 | 谨慎投放 / 否定 |

---

## 10. 第四步：以消费者需求为中心搭建广告框架

广告结构应从：

```text
关键词 → 广告活动
```

升级为：

```text
需求点 → 广告活动 → 广告组 → 关键词 → 匹配模式
```

### 10.1 广告结构模板

```text
产品组合 / Portfolio
  └── 需求大类 Campaign
        └── 需求细分 Ad Group
              └── 关键词 Keyword
                    └── 匹配模式 Match Type
```

### 10.2 空气净化器示例

```text
Campaign 1：宠物家庭净化需求
  Ad Group 1：air purifier for pets
  Ad Group 2：air purifier for pet hair
  Ad Group 3：air purifier for dog smell

Campaign 2：卧室静音需求
  Ad Group 1：air purifier for bedroom
  Ad Group 2：quiet air purifier
  Ad Group 3：small air purifier for bedroom

Campaign 3：过敏/粉尘/烟雾需求
  Ad Group 1：air purifier for allergies
  Ad Group 2：air purifier for dust
  Ad Group 3：air purifier for smoke

Campaign 4：大空间需求
  Ad Group 1：large room air purifier
  Ad Group 2：air purifier for home large room
```

### 10.3 发夹示例

```text
Campaign 1：厚发强抓力需求
  Ad Group 1：claw clips for thick hair
  Ad Group 2：large claw clips
  Ad Group 3：strong hold hair clips

Campaign 2：造型风格需求
  Ad Group 1：flower hair clips
  Ad Group 2：butterfly hair clips
  Ad Group 3：y2k hair clips

Campaign 3：人群需求
  Ad Group 1：hair clips for girls
  Ad Group 2：baby hair clips
  Ad Group 3：toddler hair clips
```

---

## 11. 第五步：规划投放词和匹配模式

### 11.1 匹配模式建议

| 需求状态 | 关键词类型 | 匹配模式 | 目的 |
|---|---|---|---|
| 高需求 + 高匹配 | 核心转化词 | Exact 精准 | 价值验证 / 控转化 |
| 中高需求 + 长尾 | 场景/人群/功能词 | Phrase 词组 | 拓展精准流量 |
| 需求不确定 | 宽泛需求词 | Broad 广泛 | 探索新搜索词 |
| 已验证价值点 | 大词/核心词 | Exact + Phrase | 放量 |
| 竞品强相关 | 竞品 ASIN / 品牌词 | Product Targeting | 抢竞品流量 |
| 未知需求 | 自动广告 | Auto Close/Substitutes | 挖词和语义扩展 |

### 11.2 关键词投放分层

| 层级 | 关键词类型 | 投放动作 |
|---|---|---|
| S 层 | 高需求高匹配核心词 | 精准投放，单独预算 |
| A 层 | 高机会长尾词 | 词组/精准测试 |
| B 层 | 中机会探索词 | 词组/广泛 |
| C 层 | 低相关或不确定词 | 小预算探索 |
| R 层 | 风险词 | 谨慎或否定 |

---

## 12. 第六步：按搜索量集中度拆分广告活动

### 12.1 搜索量集中度算法

```text
单词搜索占比 = 某关键词搜索量 / 该需求点总搜索量
```

```text
Top3 搜索集中度 = 该需求点下 Top3 关键词搜索量 / 该需求点总搜索量
```

### 12.2 拆分规则

| 情况 | 操作 |
|---|---|
| 单个关键词占比 ≥ 30% | 单独 Campaign / SKAG |
| Top3 关键词占比 ≥ 60% | Top3 单独拆组 |
| 搜索量分散 | 按需求主题合并广告组 |
| 词量少但转化强 | Exact 小预算验证 |
| 搜索量大但供给弱 | 谨慎测试，不主推 |
| 搜索量小但评论痛点强 | 长尾精准测试 |

### 12.3 评估原则

即使大词被单独拆出来，最终评估时也要回到“需求点”合并评估：

```text
某需求点整体表现 =
该需求点下所有 Campaign / Ad Group / Keyword 的广告数据合并
```

---

## 13. 价值验证路径

价值打法分三阶段。

### 阶段 1：价值验证

目标：验证这个需求点是否真的能为你的产品带来点击和转化。

操作：

```text
关键词投放：Exact + Phrase
预算：小预算
结构：按需求点分组
目标：控制变量，验证供给与需求匹配
```

核心指标：

| 指标 | 判断 |
|---|---|
| CTR | 用户是否被吸引 |
| CVR | 产品是否满足需求 |
| CPC | 流量成本 |
| ACOS | 盈利可行性 |
| Search Term | 是否拓展出相似需求 |

### 阶段 2：基于已验证价值的流量拓展

操作：

```text
搜索页投放：关键词精准 + 关键词词组
商品详情页投放：目标 ASIN / 高度相似竞品 / 已验证流量来源 ASIN
```

### 阶段 3：流量泛化

操作：

```text
Broad 广泛匹配
自动广告
商品投放扩展
类目投放
相似竞品投放
Listing 文案强化
主图/A+强化需求表达
```

---

## 14. 输出表结构

最终关键词打标结果表必须尽量包含以下字段。

| 字段 | 说明 |
|---|---|
| 原始关键词 | raw keyword |
| 清洗关键词 | normalized keyword |
| 中文翻译 | 中文理解 |
| 搜索需求分类 | 品类/人群/场景/功能等 |
| 品类名称 | 产品对象 |
| 目标受众 | 谁用 |
| 使用场景 | 哪里用 / 什么时候用 |
| 功能特征 | 解决什么问题 |
| 风格款式 | 审美风格 |
| 颜色 | 颜色需求 |
| 材质材料 | 材质需求 |
| 尺寸大小 | 大小规格 |
| 容量 | 容量需求 |
| 参数 | 技术 / 规格 |
| 主题元素 | 图案 / 造型 / 元素 |
| 品牌 | 品牌 / 竞品 |
| 季节 | 季节性 |
| 节日 | 节日需求 |
| 兼容搭配 | 适配 / 搭配对象 |
| 配件 | 配件 / 耗材 |
| 其他需求 | 其他 |
| 出现次数词频 | TF_count |
| 搜索量加权词频 | TF_weighted |
| 需求强度 | Demand Score |
| 自身卖点匹配 | Supply Fit |
| 评论痛点匹配 | Review Gap |
| 价值机会分 | Value Score |
| 机会等级 | S/A/B/C/R |
| 推荐广告结构 | Campaign / Ad Group |
| 推荐匹配模式 | Exact / Phrase / Broad / Auto / Product |
| Listing 用途 | 标题 / 五点 / A+ / 后台词 |
| 视觉用途 | 主图 / 场景图 / 对比图 / A+ |
| 选品用途 | 开发 / 改款 / 包装 / 套装 |
| 备注 | 风险、季节性、低相关 |

---

## 15. 推荐输出的 Excel Sheet

处理用户上传 Excel 时，建议输出以下 Sheet：

1. 标签汇总_看板
2. 关键词打标结果
3. 高机会词清单
4. SIF需求词频统计
5. 需求供给匹配矩阵
6. 广告结构规划
7. 标签词典
8. 打标规则说明
9. 原始数据
10. 次要词快速打标（如存在）

### 15.1 标签汇总_看板

包含：

- 总关键词数
- S/A/B/C/R 机会等级数量
- 各需求分类词频
- Top 需求点
- Top 场景
- Top 功能
- Top 人群
- Top 品牌/竞品
- Top 配件/耗材

### 15.2 高机会词清单

筛选：

```text
机会等级 = S 或 A
且 Supply Fit >= 1
且非 IP/授权高风险词
且非低相关词
```

### 15.3 SIF需求词频统计

包含：

- 词根/元素
- 中文翻译
- 搜索需求分类
- 出现次数词频
- 出现次数占比
- 搜索量加权词频
- 搜索需求占比
- 代表关键词
- 相关产品卖点
- 是否适合投放

### 15.4 需求供给匹配矩阵

包含：

- 需求点
- 需求分类
- 需求强度
- 自己产品卖点
- 供给匹配分
- 评论痛点证据
- 机会等级
- 推荐动作

### 15.5 广告结构规划

包含：

- Campaign 需求大类
- Ad Group 需求细分
- 代表关键词
- 推荐匹配模式
- 拆分原因
- 预算建议
- 验证指标

---

## 16. 类目打标规则示例：空气净化器

### 16.1 品类名称

- air purifier
- air cleaner
- room air purifier
- home air purifier

### 16.2 功能/技术

- HEPA
- True HEPA
- H13
- air filter
- smoke remover
- odor eliminator
- ionizer
- UV
- quiet
- smart
- washable filter

### 16.3 场景/空间

- bedroom
- home
- large room
- office
- dorm
- living room
- basement
- nursery

### 16.4 痛点/污染物

- allergies
- dust
- smoke
- mold
- pollen
- pet hair
- pet dander
- odor
- dog smell
- wildfire smoke

### 16.5 人群/角色

- pet owners
- allergy sufferers
- baby / nursery
- smokers
- home office users

### 16.6 配件/耗材

- replacement filter
- filter cartridge
- filter for Levoit
- filter for Shark
- filter for Winix

### 16.7 品牌/竞品

- Levoit
- Shark
- Winix
- Dyson
- Honeywell
- Coway
- Blueair
- GermGuardian

### 16.8 典型广告结构

```text
Campaign：宠物家庭净化需求
- air purifier for pets
- air purifier for pet hair
- air purifier for dog smell

Campaign：过敏粉尘需求
- air purifier for allergies
- air purifier for dust
- air purifier for pollen

Campaign：烟雾异味需求
- air purifier for smoke
- air purifier for odor
- air purifier for wildfire smoke

Campaign：空间场景需求
- air purifier for bedroom
- air purifier for large room
- air purifier for office
```

---

## 17. 类目打标规则示例：Hair Clips 发夹

### 17.1 品类名称

- hair clips
- claw clips
- barrettes
- hair pins
- alligator clips
- duckbill clips
- sectioning clips

### 17.2 人群/发质

- women
- girls
- baby
- toddler
- kids
- thick hair
- thin hair
- fine hair
- curly hair

### 17.3 功能/卖点

- strong hold
- no slip
- flat / lay flat
- styling
- sectioning
- non crease

### 17.4 风格/主题

- flower
- butterfly
- star
- bow
- y2k
- cute
- vintage
- minimalist
- aesthetic

### 17.5 材质/外观

- metal
- acrylic
- plastic
- matte
- gold
- pearl
- tortoise

### 17.6 场景

- wedding
- party
- school
- work
- salon
- makeup
- shower

### 17.7 典型广告结构

```text
Campaign：厚发强抓力需求
- claw clips for thick hair
- large claw clips
- strong hold hair clips

Campaign：薄发/细软发需求
- hair clips for thin hair
- hair clips for fine hair

Campaign：风格主题需求
- flower hair clips
- butterfly hair clips
- y2k hair clips

Campaign：造型工具需求
- duckbill clips
- alligator clips
- sectioning clips
```

---

## 18. 关键词打标算法伪代码

```text
for each keyword in keyword_library:
    normalized_keyword = normalize(keyword)

    elements = extract_elements(normalized_keyword)

    tags = []
    for each element in elements:
        tag = match_tag_dictionary(element)
        tags.append(tag)

    demand_categories = classify_demand(tags)

    tf_count = count_frequency(tags)
    tf_weighted = calculate_weighted_frequency(tags, search_volume or ABA_rank)

    demand_score = calculate_demand_score(
        tf_weighted,
        tf_count,
        click_share,
        conversion_share
    )

    supply_fit = match_product_supply(tags, product_selling_points)

    review_gap = match_review_pain_points(tags, review_data)

    value_score = calculate_value_score(
        demand_score,
        supply_fit,
        review_gap,
        competition_advantage,
        profit_feasibility
    )

    opportunity_level = assign_level(value_score, risk_flag, supply_fit)

    ad_action = recommend_ad_action(opportunity_level, demand_score, supply_fit)

    listing_action = recommend_listing_action(tags)
    visual_action = recommend_visual_action(tags)
    product_action = recommend_product_action(tags, review_gap)

    output row
```

---

## 19. 广告动作判断规则

```text
if Demand高 and SupplyFit == 3:
    S级核心价值词
    推荐：Exact + Phrase，独立预算，主推

if Demand中高 and SupplyFit == 3:
    A级长尾机会词
    推荐：Phrase + Exact 测试

if Demand高 and SupplyFit == 1:
    B级谨慎测试词
    推荐：小预算验证，避免大额放量

if Demand低 and SupplyFit == 3:
    C级低量精准词
    推荐：Listing 收录，低预算精准测试

if SupplyFit == 0:
    不主推
    推荐：否定 / 仅观察 / 不进入核心广告

if IP/品牌风险 == True:
    R级风险词
    推荐：谨慎投放或剔除
```

---

## 20. Listing / 视觉 / 选品迁移规则

### 20.1 Listing 用途

| 标签类型 | Listing 动作 |
|---|---|
| 高频品类词 | 标题核心词 |
| 高频功能词 | 标题/五点前置 |
| 高频材质词 | 标题/后台属性 |
| 高频痛点词 | 五点/FAQ/对比说明 |
| 高频人群词 | 图片/A+人群场景 |
| 高频场景词 | 主图副图/A+场景模块 |
| 高频配件词 | 变体/关联销售/套装 |

### 20.2 视觉用途

| 标签类型 | 视觉动作 |
|---|---|
| 安全/安心 | 认证、材质、家庭场景 |
| 高级感 | 质感、包装、品牌调性 |
| 亲子/宠物 | 人群互动场景 |
| 技术参数 | 参数图、对比图 |
| 痛点解决 | Before/After 对比 |
| 节日礼品 | 礼盒、节日氛围、开箱图 |

### 20.3 选品用途

| 标签类型 | 产品动作 |
|---|---|
| 高频痛点 | 产品改良 |
| 高频场景 | 开发场景化变体 |
| 高频人群 | 人群专用款 |
| 高频材质 | 材质升级 |
| 高频尺寸 | 尺寸线扩展 |
| 高频配件 | 耗材/配件利润线 |
| 高频礼品 | 包装升级/套装化 |

---

## 21. 质量检查清单

输出前检查：

- 是否识别了正确的主数据 Sheet
- 是否保留原始数据 Sheet
- 是否新增完整打标字段
- 是否生成需求词频统计
- 是否区分 TF_count 和 TF_weighted
- 是否包含中文翻译
- 是否包含搜索需求分类
- 是否包含供给匹配逻辑
- 是否包含机会等级
- 是否识别品牌/竞品词
- 是否识别 IP/授权风险词
- 是否识别配件/耗材词
- 是否输出广告结构规划
- 是否输出高机会词清单
- 是否输出标签词典和规则说明
- 是否给出 Listing、视觉、选品建议

---

## 22. 标准回复格式

当完成文件处理后，回复应简洁说明：

```text
已完成【类目/站点】关键词打标，文件已生成：

[下载文件](sandbox:/mnt/data/xxx.xlsx)

本次处理：
- 主表关键词：X 条
- 高机会词：X 条
- 使用 SIF 价值打法逻辑：关键词 → 消费者需求 → 词频统计 → 供给匹配 → 价值机会分 → 广告结构规划

文件包含：
1. 标签汇总_看板
2. 关键词打标结果
3. 高机会词清单
4. SIF需求词频统计
5. 需求供给匹配矩阵
6. 广告结构规划
7. 标签词典
8. 打标规则说明
9. 原始数据

重点机会方向：
- 方向 1
- 方向 2
- 方向 3
```

---

## 23. 核心记忆句

```text
关键词价值 = 消费者需求强度 × 产品供给匹配度 × 广告验证结果 × 可规模化程度
```

```text
始于关键词，落到需求；始于投放，回到产品价值。
```

```text
原子标签解决“看懂关键词”；组合标签解决“看懂需求”；机会指数解决“该不该做”。
```
