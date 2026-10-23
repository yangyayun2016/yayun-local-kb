# 周复盘输出模板

最终报告使用中文 Markdown。结构、标题和表格顺序保持固定；没有数据的表格不要删除，填“暂无可确认信号”并说明缺口。

开头先写口径：

```markdown
复盘口径：SIF {country}，按最近完整周 {week_start} ~ {week_end} 对比上一周 {prev_week_start} ~ {prev_week_end}；如有近 7 天关键词信号，单独标注。SIF 本轮返回的是流量、广告曝光和自然排名信号；未返回广告订单/花费/ACOS 时，不直接确认订单表现。
```

## 1. 本周流量变化

```markdown
### 1. 本周流量变化

| 指标 | 上周 {prev_week_start} | 本周 {week_start} | 变化 | 判断 |
|---|---:|---:|---:|---|
| 总流量分 | {prev_total} | {this_total} | {delta_total} / {delta_total_pct} | {继续增长/回落/基本稳定} |
| 自然流量分 | {prev_natural} | {this_natural} | {delta_natural} / {delta_natural_pct} | {明显增长/回落/基本稳定} |
| 广告流量分 | {prev_ads} | {this_ads} | {delta_ads} / {delta_ads_pct} | {明显增长/明显收缩/基本稳定} |
| 广告占比 | {prev_ads_share} | {this_ads_share} | {share_change} | {自然占比提高/广告依赖升高/结构稳定} |

近 7 天滚动口径：总流量 {rolling_total}，自然 {rolling_natural}，广告 {rolling_ads}，自然占比 {rolling_natural_share}。
```

## 2. 贡献上升且有自然沉淀的词

```markdown
### 2. 贡献上升且有自然沉淀的词

| 关键词 | 贡献变化 | 自然排名 | 判断 |
|---|---:|---|---|
| {keyword} | {traffic_or_contribution_change} | {natural_rank_history_or_current} | {正向沉淀/自然扩展/样本太小继续观察} |
```

判定重点：

- “正向沉淀”只给广告贡献上升且自然排名同步上升或稳定在高位的词。
- “自然扩展”用于自然排名改善但广告曝光不明显或无 SP 曝光的词，不归功于广告。
- “样本太小”用于新词、短期只出现 1 次、贡献变化很小或排名数据不连续的词。

## 3. 有广告曝光但自然没沉淀的词

```markdown
### 3. 有广告曝光但自然没沉淀的词

| 关键词 | 承载 Campaign / Ad Group | 广告曝光信号 | 自然沉淀 | 动作 |
|---|---|---:|---|---|
| {keyword} | {campaign} / {ad_group} | {ad_signal} | {无自然排名/排名未改善/自然流量未承接} | {降 BID/否词/暂停/检查相关性} |
```

优先列出广告曝光较高、贡献占比高、但自然排名没有进入有效位置的词。

## 4. 自然排名断档词

```markdown
### 4. 自然排名断档词

| 关键词 | 当前信号 | 风险 |
|---|---|---|
| {keyword} | {natural_rank_signal} | {severe gap/moderate gap/volatile/核心词需占位/大词不适合硬冲} |
```

断档词包括：自然排名从首页或高位明显后退、SIF 标记 severe/moderate gap、排名波动大、或核心词广告在推但自然位没有承接。

## 5. Campaign / Ad Group 承载

```markdown
### 5. Campaign / Ad Group 承载

| Campaign | 本周曝光贡献 | 变化 | 主要 Ad Group | 判断 |
|---|---:|---|---|---|
| {campaign} | {contribution_score_or_share} | {change_vs_prev} | {ad_groups_and_share} | {当前主力/结构混杂/明显收缩/需检查变体承载} |
```

说明哪些 Campaign/AdGroup 是主要流量入口，是否承载核心词，是否混入泛词、弱相关词或非目标变体。

## 6. 下周动作

```markdown
### 6. 下周动作

| 动作 | 关键词 / 结构 | 执行建议 |
|---|---|---|
| 加预算或提高 BID | {keywords_or_campaigns} | {只对已出现自然沉淀的词小幅加预算或保护预算，避免断流} |
| 继续观察 | {keywords_or_campaigns} | {样本小、自然有扩展但广告证据不足，先保持低预算验证} |
| 降 BID / 否词 / 暂停 | {keywords_or_campaigns} | {有广告曝光但自然无沉淀，或相关性弱、易误导点击} |
| 结构检查 | {campaigns_or_ad_groups} | {检查是否投到非目标变体、广告组承载是否混乱、核心词是否被泛词稀释} |

一句话结论：{这周广告是在撬动自然流量 / 只是在购买短期流量 / 局部撬动但结构仍需清理 / 证据不足需继续观察}。

SIF 官网验证：
{"流量全景":"https://www.sif.com/timemachine-traffic?country={country}&from=mcp_analysis&asin={asin}","广告结构":"https://www.sif.com/adxray-structure?country={country}&from=mcp_analysis&asin={asin}"}
```

如果工具返回 `render_footer`，在报告末尾原文保留 `render_footer`，不要改写或省略。
