# 状态文件模板

## tracker_config.json

```json
{
  "marketplace": "US",
  "data_mode": "A",
  "monthly_quota": 1000,
  "track_amazon_choice": false,
  "action_window_days": 7,
  "groups": [
    {
      "group_id": "示例组-改成你的",
      "group_name": "这一组产品的统称",
      "my_products": [
        {
          "asin": "你的ASIN",
          "label": "后台SKU，可留空",
          "fallback_label": "好认的简称"
        }
      ],
      "competitors": [
        {
          "asin": "竞品ASIN",
          "label": "",
          "fallback_label": "竞品简称",
          "competitor_of": ["它对应你的哪个ASIN"],
          "match_source": "manual"
        }
      ]
    }
  ],
  "asin_detail_return_fields": "asin,bsrRank,subcategories,nodeIdPath,nodeLabelPath,title,rating,ratings,price,sellerName,fulfillment,coupon,variations,skuList,badge",
  "keyword_rank_pending": true
}
```

## quota_tracker.json

```json
{
  "_note": "本地估算记账，非卖家精灵真实余额。月初手动归零。",
  "monthly_quota": 1000,
  "reset_date": "YYYY-MM-DD",
  "used_this_month": 0,
  "warn_threshold": 850
}
```

## actions_log.json

```json
{
  "_note": "每天取数比对时自动侦测动作型变化并追加。报告渲染时挂出 action_window_days 天内的标记。",
  "action_window_days": 7,
  "actions": [
    {
      "date": "YYYY-MM-DD",
      "asin": "哪个ASIN",
      "label": "好认的简称",
      "role": "self / competitor",
      "type": "price_change / coupon_on / coupon_off / variant_change / buybox_change / badge_gain / badge_loss / review_spike",
      "note": "调价 $28.99→$26.99"
    }
  ]
}
```

## history.csv

```text
date,asin,label,role,group_id,bsrRank,subRank,subLabel,rating,ratings,price,buyBoxSeller,fulfillment
```

## 写入纪律

- 追加历史前先确认 date 和 asin。
- 自动侦测动作只在发生当天记一次，不每天重复记。
- 用户确认自动配对后，更新 `match_source` 为 `manual` 或明确确认值。
- 模式 A 每跑一次更新配额；模式 B 不更新卖家精灵配额。
