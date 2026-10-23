# Amazon Competitor Analysis Skill

亚马逊竞品ASIN推广节奏分析技能 — Claude Custom Skill

## 功能

对任意亚马逊ASIN进行系统化的推广节奏拆解，自动生成包含以下内容的HTML可视化报告：

- 核心指标概览（销量、销售额、评论增长、BSR排名）
- 关键时间节点时间线
- 排名/价格/评论趋势图表（Chart.js）
- 月度推广策略拆解（定价、评论、流量、广告）
- 风险预警（刷单嫌疑、排名异常）
- 完整明细数据表

## 技能结构

```
amazon-competitor-analysis/
├── SKILL.md                  # 技能说明文件（必需）
├── references/
│   └── report-template.md    # HTML报告模板、CSS样式、Chart.js配置
├── scripts/                  # 预留脚本目录
└── assets/                   # 预留素材目录
```

## 依赖的MCP工具

- **卖家精灵MCP**（主要数据源）：asin_detail, keepa_info, asin_prediction, traffic_keyword, traffic_keyword_stat, traffic_listing_stat, review
- **SIF MCP**（补充数据源）：ops_get_asin_sales_trend, ops_get_asin_traffic_trend, ops_get_listing_traffic_overview

## 使用方式

将此文件夹作为 Claude Custom Skill 安装即可。触发示例：

- "帮我分析一下 B0DFY7C9BK 这个竞品的推广节奏"
- "这个ASIN怎么做起来的？"
- 粘贴亚马逊商品链接

## 设计原则

基于 TRACE 五原则构建：

| 维度 | 说明 |
|------|------|
| **T**rust 信任 | 不编造数据，数据缺失明确标注 |
| **R**eliability 可靠性 | 单工具失败不中断流程，异常处理完善 |
| **A**daptability 适用性 | 宽触发条件覆盖多种用户表达方式 |
| **C**onvention 规范性 | 渐进式披露，SKILL.md < 200行，重内容放references/ |
| **E**ffectiveness 有效性 | 输出开箱即用的HTML报告，含图表和风险判断 |

## License

MIT
