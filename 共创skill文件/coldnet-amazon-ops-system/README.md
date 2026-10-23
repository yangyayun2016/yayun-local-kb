# 天机OS 亚马逊广告健康诊断系统

基于用户提供的 PRD、广告诊断提示、处理清单、报告截图和天机OS界面参考图，构建的本地可运行 MVP 原型。

## 已实现

- 广告中心看板：昨日、7天、30天指标对比和店铺广告明细
- 提交广告健康诊断：ASIN、店铺、站点、竞品、ABA/SIF开关
- 13步广告诊断报告：产品、基础面、毛利、Campaign、关键词、广告位、预算、竞品、根因、动作、ABA、机会词
- 处理清单：风险等级、核心指标、建议动作、采纳/部分采纳/忽略状态流转
- 关键词机会：停投、加投、降价/否词、自然排名布局
- ASIN视图：产品基础、利润风险、月度广告毛利和截图依据
- 系统版图：1-3-5年规划、模块积木、规则引擎
- 后端API：系统数据、诊断任务、报告、处理清单、关键词机会

## 本地启动

```powershell
cd C:\Users\ouyan\Documents\共创skill文件\coldnet-amazon-ops-system
.\scripts\start.ps1
```

打开：

```text
http://127.0.0.1:8765
```

## 核心接口

- `GET /api/health`
- `GET /api/system`
- `GET /api/ad-dashboard/summary`
- `POST /api/diagnosis/jobs`
- `GET /api/diagnosis/reports/main`
- `GET /api/tasks`
- `PATCH /api/tasks/{id}`
- `GET /api/keywords/opportunities`
- `GET /api/asins/{asin}/ad-view`

## 产品边界

当前版本是可演示 MVP，不会自动改 Amazon 广告出价、预算或Campaign状态。所有高风险动作只生成建议和处理清单，必须人工确认后执行。
