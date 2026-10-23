# 示例案例：B0DMV84TDX

本案例用于校准 ASIN Center 输出粒度。不要把这里的指标套用到其他 ASIN。

## Header

- ASIN: `B0DMV84TDX`
- Product: `Auxbeam Jump Starter with Air Compressor 3000A Car Battery Jump Starter`
- Account: `Vester_US`
- Owner: `罗志明`
- L2: `E流量质量差`
- L3: `精密`
- Inventory mode: `正常`
- Sellable months: `16.06`
- Rating: `4.1`
- Lifecycle: `成熟期`
- Generated: `2026-06-04 16:11:02`

## 数据复核

- Visitors: `513`, change `-15.21%`
- Conversion rate: `1.56%`, change `34.78%`
- ACOS: `220.83%`, change `61.61%`
- Ad clicks: `280`, change `-34.27%`
- Ad conversion: `1.07%`, change `-61.96%`
- Orders: `8`, change `0.00%`
- Sales: `$470.88`, change `15.43%`
- Margin: `14.00%`
- Category rank: `857`, change `30.44%`

交叉验证：销售额上涨、订单持平，说明销售和订单方向基本一致，但广告效率很差。

## 诊断信号

- 访客高于基线。
- 转化率低于基线。
- ACOS 高于基线。
- L2 为 `E流量质量差`。
- L3 为 `精密`。

## 广告架构信号

- 策略方向：Protect/Conquest 品牌防守/竞品抢夺。
- 探索层目标 10%，实际 69%，严重超配。
- 转化层目标 45%，实际 5%，严重承接不足。
- 探索层保留了 `$600` 否定词花费，4 个词未控制。
- 探索层空壳率 `86%`，空壳花费 `$381`。
- SP 存在；SB、SD 缺失。
- 利润率 `<25%`，预算应先收紧。

## 动作信号

- 库存正常：可销月 `16.06`。
- ASIN 级动作包含 8 行。
- 价格/促销检查包含 19 行。
- 模块覆盖：B/C/D 已覆盖；A 暂无优化需要。
- operationStats 包含 17 行。
- adTree 包含 501 行 campaign/ad group/targeting/search-term 层级数据。

重要动作 ID：

- `B7-6`：否定关键词，由 `L2=E流量质量差` 触发。
- `B5-1`：Exact 承接，由 `L2=E流量质量差` 触发。
- `C14-9-up`、`C13-1`、`C14-2-down`、`C14-3-up`：价格/促销转化检查。
- `D16-1`：Review/Vine 相关动作。

## 示例根因链

高 ACOS 和低广告转化说明流量效率低。探索层相对策略目标严重超配，否定词控制不足，空壳消耗高。由于利润率低于 25%，建议先清理浪费和收紧预算，再考虑扩量。
