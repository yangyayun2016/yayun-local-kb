---
type: note
title: 'Gbrian Brain Schema'
created: 2026-05-17
updated: 2026-05-17
confidence: medium
---

# Gbrian Brain Schema

本知识库采用 “Compiled Truth + Timeline” 结构。

## Page Structure

```markdown
# Title

> 一句话摘要：当前最重要的结论。

## State

- **Status:** active / dormant / archived / 待确认
- **Confidence:** high / medium / low
- **Last updated:** YYYY-MM-DD

## Compiled Truth

当前最可信、最有用、已提炼的知识。这里可以被重写，以保持最新。

## Open Threads

- 仍需确认、跟进或补充的信息。

## See Also

- `[[related-page]]`

---

## Timeline

- **YYYY-MM-DD** | Source — What happened.
```

## Citation Rules

- 事实尽量包含来源、日期和可信度。
- 用户纠正是高价值来源，应写入 Timeline。
- 未验证内容必须标为 `待确认`。
- 不要把推测写成事实。

## Naming

- 文件名使用小写英文、数字和连字符。
- 人名：`first-last.md`
- 公司或组织：`company-name.md`
- 项目：`project-name.md`
- 会议：`YYYY-MM-DD-topic.md`
- 来源：`YYYY-MM-DD-source-title.md`

## Privacy

禁止保存：

- 密码、API key、token、私钥
- 银行卡、证件号、完整住址
- 不需要长期保存的敏感个人信息

## Maintenance

- `index.md` 可定期重建，不必每次手工完整更新。
- `log.md` 只追加，不重写历史。
- `inbox/` 应定期清理。
- 发现重复页面时，合并到更完整的页面，并更新交叉引用。

