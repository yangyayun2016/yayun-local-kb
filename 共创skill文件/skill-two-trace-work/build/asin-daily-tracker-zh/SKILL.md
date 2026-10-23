---
name: asin-daily-tracker-zh
description: |
  中文亚马逊 ASIN 每日竞争追踪 skill，用于配置自有 ASIN 与竞品 ASIN，按竞争组每日拉取或接收 BSR、评分、评分数、价格、Buy Box、coupon、变体、Amazon's Choice/Best Seller 标识等数据，与历史记录比对，生成当天异动报告、7天动作标记、竞品深挖提示和卖家精灵 MCP 配额提醒。Use when 用户说跑今天的追踪、每日追踪、ASIN竞争监控、竞品异动、BSR变化、价格/评分/Buy Box变化、初始化追踪配置、手动喂数追踪或需要连接竞品监控深挖。
---

# ASIN 每日竞争追踪

## 核心目标

每天一次追踪自有 ASIN 和竞品 ASIN，只报告值得运营关注的变化。重点是竞争组判断、异动阈值、动作标记、历史对比和配额纪律，不是盲目抓取更多数据。

## TRACE 执行原则

- Trust: 不内置爬虫；优先使用卖家精灵 MCP 或用户手动提供的数据；不伪造接口返回、不编造剩余额度、不把评论异常直接定性为刷单。
- Reliability: 每次先读配置、历史、动作记录和配额记录；缺文件就初始化；字段名首次必须用真实返回核对。
- Adaptability: 这是用户触发的半自动每日追踪，不是无人值守定时任务；没有 MCP 时使用手动喂数模式。
- Convention: 按 `tracker_config.json` 的竞争组输出；显示名优先用 label/fallback_label，不只甩 ASIN。
- Effectiveness: 今日重点放前面，组内表格只标明显变化，报告末尾固定给竞品深挖入口。

## 模式选择

1. 首次配置或修改配置：读 `references/setup-and-data.md`。
2. 每日追踪执行：读 `references/daily-workflow.md`。
3. 判断异动、动作标记和升级深挖：读 `references/change-rules.md`。
4. 输出报告：读 `references/report-template.md`。
5. 需要生成或维护配置/历史/配额/动作文件：读 `references/state-file-templates.md`。

## 默认工作流

1. 确认数据模式：A 卖家精灵 MCP 自动取数，或 B 手动喂数。
2. 读取或生成 `tracker_config.json`，按竞争组组织自有 ASIN 和竞品 ASIN。
3. 模式 A 下按 ASIN 调 `asin_detail`，每个 ASIN 一次调用；模式 B 下让用户贴当日字段。
4. 读取历史记录，按 ASIN 取上一条作为对比基线。
5. 比对今天与上一条，生成异动项，并同步侦测动作型变化写入 `actions_log.json`。
6. 读取 7 天窗口内的动作标记，挂在对应产品行下。
7. 追加写入 `history.csv`，模式 A 下更新 `quota_tracker.json`。
8. 输出报告：今日重点、按竞争组表格、组内 AI 分析、待确认配对、配额提醒、竞品深挖入口。

## 关键边界

- 不要跨竞争组比较不相关产品。
- 自动配对必须标“待确认”，用户确认后再写回配置。
- BSR 数字变小代表排名上升，报告箭头按名次方向，不按数字增减方向。
- 评论数异常只写“关注是否买评/站外/促销”，不要直接下结论。
- 深挖竞品要用户确认，因为会额外消耗额度；本 skill 只提示入口，不自动执行。
- 卖家精灵 MCP 没有真实余额查询时，只能本地估算配额。

## 默认触发句

```text
跑今天的追踪
我要开始配置追踪
今天这些 ASIN 手动数据如下...
深挖某个竞品
```

## 默认报告结构

```text
### 今日重点
### 按竞争组分段
### 组内 AI 分析
### 待确认配对
### 配额提醒
### 下一步：竞品深挖入口
```
