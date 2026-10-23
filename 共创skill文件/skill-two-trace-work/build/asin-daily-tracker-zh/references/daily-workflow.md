# 每日执行流程

## 执行步骤

1. 读取 `tracker_config.json`。
2. 按竞争组遍历自有 ASIN 和竞品 ASIN。
3. 获取当天数据：
   - 模式 A：对每个 ASIN 调一次 `asin_detail`。
   - 模式 B：解析用户贴入的手动数据。
4. 读取 `history.csv`，找到每个 ASIN 最近一条历史。
5. 比对今天 vs 上一条，生成异动项。
6. 侦测动作型变化，并追加到 `actions_log.json`。
7. 读取最近 `action_window_days` 天内动作，挂到报告对应产品行下。
8. 追加今天数据到 `history.csv`。
9. 模式 A 更新 `quota_tracker.json`。
10. 输出今日报告。

## 显示名规则

报告中产品名按以下顺序选择：

1. `label`：通常是后台 SKU 或用户自定义简称。
2. `fallback_label`：好认的简称。
3. ASIN。

不要只在表格里甩 ASIN。

## 文件持久化

本地工作区使用时，数据文件直接保存在工作目录，可以跨会话继续追踪。

聊天类临时环境使用时，提醒用户每次追踪后保存这些文件：

- `tracker_config.json`
- `history.csv`
- `actions_log.json`
- `quota_tracker.json`

换会话或换设备时，先上传这些文件再继续追踪。

## 模式 B 手动数据要求

用户至少提供：

- ASIN 或显示名
- 角色：自有 / 竞品
- BSR
- 评分
- 评分数
- 价格
- Buy Box 卖家

如要侦测动作，还需要：

- coupon
- 变体数量或 skuList
- Amazon's Choice / Best Seller 标识

缺字段时，只对已有字段做判断，并在报告中写“未提供，无法判断”。
