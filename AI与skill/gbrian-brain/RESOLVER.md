---
type: note
title: 'Gbrian Brain Resolver'
created: 2026-05-17
updated: 2026-05-17
confidence: medium
---

# Gbrian Brain Resolver

新增或整理知识前，先走这个决策树。每条知识只能有一个主要归属目录。

## Decision Tree

1. 具体的人 → `people/`
2. 具体组织、公司、团队、机构 → `companies/`
3. 正在推进、有明确行动或产出的事情 → `projects/`
4. 还没有开始执行的可能性或想法 → `ideas/`
5. 可复用的模型、原则、方法论、长期观点 → `concepts/`
6. 会议、通话、访谈、同步记录 → `meetings/`
7. 原始资料、网页、PDF、聊天记录、外部文档摘要 → `sources/`
8. agent 生成的报告、摘要、简报、研究输出 → `agent/`
9. 可复用提示词 → `prompts/`
10. 不确定、未分类、待验证 → `inbox/`
11. 已失效但需要保留历史 → `archive/`

## Disambiguation

- 人 vs 组织：如果主体是“这个人是谁、怎么合作”，放 `people/`；如果主体是“这个组织是什么、做什么”，放 `companies/`。
- 项目 vs 想法：已经有人在推进，放 `projects/`；只是可能性，放 `ideas/`。
- 概念 vs 写作：能作为方法或原则复用，放 `concepts/`；完整文章或草稿可以先放 `agent/` 或 `sources/`，后续再拆成概念。
- 来源 vs 知识页：原始材料或材料摘要放 `sources/`；提炼后的长期结论放到对应知识页。
- 不确定内容：先放 `inbox/`，并标记 `待确认`。

## Before Creating a Page

1. 搜索同名、别名和相关关键词。
2. 检查目标目录的 `README.md`。
3. 使用 `templates/` 中最接近的模板。
4. 在页面底部保留 Timeline。
5. 在 `log.md` 追加一条记录。

