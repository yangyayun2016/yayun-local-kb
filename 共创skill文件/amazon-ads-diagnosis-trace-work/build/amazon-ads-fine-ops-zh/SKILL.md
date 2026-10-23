---
name: amazon-ads-fine-ops-zh
description: |
  中文亚马逊精细化运营与广告优化诊断 skill，用于店铺维度和单个 ASIN/SKU 维度的广告智能诊断、ACOS/TACOS/CVR/ROAS/CPC/预算异常分析、盈亏平衡ACOS与毛利止损、广告活动/搜索词/广告位/预算打满/竞品/ABA/SIF线索交叉验证，并输出“店铺-星辰大海 北美站US-日期诊断 ACOS提升（极高）”或“ASIN-星辰大海 北美站US-日期诊断 ACOS提升（极高）”这类中文处理清单、根因链路和可执行动作。Use when 用户要求亚马逊店铺诊断、ASIN或SKU诊断、广告健康扫描、ACOS暴涨、广告亏损、自然流量掩盖广告亏损、广告预算止损、关键词治理、广告位下钻、竞品对标、ABA搜索词绩效或精细化运营复盘。
---

# 亚马逊精细化广告诊断

## 核心目标

把店铺、ASIN、SKU、广告活动、搜索词、广告位、竞品和利润数据转成中文广告诊断处理清单。输出必须能帮助运营判断：哪里在烧钱、为什么亏、先停什么、保什么、加什么、还缺什么数据。

## TRACE 执行原则

- Trust: 只把用户提供的报表、TJ OS 数据、Amazon Ads 报告、ABA、SIF、卖家精灵、竞品截图或明确口径当作事实；不要编造 ASIN、活动名、关键词、利润率、排名或已执行动作。
- Reliability: 先做数据完整性检查，再判断异常级别；缺搜索词报告、广告活动报告、广告位明细或利润口径时，必须写清无法定位的部分和补数要求。
- Adaptability: 根据“店铺维度”或“ASIN/SKU维度”选择诊断路径；不要把纯 Listing 文案、泛市场分析或非亚马逊广告问题误触发成本 skill。
- Convention: 主流程保持短，按需读取 `references/`；输出使用固定处理清单和报告结构，方便 TJ OS 自动展示。
- Effectiveness: 每条动作都必须包含对象、证据、动作、预期影响、风险和确认状态；高影响止损动作写成“建议/需人工确认”，不得写成已执行。

## 模式选择

1. 店铺维度诊断：用户说“店铺诊断、店铺维度、账号、站点、全店 ACOS、店铺-星辰大海 北美站US-日期诊断”时，读 `references/store-diagnosis.md`。
2. ASIN/SKU 维度诊断：用户给出 ASIN、SKU、父体/子体、产品维度或“ASIN-星辰大海 北美站US-日期诊断”时，读 `references/asin-sku-diagnosis.md`。
3. ACOS/利润止损：出现 ACOS 提升、广告亏损、负毛利、盈亏平衡 ACOS、CVR 下滑或自然流量掩盖广告亏损时，读 `references/acos-profit-guardrails.md`。
4. 数据接入与字段归一：用户上传广告报表、TJ OS 表、ABA、SIF、卖家精灵或复制表格时，读 `references/data-contract.md`。
5. 关键词、广告位和流量结构：用户要求搜索词、Campaign、预算打满、广告位、竞品对标、ABA 词机会时，读 `references/traffic-keyword-workflow.md`。
6. 输出处理清单或完整报告：用户要求“处理清单、完整 prompt、完整版本、报告单、智能诊断列表”时，读 `references/output-templates.md`。

如果多个模式同时命中，先做数据完整性与利润止损，再做店铺或 ASIN/SKU 诊断，最后输出处理清单。

## 默认诊断流程

1. 识别维度：店铺、站点、账号、ASIN、SKU、父体/子体、日期、诊断主题和严重度。
2. 识别数据源：TJ OS 数据库、Amazon Ads 报表、Campaign 操作日志、ABA、SIF、卖家精灵、竞品数据、利润表、库存表、Listing 质量。
3. 校验利润口径：区分广告前毛利率、广告后毛利率、盈亏平衡 ACOS、目标毛利率和广告亏损金额。
4. 判断异常级别：ACOS 是否高于盈亏平衡、CVR 是否下降、花费是否未收紧、CPC 是否上涨、预算是否打满、自然流量是否掩盖广告亏损。
5. 下钻责任对象：店铺层先找异常 ASIN/SKU 和 Campaign 集群；ASIN/SKU 层再下钻 campaign、ad group、keyword/search term、placement、budget、竞品与 ABA。
6. 建立根因链：市场/竞品变化 -> CPC/预算/曝光变化 -> 广告流量质量 -> CVR/订单 -> ACOS/毛利 -> 排名/BSR。
7. 输出动作清单：先止损，再修结构，再放量，再中期布局。
8. 标注数据缺口：缺少搜索词、活动、广告位、预算打满、利润或竞品数据时，明确写出补充数据和用途。

## 默认输出

优先输出短处理清单；当用户要求完整报告时再展开。

```text
处理清单：店铺-星辰大海 北美站US-YYYY-MM-DD诊断   ACOS提升（极高）
或
处理清单：ASIN-星辰大海 北美站US-YYYY-MM-DD诊断   ACOS提升（极高）

诊断摘要：
核心证据：
根因判断：
建议动作：
需补充数据：
确认状态：
```

## 高影响动作确认

以下动作必须写成“建议人工确认/候选动作”，不能写成已执行：降低全店或 ASIN 广告预算、暂停 Campaign/Ad Group/Keyword、否定搜索词、提高预算、提高 bid、关闭搜索首位倍增、跨 ASIN 预算迁移、重建 Campaign 架构。

## 不适用场景

- 没有广告、销售、利润或搜索词数据，却要求精确判断具体亏损词。
- 要求直接登录 Amazon Ads 后台操作。
- 只做通用运营知识解释，不需要诊断、归因或动作清单。
- 要求凭空判断竞品、ABA、SIF、库存、利润或排名。
