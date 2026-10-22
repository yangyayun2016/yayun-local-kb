← [业务接口分主题](03-业务接口分主题.md)　·　[返回目录](../README.md)　·　[接入与授权](05-接入与授权.md) →

# 4 AI · MCP · 工作流

## 4.1 五个组件各负责什么

| 组件 | 白话解释 | 例子 |
|---|---|---|
| AI Agent | 理解需求、选择工具并解释结果的助手 | 理解"查昨天销售，再对账" |
| MCP | AI 与工具沟通的协议 | 把查询需求交给外部工具 |
| SP-API | 亚马逊业务接口体系 | 读取库存、订单、财务 |
| Reports API | 按预设类型生成或读取报表 | 获取促销效果报表 |
| Data Kiosk | 在支持的数据集中按字段和条件查询 | 只取某完整日期的销售汇总 |

官方 Local MCP 包含两个可独立使用的服务器：**开发助手**负责找接口和发起请求；**工作流服务器**负责保存及运行多个步骤。它们是官方集成示例，生产使用仍需团队测试、维护与权限控制。

## 4.2 开发助手的六个工具

| 工具 | 主要用途 |
|---|---|
| `sp_api_reference` | 检索官方文档 |
| `sp_api_explore_catalog` | 查看路径、参数、响应结构与目录 |
| `sp_api_execute` | 执行获授权的真实业务请求 |
| `sp_api_generate_code_sample` | 辅助生成 SDK 代码示例 |
| `sp_api_migration_assistant` | 分析版本迁移与代码变化 |
| `sp_api_optimize` | 检查分页、限流、缓存及错误处理等集成问题 |

## 4.3 工作流如何运行

**链路：** 业务目标 → AI 查接口与参数 → 创建或复用 JSON → 校验流程 → 本地执行器调用接口 → 保存结果与日志 → AI 解释结果。

JSON 用状态和转移规则描述步骤；**ASL** 是 Amazon States Language。本地工作流服务器使用 Node.js 执行器，提供等待、分支、文件获取、暂停恢复和人工输入等工具。某批连接记录发现 30 个工具，这只是该版本的观察值。

**Data Kiosk 查询是异步的：** 创建查询 → 等待完成 → 获取文档下载地址 → 下载 JSONL 文件。JSONL 每行是一条 JSON 数据，便于逐条解析。**提交成功只表示任务已受理**，不能代替完成状态和文件内容校验。

> **本地 JSON 与云端 JSON 不一定通用。**
> 官方云端示例使用 AWS Step Functions 调度 Lambda；本地执行器支持的任务资源不同。测试中 AWS 示例原样导入成功，但运行时因不支持 Lambda 资源而失败，适配成本地任务后才跑通。

已有流程可查找、查看定义、导入、校验和执行。导出 Mermaid 流程图或独立 Node.js 脚本的能力通过工具及源码确认，但**没有单独执行导出脚本**。保存流程也不会自动创建每日定时任务。

## 4.4 三种版本分开记

| 版本号 | 是什么 |
|---|---|
| `v2023-11-15` | Data Kiosk 接口版本 |
| `analytics_salesAndTraffic_2024_04_24` | 数据集结构版本 |
| `1.0.5` | 本批 npm 工具包版本 |

源资料还记录 2025-08-27 新增 `salesAndTrafficTrends` 趋势查询，但本批工作流使用按日期汇总，**未实测趋势查询**。

## 4.5 AI 辅助迁移演示（MCF 案例）【现场 IMG_2390–2392】

### 演示链路

1. 向 AI 提问 Fulfillment Outbound 2020 与 2025 版本有什么区别
2. 调用 `sp_api_migration_assistant`，传入源版本与目标版本
3. 生成请求字段、响应结构、状态和新能力差异
4. 进一步让 AI 阅读本地 Java 多渠道履约代码目录
5. 对 4 个 Java 文件输出迁移问题与严重程度

> **不应合并成同一正式规范【待核实 Q01】**
> 演讲页 IMG_2388 使用 **v2026-07-04**；Kiro 演示 IMG_2390–2392 使用 **v2020-07-01 → v2025-09-24**，且屏幕明确提示目标 schema 是 **pre-release，可能变化**。以下仅忠实记录 AI 演示输出，不是已核验的正式迁移指南。

### 高层变化（演示输出）

| 项目 | 演示中的旧版 | 演示中的目标版 |
|---|---|---|
| 基础路径 | `/fba/outbound/2020-07-01` | `/fulfillment/outbound/2025-09-24` |
| 响应结构 | 包在 `payload` 中 | 直接返回对象 |
| 枚举风格 | `Standard`、`FillOrKill` | `STANDARD`、`FILL_OR_KILL` |
| 多租户 | 表中称不支持 | 使用 `x-amzn-fulfillment-service-id` 请求头 |

### 请求字段变化（演示输出）

| 旧字段 | 演示建议的新字段 |
|---|---|
| `sellerFulfillmentOrderId` | `orderId` |
| `shippingSpeedCategory` | `deliveryServiceLevel` |
| `destinationAddress` | `destination.deliveryAddress` |
| `marketplaceId` | `origin.countryCode` |
| `items` | `lineItems` |
| `items[].sellerSKU` | `lineItems[].product.productIdentifier.amazonSku` |
| `items[].quantity`（整数） | `lineItems[].amount`（对象，含 `value`、`unitOfMeasure`） |
| `featureConstraints` | `services`（含 packaging、additionalServices 子对象） |

**注意：** 尤其是商城 ID 到国家代码，不能理解成只改字段名、值原样照搬；必须进一步检查真实映射规则。

### 响应与状态变化（演示输出）

- 去掉 `payload`；商品与货件放入 `fulfillmentOrder` 对象
- `fulfillmentOrderStatus` → `status`
- `fulfillmentCenterId`（字符串）→ 含 id、address 的 `fulfillmentCenter` 对象
- 承运商与追踪号嵌入 `carrierTracking`
- `nextToken` → `pagination.pageToken`
- `cancelOrder` 和 `updateOrder` 返回无响应体的 `202 Accepted`
- 旧的 New、Received、Planning、Processing 映射为 `PROCESSING`；新增包裹状态 `IN_TRANSIT`、`DELAYED`、`OUT_FOR_DELIVERY`、`DELIVERED`、`UNDELIVERABLE`
- `getFeatures`、`getFeatureSKU`、`getFeatureInventory` 标为弃用并提及 `getOrderPreview`；`createFulfillmentReturn`、`listReturnReasonCodes` 也标为弃用
- 新能力列表提到多租户、Webhook 包裹级通知、CEL 事件过滤、沙盒状态模拟、具有过期时间的配送报价

### 代码风险清单（演示输出）

| 文件 | 演示评级 | 主要问题 |
|---|---|---|
| `McfConstants.java` | High | SKU、数量与地址的请求体嵌套重构 |
| `McfCreateOnHoldAndShipOrderRecipe.java` | Critical | 旧追踪操作被移除、update 返回变化、payload 去除 |
| `McfCreateAndCancelOrderRecipe.java` | Critical | cancel 返回 202 且无对象、payload 去除 |
| `McfCreateAndTrackOrderRecipe.java` | Critical | 旧追踪操作被移除、payload 去除 |

**本段能确认的结论：** AI 可以输出版本与文件级迁移清单。照片没有展示编译、集成测试、真实订单执行或回滚验证；High/Critical 是工具评级，不是独立审计评级。

## 4.6 现场 AI 环境【现场 IMG_2404】

Kiro 界面标题为 DataKiosk MCP Demo，左侧连接项：`builder-mcp`（界面显示 36 tools）、`sp-api-dev-assistant`、`sp-api-workflow`（工具数量后半被截断，不据此确认总数）。界面还显示 Specs、Agent Hooks、Agent Steering & Skills，以及 Vibe、Spec 两种工作入口。

**能确认演示环境已连接这些服务器；不能确认所有公众账号都能直接使用相同配置。**

## 4.7 接口目录快照：57 类【实测】

**本批快照：57 类、370 条方法与路径记录；按 endpoint ID 去重为 349 个。**

该快照用于理解本次 MCP 所包含的业务范围，保留原始目录名称（含拼写和标点差异）；同类名称可能对应不同版本。**数量不代表当前权限，也不代表最新官方总量**；该快照未列入近期 Promotions 类别。完整表见 [12.1 接口目录快照](#121-接口目录快照57-类)。

## 4.8 官方仓库核验要点（2026-09-17 复核）【官方】

以下来自官方仓库 [sp-api-dev-mcp](https://github.com/amzn/selling-partner-api-samples/tree/main/use-cases/sp-api-dev-mcp) 与 [发布公告 #382](https://github.com/amzn/selling-partner-api-samples/discussions/382)，用于校准会议照片中的口径。

**官方定位声明：** Local MCP for SP-API 是**示例 MCP**，演示 SP-API 的 AI 开发集成实践，**不是受支持的产品**。集成进自有应用前，应按本方安全标准完成测试、加固与优化，再进入生产或承接生产负载。

**运行前提与安装**

- Node.js **>= 20**
- `npm install -g @amazon-sp-api-release/sp-api-dev-mcp`，或直接用 `npx` 免安装运行
- 一个 npm 包内打包两个 MCP 服务器，可独立使用，也可同时使用

**MCP 客户端配置示例（npx 形式，变量值请用受控方式注入）**

```json
{
  "mcpServers": {
    "sp-api-dev-assistant": {
      "command": "npx",
      "args": ["-y", "@amazon-sp-api-release/sp-api-dev-mcp", "sp-api-dev-assistant-mcp-server"],
      "env": {
        "SP_API_CLIENT_ID": "your-client-id",
        "SP_API_CLIENT_SECRET": "your-client-secret",
        "SP_API_REFRESH_TOKEN": "your-refresh-token"
      }
    },
    "sp-api-workflow": {
      "command": "npx",
      "args": ["-y", "@amazon-sp-api-release/sp-api-dev-mcp", "sp-api-workflow-mcp-server"],
      "env": {
        "SP_API_CLIENT_ID": "your-client-id",
        "SP_API_CLIENT_SECRET": "your-client-secret",
        "SP_API_REFRESH_TOKEN": "your-refresh-token"
      }
    }
  }
}
```

**六个工具的官方描述**

| 工具 | 官方描述 |
|---|---|
| `sp_api_reference` | 用自然语言检索官方 SP-API 文档 |
| `sp_api_explore_catalog` | 浏览接口目录（参数、schema、示例） |
| `sp_api_execute` | 带鉴权与签名执行真实 SP-API 请求 |
| `sp_api_generate_code_sample` | 生成 Python、Java、JavaScript、C#、PHP 代码示例 |
| `sp_api_migration_assistant` | 版本迁移分析，例如 Orders v0 到 v2026-01-01 |
| `sp_api_optimize` | 对集成代码做 well-architected 审查 |

> **本次核验补充的一条重要边界：** 官方说明中，**除 `sp_api_execute` 需要 SP-API 凭证发起真实调用外，其余工具均在本地运行、不需要凭证**。这与第 6.5 节"工作流能触发写操作、不是天然只读"并不矛盾：需要收紧的是 `execute` 与工作流执行这两条路径，文档检索类工具风险等级不同，可分别设定权限策略。

**工作流服务器的官方描述：** 开发者用自然语言描述目标，AI 发现对应接口、基于 **Amazon States Language** 逐步构建工作流（状态类型为 Task、Choice、Wait、Pass、Succeed、Fail），并在确认后带 OAuth 令牌管理**确定性地执行**。这与 4.3 节记录的本地执行器观察一致。

**与会议照片的差异处理：** 官方仓库未使用"36 tools""30 tools"这类计数（那是现场演示环境的界面观察值，见 4.6）。以官方工具表为准，界面计数仅作为演示环境记录保留。

---

---

← [业务接口分主题](03-业务接口分主题.md)　·　[返回目录](../README.md)　·　[接入与授权](05-接入与授权.md) →
