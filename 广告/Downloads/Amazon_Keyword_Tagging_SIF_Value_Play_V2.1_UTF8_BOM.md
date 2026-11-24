---
name: amazon-keyword-tagging-sif-value
description: >-
  面向亚马逊运营、选品与广告决策的关键词原子级打标 Skill。基于 SIF 价值打法六步流程，
  对 ABA、商机探测、SIF、广告搜索词、竞品 Listing、评论等来源建立词库，
  实施清洗、需求元素识别、词频与搜索量加权、供给匹配(0/1/3)、价值机会评分，
  然后输出需求中心广告架构、关键词匹配模式、Listing/视觉/产品开发建议与 Excel 数据表。
---

# Amazon Keyword Tagging · SIF 价值打法 Skill

**版本**：V2.1.0（2026-11-17）  
**状态**：可复用的需求打标与决策规范  
**适用站点**：Amazon US / UK / DE 及其他站点；须按站点语言和商品类型换词典  
**适用对象**：亚马逊选品、产品开发、Listing、广告、VOC、竞品分析团队和 Agent  
**文件编码**：UTF-8；本文件保留标准 `SKILL.md` 可解析结构

> **核心思想**：关键词是消费者需求的外显表达。先由关键词还原需求，再由自家产品供给验证需求，围绕需求搭建广告，而不是只按字面关键词堆广告活动。

## 0. 来源边界与使用要求

- **SIF 原始方法来源**：用户提供的《价值打法.pdf》（25 页，署名“Sif关键词 CEO & 亚马逊广告卖家讲师 刘松”），尤其是第 8、14–15、17–24 页。
- **来源原意**：①搭建词库；②词频分类；③自家产品供给匹配市场需求；④以消费者需求搭建广告框架；⑤按需求点整理关键词及匹配方式；⑥按搜索量集中度拆分广告活动；后续分“价值验证 → 已验证价值拓展 → 流量泛化”。
- **本 Skill 扩展**：0-1-3 颗粒度、需求多标签词典、评分模型、置信度、数据表规范、自动化执行与质检是对上述方法的工程化设计，**不是 SIF 原文给出的官方公式或阈值**。
- **所有市场规模、流量、CPC、CVR、Review、销量、利润均须有真实数据来源**。无来源的字段标为 `null/待补充`；不可把推算写成实测。
- **供给匹配必须基于当前 SKU/ASIN 的实际规格、认证、图片、说明书、测试结果**；不得把竞品页面卖点冒充为自家供给。
- **只在明确许可后执行不可逆动作**：对外发布、广告启停/调预算/改出价、动用资金、删除数据等需用户审批。默认仅出分析与执行建议。

## 1. 触发条件与交付定义

当用户提出下列任务时启用本 Skill：

- “美国站空气净化器/德国布艺清洗机/英国 spot cleaner / hair clips 关键词打标”；
- “结合 SIF 价值打法建词库、词频统计、加权词频、需求分类”；
- “把自家卖点反向匹配消费者需求并判断可投词”；
- “根据需求点组织 SP 广告，拆分 SKAG，规划 Exact/Phrase/Broad”；
- “用关键词、评论与广告数据发现机会点并迁移到 Listing、视觉、产品开发”。

**默认交付**：一份可筛选的主打标表、需求词频汇总、供需匹配矩阵、机会词清单、广告结构草案、规则词典、数据质量报告、方法说明。任务只要求 Markdown 时，交付规范和示例，不伪称已生成 Excel 或接入广告后台。

---

# 第一部分 · SIF 价值打法六步工作流

## 第一步：搭建词库——收集消费者需求

### 1.1 数据源与可信度

| 来源 | 关键字段 | 用途 | 注意 |
|---|---|---|---|
| ABA / Search Query Performance | 搜索词、Search Frequency Rank、点击/购买份额等（依报告口径） | 真实搜索意图和相对集中度 | ABA 排名≠搜索量 |
| 商机探测 / Niche Insights | 搜索词、360 天搜索量、90/180 天增长、搜索转化率、相关 ASIN | 需求规模和趋势 | 先确认“搜索量”的时间窗与定义 |
| SIF / 第三方关键词工具 | 估算搜索量、关键词拓展、自然/广告位置、竞品 ASIN | 扩词和竞争结构 | 标明“第三方估算”，不可混作官方实测 |
| 广告 Search Term 报告 | 实际搜索词、匹配类型、展示、点击、CPC、花费、订单、销售额 | 验证需求的商业价值 | 关键词不等于消费者实际搜索词 |
| 竞品前台 | 标题、五点、A+、图片、参数、价格、变体 | 识别竞品供给与价值表达 | 页面主张不等于真实功能 |
| Product Type / 后台属性 | 类目属性、材质、尺寸、功率、容量、兼容性 | 规范属性标签 | 实际接口字段依站点和品类变化 |
| 评论 / Q&A / 退货原因 | 场景、期待、投诉、褒义词、负向词 | VOC、痛点验证 | 要做评论样本量与偏差提示 |
| 站外趋势 | 搜索趋势、社媒讨论、社区痛点 | 新需求及情绪信号 | 与站内数据分开呈现，避免来源混淆 |
| 自家产品主数据 | SKU、型号、卖点、规格、认证、BOM、成本、价格 | 供给侧匹配 | 缺失时不能默认强匹配 |

建议每条数据保留：`marketplace`、`locale`、`category`、`source`、`source_date`、`window_days`、`source_record_id`、`asin`、`raw_keyword`、`raw_metrics`、`ingested_at`。

### 1.2 数据清洗

1. 保留原词 `raw_keyword` 和原始行号，绝不覆盖原始数据。
2. 做大小写、全角、空格、标点、单位、字符编码和重复行规范化。
3. 分语言和站点处理英文、德文、法文、西语；德语变音字 `ä/ö/ü/ß` 可做**辅助检索规范化**，仍保留原词。
4. 区分单复数、词形变化、行业同义词、可疑拼写和真实品牌；同义词归一不代表搜索词可以随意合并投放。
5. 标识：`核心产品词`、`配件/耗材词`、`竞品品牌词`、`不相关词`、`跨品类词`、`IP/合规风险词`、`待人工复核词`。
6. 关键词去重键建议：`marketplace + locale + normalized_keyword + source + window`；跨来源相同词仍保留各自证据。
7. 统一搜索量口径：月、90 天、360 天不得未经换算直接加总。日期区间不同的数据不能直接做同比排名。

**清洗后的最小记录**：

```json
{
  "marketplace": "DE",
  "locale": "de-DE",
  "raw_keyword": "Polsterreiniger Gerät",
  "normalized_keyword": "polsterreiniger gerät",
  "source": "niche_insights",
  "window_days": 360,
  "search_volume": null,
  "aba_rank": null,
  "data_status": "awaiting_actual_source_data"
}
```

## 第二步：词频统计——按消费者需求，而非按单词字面堆叠

### 2.1 必须区分三个指标

**传统 TF（Term Frequency）**：某个词根在某份文本中出现次数。  
`TF(t, d) = count(term t in document d)`

**标签覆盖词频（本 Skill 中的关键词出现次数）**：含某需求标签的**去重关键词数量**。它在信息检索术语上更接近标签的文档频率（DF），不是简单把所有文字出现次数相加。  
`DF_tag(t) = Σ 1(tag t appears in keyword k)`

**搜索量加权需求词频**：  
`WeightedDemand(t) = Σ [Volume(k) × Presence(t,k)]`

其中 `Presence(t,k)∈{0,1}`；同一关键词中重复提及同一标签只计一次，除非用户明确要求 token 频次。真实搜索量最好选 **同一时间窗口** 的指标。

如果没有真实搜索量、只有 ABA 排名，可另建**代理需求权重**：  
`RankWeight(k) = 1 / ln(ABA_rank(k) + 1)`（ABA 排名须为正整数）；  
`WeightedRankProxy(t) = Σ [RankWeight(k) × Presence(t,k)]`。

> **注意**：RankWeight 是排序代理，不是搜索量，也不能称为“加权搜索量”。应在列名中明确写 `ABA排名代理权重`。

### 2.2 词频计算示例（虚构数据，仅说明算法）

| 关键词 | 360天搜索量（示例） | 原子标签 |
|---|---:|---|
| claw clips for thick hair | 8,000 | 抓夹、厚发 |
| large claw clips | 5,000 | 抓夹、大号 |
| strong hold claw clips | 3,000 | 抓夹、强抓力 |

得到：

- `抓夹`：DF=3，WeightedDemand=16,000；
- `厚发`：DF=1，WeightedDemand=8,000；
- `大号`：DF=1，WeightedDemand=5,000；
- `强抓力`：DF=1，WeightedDemand=3,000。

**多标签口径注意**：一条关键词可以同时落入产品、功能、场景、人群等多个维度。各标签的 `搜索量加权词频` 存在重叠，**不能将各标签加总当作不重复的市场总量**。同维度多标签比例也可能合计超过 100%。如需真正不重复的市场规模，必须先按 `keyword_id` 去重计算并标明分摊方案。

### 2.3 需求词频表必需字段

`tag_id | 标签中文 | 标签英文 | 一级维度 | 原子词根 | 中文翻译 | DF_count | DF_ratio | WeightedDemand | demand_share_in_scope | ABA_proxy_weight | source_metric | source_window | representative_keywords | notes`

`demand_share_in_scope = WeightedDemand(t) / Σ Volume(去重后的相关词库)`，只在“同一数据源、同一时间窗、同一市场范围”内使用。

## 第三步：用自己的产品卖点（供给）反向匹配市场需求

### 3.1 两种 0-1-3 不可混淆

**颗粒度路径**：`0 原始记录 → 1 原子标签 → 3 跨标签组合需求/可执行策略`。这里的 0、1、3 是层级名称，不是分数。

**供给匹配分**：

| `supply_fit` | 含义 | 证据 |
|---:|---|---|
| `0` | 产品明确不具备 / 不满足需求 | 实际规格或兼容性排除 |
| `1` | 部分满足、非核心卖点或需验证 | 有有限证据但不足以强承诺 |
| `3` | 产品明确强匹配，且有可验证的卖点与场景能力 | 产品规格、测试、认证或可靠实测 |
| `null` | 信息不足，未完成供给判断 | 必须补充 SKU/ASIN 的供给资料 |

**禁止**在没有产品规格资料时，将所有“行业相关”词自动记为 3 分。`null` 不可在评分时偷偷换成 1 或 3。

### 3.2 产品主数据模板

`SKU | ASIN | 站点 | 产品形态 | 材质 | 尺寸 | 重量 | 功率 | 吸力/过滤级别/技术 | 容量 | 适用场景 | 已验证卖点 | 不支持功能 | 认证及证据 | 售价 | Coupon | 单件可用广告毛利 | 目标人群 | 备注`

例如德国布艺清洗机：只有确认产品**实际具备**蒸汽/热水能力，才允许标记相应强匹配；`Nasssauger` 也可能代表普通湿吸或干湿吸尘器，**不应默认等同于喷洗抽吸式布艺清洗机**。

### 3.3 VOC/评论与心理层级

从评论提取：`用户角色`、`JTBD待完成任务`、`期待结果`、`抱怨/失败场景`、`满意证据`、`情绪词`、`使用环境`、`购买前顾虑`、`替代方案`。

心理与价值层可标记：`生理舒适`、`健康安全感`、`爱与归属/陪伴`、`自尊/身份认同`、`自我实现/生活方式`；这些只是**消费者动机解释标签**，不得把马斯洛层次当作销量因果证据。

评论缺失时，`review_gap_score=null`；允许输出“可能痛点假设”，但不能写“已被大量评论验证”。

## 第四步：以消费者需求为中心搭建广告框架

建议逻辑：

```text
Portfolio / 产品业务线
  └─ Demand Theme / 核心需求点（如 厚发强抓力）
       ├─ Campaign / 验证型或放量型广告活动
       │    ├─ Ad Group / 同质化关键词簇
       │    └─ Keyword / Search Term / ASIN Target
       └─ Evaluation Group / 需求点归因与汇总
```

**Campaign 不必机械地等于一个需求点**。按预算隔离、搜索量集中度、匹配类型、投放目标、阶段和可操作性决定拆分；同时维护 `demand_group_id`，保证跨广告活动仍可回收同一需求的整体表现。

原则：

- 强供给匹配、高需求、可盈利的价值点优先；
- 场景、人群、痛点、功能各成逻辑词包；
- 品牌/IP、耗材、跨品类、低相关词独立管理；
- 关键词、商品投放、自动广告都应回收到相同的需求标签；
- 同一个搜索词跨广告活动造成重复覆盖时，必须有预算与否词冲突检查。

## 第五步：整理需求对应关键词与匹配模式

| 需求状态 | 初始广告策略 | 验证重点 |
|---|---|---|
| `Fit=3` 且需求高、证据强 | SP Exact + Phrase，必要时单独预算 | CTR、CVR、CPA、ACOS、自然位 |
| `Fit=3` 需求小但高相关 | 低成本 Exact/Phrase 长尾 | 低 CPC、高 CVR 和可持续订单 |
| `Fit=1` | 小预算 Exact/Phrase 验证，先核对供给 | 转化后退货/差评风险 |
| `Fit=0` | 不以该需求承接；必要时否定 | 避免误导与浪费 |
| `Fit=null` | 人工确认前不标“可主推” | 补充供给证据 |
| 品牌词 / 竞品 ASIN | 独立商品投放或品牌词测试 | 品牌合规、相关性、ROI |
| 配件/耗材词 | 单独耗材词包；不是主机则谨慎 | 用户要买的究竟是什么 |
| 不确定新需求 | Broad / Auto 用于探索 | Search Term 新词和转化证据 |

匹配类型选择需结合真实投放数据，不把“Broad→Phrase→Exact”当成任何品类都必须固定执行的单一路线。

## 第六步：按搜索量集中度拆 Campaign，统一按需求归因

同一需求点 `d` 下，若同口径搜索量齐全：

`DemandVolume(d) = Σ UniqueSearchVolume(k) for k∈d`

`KeywordShare(k | d) = SearchVolume(k) / DemandVolume(d)`

`Top3Concentration(d) = (V_top1 + V_top2 + V_top3) / DemandVolume(d)`

**用于试运行的阈值（本 Skill 建议，非 SIF 官方阈值）**：

- 单个词占该需求搜索量 ≥30%：评估单独 Campaign 或 SKAG；
- 前三词合计占比 ≥60%：考虑将大词与长尾分开管控预算；
- 搜索分散：按相同消费者需求归并词组；
- 无真实搜索量：仅输出 `集中度无法可靠计算`，可以附 ABA 排名代理观察，不给出“实际占比”。

**归因红线**：多个关键词/标签/广告活动可能重复贡献同一需求；广告实际点击、订单需按报表实体和去重规则做汇总，不可把同一订单在多个需求组重复计作净销量。

---

# 第二部分 · 原子标签本体与重组

## 2.1 统一一级分类（可多标签）

1. **品类名称**：主商品、细分品类、商品用途、产品形态；
2. **目标受众/角色**：购买者、使用者、收礼者、年龄/发质/家庭角色；
3. **使用场景/时机**：卧室、沙发、汽车、学校、办公室、派对等；
4. **功能特征**：强抓力、防滑、除味、喷洗吸干、抗折痕等；
5. **风格款式**：极简、Y2K、复古、哑光、便携形态等；
6. **颜色**：颜色及配色；
7. **材质材料**：不锈钢、硅胶、金属、塑料、织物等；
8. **尺寸大小**：large/small/mini、长宽高、覆盖面积；
9. **容量**：升、毫升、盎司、水箱等；
10. **参数与技术**：功率、吸力、CADR、HEPA 等；
11. **主题元素**：花朵、蝴蝶、星星、礼盒图案等；
12. **品牌与竞品**：品牌词、型号词、竞品 ASIN；
13. **季节**：夏季、雨季、花粉季、开学季；
14. **节日**：圣诞、母亲节、万圣节、生日等；
15. **兼容搭配**：适用型号、适合发质、适配设备/场景；
16. **配件/套装/包装**：替换件、收纳盒、几件套、礼品包装；
17. **痛点与期待**：异味、易滑落、破损、清洁困难、耐用诉求；
18. **情绪/心理/价值认同**：安心、体面、陪伴、愉悦、健康、环保；
19. **购买意图与路径**：了解、比较、规格筛选、购买、替换/复购、送礼；
20. **风险/其他**：无关、宽泛误导词、疑似商标/IP、绝对化/医学功效词。

同一个词可有多个标签，但必须给出标签所属维度和识别证据；“厚发”不能随意既当作材料又当作场景。

## 2.2 标签词典的数据结构

```yaml
tag_id: HAIR_FUNC_STRONG_HOLD
label_cn: 强抓力
dimension: 功能特征
label_en: strong hold
synonyms:
  - strong grip
  - secure hold
match_patterns:
  - "\\bstrong hold\\b"
exclusion_patterns: []
product_categories:
  - hair_accessories
marketplaces:
  - US
source: user_defined_taxonomy
status: active
requires_review: false
business_applications:
  - PPC
  - Listing
  - Visual
```

词典应版本化：`taxonomy_version`、`synonym_rule_version`、`reviewed_by`、`updated_at`，并保留历史映射以支持复现旧报告。

## 2.3 原子标签→组合需求→可执行动作

例：`claw clips for thick hair`：

```text
原始词: claw clips for thick hair
  → 产品: claw clips/抓夹
  → 发质: thick hair/厚发
  → 隐含期望(需验证): strong hold/强抓力
  → 组合需求: 厚发人群 × 抓夹 × 稳固固定
  → 供给验证: 夹齿结构、弹簧力度、产品实测
  → 投放: thick hair 词包的 Exact/Phrase 验证
  → 视觉: 厚发真人佩戴、抓力与尺寸证据
```

**严格区分显性与推断**：`thick hair` 是显性标签；`strong hold` 只是在常见使用意图下的推断，必须设 `inferred=true` 和置信度，不能当成关键词直接出现的词根。

---

# 第三部分 · 标准化价值打分算法 V2.1

## 3.1 先评估数据可用性

对每个 `keyword × demand_group × SKU`：

- `search_volume` 缺失：不能计算真实需求加权量；
- `review_evidence` 缺失：痛点缺口只能是待验证假设；
- `own_product_spec` 缺失：`supply_fit=null`；
- `cost_margin` 缺失：不能得出盈利机会或保本 CPC；
- `ads_report` 缺失：不能宣称广告实测价值。

先计算 `data_completeness`（可用证据字段/必需字段）与 `confidence`（高/中/低），再允许给分。

## 3.2 五个 0–100 分子项

| 分项 | 定义 | 证据优先级 |
|---|---|---|
| `D` 需求强度 | 同期搜索量、趋势、标签加权需求与相关搜索份额 | 官方同口径 > 第三方估算 > ABA 代理 |
| `F` 供给匹配 | 0/1/3 映射为 0/33.3/100；缺失则 `null` | 实测规格/可信资料 |
| `G` 未满足需求缺口 | 评论频率、严重度、竞品解决不足、Q&A 反复出现的问题 | VOC 样本与竞品证据 |
| `C` 转化验证 | 广告订单、点击、CVR、CPA、ACOS；SFR/ABA份额不可直接代替实际 CVR | 自己真实投放 > 竞品/市场代理 |
| `P` 利润可行性 | 含 Coupon 后到手价、物流、FBA、佣金、退货、广告前毛利 | SKU 成本核算 |

可先采用：

`ValueScore_raw = 0.35D + 0.25F + 0.15G + 0.15C + 0.10P`

**必须实现的门控**：

1. `F=0`：标签为“不匹配/剔除”，不能因为搜索量高升为 S/A；
2. `F=null`：标签为“待确认供给”，暂不输出可主推等级；
3. `P=null`：只能输出 `需求机会分`，不能输出 `盈利机会分`；
4. `C=null`：可输出“待广告验证”的模型机会，不能写“已验证高转化”；
5. 医疗功效、认证、品牌/IP 或兼容性存在风险：`compliance_status=review_required`，不自动投放。

**缺失值处理**：推荐输出 `ValueScore_partial` + `data_completeness`，只对有数据的子项重新归一化用于探索排序，同时标出**不可与完整分数直接比较**。不要擅自把所有缺失项填 50 分后宣称精确结论。

## 3.3 需求标准化建议

若有同口径搜索量 `V_k`，可以用对数减少超大词支配：

`VolumeScore(k) = 100 × ln(1+V_k) / ln(1+V_max)`

如要反映趋势：

`GrowthScore(k) = clamp(50 + 50 × growth_rate, 0, 100)`

注意：`growth_rate` 用小数，例如 +20%=0.2。样本与跨度必须一致。

可以将 `D = 0.70 VolumeScore + 0.20 TrendScore + 0.10 DemandBreadthScore` 作为**可调整初值**。若无趋势则不强行计算完整 D。

## 3.4 竞争度与机会指数要单列

**需求强并不等于容易进入。** 另设：

- `competition_intensity`：相关竞品数量、头部品牌集中度、Review 门槛、广告 CPC/Top of Search、价格带等；
- `supply_gap`：需求强但竞品页面、参数、评论的解决率弱；
- `own_moat`：供应链成本、差异化技术、专利、认证、交付时效；
- `opportunity_index`：综合需求-供给-竞争-利润的进入机会。

推荐分级：`S/A/B/C/Risk/ReviewNeeded`。各阈值必须允许针对类目回测后修改，**不能把样例阈值认作亚马逊平台标准**。

## 3.5 广告财务约束（若输入 CPC、CVR、售价、利润）

```text
ClicksPerOrder = 1 / CVR
CPA = CPC / CVR
AdRevenuePerOrder = RealizedSellingPrice
ACOS = CPA / AdRevenuePerOrder
BreakEven_ACOS = AdvertisingContributionPerUnit / RealizedSellingPrice
BreakEven_CPC = AdvertisingContributionPerUnit × CVR
Target_CPC = Target_ACOS × RealizedSellingPrice × CVR
```

`AdvertisingContributionPerUnit` 指广告前可用于获客的**贡献利润**，不是未经扣除平台佣金/FBA/运费/促销/预期退货等费用的名义毛利。若 Coupon 改变实际成交价，必须以实际到手价口径核算。

**算例（仅公式示范）**：售价 $49.99、CPC $1.20、CVR 5%，则 20 次点击/单、CPA=$24、ACOS≈48.01%。若单件可投广告贡献利润只有 $6、CVR 8%，保本 CPC=$0.48。**这不是任何具体 ASIN 的实测盈利能力**。

---

# 第四部分 · 价值验证与广告自动诊断

## 4.1 三阶段

### 阶段 A：价值验证（PMF）

以 `Fit=3 + 可解释需求点` 为单位控制预算，先用 Exact/Phrase 观察：展示、CTR、CPC、点击、CVR、CPA、ACOS、评论/退款。验证的是**用户需求与当前产品之间的匹配**，不是盲目争抢大词排名。

### 阶段 B：已验证价值的拓展

在真实转换表现达到目标后，扩展相关 Phrase/Broad、近义搜索词、高相似商品投放和目标竞品 ASIN，保持需求组归因统一。

### 阶段 C：流量泛化

成熟后加自动广告、类目商品投放、相近价值主张和更广覆盖；检查新流量是否挤占核心需求预算。将 Search Term 的新需求标签回流词典。

## 4.2 广告健康诊断建议

至少按 `Campaign → Ad Group → Targeting → Search Term → Placement` 五层记录：

`impressions | clicks | CTR | CPC | spend | orders | sales | CVR | CPA | ACOS | ROAS | TACOS(需总销售口径) | placement | period | budget | keyword_rank`。

人工阈值不能机械照搬：高 CPC 但高 CVR 可能盈利；20 点击零单可作为**复核触发**，并结合预期 CVR、统计不确定性、样本量和新品阶段决定是否否词或降价。默认仅建议，**不自动执行否定、暂停或加预算**。

## 4.3 按需求组归因的复盘格式

```text
需求点: 宠物家庭除异味
供给证据: 活性炭滤网结构和测试（实际待输入）
关键词组: air purifier for pets, air purifier for odors, ...
广告实体: SP-Exact-Pet, SP-Phrase-Pet, SP-Product-Pet
本期: 展示 / 点击 / 订单 / 广告销售 / 花费 / CVR / ACOS
与上期差异: 点击质量 / 页面转化 / 出价 / 竞争变化
结论: 已验证 / 继续测试 / 暂停该假设
动作: 关键词 / 广告 / Listing / 视觉 / 供给研发
审批状态: draft
```

---

# 第五部分 · 场景化例子（仅示意，不代表已采集市场数据）

## 5.1 美国空气净化器

| 关键词 | 显性标签 | 可能的组合意图 | 投放和视觉建议 |
|---|---|---|---|
| air purifier for bedroom | 品类、卧室场景 | 卧室空气舒适 | 低噪参数与睡眠场景；需验证低噪功能 |
| air purifier for pet hair | 品类、宠物毛发痛点 | 养宠家庭清洁 | 宠物场景图、滤网能力证据 |
| true hepa air purifier | HEPA功能 | 过滤性能认知 | 只有真实符合技术参数才能强匹配 |
| levoit air purifier filter | 竞品品牌、配件/滤芯 | 特定品牌滤芯替换需求 | 若无合法兼容产品，应隔离或排除 |

## 5.2 美国 Hair Clips

| 关键词 | 标签拆解 | 组合需求 | 供给检查 |
|---|---|---|---|
| claw clips for thick hair | 抓夹 × 厚发 | 厚发抓力 | 弹簧/齿形、夹持实测 |
| flat hair clips for women | 扁平抓夹 × 女性 | 平躺舒适/造型 | 扁平结构、佩戴舒适 |
| flower hair clips | 花朵图案 | 情绪审美、搭配 | 实际造型和材质 |

## 5.3 德国 Polsterreiniger / Waschsauger

| 关键词 | 标签拆解 | 风险与建议 |
|---|---|---|
| polsterreiniger gerät | 布艺/软垫清洁机 | 主品类强相关；供给匹配仍按 SKU 验证 |
| nasssauger | 湿式吸尘器泛词 | 意图较宽，不必然是喷洗抽吸布艺机 |
| sofa reiniger gerät | 沙发场景 × 清洁机 | 沙发痛点图，Exact/Phrase 价值验证 |
| waschsauger mit dampffunktion | 抽洗机 × 蒸汽功能 | **只有产品实际带蒸汽功能才可打强匹配** |

---

# 第六部分 · Excel/数据库输出标准

## 6.1 默认九张 Sheet

| Sheet | 必备字段/目的 |
|---|---|
| `01_原始词库` | 源文件全部字段、源行号、数据窗口、来源、不可覆盖 |
| `02_清洗关键词` | normalized_keyword、语言、同义词标准化、品牌/IP/无效词识别 |
| `03_原子标签结果` | keyword_id、多维原子标签、是否显性、置信度、证据 |
| `04_SIF词频统计` | TF、DF、出现占比、真实加权词频或 ABA 代理权重、代表关键词 |
| `05_需求供给矩阵` | demand_group_id、需求规模、SKU 卖点、Fit(0/1/3/null)、证据和缺口 |
| `06_机会与风险评分` | D/F/G/C/P、部分/完整得分、竞争度、评级、缺失字段、限制条件 |
| `07_高机会词清单` | 只输出合规且供给已确认的主推候选；待验证另列 |
| `08_广告结构规划` | Demand → Campaign → Ad Group → Keyword/ASIN → 匹配模式/预算建议 |
| `09_标签词典与方法说明` | 词典、规则版本、公式、变更记录、质量检测 |

若已有用户指定表结构，**尽量保留原字段和原 sheet，新增列/新增工作表**；不要把所有来源混在一起后丢掉来源信息。

## 6.2 主表列建议

```text
source_row | marketplace | category | asin | raw_keyword | normalized_keyword
keyword_translation_cn | source | window_days | search_volume | aba_rank
search_volume_estimated | growth_90d | growth_180d | click_share | purchase_share
product_type | audience | scene | function | style | color | material
size | capacity | technical_spec | theme | brand | season | holiday
compatibility | accessory | pain | emotion | value_identity | purchase_intent
atomic_tags | inferred_tags | composite_demand | evidence_refs | tag_confidence
demand_group_id | DF_count | WeightedDemand | ABA_rank_proxy | D_score
supply_fit_0_1_3 | supply_evidence | review_gap_score | conversion_score
profit_score | value_score_partial | value_score_full | competition_intensity
opportunity_level | compliance_status | recommended_campaign
recommended_ad_group | match_type | visual_angle | listing_angle
product_action | human_review_needed | taxonomy_version
```

**Excel 提醒**：

- 冻结表头、筛选、统一币种和百分比格式；
- 日期必须保留实际报告日期，不能用系统运行日替换；
- 数值列是数值，不能把 `1.5%` 写成任意文本再用于公式；
- 加权词频需要保留计算口径列；
- 大词、品牌、风险、配件、待验证分开展示；
- 有真实搜索量则按同期加权；只有 ABA 排名则输出排名代理，不混称“搜索量”。

## 6.3 机器可读输出 JSON

```json
{
  "keyword_id": "DE|polsterreiniger geraet|niche|360d",
  "raw_keyword": "polsterreiniger gerät",
  "locale": "de-DE",
  "source": "niche_insights",
  "search_volume": null,
  "search_volume_window_days": 360,
  "explicit_tags": [
    {"dimension": "product_type", "tag": "upholstery_cleaner"}
  ],
  "inferred_tags": [],
  "demand_group_id": "DE_UPHOLSTERY_CLEANING",
  "supply_fit": null,
  "fit_reason": "尚未提供本次待推广 SKU 的产品供给参数",
  "scores": {"D": null, "F": null, "G": null, "C": null, "P": null},
  "opportunity_level": "review_needed",
  "ads_recommendation": "供给确认后决定 Exact/Phrase 验证",
  "compliance_status": "pending_check"
}
```

---

# 第七部分 · Agent 执行步骤（必须按顺序）

1. **读取数据**：识别所有 sheet、列名、行数、日期、站点、关键词口径；记录源文件信息。
2. **确认产品主数据**：SKU/ASIN、目标商品形态、实际卖点与利润；缺少时启用 `demand_only_mode`。
3. **建立分类词典**：按站点和品类调用已有词典，并提取候选新增词根；品牌、IP、通用词需人工复核。
4. **清洗与多标签打标**：输出显性词根和推断意图，建立原词到标签的证据映射。
5. **计算 TF / DF / 加权需求**：有真实搜索量就按真实口径；仅有 ABA 排名就用代理且标明。
6. **构建消费者需求簇**：通过人群×场景×痛点×功能×产品组合形成 `demand_group_id`。
7. **做供给适配**：依据产品规格赋 0/1/3/null；记录证据与未满足需求。
8. **计算价值机会**：分开报告需求、Fit、痛点缺口、转化、利润与竞争度；缺失项写明。
9. **生成广告结构**：按需求分类、匹配模式和流量集中度建活动草案；不给出无证据的“必赚”判断。
10. **生成迁移建议**：标题、五点、A+、主图、副图、视频、包装、配件、产品改良。
11. **生成质检报告**：统计总词数、无效词、品牌词、配件词、缺失值、同义词冲突、规则命中率。
12. **输出并验证**：实际生成文件后检查中文编码、行数、字段、公式和文件是否存在；无文件不得提供下载链接。

### 质量验收标准

- 关键词全量覆盖率 = 已输出关键词 / 有效原始关键词；
- 每条非空词至少有 `product_type` 或 `other/unclassified`；
- 允许多标签，但每条标签必须可追溯到词典规则/证据；
- 真实搜索量与排名代理必须严格分开；
- 品牌/IP/配件/低相关词不会混入“无条件核心必打”；
- `Fit=0`、`Fit=null` 不会被误判为 S/A 主推；
- 评分变量的来源、缺失与公式能复现；
- 广告结构建议和 `demand_group_id` 一一对应，有去重规则；
- 中文、德语变音、英文与特殊字符可正确打开，无乱码或替换字符 `U+FFFD`。

---

# 第八部分 · 标准执行提示词（复制可用）

```text
你是「亚马逊关键词需求打标与SIF价值打法分析师」。
输入：站点、品类、用户上传词库/ABA/商机探测/广告报告、产品SKU及实际卖点。
严格执行：
1. 识别全部Sheet与数据口径，不丢失原始信息；
2. 清洗关键词，输出显性原子标签和推断标签；
3. 根据品类名称、目标受众、使用场景、功能特征、风格款式、颜色、材质、
   尺寸、容量、参数、主题元素、品牌、季节、节日、兼容搭配、配件、
   痛点、情绪心理、购买意图等维度进行多标签分类；
4. 计算TF、标签出现次数DF、真实搜索量加权需求；无真实搜索量时只用ABA排名代理；
5. 把自家产品卖点与需求点按0/1/3/null匹配，缺少证据不得标3；
6. 计算需求分、供给分、VOC缺口、转化、利润和竞争；无法计算的项标缺失；
7. 以需求点为中心设计Campaign、Ad Group、关键词与Exact/Phrase/Broad/Auto、商品投放；
8. 以同口径搜索量集中度决定是否拆SKAG，需求归因必须统一；
9. 输出高机会/待验证/风险/配件/竞品词，以及Listing、视觉、产品升级建议；
10. 交付结果主表、SIF词频、供需匹配、评分、广告架构、标签词典、质检说明。
禁止：凭空编造关键词流量、评价、利润、CPC、CVR和认证；
      未经审批修改广告、动用资金或对外发布。
```

---

# 第九部分 · 版本说明

**V2.1.0（2026-11-17）**

- 解决先前 Markdown 乱码问题：提供标准 UTF-8 Skill 与 Windows 兼容 UTF-8 BOM 版本。
- 严格复原 SIF 六步价值打法，以及“价值验证 → 拓展 → 泛化”的三阶段路径。
- 明确区分 TF、关键词标签 DF、真实搜索量加权词频、ABA 排名代理。
- 区分“0→1→3 数据颗粒度”与“0/1/3 供给匹配分”，并允许缺失 `null`。
- 防止未经核实将竞品功能、评论痛点或销量推断为自家产品能力。
- 新增机会评分的缺失项门控、来源可追踪、广告需求归因与质检清单。
- 适配空气净化器、hair clips、布艺清洗机多品类的基础词典框架。

**源材料说明**：本 Skill 的六步方法依据用户提供的 SIF《价值打法》材料整理；具体的计算公式、权重、工程门控与数据结构均是本 Skill 的增强实现，应在真实品类数据上回测和校准。
