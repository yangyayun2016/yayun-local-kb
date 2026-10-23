---
name: amazon-ads-organic-weekly-review
description: |
  用 SIF MCP 为亚马逊新品或在推 ASIN 做每周“广告撬动自然流量”复盘，判断广告曝光或用户提供的广告订单是否沉淀为自然流量、自然排名和关键词权重，并输出中文运营周报。Use when 用户要求“广告撬动自然流量复盘”“新品周复盘”“广告是否带来自然流量”“SIF MCP 周复盘”“亚马逊运营每周复盘”，或提供 ASIN 要分析广告流量、自然流量、关键词排名、Campaign/AdGroup 承载和下周动作。
---

# 亚马逊运营：每周广告撬动自然流量复盘

## Purpose

为亚马逊运营每周产出固定格式复盘，核心问题是：这周广告是在撬动自然流量，还是只是在购买短期销量。

不要只看 ACOS。用 SIF 的流量、广告曝光、关键词排名、Campaign/AdGroup 承载信号，判断广告是否带来自然排名提升、自然流量占比提升、关键词权重沉淀，并给出下周动作。

## Inputs

- 必须有目标 ASIN；没有 ASIN 时先要求用户补充。
- 市场默认 `US`，用户指定其他站点时按用户指定站点。
- 周期默认取 SIF 可用的最近完整周，并与上一完整周对比。SIF 周口径以周日为一周起始日；当周数据不完整时，不把当周当作完整周判断。
- 如果用户提供广告后台订单、花费、ACOS、转化等数据，可以合并分析；如果没有提供，不要编造订单、花费或 ACOS。
- 如果用户只给 ASIN 且没有复盘意图，先确认这是自己的新品/在推 ASIN 还是竞品；如果用户明确要求周复盘，默认按自己的 ASIN 处理。

## Workflow

1. 读取 `references/judgement-rules.md`，按其中的证据链和动作分类做诊断。
2. 读取 `references/report-template.md`，最终严格按模板输出中文周报。
3. 接入 SIF MCP；如果有 `ping` 工具，先调用 `ping` 确认可用。
4. 确定本周与上周窗口：优先用最近完整自然周；需要近 7 天补充时，明确标注“近 7 天滚动口径”，不要混成周口径。
5. 采集流量侧信号：
   - 优先使用可用的 ASIN 流量趋势与关键词明细工具；如果环境提供 `asinOpTrafficTrend` / `asinOpTrafficTrendDetail`，先查周期趋势再下钻关键词。
   - 如果环境提供 `ops_get_listing_traffic_overview`，分别查本周与上周的总流量、自然流量、广告流量及广告占比。
   - 需要看变体承载时，使用 `ops_get_listing_traffic_structure`。
6. 采集广告侧信号：
   - 用 `ads_get_asin_ad_structure` 看历史广告规模和类型分布。
   - 用 `ads_get_asin_ad_traffic_trend` 定位 SP/SB/SBV 曝光变化。
   - 用 `ads_get_asin_campaign_contribution_overview` 找本周主要 Campaign。
   - 对头部 Campaign 用 `ads_get_campaign_contribution_breakdown` 按 `keyword` 和 `ad_group` 下钻。
   - 需要验证广告组和展示 ASIN 时，用 `ads_get_campaign_structure` 与 `ads_get_ad_group_keyword_breakdown`。
7. 采集关键词市场信号：
   - 对关键判断词，必要时用 `market_get_keyword_history` 看搜索量、ABA 排名、Top3 集中度。
   - 对大词/长尾词取舍，必要时用 `market_get_keyword_root_trend` 判断需求是否分散到长尾。
   - 对竞争压力，必要时用 `market_get_keyword_competition` 验证是否被竞品替代。
8. 综合诊断时必须同时看三类证据：广告曝光/贡献变化、自然排名变化、自然流量或自然占比变化。缺一项时，结论要降级为“观察”或“待验证”。
9. 输出固定 6 部分：本周流量变化、自然沉淀词、广告曝光但未沉淀词、自然排名断档词、Campaign/AdGroup 承载、下周动作。
10. 报告末尾必须给一句话结论，并附 SIF 官网验证链接；如果 SIF 工具返回 `render_footer`，原文保留该字段内容。

## Required Questions

报告必须回答：

1. 本周总流量、自然流量、广告流量分别怎么变。
2. 哪些关键词贡献上升，是否伴随自然排名上升。
3. 哪些关键词广告有曝光或订单，但自然排名没有沉淀。
4. 哪些关键词自然排名断档，需要重点关注。
5. 哪些 Campaign/AdGroup 承载了主要曝光。
6. 下周动作分为：加预算或提高 BID、继续观察、降 BID/否词/暂停。

## Evidence Rules

- 结论必须有机制性证据，不要写“可能是竞争加剧”这类空泛判断。写清楚“哪个词/哪个 Campaign 的广告曝光怎么变，自然排名怎么变，自然流量怎么变，所以判断为什么”。
- 区分“广告带来自然沉淀”和“自然本来在增长”。没有广告曝光或广告贡献同步变化时，不把自然增长归因给广告。
- 区分“广告有曝光”和“广告有效”。广告曝光增加但自然排名无改善、自然流量无承接时，归为未沉淀或待验证。
- 对订单、ACOS、花费、转化率只引用用户提供或工具明确返回的数据；SIF 未返回时要明说“本轮 SIF 数据不含订单/花费明细”。
- 每个动作建议都要落到关键词、Campaign 或 AdGroup，不只给泛泛策略。

## Guardrails

- 不输出虚构数据，不把估算写成事实。
- 不建议盲目加预算；只有“广告贡献上升 + 自然排名/自然流量沉淀”同时成立时，才建议保护或小幅加预算。
- 不把一个 ASIN 的变体流量误认为目标 ASIN 流量；发现 Campaign 展示到非目标变体时，要求做结构检查。
- 不把品牌词、防守词、强相关类目词混在一起判断；必要时单独标注。
- 不承诺广告一定能撬动自然流量，只输出基于本周数据的运营判断和下周验证动作。
