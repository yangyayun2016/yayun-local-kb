# 亚马逊竞品ASIN推广节奏分析 Skill

## 功能
对亚马逊竞品ASIN进行系统化的推广节奏分析，自动生成一份结构化的HTML报告。

## 报告模块
1. **报告头部** — 核心指标卡片（销量/销售额/评论增长/BSR）
2. **关键时间节点** — 时间线展示（上架/首评/改价/DEAL/广告等）
3. **核心趋势图表** — 排名/价格/评论综合趋势 + 月度销量柱状图 + 评论柱状图
4. **前4月汇总表** — 按月汇总关键指标
5. **月度推广节奏拆解** — Listing/价格/评论/流量策略 + 风险判断
6. **效果总结** — 排名变化/累计销量/成交额
7. **明细数据表** — 多维度聚合（日/周/月），可折叠展开

## 触发关键词
`竞品分析` `ASIN分析` `推广节奏` `竞品拆解` `对标分析`

## 数据源
- 卖家精灵MCP（asin_detail / keepa_info / traffic_keyword_stat 等）
- SIF MCP（ops_get_asin_sales_trend / ops_get_asin_traffic_trend 等）

## 目录结构
```
amazon-competitor-analysis/
├── SKILL.md                      # 技能主文件
├── README.md                     # 说明文档
├── references/
│   └── report-template.md        # HTML报告模板 + CSS + Chart.js配置
└── B0DY4S3HP2_竞品分析报告.html   # 示例报告
```

## 安装
下载 `.skill` 文件后导入 Claude 即可使用。
