---
name: amazon-feature-word-analysis
description: 亚马逊特征词分析技能（搜索词报告词根拆解/单词+双词n-gram聚合/CPC·CTR·CVR·ACOS·CPA全指标/目标BID测算）。当用户提到"特征词分析"、"词根分析"、"广告词根"、"搜索词报告分析"、"搜索词拆词"、"n-gram"、"哪些词根在烧钱"、"哪些词根出单"，或上传亚马逊广告后台搜索词报告（7天/30天/90天）要求分析时，务必使用此技能。即使用户只说"帮我看看这份搜索词报告"、"这些词哪些该否掉"、"广告词整理一下"，也应触发此技能。输出为 Excel 多 Sheet 分析表（单词结果 + 双词结果 + 出价建议），可选交互式 HTML 报告。
---

# 亚马逊特征词分析（Feature Word Analysis）

把亚马逊广告后台搜索词报告（Search Term Report）拆解为**单个词（1-gram）**与**两个词组合（2-gram）**的词根级聚合结果，为每个词根算出完整广告指标（CPC / CTR / CVR / ACOS / CPA），并结合目标 ACOS 与客单价给出目标 BID（CPC 上限）建议。

## TRACE 原则

- **T (Trigger)**：用户上传搜索词报告或提到词根/特征词/搜索词分析即触发，不等用户给全参数。
- **R (Required data)**：必需字段缺失先向用户确认列名映射，绝不猜数据含义；客单价/目标 ACOS 缺失时只出指标不出出价建议。
- **A (Assumption)**："15 个点击出一单"等经验值一律标注 `engineering_assumption`；报告归因窗口（7 Day）按亚马逊官方口径。
- **C (Calculate)**：一律用 `scripts/feature_word_analyzer.py` 计算，不手算，保证口径一致、结果可复现。
- **E (Explain)**：每个高消耗词根给出动作建议（加价 / 降价 / 否定 / 拓词），不只丢一张表。

## 触发条件

- 用户上传广告后台搜索词报告（CSV / XLSX，7 天 / 30 天 / 90 天任意时间段）
- 用户要知道：哪些词根在烧钱不出单、哪些词根 CVR 高值得单独打
- 用户要做：否定词清单、拓词方向、词根级出价（目标 BID）
- 用户提到：特征词、词根、拆词、n-gram、搜索词聚合

## 数据要求（R 步骤）

### 必需字段（列名自动模糊匹配，中英文均可）

| 标准字段 | 常见列名变体 |
|---|---|
| Customer Search Term | 消费者搜索词 / Customer Search Terms / 客户搜索词 |
| Impressions | 曝光量 / 展示量 |
| Clicks | 点击量 |
| Spend | 广告花费 / 花费 / Cost |
| 7 Day Total Sales | 7天总销售额 / 14 Day Total Sales（其它归因窗口同样接受） |
| 7 Day Total Orders (#) | 7天总订单量 / Orders |

### 可选参数（用于出价建议）

- `--price` 客单价（美金/英镑等，与报告币种一致）
- `--target-acos` 目标 ACOS（如 0.30）
- `--min-clicks` 词根最低点击数门槛（默认 1，建议 ≥5 再看 CVR 结论）

## 执行流程（C 步骤）

```bash
pip install pandas openpyxl --break-system-packages --quiet

# 基本分析（只出指标）
python scripts/feature_word_analyzer.py 搜索词报告.xlsx -o 特征词分析结果.xlsx

# 带出价建议（推荐）
python scripts/feature_word_analyzer.py 搜索词报告.xlsx \
    -o 特征词分析结果.xlsx --price 30 --target-acos 0.30 --min-clicks 5

# 可选：同时输出 HTML 交互报告
python scripts/feature_word_analyzer.py 搜索词报告.xlsx \
    -o 特征词分析结果.xlsx --html 特征词分析报告.html --price 30 --target-acos 0.30
```

## 输出结构（固定模板）

Excel 包含 4 个 Sheet：

1. **原始数据（清洗后）**：保留 6 个必需字段 + 派生指标（CPC/CTR/CVR/ACOS/CPA），按 Spend 降序
2. **单词结果（1-gram）**：每个词根聚合 Impressions/Clicks/Spend/Sales/Orders → 派生全指标，附出现的搜索词数
3. **双词结果（2-gram）**：相邻两词组合的同口径聚合，并列出组合内两个单词各自的 CVR/ACOS/CPA 供对照
4. **出价建议**（提供 price+target-acos 时生成）：每个词根的 CPC上限 = 目标ACOS × 客单价 × 词根CVR，与实际 CPC 对比，给出【加价/维持/降价/候选否定】标签

## 指标口径（共识公式）

```
CPC  = Spend / Clicks
CTR  = Clicks / Impressions
CVR  = Orders / Clicks
ACOS = Spend / Sales
CPA  = Spend / Orders
CPC上限（目标BID） = 目标ACOS × 客单价 × CVR
CPA目标            = CPC上限 / CVR = 目标ACOS × 客单价
日广告预算         = 预计日单量 × CPA
```

ACOS 与 CPA 成正比（售价固定时）：`ACOS = CPA / 客单价`。

## 判读规则（E 步骤）

| 情形 | 判定 | 建议动作 |
|---|---|---|
| 词根 Clicks ≥ 出单临界值（默认15，`engineering_assumption`）且 Orders = 0 | 烧钱不出单 | 候选否定（词组否定该词根） |
| 词根 CVR ≥ 全表平均 CVR × 1.5 且 Clicks ≥ min-clicks | 高转化词根 | 拓词/提价，考虑单独精准打 |
| 实际 CPC > CPC上限 × 1.2 | 出价过高 | 降价至 CPC 上限附近 |
| 实际 CPC < CPC上限 × 0.8 且 CVR 达标 | 有加价空间 | 小步加价抢位 |
| 词根 CVR < 目标 CVR 长期 | 结构性问题 | 客单价固定下 CVR 不达标则目标 ACOS 长期无法达成（提示优化 Listing 而非只调价） |

新品期策略提示：前期可用全部毛利做广告（ACOS = 毛利率，平本打法），后期 CVR 稳定后压 CPC、控 ACOS 拉利润。深度盈亏三态测算转交 `amazon-ppc-economics` 技能。

## 参考资料

- `references/methodology.md`：完整方法论——数据来源、清洗规则、n-gram 拆词逻辑、出价策略（保守/正常/激进）、梯度预估法、整体转化率拆分。首次使用或用户追问"为什么这样算"时阅读。
