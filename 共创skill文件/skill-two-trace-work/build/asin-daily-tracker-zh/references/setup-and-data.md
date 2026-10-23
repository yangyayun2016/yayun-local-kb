# 配置与数据来源

## 两种数据模式

模式 A：卖家精灵 MCP 自动取数。

- 每个 ASIN 调用一次 `asin_detail`。
- 指定 return_fields 可以省 token，但不省调用次数。
- 必须提醒用户配额消耗。

模式 B：手动喂数。

- 用户从卖家精灵网页端、Helium10、亚马逊前台或其他工具复制数据。
- 判断逻辑和报告结构不变。
- 效果取决于用户提供字段完整度。

不要让 AI 自己爬亚马逊前台。前台反爬、验证码、代理和字段变化会导致不稳定。

## 首次配置要问

```text
1. 数据模式：A 卖家精灵 MCP（自动） / B 手动喂数
2. 自己的 ASIN（可多个）：
3. 竞品 ASIN（可多个）：
4. 哪个竞品对应你哪个产品？（可选；不填按类目+标题自动配对后请确认）
5. 模式 A：卖家精灵套餐月额度（默认 1000 次）：
6. 是否追踪 Amazon's Choice 标变化？（默认不追）：
7. 每个 ASIN 的代号 / 后台 SKU：
8. 动作记录窗口天数（默认 7 天）：
```

## 配额纪律

一次追踪消耗次数 = 自有 ASIN 数 + 竞品 ASIN 数。

示例：

```text
你配置了 2 个自有 + 3 个竞品，共 5 个 ASIN。
每天约 5 次调用，30 天约 150 次。
如果月额度 1000 次，占 15%，仍给临时调研留有余量。
```

建议每日追踪总数不超过 5 个 ASIN，除非用户明确接受配额消耗。

卖家精灵 MCP 若没有真实余额接口，只能维护 `quota_tracker.json` 做本地估算；用户在别处的调用不会被统计。

## 竞争组规则

每组 = 一个自有产品集合 + 对应竞品集合。只在组内比较，不跨组比较。

配对优先级：

1. 用户手动指定，最高优先级。
2. 类目父节点粗筛，排除明显不相关。
3. 标题/产品名关键词兜底判断。

自动归组必须标记“自动配对，待确认”。无法归组的竞品单独列出并询问用户。

## 字段建议

模式 A 建议 return_fields：

```text
asin,bsrRank,subcategories,nodeIdPath,nodeLabelPath,title,rating,ratings,price,sellerName,fulfillment,coupon,variations,skuList,badge
```

首次正式跑必须核对真实返回字段名，尤其是 `coupon`、`variations`、`skuList`、`badge.amazonChoice`、`badge.bestSeller`。字段对不上时，调整配置和动作侦测逻辑，不要静默漏标。
