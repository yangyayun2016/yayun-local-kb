amazon_analysis


```
# Skill: Amazon Competitor & Market Researcher
# ID: amazon_analysis
# Description: 深入研究亚马逊竞品，分析其优缺点、定价策略、评论痛点，并提供优化建议。

## Context
当用户提供一个亚马逊产品链接、ASIN 或关键词时，调用此 Skill。该 Skill 旨在利用 Tavily 联网能力获取最新市场数据，并结合电商运营逻辑生成报告。

## Workflow
1. **数据抓取**：使用 `web_search` (Tavily) 检索该产品的基本信息、当前价格、BSR 排名及主要竞争对手。
2. **痛点挖掘**：搜索该产品及同类竞品的差评（Critical Reviews），提取用户最不满意的 3 个点。
3. **差异化分析**：对比用户产品与 Top 3 竞品的参数（如尺寸、功率、材质）。
4. **策略建议**：基于以上数据，给出 Listing 优化或产品改良建议。

## Tool Requirements
- `web_search`: 必须启用 Tavily 深度搜索。
- `mcp`: 需要访问存储在数据库中的历史销售数据（如有）。

## Output Format
请按以下结构输出报告：
---
### 📊 亚马逊竞品分析报告 - [产品名称]
- **市场现状**：[价格区间 / 竞争程度]
- **竞品 Top 3**：[ASIN/链接及核心卖点]
- **消费者痛点 (Critical Insights)**：
  1. [痛点 1]
  2. [痛点 2]
- **建议动作**：[如：修改图片、增加某项功能、调整定价]
---

## Examples
User: "分析这个 ASIN: B0XXXXXXXX 的竞争对手。"
Agent: "正在使用 Tavily 检索 B0XXXXXXXX 的实时数据... 发现主要对手为 [Brand A]，其优势在于..."

```

---