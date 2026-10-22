---
name: amazon-cdq-score
description: 亚马逊Listing的CDQ（Composite Data Quality，目录数据质量）自动打分技能。当用户提供一个ASIN和站点，要求"打CDQ分"、"listing质量评分"、"目录数据质量检测"、"CDQ打分"、"检测这个listing质量"时，务必使用此技能。只需要用户提供ASIN和站点（如美国/德国/英国），技能会自动抓取公开页面数据并调用已连接的MCP工具补充信息，跑CDQ七维度算法，输出结构化HTML评分报告，包含每个维度的分数、缺陷、优先修复建议，以及每项数据的置信度标注（实测/估算/无法获取需登录后台核实）。即使用户只说"帮我看看B0XXXXXXXX的CDQ"或"这个listing质量怎么样"，也应触发此技能。
---

# 亚马逊 CDQ 自动打分技能

## 概述

本技能对亚马逊Listing进行CDQ（Composite Data Quality）七维度自动打分：结构化属性质量(30%)、标题质量(25%)、图片质量(15%)、变体质量(20%，孤儿ASIN权重重分配)、五点描述(5%)、A+页面(5%)、可搜索性/Discoverability(0-20%加分)。算法细节基于Amazon官方CDQ v3公开文档。

**核心原则：用户只需要提供ASIN + 站点，其余全部由Claude自动完成**——不要向用户索要标题字数、图片数量、是否有A+这类细节，这些都应该由Claude自己抓取或调用工具获得。只有在数据抓取失败、需要用户确认二义性信息（比如同一ASIN在多个站点都有售）时才追问。

## 触发条件

- 用户提供ASIN + 站点，要求CDQ打分/listing质量评分
- 用户说"检测一下这个listing的目录质量"
- 用户只给了ASIN没给站点 → 先问站点（默认可推断：如果用户历史上下文/记忆里提到主要做欧盟/英国/德国站，优先确认是否是这些站点，而不是默认美国站）

## 执行流程

### 第一步：确认ASIN与站点

如果用户只提供了ASIN没给站点，直接问一句"哪个站点？（美国/英国/德国/法国/意大利/西班牙/日本/加拿大...）"，不要问其他任何细节。

站点 → 域名映射：

| 站点 | 域名 |
|------|------|
| 美国 US | amazon.com |
| 英国 UK | amazon.co.uk |
| 德国 DE | amazon.de |
| 法国 FR | amazon.fr |
| 意大利 IT | amazon.it |
| 西班牙 ES | amazon.es |
| 日本 JP | amazon.co.jp |
| 加拿大 CA | amazon.ca |
| 荷兰 NL | amazon.nl |
| 瑞典 SE | amazon.se |
| 波兰 PL | amazon.pl |

### 第二步：数据获取（优先级从高到低）

**优先级1 — 已连接的MCP工具**（数据更可靠，优先使用）：
- 若"卖家精灵MCP"已连接：调用 `asin_detail` 获取标题、品牌、图片数、类目路径、变体信息
- 若"SIF MCP"已连接：调用相关 `ops_get_*` 工具补充流量/类目结构信息
- 若"Sorftime"已连接：调用 `product_detail` 获取产品详情

**优先级2 — 公开页面抓取**（MCP工具未连接或数据不全时使用）：
1. 先用 `web_search` 搜索 `{ASIN} site:amazon.{域名}`，从搜索结果里拿到该ASIN在目标站点的规范URL（web_fetch工具只能抓取已经出现在对话/搜索结果中的URL，不能凭空拼接dp链接直接抓取，必须先搜索一次）
2. `web_fetch` 该URL，抓取以下内容：
   - 标题（productTitle）
   - 五点描述（feature-bullets区块）
   - 主图+附图数量（图片缩略图区块的图片计数）
   - 是否有A+页面（页面中是否存在aplus/product description模块）
   - 类目面包屑（wayfinding-breadcrumbs，最后一级即叶节点）
   - 品牌（byline/品牌链接文字）
   - 是否为变体listing、变体数量（twister选择器区块）
   - "Product information"/"产品信息"规格参数表里的可见字段（作为结构化属性完整度的**估算代理**，不是真实后台RAI数据）

### 第三步：运行CDQ打分引擎

调用本技能自带的打分脚本：

```bash
python3 /mnt/skills/user/amazon-cdq-score/scripts/cdq_score_engine.py --input extracted_data.json --output report_data.json
```

脚本输入格式（`extracted_data.json`）见 `scripts/cdq_score_engine.py` 顶部的 `ExtractedListingData` 字段说明；直接把第二步抓到的数据按该结构组织成JSON传入即可。脚本内置：
- 与CDQ官方权重一致的七维度打分逻辑（复用标题TQS三级判分、图片四象限打分表、A+二元判分、五点0/1/3判分规则）
- 每个维度的**数据置信度标注**：`实测`（页面/MCP工具直接给出的硬数据，如图片数、A+有无、字数）/ `估算`（用可见数据做代理推算，如结构化属性完整度、变体质量缺陷）/ `无法获取`（必须登录卖家后台Listing Quality Dashboard才能拿到真实值，如Top6 RAI属性准确性）

**不要跳过这一步自己口算分数**——必须实际运行脚本，保证权重、分位数、判分阈值精确一致。

### 第四步：生成HTML报告

按照下面的结构生成单文件HTML报告，深色主题风格（参考`amazon-competitor-analysis`技能的视觉风格：深蓝/深灰背景+亮色文字，指标卡片渐变色，风险用红黄绿颜色编码）。

**报告结构：**

1. **头部**：ASIN、站点、抓取时间、总分（大号数字）、等级徽章（A++/A+/A/B/C/D/U，用对应CDQ算法详解.md的等级映射）
2. **数据置信度提示条**：醒目位置提示"结构化属性质量为公开数据估算值，非卖家后台真实CDQ分数，如需精确值请登录Seller Central查看Listing Quality Dashboard"
3. **七维度分数卡片**：每个维度一张卡片，显示：维度名/权重/得分/该维度的数据置信度标签（实测·估算·无法获取，三种颜色区分）
4. **优先修复TODOLIST**：按"权重×损失分"排序的前5条具体建议（脚本会计算好，直接渲染）
5. **原始抓取数据附录**（可折叠）：标题原文、五点原文、图片数、类目路径等，方便用户核对抓取是否准确

**文件输出**：保存到 `/mnt/user-data/outputs/{ASIN}_CDQ评分报告_{日期}.html`，用 `present_files` 展示给用户。

## 数据不足时的处理

- 抓取失败的字段（如无法判断是否有A+）：该维度标注"数据不足，按保守值估算"，不要编造
- 若MCP工具和网页抓取都拿不到某个ASIN（比如listing已下架），明确告知用户，不要虚构分数
- 结构化属性质量维度**永远**标注为"估算"，不管数据来源多好，因为公开数据无法看到真实的Top6/Top10 RAI属性判定结果

## 参考资料

- CDQ算法完整规则（七维度权重、TQS三级判分、图片四象限表、等级映射）：`references/cdq-algorithm.md`
- 打分引擎脚本：`scripts/cdq_score_engine.py`
