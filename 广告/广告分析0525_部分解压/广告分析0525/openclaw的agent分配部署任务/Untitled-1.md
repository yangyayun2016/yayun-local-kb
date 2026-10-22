AI自动化管理与实战分享 — 全技能体系总结
要将亚马逊竞品分析流程固化为 OpenClaw 的能力，你需要编写一个包含**结构化指令（Prompt）**、**工具调用逻辑**和**输出规范**的 Markdown 文件。

以下是为你设计的 `amazon_analysis.md` 模板，专门针对你关注的跨境电商场景：

### 1. 编写 Skill 文件 (`amazon_analysis.md`)

你可以将以下内容保存为本地文件：

```markdown
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

### 2. 使用指令导入 Skill

保存文件后，在终端执行以下命令将其注入 OpenClaw：

```bash
# 假设你的文件放在当前目录下
openclaw skill add ./amazon_analysis.md

```

**验证导入是否成功：**

```bash
openclaw skill list

```

你应该能在列表中看到 ID 为 `amazon_analysis` 的技能。

---

### 3. 在 OpenClaw 中调用

导入后，你不需要死记硬背指令，直接在对话中触发即可：

* **直接对话：** “请用 `amazon_analysis` 技能帮我研究一下最近很火的空炸锅（Air Purifier）市场。”
* **结合 Subagent：** 你可以派生一个专门的调研代理：
```bash
# 在对话中让主代理操作
/spawn Researcher --skill amazon_analysis "去调研德国站前五名的除螨仪，重点看用户对噪音的评价。"

```



---

### 💡 针对“灵鹿 (LingLu)”的进阶技巧

既然你在做 **Xflow OS**，你可以进一步优化这个 Skill：

1. **多语言翻译**：在 `Workflow` 中加入“如果是欧洲站点，请自动将德语/法语评论翻译成中文分析”。
2. **联动 n8n**：通过 MCP 协议，让 OpenClaw 分析完后，自动把结果推送到你的 n8n 工作流，生成一份 Excel 表格存入 Google Drive。

**你需要我帮你写一段如何让 OpenClaw 通过这个 Skill 联动 n8n 的配置吗？**