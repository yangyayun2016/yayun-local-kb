# ColdNet 业务化设计说明

## 论文核心到系统映射

ColdNet 解决三个问题：极端处理不平衡、零膨胀结果、冷启动画像不完整。本系统把这些机制转成亚马逊运维可执行模块：

1. 按结果分层的集成学习  
   后端使用 10 个稳定成员模拟生产集成，并选择最接近中位 CATE 的成员输出，降低异常模型对决策的影响。

2. 目标正则化与倾向重叠  
   论文中的反事实校正项 `cc = T/pi(X) - (1-T)/(1-pi(X))` 用于学习平衡表征。本系统在推理层保留倾向得分、重叠质量、集成分散度，用于置信度校准和风险提示。

3. 基于聚类的冷启动增强  
   冷启动 ASIN 会进入聚类近邻流程：标准化非历史特征，分配到最近聚类，取 10 个近邻，用第 45 分位结果聚合，再按 `0.1 * NCM + 0.9 * 近邻结果` 混合两个潜在结果头。

## 冷启动判断

以下任一历史活动字段为 0 时，系统判定为冷启动：

- `offer_net_ordered_gms_amt_sum_90d`
- `offer_net_ordered_gms_amt_sum_365d`
- `offer_net_shipped_units_sum_90d`
- `offer_net_shipped_units_sum_365d`
- `offer_asin_net_ord_gms_sum_90d`
- `offer_asin_net_ship_units_sum_90d`

## 输出解释

- `mu0`：不执行干预时的潜在结果。
- `mu1`：执行推荐干预时的潜在结果。
- `cate`：`mu1 - mu0`，代表处理效应。
- `raw_ncm_cate`：冷启动增强前的 NCM 处理效应。
- `confidence`：由倾向重叠、近邻质量、历史完整度和集成分散度综合得到。
- `score`：将 CATE、需求、毛利、库存、内容质量和风险折算成运营优先级。

## 后续生产化建议

- 数据层：接入 SP-API、Advertising API、库存、Review、关键词排名和财务毛利数据。
- 模型层：将 `backend/coldnet_engine.py` 中的确定性 NCM 替换为训练好的 DragonNet/ColdNet 模型服务。
- 存储层：把 `data/sample_asins.json` 替换为数据库或对象存储输入。
- 调度层：使用定时任务每周重算推荐，每季度重训模型。
- 审计层：保存每次推荐的特征快照、模型版本、CATE、置信度和最终运营动作。
