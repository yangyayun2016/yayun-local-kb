---
name: hot-product-lifecycle-judgment
description: 判断产品方向或ASIN是否处于红利期，避免追高进入衰退或过度拥挤市场
version: 1.0.0
author: assistant
trigger: 爆品生命周期 / 判断时机 / 红利期 / 衰退期 / 进入时机 / 产品趋势
requires:
  bins: [python3, openpyxl]
  config: []
  mcp: [sorftime]
---

# 爆品生命周期判断

判断一个产品方向或 ASIN 是否仍处于红利期，避免追高进入已经衰退或过度拥挤的市场。

## 输入参数
| 参数 | 说明 | 示例 |
|------|------|------|
| 站点 | Amazon 站点 | US |
| 关键词 | 核心产品词 | portable blender |
| 代表 ASIN | 可选，建议 3-5 个 | B09XXXXXX |
| 目标月份 | 可选 | yyyyMM |
| 趋势周期 | 默认近 12-14 个月 | |
| 启用 Google 趋势 | 是 / 否 | |
| 关注维度 | 销量/搜索/价格/BSR/新品 | |

## 执行步骤
1. **关键词趋势** - keyword_research_trends 查询搜索量/购买量/购买率/同比/环比
2. **外部验证** - google_trend 判断 Google 搜索热度同步情况
3. **竞品分析** - competitor_lookup 查询市场上架时间/销量增长/销售额增长
4. **ASIN 预测** - asin_prediction 查询代表 ASIN 近 14 个月趋势
5. **新品研究** - product_research 判断新品数量和销售表现

## 输出格式
HTML 报告，包含：
- 生命周期阶段（萌芽期/增长期/成熟期/衰退期/季节波动）
- 趋势证据（Amazon搜索/购买/Google/头部ASIN/新品）
- 机会判断（能否进入/快进快出/差异化/红海化）
- 风险提示（搜索下降/销量集中老品/价格下探/新品难出单）

## 异常处理
- 缺少关键词：追问用户
- ASIN 无数据：扩大范围至关键词市场
- 趋势周期过短：自动扩展至可获取范围
- MCP 调用失败：提示重试
