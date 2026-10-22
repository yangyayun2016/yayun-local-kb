# 03 Skill 编写规范 TRACE

## 要解决什么问题

让每个 Skill 都「会问数据、不乱编数、算得一致、讲得清楚」。TRACE 是一套五字原则。

## 准备什么

- 一个重复的、步骤固定的分析任务
- 该任务的真实输入样例和正确答案（用来测试）

## 一步步怎么做

### Step 1：理解 TRACE

| 字母 | 含义 | 要求 |
|---|---|---|
| T | Trigger 触发 | 用户一提到相关问题就触发，不等数据给全；在描述里列出触发词 |
| R | Required data 必需数据 | 缺什么先列清单向用户要，绝不编造 |
| A | Assumption 假设 | 所有非官方值必须标注为 `engineering_assumption` |
| C | Calculate 计算 | 一律用脚本计算，不靠模型心算，保证口径一致 |
| E | Explain 解释 | 每个数字给出经营含义：能不能做、卡在哪、先改什么 |

### Step 2：目录结构

```
my-skill/
├── SKILL.md              # 触发条件、数据清单、工作流、判断规则
├── scripts/              # 计算脚本（可独立运行、可测试）
├── references/
│   └── methodology.md    # 公式推导、示例、情景表
└── weights.json          # 如有权重，逐项标注 engineering_assumption
```

### Step 3：SKILL.md 模板

```markdown
---
name: your-skill-name
description: 一句话说明用途，并列出触发词，让模型知道何时使用
---

# 标题

## TRACE 原则
- T / R / A / C / E 各一句

## 触发条件
## 前提数据清单（缺什么先问）
## 核心公式
## 工作流
## 判断规则
## 数据不足时的处理
```

### Step 4：区分官方值与假设

在 `weights.json` 或表格里，给每个非官方数字加标记：

```json
{ "click_threshold": { "value": 15, "engineering_assumption": true, "note": "按类目转化率校准" } }
```

### Step 5：测试

- 用真实样例跑一遍，对照人工结果
- 缺数据时，Skill 应输出「缺口清单」而不是估一个数
- 边界情况：零订单、极端价格、缺少毛利率

### Step 6：版本与复盘

每次修改公式或阈值，记录原因和前后差异，放进 `references/` 或变更日志。

## 常见坑

- Skill 写成「大段提示词」，没有脚本，每次结果口径不同。
- 假设值混在公式里，使用者不知道哪些是拍脑袋。
- 没有测试样例，改一次坏一次。

## 完成检查清单

- [ ] description 里有触发词
- [ ] 必需数据清单明确
- [ ] 所有假设都标了 engineering_assumption
- [ ] 计算由脚本完成
- [ ] 至少一个真实样例通过测试

## 延伸阅读

- [广告篇 02 广告经济模型](../ads/02-广告经济模型.md)（一个典型的 TRACE 化示例）
- [04 提示词与质检](04-提示词与质检.md)
