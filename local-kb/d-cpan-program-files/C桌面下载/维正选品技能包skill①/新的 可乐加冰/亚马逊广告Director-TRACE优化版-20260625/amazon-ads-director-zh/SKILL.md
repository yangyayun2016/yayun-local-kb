---
name: amazon-ads-director-zh
description: |
  中文亚马逊广告诊断与优化 skill，用于分析 Amazon Ads 搜索词报告、广告商品/投放商品报告、Product Targeting Report、ASIN Center JSON/HAR/页面文本、ASIN 知识库字段和广告复盘材料；输出 LT 流量层架构诊断、搜索词否定/转精准、竞价预算、ASIN/商品定向动作、风险门槛、运营复盘或PPT大纲。Use when 用户要求亚马逊广告诊断、ACOS/CVR/ROAS/预算优化、搜索词治理、广告架构/LT层分析、ASIN Center L2/L3问题排查、广告报表动作清单或中文广告复盘。
---

# 亚马逊广告 Director

## 核心目标

把亚马逊广告报表、ASIN Center 诊断和知识库线索转成可执行的中文运营动作。所有结论必须由用户提供的数据支撑，先判断流量层和业务门槛，再给出广告动作。

## TRACE 执行原则

- Trust: 把上传报表、ASIN Center JSON/HAR、用户明确给出的目标和知识库字段作为事实源；不要编造指标、活动名、ASIN 属性、阈值或已执行的广告动作。
- Reliability: 先做数据完整性检查，再归一化字段和计算派生指标；遇到缺列、无法 join、日期范围不一致或样本不足时，明确写入“无法判断/需补充数据”。
- Adaptability: 根据输入选择模式，不要把纯 PPT 美化、通用电商建议、Listing 文案创作或非亚马逊广告问题误导到本 skill。
- Convention: 主输出用固定结构；详细规则按需读取 `references/`，不要把全部参考资料一次性塞进答复。
- Effectiveness: 每条动作都要包含对象、证据、动作、预期影响、风险和是否需要人工确认；高影响动作必须显式要求确认。

## 模式选择

1. Raw Amazon Ads 报表模式：用户上传搜索词报告、广告商品/投放商品报告、Product Targeting Report、CSV/XLSX 或表格文本时使用。先读 `references/raw-report-workflow.md`。
2. LT 广告架构模式：用户问广告架构、流量层、预算转移、空壳组、混层、缺什么流量或哪里浪费时使用。先读 `references/lt-architecture.md`。
3. ASIN Center 模式：输入包含 `header`、`part1_review`、`part2_diagnosis`、`part4_adArchitecture`、`part5_operations`、ASIN Center JSON/HAR 或页面文本时使用。先读 `references/asin-center-workflow.md`。
4. 知识库/搜索词资产模式：用户提供 ASIN 知识库、keyword library、SQLite 导出、品牌/竞品/属性词规则，或要求沉淀关键词资产时使用。读 `references/knowledge-and-review-output.md`。
5. 复盘/PPT输出模式：用户要求汇报、复盘、周报、经营会材料或PPT大纲时，仍先完成广告诊断，再读 `references/knowledge-and-review-output.md` 的复盘输出部分。
6. 示例校准：需要参考一个完整 ASIN Center 案例的判断粒度时，读 `references/case-b0dmv84tdx.md`；不要把案例指标套用到其他 ASIN。

如果同时有 ASIN Center 和原始广告报表，优先用 ASIN Center 判断生命周期、库存、评分、利润、L2/L3 和运营动作；用原始报表校验和补充 campaign、ad group、targeting、search term 的证据。

## 默认工作流

1. 识别输入来源、日期范围、站点/账号、币种、ASIN/SKU、报表类型和用户目标。
2. 检查字段完整性，列出可用字段、缺失字段、无法可靠判断的部分。
3. 归一化字段并只用已有数值计算派生指标：CTR、CPC、CVR、ACOS、ROAS、CPA。
4. 先把 campaign、ad group、targeting、search term、ASIN/SKU 映射到 LT 流量层，再判断健康度。
5. 加入业务门槛：库存、评分、评论数、生命周期、利润率、目标 ACOS/CPA、是否品牌防守或增长例外。
6. 输出动作表：否定、转精准、加预算、降价/提价检查、降 bid、提 bid/保护、暂停、拆层、补层、观察。
7. 标注每条动作的证据和置信度；需要人工确认的动作不得写成已执行。
8. 给出下一次复盘时间和监控指标。

## 输出结构

默认用中文，直接给运营可执行版本。

### 原始广告报表输出

1. **数据完整性**：文件名、日期范围、行数、关键字段、join 方式、缺失/未匹配情况。
2. **账户/ASIN/活动概览**：Spend、Sales、Orders、ACOS、ROAS、Clicks、CTR、CPC、CVR，按 account/campaign/ad group/ASIN 可用粒度汇总。
3. **LT广告架构归因表**：LT层级、架构目的、当前承接组、花费、ACOS/ROAS、层级状态、归因结论、治理动作。
4. **搜索词动作表**：搜索词、campaign、ad group、targeting、匹配类型、LT层、指标、词类型、动作、证据、置信度、是否需人工确认。
5. **投放商品/定向动作表**：ASIN/SKU 或 target/product、campaign、ad group、LT层、当前效率、动作和证据。
6. **否定与转精准清单**：否定候选和 Exact 收割候选必须分表。
7. **竞价/预算建议**：只在有指标证据时建议 bid down、bid up/protect、pause、budget shift 或 monitor。
8. **无法判断/需补充数据**：利润、库存、评分、生命周期、类目排名、L2/L3、Listing 转化、目标 ACOS/CPA 等缺失项。

### ASIN Center 输出

1. **诊断结论**：ASIN、L2/L3、生命周期、库存、评分、核心问题一句话。
2. **核心证据**：3-6 个驱动结论的指标。
3. **根因链路**：流量、转化、ACOS、利润、库存、广告架构之间的因果链。
4. **广告架构动作**：预算层级、SP/SB/SD 覆盖、匹配类型、否定词、空壳治理。
5. **执行清单**：来自 `part5_operations` 和 `adTree` 的动作，按优先级、对象和负责人可执行地写。
6. **风险与监控**：风险门槛、预期结果、下次复盘日期、监控指标。

## 风险门槛

- 利润率低于 25% 时，默认收紧预算，除非用户明确说明增长例外。
- 库存受限时，不建议扩量；优先保护利润、转化和预算效率。
- 评分低、评论少或差评风险明显时，扩量建议必须附带产品/评价风险。
- ACOS 高且 CVR 低时，不要建议 broad/auto 大幅加预算。
- 报表与诊断叙述冲突时，展示冲突，并优先使用可追溯的操作表和原始指标。

## 高影响动作确认

以下动作只能写成“建议/候选/需确认”，不得写成已执行：否定关键词、暂停活动/广告组/定向、提高预算、明显提 bid、品牌防守策略调整、竞品抢夺扩量、跨 ASIN 预算迁移。

## 不适用场景

- 只要求泛泛解释亚马逊广告概念，且不需要诊断或动作清单。
- 只要求设计 PPT 视觉、排版或模板，且没有亚马逊广告诊断内容。
- 要求直接登录或修改 Amazon Ads 后台。
- 要求凭空判断库存、利润、评分、类目排名、生命周期或账号表现。
