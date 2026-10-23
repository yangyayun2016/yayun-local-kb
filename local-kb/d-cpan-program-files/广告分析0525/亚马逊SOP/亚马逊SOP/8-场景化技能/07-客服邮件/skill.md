# 客服邮件生成技能使用指南

## 触发场景

当用户描述以下问题时自动触发：
- "帮我写一封客服邮件"
- "客户问物流到哪里了"
- "客户要退货，怎么回复"
- "收到差评了，联系客户"
- "发错货了，怎么跟客户说"

## 使用方法

提供以下信息，技能自动生成邮件：

**必填信息**：
- 场景类型
- 订单编号
- 客户名称

**选填信息**：
- 问题详情
- 解决方案偏好
- 补偿金额/方式

## 示例对话

```
用户：客户订单#123-456789的快递延误了，帮我写一封邮件

助手（使用本技能）：
已为您生成物流延误回复邮件：

---
Subject: Re: Your Order Delay - Order #123-456789

Dear [Customer Name],

Thank you for reaching out. We sincerely apologize for the delay
with your order #123-456789.

After checking with our logistics partner, the current status shows:
[在此填入当前物流状态]

The estimated new delivery date is: [在此填入新日期]

As a gesture of our apology, we would like to offer you:
[在此选择：10%折扣 / 优惠券 / 部分退款]

We truly appreciate your patience and understanding.

Best regards,
[店铺名称]
---

请将[方括号]内的内容替换为实际信息后使用。
```

## 邮件场景速查

| 场景 | 路径 | 紧急程度 |
|------|------|---------|
| 订单查询 | 站内信 | 普通 |
| 物流延误 | 站内信 | 优先 |
| 退货处理 | 站内信 | 优先 |
| 差评联系 | 站内信 | 紧急 |
| 发错货 | 站内信 | 紧急 |
| 索评回访 | 站内信 | 普通 |
