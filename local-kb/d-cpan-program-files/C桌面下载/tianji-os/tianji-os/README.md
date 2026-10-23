# 天机智能决策OS（Tianji Decision OS）

亚马逊企业 AI 运营系统 —— **数据自动进入系统 → 系统自动发现异常 → AI 自动判断原因 → 人只做关键确认 → RPA 自动执行 → 经验自动沉淀**。

UI 风格对齐 CompanyOS 驾驶舱（浅蓝 SaaS 风：左侧导航 + KPI 卡 + 双轴趋势图 + 主动提醒卡片流）。

## 一分钟跑起来

```bash
pip install -r requirements.txt
cd backend
python seed.py                                  # 生成近30天演示数据
uvicorn main:app --host 0.0.0.0 --port 8000
# 打开 http://localhost:8000
```

或 Docker：

```bash
cp .env.example .env
docker compose up --build
```

## 系统架构（五层）

```
前端界面层   frontend/index.html（销售中心/工作台/广告中心/库存预警/人机协同/Skill中心/自动任务）
业务应用层   backend/main.py（驾驶舱API、老板日报、广告诊断、库存预警、人工确认）
AI Agent层   services/ai_agent.py（日报Agent + 广告止损规则引擎，可接Claude API）
Workflow层   services/scheduler.py（APScheduler 定时触发6大闭环）+ workflows 表
数据服务层   services/mcp_client.py（卖家精灵/SIF/Sorftime MCP）、services/feishu.py、services/rpa.py
数据存储层   SQLite（默认）/ PostgreSQL（生产），10张核心表见 backend/models.py
```

## 已实现的自动化闭环

| 闭环 | 触发 | 链路 |
|---|---|---|
| 老板日报 | 每天 8:00 / 手动 | 拉数据 → 算指标 → 识异常 → AI生成 → 推飞书 |
| 广告异常 | 每天 8:30 / 一键诊断 | 7天指标 → 止损规则匹配 → 生成待确认任务 → 人确认 → RPA执行 |
| 库存预警 | 每天 9:00 | 可售天数 → 风险分级 → 推送负责人 |
| 竞品监控 / Listing巡检 / 选品发现 | workflows 表已定义 | 通过 MCP 工具接入真实数据后启用 |

## 人机协同（核心安全设计）

高风险动作（暂停广告 / 否词 / 调价）**必须人工确认**才会触发 RPA：

```
POST /api/tasks/{id}/decide  {"decision":"approved","approver":"admin"}
→ 写入 human_approvals 审批记录
→ RPA 执行（默认 dry_run 演练模式，TIANJI_RPA_DRY_RUN=0 开启真实执行）
→ 回写任务状态，经验沉淀
```

## 广告止损规则引擎（公司方法论，防止模型自由发挥）

- 7天 ≥35 点击无订单 → 暂停 + 否词
- ACOS > 100% → 出价下调30%
- ACOS 35%~100% → 出价下调15-20% + 否词
- 高曝光低点击（CTR<0.25%）→ 检查主图/价格

规则在 `services/ai_agent.py` 的 `STOP_LOSS_RULES`，按你的实际阈值修改即可。

## API 速查

| 端点 | 说明 |
|---|---|
| `GET /api/dashboard/summary?days=30` | 5个KPI卡（销售额/订单/日均/销量/毛利+环比） |
| `GET /api/dashboard/trend` | 销售额+毛利双线趋势 |
| `GET /api/sales/products` | 商品表现排名 |
| `GET /api/ads/campaigns` `POST /api/ads/diagnose` | 广告表现 / 一键诊断 |
| `GET /api/inventory` | 库存可售天数+风险分级 |
| `GET /api/alerts` `POST /api/alerts/{id}/ack` | 主动提醒卡片 |
| `GET /api/tasks` `POST /api/tasks/{id}/decide` | 人机协同 |
| `POST /api/report/daily?push=true` | 生成日报（push=true 推飞书） |
| `GET /api/skills` `GET /api/workflows` | Skill资产 / 闭环定义 |
| `GET /api/mcp/keyword?keyword=x` 等 | MCP 工具透传（卖家精灵/SIF/Sorftime） |

## 接入真实数据的顺序（建议）

1. **MCP token**：`.env` 配置卖家精灵/SIF token → 竞品监控、关键词分析立刻有真数据
2. **ANTHROPIC_API_KEY**：日报和建议从模板升级为 Claude 生成
3. **飞书 webhook**：信息开始主动找人
4. **SP-API / Ads API**：写一个同步任务把真实销售/广告数据灌入 `sales_daily` / `ads_daily`（表结构已就绪）
5. **PostgreSQL + Playwright**：切生产库，`TIANJI_RPA_DRY_RUN=0` 启用真实 RPA

## 目录结构

```
tianji-os/
├── backend/
│   ├── main.py          # FastAPI 全部路由
│   ├── database.py      # SQLite/PostgreSQL 切换
│   ├── models.py        # 10张核心表
│   ├── seed.py          # 演示数据（含埋好的广告异常/断货风险）
│   └── services/
│       ├── ai_agent.py  # 日报Agent + 止损规则引擎
│       ├── mcp_client.py# MCP Streamable HTTP 客户端
│       ├── rpa.py       # Playwright RPA（dry-run 安全模式）
│       ├── feishu.py    # 飞书文本/卡片推送
│       └── scheduler.py # 定时闭环
├── frontend/index.html  # CompanyOS 风格 SPA（ECharts）
├── requirements.txt / Dockerfile / docker-compose.yml / .env.example
```
