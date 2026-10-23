# Account Health Monitor Skill

## 用途

账号健康监控，提前预警风险，及时处理问题。

## 绩效指标

### 核心指标
| 指标 | 全称 | 目标 | 超标后果 |
|------|------|------|---------|
| ODR | Order Defect Rate | <1% | 账号冻结 |
| CR | Cancellation Rate | <2.5% | 警告 |
| LSR | Late Shipment Rate | <4% | 警告 |
| VTR | Valid Tracking Rate | >95% | 影响流量 |

### ODR组成
```
ODR = (差评数 + A-Z claim数 + 信用卡拒付数) / 总订单数

降低ODR方法：
1. 提高产品质量，减少差评
2. 及时处理客户问题
3. 减少物流问题
4. 主动联系客户解决问题
```

## 违规类型

| 违规类型 | 严重程度 | 后果 |
|---------|---------|------|
| 操纵评论 | 严重 | 永久封号 |
| 销售假货 | 严重 | 永久封号 |
| 商标侵权 | 中 | Listing下架 |
| 专利侵权 | 严重 | 永久封号 |
| 操纵排名 | 中 | 降权/封号 |
| 违规变体 | 中 | Listing下架 |
| 虚假产品 | 严重 | 永久封号 |

## 监控看板

### 每日监控
```
早晨检查：
1. 绩效通知邮件
2. 订单缺陷数变化
3. 新增差评/A-Z
4. 账号状态
5. Listing状态
```

### 每周复盘
```
1. 绩效指标趋势
2. 问题分析
3. 改进措施
4. 下周计划
```

## 合规检查

### Listing合规
```
检查项目：
1. 标题长度（<200字符）
2. 图片合规（主图白色背景）
3. 五点描述（5条，每条<500字符）
4. 产品描述（<2000字符）
5. 关键词合规（无违禁词）
```

### 违禁词清单
```
禁止使用：
- 最高级：Best, #1, Number 1
- 保证类：Guarantee, Promise
- 免费：Free
- 绝对：Absolutely
- 便宜：Cheap
- 刺激购买：Buy now

处罚：Listing被删除或账号警告
```

### 产品合规
| 产品类型 | 可能需要的认证 |
|---------|--------------|
| 电子产品 | FCC, UL |
| 儿童产品 | CPC, CPSIA |
| 食品 | FDA |
| 化妆品 | FDA |
| 户外用品 | REACH |
| 灯具 | ETL |

## 申诉流程

### 申诉准备清单
```
1. 问题详情
   - 违规类型
   - 违规时间
   - 影响范围

2. 根本原因分析
   - 问题发生的原因
   - 内部调查发现

3. 改进措施
   - 已经采取的措施
   - 未来预防措施

4. 证明材料
   - 发票/采购证明
   - 产品检测报告
   - 沟通记录
```

### 绩效不达标申诉模板
```
Subject: Action Plan for Improving Performance Metrics

Dear Amazon Seller Performance Team,

Thank you for bringing this matter to our attention. We take the
health of our seller account very seriously and are committed to
improving our performance.

ISSUE:
Our [指标] has fallen below the target threshold.

ROOT CAUSE:
[详细说明问题原因]

ACTIONS TAKEN:
1. [已采取的措施1]
2. [已采取的措施2]
3. [已采取的措施3]

PREVENTIVE MEASURES:
1. [未来预防措施1]
2. [未来预防措施2]
3. [未来预防措施3]

We request the opportunity to improve our account standing and
appreciate your guidance on any additional steps we should take.

Sincerely,
[卖家名称]
```

### 侵权申诉模板
```
Subject: Appeal for [ASIN] Infringement Notice

Dear Amazon,

We are writing to appeal the infringement notice for ASIN: [ASIN]

EVIDENCE OF AUTHORIZATION:
[提供授权证明，如商标证书、授权书]

PRODUCT DIFFERENTIATION:
[说明产品与投诉产品的差异]

REQUEST:
We respectfully request reinstatement of our listing as we have
not violated any intellectual property rights.

Best regards,
[卖家名称]
```

## 风险防控

### 高风险行为
| 行为 | 风险等级 | 建议 |
|------|---------|------|
| 新账号刷单 | 极高 | 绝对禁止 |
| 变体违规 | 高 | 谨慎操作 |
| 侵权产品 | 极高 | 严格审核 |
| 虚假发货 | 高 | 真实发货 |
| 重复上架 | 中 | 清理重复 |

### 防护措施
```
1. 账号隔离 - 不同账号用不同网络
2. 品牌备案 - 保护Listing
3. 记录留存 - 保留所有发票和沟通
4. 定期审计 - 每月检查Listing合规
5. 培训员工 - 确保团队了解政策
```

## 使用示例

### 示例1：绩效指标异常
```
用户：发现ODR突然从0.8%升到1.5%
助手：
1. 分析原因：
   - 查看最近30天订单
   - 找出新增的差评、A-Z、拒付

2. 发现问题：
   - 3个差评来自同一批次产品
   - 该批次可能有质量问题

3. 采取行动：
   - 暂停该批次产品销售
   - 联系客户道歉退款
   - 联系工厂追责

4. 申诉准备：
   - 准备根因分析
   - 准备改进措施
   - 监控后续ODR变化
```

### 示例2：收到侵权通知
```
用户：收到商标侵权通知，ASIN被下架
助手：
1. 分析通知：
   - 确认侵权类型：商标侵权
   - 确认涉事ASIN
   - 查看具体侵权内容

2. 调查核实：
   - 是否真的使用了该商标
   - 商标注册状态
   - 投诉方身份

3. 应对策略：
   - 确实侵权：立即下架，申诉恢复
   - 误判侵权：准备证据申诉

4. 申诉材料：
   - 商标证书
   - 采购发票
   - 产品对比说明
```

## 最佳实践

1. **每日监控** - 早晨检查绩效通知
2. **指标预警** - 设置邮件/工具预警
3. **问题及时处理** - 24小时内响应
4. **记录完整** - 所有运营操作留档
5. **合规操作** - 严格遵守亚马逊政策
6. **定期复盘** - 每周绩效复盘
7. **申诉准备** - 提前准备申诉模板
