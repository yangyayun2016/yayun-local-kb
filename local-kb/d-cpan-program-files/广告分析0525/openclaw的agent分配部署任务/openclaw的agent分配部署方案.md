openclaw的agent分配部署任务
QA 现在需要完成openclaw的agent分配部署任务，亚马逊运营，亚马逊广告，和亚马逊选品，怎么分配 openclaw 这些 agent，具体用法

# OpenClaw Agent 分配部署方案 — 亚马逊业务

> **说明**：OpenClaw   **多 Agent 系统架构的通用最佳实践** 来设计方案，适用于 OpenClaw 或任何类似的多 Agent 平台（如 CrewAI、AutoGen、LangGraph 等）。如果 OpenClaw ，请补充其 API/配置文档，我可以进一步细化。

---

## 一、整体架构总览

```
┌─────────────────────────────────────────────────────┐
│                  Orchestrator Agent                  │
│              (总调度 / Supervisor)                    │
└────────┬──────────────┬──────────────┬──────────────┘
         │              │              │
         ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Agent 1     │ │  Agent 2     │ │  Agent 3     │
│  亚马逊运营   │ │  亚马逊广告   │ │  亚马逊选品   │
│  (Operations)│ │ (Advertising)│ │  (Product    │
│              │ │              │ │  Selection)  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Tools/MCP   │ │  Tools/MCP   │ │  Tools/MCP   │
│  - SP-API    │ │  - Ads API   │ │  - Keepa     │
│  - Listing   │ │  - Bid Mgmt  │ │  - Jungle    │
│  - Inventory │ │  - Reports   │ │    Scout     │
│  - FBA       │ │  - Budget    │ │  - Helium10  │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 二、三大 Agent 详细定义

### Agent 1: 亚马逊运营 Agent (Operations Agent)

```yaml
# agent_operations.yaml
agent:
  name: "amazon_operations_agent"
  role: "亚马逊运营专家"
  goal: "管理和优化亚马逊店铺日常运营，包括Listing优化、库存管理、订单处理、客服回复、绩效监控"
  backstory: |
    你是一位资深亚马逊运营专家，拥有5年以上亚马逊FBA运营经验。
    精通Listing优化、A+内容制作、库存周转管理、差评处理、
    账号健康维护、Buy Box竞争策略。

  tools:
    - amazon_sp_api          # Selling Partner API
    - listing_optimizer       # Listing标题/五点/描述优化
    - inventory_manager       # 库存监控与补货建议
    - review_monitor          # 评论监控与回复
    - competitor_tracker      # 竞品监控
    - pricing_engine          # 动态定价工具

  tasks:
    - listing_optimization    # Listing优化
    - inventory_forecasting   # 库存预测
    - order_management        # 订单管理
    - performance_monitoring  # 绩效监控
    - customer_service        # 客服处理
    - buybox_strategy         # Buy Box策略
```

**核心职责与具体用法**：

```python
# operations_agent.py

class AmazonOperationsAgent:
    """亚马逊运营 Agent"""

    def __init__(self, config):
        self.agent = Agent(
            name="amazon_operations_agent",
            system_prompt="""
            你是亚马逊运营专家，负责以下核心任务：

            1. 【Listing优化】
               - 分析关键词并优化标题（<200字符，核心词前置）
               - 优化五点描述（突出卖点、嵌入关键词）
               - 优化后台Search Terms
               - A+页面内容建议

            2. 【库存管理】
               - 监控IPI分数（目标>400）
               - FBA库存周转率分析
               - 自动补货提醒（基于销售速度+物流时效）
               - 长期仓储费预警

            3. 【绩效监控】
               - ODR（订单缺陷率）< 1%
               - 迟发率 < 4%
               - 有效追踪率 > 95%
               - 账号健康仪表盘

            4. 【竞品分析】
               - 监控竞品价格变动
               - 跟踪竞品Listing变化
               - Buy Box占有率分析

            5. 【客户服务】
               - 差评分析与回复建议
               - A-to-Z索赔处理建议
               - 退款/退货趋势分析
            """,
            tools=[
                sp_api_tool,
                listing_tool,
                inventory_tool,
                review_tool,
                pricing_tool,
            ],
            model="gpt-4o",  # 或其他LLM
        )

    # ---- 具体任务方法 ----

    def optimize_listing(self, asin: str) -> dict:
        """优化指定ASIN的Listing"""
        task = Task(
            description=f"""
            分析ASIN {asin} 的当前Listing，提供优化建议：
            1. 调用SP-API获取当前Listing数据
            2. 分析竞品Top 10的标题和关键词
            3. 生成优化后的标题、五点、描述、Search Terms
            4. 输出对比报告（Before vs After）
            """,
            expected_output="优化后的完整Listing内容 + 关键词报告"
        )
        return self.agent.execute(task)

    def check_inventory_health(self) -> dict:
        """库存健康检查"""
        task = Task(
            description="""
            执行全店库存健康检查：
            1. 获取所有FBA SKU的库存数据
            2. 计算每个SKU的日均销量和可售天数
            3. 标记需要补货的SKU（可售天数<30天）
            4. 标记滞销SKU（90天无销售）
            5. 计算预计长期仓储费
            6. 生成补货计划表
            """,
            expected_output="库存健康报告 + 补货建议表"
        )
        return self.agent.execute(task)

    def daily_report(self) -> dict:
        """每日运营报告"""
        task = Task(
            description="""
            生成每日运营报告，包含：
            1. 昨日销售额、订单量、客单价
            2. 各ASIN销售排名变化
            3. Buy Box占有率变化
            4. 新增评论/差评预警
            5. 库存预警
            6. 账号健康指标
            7. 关键行动建议（Top 3）
            """,
            expected_output="结构化每日运营报告"
        )
        return self.agent.execute(task)
```

---

### Agent 2: 亚马逊广告 Agent (Advertising Agent)

```yaml
# agent_advertising.yaml
agent:
  name: "amazon_advertising_agent"
  role: "亚马逊广告优化专家"
  goal: "管理和优化亚马逊PPC广告，最大化ROAS，降低ACoS，提升广告驱动的销售额"
  backstory: |
    你是一位资深亚马逊广告专家，精通SP/SB/SD三种广告类型，
    擅长关键词策略、竞价优化、预算分配、广告结构搭建。
    目标ACoS控制在15-25%之间，ROAS > 4。

  tools:
    - amazon_ads_api          # Amazon Advertising API
    - keyword_research        # 关键词研究工具
    - bid_optimizer           # 竞价优化引擎
    - budget_allocator        # 预算分配工具
    - search_term_analyzer    # 搜索词分析
    - ads_report_generator    # 广告报表生成

  tasks:
    - campaign_management     # 广告活动管理
    - keyword_optimization    # 关键词优化
    - bid_adjustment          # 竞价调整
    - budget_optimization     # 预算优化
    - negative_keyword_mgmt   # 否定词管理
    - performance_reporting   # 效果报告
```

```python
# advertising_agent.py

class AmazonAdvertisingAgent:
    """亚马逊广告 Agent"""

    def __init__(self, config):
        self.agent = Agent(
            name="amazon_advertising_agent",
            system_prompt="""
            你是亚马逊PPC广告优化专家，负责以下核心任务：

            1. 【广告架构搭建】
               - SP广告：自动/手动-广泛/词组/精确 三层漏斗
               - SB广告：品牌推广+视频广告
               - SD广告：受众定向+商品定向

            2. 【关键词策略】
               - 从自动广告挖掘高转化词 → 手动精确
               - 竞品ASIN定向
               - 否定词管理（ACoS>50%且无转化的词）

            3. 【竞价优化规则】
               - ACoS < 目标ACoS → 提高竞价10-20%
               - ACoS > 目标ACoS x 1.5 → 降低竞价15-25%
               - 点击>20次无转化 → 暂停/否定
               - 新词首周给予较高竞价获取数据

            4. 【预算管理】
               - 按ASIN/Campaign分配预算
               - 高ROAS Campaign自动加预算
               - 低效Campaign降预算或暂停
               - 日预算用完提醒

            5. 【报表分析】
               - 每日：花费、销售额、ACoS、ROAS
               - 每周：关键词表现、搜索词报告
               - 每月：广告归因分析、整体ROI
            """,
            tools=[
                ads_api_tool,
                keyword_tool,
                bid_tool,
                budget_tool,
                report_tool,
            ],
            model="gpt-4o",
        )

    def optimize_bids(self, campaign_id: str) -> dict:
        """优化指定Campaign的竞价"""
        task = Task(
            description=f"""
            优化Campaign {campaign_id} 的竞价：
            1. 拉取最近14天的关键词级别数据
            2. 按以下规则调整：
               - 高转化词（CVR>15%, ACoS<目标）：竞价+15%
               - 中等表现词（ACoS在目标±5%）：维持不变
               - 低效词（ACoS>目标x2）：竞价-20%
               - 无转化词（clicks>20, orders=0）：暂停
            3. 生成调整前后对比报告
            4. 执行竞价调整（需确认）
            """,
            expected_output="竞价调整方案 + 预估效果"
        )
        return self.agent.execute(task)

    def harvest_keywords(self) -> dict:
        """从自动广告收割关键词到手动广告"""
        task = Task(
            description="""
            执行关键词收割流程：
            1. 拉取所有自动Campaign的搜索词报告（最近30天）
            2. 筛选高价值词：orders>=2 且 ACoS<目标ACoS
            3. 检查这些词是否已存在于手动Campaign
            4. 对不存在的词：
               - 添加到对应手动Campaign（精确匹配）
               - 在自动Campaign中添加为精确否定
            5. 生成收割报告
            """,
            expected_output="关键词收割报告 + 操作日志"
        )
        return self.agent.execute(task)

    def weekly_ads_report(self) -> dict:
        """每周广告报告"""
        task = Task(
            description="""
            生成每周广告绩效报告：
            1. 总花费、总销售额、整体ACoS、TACoS
            2. Top 10 高ROAS关键词
            3. Top 10 高花费低转化关键词（需优化）
            4. 各Campaign类型表现对比（SP/SB/SD）
            5. 预算利用率分析
            6. 下周优化建议（Top 5 行动项）
            """,
            expected_output="结构化周报"
        )
        return self.agent.execute(task)
```

---

### Agent 3: 亚马逊选品 Agent (Product Selection Agent)

```yaml
# agent_product_selection.yaml
agent:
  name: "amazon_product_selection_agent"
  role: "亚马逊选品分析专家"
  goal: "通过数据驱动的方法发现高潜力、低竞争的产品机会，评估市场容量和利润空间"
  backstory: |
    你是一位资深亚马逊选品专家，精通市场分析、竞争评估、
    利润计算、趋势预测。你的选品命中率在行业中名列前茅。
    擅长用数据说话，每个推荐都有充分的数据支撑。

  tools:
    - keepa_api               # Keepa价格/排名历史
    - jungle_scout_api        # 市场数据
    - helium10_api            # 关键词/市场分析
    - alibaba_sourcing        # 1688/阿里巴巴采购成本
    - fba_calculator          # FBA费用计算器
    - google_trends           # 趋势分析
    - patent_search           # 专利检索
    - review_analyzer         # 竞品评论分析

  tasks:
    - market_research         # 市场调研
    - competition_analysis    # 竞争分析
    - profit_calculation      # 利润核算
    - trend_analysis          # 趋势分析
    - supplier_research       # 供应商调研
    - risk_assessment         # 风险评估
```

```python
# product_selection_agent.py

class AmazonProductSelectionAgent:
    """亚马逊选品 Agent"""

    def __init__(self, config):
        self.agent = Agent(
            name="amazon_product_selection_agent",
            system_prompt="""
            你是亚马逊选品分析专家，负责以下核心任务：

            1. 【市场调研】
               - 分析目标品类的市场容量（月搜索量、月销售额）
               - 评估市场集中度（Top 10品牌占比）
               - 分析价格区间分布
               - 新品上架成功率

            2. 【选品标准（硬指标）】
               ✅ 月搜索量 > 10,000
               ✅ 头部竞品月销 > 300单
               ✅ 售价区间 $15-$75
               ✅ 毛利率 > 30%
               ✅ 评论门槛 < 500条（Top 10平均）
               ✅ 非季节性（或可预测季节性）
               ✅ 产品重量 < 2磅（降低FBA费用）
               ✅ 无专利/品牌壁垒

            3. 【竞品分析】
               - 分析Top 20竞品的Listing质量
               - 评论分析：挖掘痛点和改进机会
               - 价格趋势和利润空间
               - 上架时间和成长曲线

            4. 【利润核算】
               - 采购成本（含运费）
               - FBA费用（配送费+仓储费）
               - 广告费用预估（占比20-30%）
               - 退货率预估
               - 净利润率目标 > 15%

            5. 【风险评估】
               - 侵权风险检查
               - 季节性风险
               - 供应链风险
               - 合规/认证要求
               - 竞争加剧风险
            """,
            tools=[
                keepa_tool,
                jungle_scout_tool,
                helium10_tool,
                sourcing_tool,
                fba_calc_tool,
                trends_tool,
                patent_tool,
                review_tool,
            ],
            model="gpt-4o",
        )

    def analyze_niche(self, keyword: str, marketplace: str = "US") -> dict:
        """分析某个细分市场"""
        task = Task(
            description=f"""
            深度分析细分市场："{keyword}"（站点：{marketplace}）

            请按以下步骤执行：
            1. 通过Helium10获取该关键词的月搜索量和趋势
            2. 获取搜索结果前20名的产品数据
            3. 分析市场指标：
               - 月总销售额和平均月销量
               - 价格分布（最低/最高/平均/中位数）
               - 评论数分布
               - 品牌集中度
               - 新品占比（上架<1年）
            4. 计算市场机会评分（1-100）
            5. 给出明确结论：推荐进入/谨慎/不推荐

            输出格式：结构化分析报告
            """,
            expected_output="市场分析报告 + 机会评分"
        )
        return self.agent.execute(task)

    def evaluate_product(self, asin: str) -> dict:
        """评估某个具体产品的可行性"""
        task = Task(
            description=f"""
            评估产品 {asin} 作为选品对象的可行性：
            1. Keepa拉取价格和排名历史（12个月）
            2. 分析评论内容（差评痛点 → 改进机会）
            3. 估算采购成本（1688/阿里巴巴）
            4. 计算完整利润表：
               - 售价
               - 采购成本 + 头程运费
               - FBA费用
               - 广告预算（预估ACoS 25%）
               - 退货预留（5%）
               - 净利润和利润率
            5. 专利/品牌侵权风险检查
            6. 给出综合评分和建议
            """,
            expected_output="产品可行性评估报告"
        )
        return self.agent.execute(task)

    def discover_opportunities(self, category: str) -> dict:
        """在指定品类中发现机会"""
        task = Task(
            description=f"""
            在品类 "{category}" 中发现选品机会：
            1. 扫描该品类下的子品类和热门关键词
            2. 筛选符合以下条件的细分市场：
               - 月搜索量 > 10,000
               - 竞品平均评论 < 500
               - 平均售价 $15-$75
               - 非垄断市场（Top 3品牌占比 < 50%）
            3. 对每个机会计算"机会分数"
            4. 输出Top 10机会清单（附数据支撑）
            5. 对Top 3机会提供详细分析
            """,
            expected_output="选品机会清单 + Top 3详细报告"
        )
        return self.agent.execute(task)
```

---

## 三、Orchestrator 总调度 Agent

```python
# orchestrator.py

class AmazonOrchestrator:
    """总调度Agent - 协调三个子Agent"""

    def __init__(self):
        self.ops_agent = AmazonOperationsAgent(config)
        self.ads_agent = AmazonAdvertisingAgent(config)
        self.selection_agent = AmazonProductSelectionAgent(config)

        self.orchestrator = Agent(
            name="amazon_orchestrator",
            system_prompt="""
            你是亚马逊业务总调度员。根据用户的需求，判断应该：
            1. 分配给哪个专业Agent处理
            2. 是否需要多个Agent协作
            3. 汇总各Agent的结果给用户

            Agent清单：
            - operations_agent: 运营相关（Listing、库存、订单、客服）
            - advertising_agent: 广告相关（PPC、竞价、关键词、预算）
            - selection_agent: 选品相关（市场分析、竞品、利润、趋势）

            协作场景示例：
            - "新品上架" → selection_agent(评估) → ops_agent(Listing) → ads_agent(广告计划)
            - "这个产品值不值得卖" → selection_agent
            - "优化广告" → ads_agent
            - "日常运营报告" → ops_agent + ads_agent
            """,
            sub_agents=[self.ops_agent, self.ads_agent, self.selection_agent],
        )

    def handle_request(self, user_input: str):
        """处理用户请求，自动路由到对应Agent"""
        return self.orchestrator.execute(user_input)


# ====== 使用示例 ======
if __name__ == "__main__":
    amazon = AmazonOrchestrator()

    # 场景1：选品分析
    amazon.handle_request("帮我分析 yoga mat 这个品类值不值得进入")

    # 场景2：广告优化
    amazon.handle_request("我的SP广告ACoS太高了，帮我优化竞价")

    # 场景3：运营管理
    amazon.handle_request("生成今天的运营日报")

    # 场景4：多Agent协作 - 新品上架全流程
    amazon.handle_request("""
        我想在美国站上架一款新的瑜伽垫，请帮我：
        1. 分析市场竞争情况
        2. 写一份优化的Listing
        3. 制定前期广告推广计划
    """)
```

---

## 四、Agent 间协作流程

### 新品上架全流程（三 Agent 协作）

```
┌──────────────────────────────────────────────────────────┐
│                    新品上架全流程                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Phase 1: 选品Agent                                      │
│  ┌─────────────────────────────────────┐                │
│  │ ① 市场容量分析                       │                │
│  │ ② 竞争格局评估                       │                │
│  │ ③ 利润核算                           │                │
│  │ ④ 输出：选品报告 + 关键词列表          │                │
│  └──────────────┬──────────────────────┘                │
│                 │ 传递：关键词列表、竞品分析、定价建议        │
│                 ▼                                        │
│  Phase 2: 运营Agent                                      │
│  ┌─────────────────────────────────────┐                │
│  │ ① 基于关键词撰写Listing                │                │
│  │ ② 设置定价策略                        │                │
│  │ ③ 制定FBA发货计划                     │                │
│  │ ④ 输出：完整Listing + 运营计划          │                │
│  └──────────────┬──────────────────────┘                │
│                 │ 传递：目标关键词、ASIN、售价               │
│                 ▼                                        │
│  Phase 3: 广告Agent                                      │
│  ┌─────────────────────────────────────┐                │
│  │ ① 搭建广告架构（自动+手动）             │                │
│  │ ② 设置初始竞价和预算                   │                │
│  │ ③ 制定前30天推广节奏                   │                │
│  │ ④ 输出：广告计划 + 预算方案              │                │
│  └─────────────────────────────────────┘                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

```python
# workflows/new_product_launch.py

async def new_product_launch_workflow(product_idea: str):
    """新品上架工作流 — 三Agent协作"""

    # Phase 1: 选品分析
    selection_result = await selection_agent.analyze_niche(product_idea)

    if selection_result["opportunity_score"] < 60:
        return {"status": "不推荐", "reason": selection_result["summary"]}

    # Phase 2: 运营准备
    ops_result = await ops_agent.create_listing(
        keywords=selection_result["top_keywords"],
        competitors=selection_result["top_competitors"],
        price_suggestion=selection_result["suggested_price"],
    )

    # Phase 3: 广告计划
    ads_result = await ads_agent.create_launch_plan(
        asin=ops_result["asin"],
        keywords=selection_result["top_keywords"],
        target_acos=selection_result["max_acos"],
        daily_budget=selection_result["suggested_ad_budget"],
    )

    return {
        "selection_report": selection_result,
        "listing": ops_result,
        "ads_plan": ads_result,
    }
```

---

## 五、工具 (Tools / MCP) 配置

```python
# tools/amazon_tools.py

# ---- 运营Agent的Tools ----
sp_api_tool = Tool(
    name="amazon_sp_api",
    description="调用Amazon Selling Partner API获取订单/库存/Listing数据",
    function=call_sp_api,
    params=["endpoint", "method", "payload"]
)

listing_tool = Tool(
    name="listing_optimizer",
    description="分析和优化亚马逊Listing的标题、五点、描述、关键词",
    function=optimize_listing,
    params=["asin", "marketplace", "target_keywords"]
)

# ---- 广告Agent的Tools ----
ads_api_tool = Tool(
    name="amazon_ads_api",
    description="调用Amazon Advertising API管理广告活动",
    function=call_ads_api,
    params=["endpoint", "method", "payload"]
)

bid_tool = Tool(
    name="bid_optimizer",
    description="根据历史数据和规则自动优化关键词竞价",
    function=optimize_bids,
    params=["campaign_id", "strategy", "target_acos"]
)

# ---- 选品Agent的Tools ----
keepa_tool = Tool(
    name="keepa_api",
    description="获取亚马逊产品的历史价格、排名、评论数据",
    function=call_keepa,
    params=["asin", "domain", "days"]
)

fba_calc_tool = Tool(
    name="fba_calculator",
    description="计算FBA费用（配送费+仓储费+其他费用）",
    function=calculate_fba_fees,
    params=["dimensions", "weight", "price", "category"]
)
```

---

## 六、定时任务调度

```python
# scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# ===== 每日任务 =====
@scheduler.scheduled_job('cron', hour=8, minute=0)
async def daily_operations_report():
    """每天早8点 — 运营日报"""
    report = await ops_agent.daily_report()
    send_to_dingtalk(report)  # 推送到钉钉/企业微信

@scheduler.scheduled_job('cron', hour=9, minute=0)
async def daily_ads_check():
    """每天早9点 — 广告数据检查"""
    alerts = await ads_agent.check_anomalies()
    if alerts:
        send_to_dingtalk(alerts)

# ===== 每周任务 =====
@scheduler.scheduled_job('cron', day_of_week='mon', hour=10)
async def weekly_ads_report():
    """每周一上午10点 — 广告周报"""
    report = await ads_agent.weekly_ads_report()
    send_to_email(report)

@scheduler.scheduled_job('cron', day_of_week='mon', hour=10)
async def weekly_keyword_harvest():
    """每周一 — 关键词收割"""
    result = await ads_agent.harvest_keywords()
    log_operation(result)

# ===== 每月任务 =====
@scheduler.scheduled_job('cron', day=1, hour=10)
async def monthly_product_scan():
    """每月1号 — 选品机会扫描"""
    opportunities = await selection_agent.discover_opportunities("全品类扫描")
    send_to_email(opportunities)

scheduler.start()
```

---

## 七、部署架构建议

```
┌─────────────────────────────────────────────────┐
│                 部署架构                          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐    ┌──────────────────────┐  │
│  │   Frontend    │    │   Message Queue      │  │
│  │  (Web UI /    │───▶│   (Redis / RabbitMQ) │  │
│  │   API)        │    └──────────┬───────────┘  │
│  └──────────────┘               │               │
│                                 ▼               │
│  ┌──────────────────────────────────────────┐   │
│  │         Orchestrator Service              │   │
│  │      (FastAPI / Flask + Celery)           │   │
│  └────┬──────────────┬──────────────┬───────┘   │
│       │              │              │            │
│       ▼              ▼              ▼            │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │ Ops     │  │ Ads     │  │ Selection   │    │
│  │ Worker  │  │ Worker  │  │ Worker      │    │
│  └────┬────┘  └────┬────┘  └──────┬──────┘    │
│       │            │              │             │
│       ▼            ▼              ▼             │
│  ┌──────────────────────────────────────────┐   │
│  │         Shared Database                   │   │
│  │   (PostgreSQL + Redis Cache)              │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │         External APIs                     │   │
│  │  SP-API | Ads API | Keepa | Helium10     │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 八、快速对照总结

| 维度 | 运营 Agent | 广告 Agent | 选品 Agent |
|------|-----------|-----------|-----------|
| **核心职责** | 店铺日常管理 | PPC广告优化 | 产品机会发现 |
| **关键指标** | BSR, CVR, 评分 | ACoS, ROAS, CTR | 市场容量, 利润率 |
| **数据源** | SP-API, Seller Central | Advertising API | Keepa, Helium10, 1688 |
| **执行频率** | 每日 | 每日/每周 | 按需/每月 |
| **输出物** | 运营报告, Listing | 广告方案, 竞价表 | 选品报告, 利润表 |
| **自动化程度** | 中（需人工确认） | 高（规则可自动） | 低（决策需人工） |
| **协作关系** | 接收选品的关键词 | 接收运营的ASIN | 为另外两者提供数据基础 |

---

如果你能分享 **OpenClaw 的具体文档、API 或配置格式**，我可以将以上方案直接转化为 OpenClaw 的原生配置文件和代码。






# 亚马逊卖家全链路 Sub-Agent 分配指南

---

## 一、先看全貌：卖家业务链路全景图

```
一个产品从0到1再到持续盈利的完整生命周期：

发现机会 → 验证可行 → 找到供应商 → 采购生产 → 国际物流 → FBA入仓
   │                                                        │
   ▼                                                        ▼
市场调研    ←──────────── 数据反馈 ──────────────→    上架销售
                                                        │
                    ┌───────────┬──────────┬────────────┤
                    ▼           ▼          ▼            ▼
                  Listing     广告推广    定价策略     客服/售后
                    │           │          │            │
                    └───────────┴──────────┴────────────┘
                                    │
                                    ▼
                            数据分析/财务核算
                                    │
                                    ▼
                          复盘 → 扩品/弃品决策
```

---

## 二、Sub-Agent 分层架构

```
                        ┌─────────────────────┐
                   L0   │   Boss Agent (你)    │  ← 卖家本人 / 总决策
                        │   战略决策层          │
                        └──────────┬──────────┘
                                   │
            ┌──────────┬───────────┼───────────┬──────────┐
            ▼          ▼           ▼           ▼          ▼
     ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
L1   │ 选品总监  ││ 供应链   ││ 运营总监  ││ 营销总监  ││ 财务总监  │
     │ Agent    ││ Agent    ││ Agent    ││ Agent    ││ Agent    │
     └────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘└────┬─────┘
          │           │           │           │           │
     ┌────┴────┐ ┌────┴────┐ ┌───┴────┐ ┌───┴────┐ ┌───┴────┐
L2   │ 具体    │ │ 具体    │ │ 具体   │ │ 具体   │ │ 具体   │
     │ 执行    │ │ 执行    │ │ 执行   │ │ 执行   │ │ 执行   │
     │ Sub-    │ │ Sub-    │ │ Sub-   │ │ Sub-   │ │ Sub-   │
     │ Agents  │ │ Agents  │ │ Agents │ │ Agents │ │ Agents │
     └─────────┘ └─────────┘ └────────┘ └────────┘ └────────┘
```

---

## 三、每个 Sub-Agent 的详细拆解

### 🔵 模块 1：选品研究 (Product Research)

```
┌─────────────────────────────────────────────────────┐
│              选品总监 Agent (L1)                      │
│  职责：汇总分析结果，给出 Go / No-Go 决策建议          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Sub-Agent 1.1 ─ 市场扫描员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 监控亚马逊BSR榜单变化（New Release/Movers） │   │
│  │ • 抓取社交媒体/TikTok热门产品趋势             │   │
│  │ • Google Trends关键词趋势追踪                 │   │
│  │ • 输出：潜在机会清单（每周更新）                │   │
│  │ 工具：Helium10 BlackBox, Google Trends API    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 1.2 ─ 市场验证员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 分析品类月搜索量、月销售额                   │   │
│  │ • 评估竞争强度（评论门槛、品牌集中度）          │   │
│  │ • 分析价格区间和利润空间                       │   │
│  │ • 检查季节性波动                              │   │
│  │ • 输出：市场可行性评分（1-100）                │   │
│  │ 工具：Jungle Scout, Keepa API                 │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 1.3 ─ 竞品解剖员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 拆解Top 20竞品的Listing结构                  │   │
│  │ • 分析竞品差评（1-3星）→ 提炼用户痛点           │   │
│  │ • 分析竞品好评（4-5星）→ 提炼核心卖点           │   │
│  │ • 评估竞品图片/A+质量                          │   │
│  │ • 输出：竞品分析矩阵 + 差异化机会               │   │
│  │ 工具：Review分析器, Listing抓取器               │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 1.4 ─ 合规检查员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 专利检索（USPTO/Google Patents）             │   │
│  │ • 商标检索（避免侵权）                         │   │
│  │ • 产品认证需求（FDA/FCC/UL等）                 │   │
│  │ • 亚马逊品类审核要求                           │   │
│  │ • 输出：合规风险报告                           │   │
│  │ 工具：USPTO API, 商标数据库                    │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 🟢 模块 2：供应链管理 (Supply Chain)

```
┌─────────────────────────────────────────────────────┐
│              供应链总监 Agent (L1)                     │
│  职责：统筹采购、质检、物流全流程                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Sub-Agent 2.1 ─ 供应商猎手                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 在1688/阿里巴巴搜索匹配供应商               │   │
│  │ • 比价分析（至少3家对比）                      │   │
│  │ • 供应商资质评估（年限、产能、认证）             │   │
│  │ • 生成询价模板和沟通话术                       │   │
│  │ • 输出：供应商对比表 + 推荐排名                 │   │
│  │ 工具：1688 API, 企查查                        │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 2.2 ─ 成本核算员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 产品单价 + 包装 + 贴标                      │   │
│  │ • 头程运费（海运/空运/快递对比）                │   │
│  │ • FBA费用精算                                 │   │
│  │ • 关税/增值税                                  │   │
│  │ • 总成本 → 定价 → 利润率                       │   │
│  │ • 输出：完整利润核算表                         │   │
│  │ 工具：FBA计算器, 运费查询API                   │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 2.3 ─ 物流调度员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 货代比价和时效对比                           │   │
│  │ • FBA入仓计划创建                              │   │
│  │ • 物流节点追踪                                 │   │
│  │ • 到货提醒                                    │   │
│  │ • 输出：物流方案 + 追踪报告                     │   │
│  │ 工具：货代API, SP-API(Inbound)                │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 2.4 ─ 库存管家                            │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 实时库存监控                                 │   │
│  │ • 销售速度预测 → 自动补货提醒                   │   │
│  │ • IPI分数管理                                  │   │
│  │ • 长期仓储费预警 + 清库存建议                   │   │
│  │ • 安全库存计算                                 │   │
│  │ • 输出：补货计划表（何时补、补多少）             │   │
│  │ 工具：SP-API(Inventory), 预测模型              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 🟠 模块 3：运营管理 (Operations)

```
┌─────────────────────────────────────────────────────┐
│              运营总监 Agent (L1)                      │
│  职责：Listing质量、日常运营、账号健康                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Sub-Agent 3.1 ─ Listing架构师                       │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 关键词调研和布局策略                         │   │
│  │ • 标题撰写（核心词+长尾词+卖点，<200字符）      │   │
│  │ • 五点描述撰写（痛点→方案→卖点）               │   │
│  │ • 产品描述/A+内容策划                          │   │
│  │ • Backend Search Terms优化                    │   │
│  │ • 主图/副图拍摄方案建议                        │   │
│  │ • 输出：完整Listing文案包                      │   │
│  │ 工具：Helium10 Cerebro/Magnet, SP-API         │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 3.2 ─ 定价策略师                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 竞品价格监控（实时）                         │   │
│  │ • Buy Box价格跟踪                             │   │
│  │ • 动态定价规则（跟价/压价/维持）                │   │
│  │ • 促销价格策划（Coupon/Lightning Deal）        │   │
│  │ • 价格弹性分析                                │   │
│  │ • 输出：定价方案 + 价格异动告警                 │   │
│  │ 工具：Keepa, SP-API(Pricing)                  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 3.3 ─ 评论管理员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 新评论实时监控                               │   │
│  │ • 差评预警（1-2星立即通知）                     │   │
│  │ • 差评分析归因（产品问题/物流/期望差异）         │   │
│  │ • 生成差评回复方案                             │   │
│  │ • Vine计划/Request a Review管理               │   │
│  │ • 输出：评论日报 + 差评处理方案                 │   │
│  │ 工具：SP-API(Reviews), 情感分析模型            │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 3.4 ─ 客服机器人                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 买家消息自动分类                             │   │
│  │ • 常见问题自动回复草稿                         │   │
│  │ • 退货/退款原因分析                            │   │
│  │ • A-to-Z Claim应对方案                        │   │
│  │ • 回复时效监控（<24h）                         │   │
│  │ • 输出：回复草稿（人工确认后发送）               │   │
│  │ 工具：SP-API(Messaging), 模板库                │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 3.5 ─ 账号健康守卫                        │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 账号健康指标实时监控                         │   │
│  │ • ODR/迟发率/有效追踪率 阈值告警               │   │
│  │ • 政策违规预警                                 │   │
│  │ • 侵权投诉应对方案                             │   │
│  │ • 输出：账号健康周报 + 紧急告警                 │   │
│  │ 工具：SP-API(Account Health)                  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 🔴 模块 4：营销推广 (Marketing)

```
┌─────────────────────────────────────────────────────┐
│              营销总监 Agent (L1)                      │
│  职责：站内广告 + 站外推广，最大化流量和转化            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Sub-Agent 4.1 ─ SP广告专员 (Sponsored Products)     │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 自动广告 → 数据收集（新品前2周）              │   │
│  │ • 手动广告搭建（广泛→词组→精确 漏斗）           │   │
│  │ • 每日竞价优化                                 │   │
│  │ • 搜索词报告分析 → 关键词收割                   │   │
│  │ • 否定词管理                                   │   │
│  │ • ASIN定向（竞品投放）                         │   │
│  │ 工具：Ads API(SP)                             │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 4.2 ─ SB/SD广告专员                       │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 品牌推广(SB)活动管理                         │   │
│  │ • 视频广告(SBV)脚本建议                        │   │
│  │ • 展示广告(SD)受众定向                         │   │
│  │ • 品牌旗舰店流量分析                           │   │
│  │ 工具：Ads API(SB/SD)                          │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 4.3 ─ 预算管控员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 广告总预算分配（按ASIN/Campaign）             │   │
│  │ • TACoS监控（广告占总销售比）                   │   │
│  │ • ROI最大化分配策略                            │   │
│  │ • 日预算耗尽预警                               │   │
│  │ • 分时竞价策略（高峰时段加码）                   │   │
│  │ 工具：Ads API(Budget), 自定义优化模型           │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 4.4 ─ 促销策划员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • Coupon/Deal策划和提报                        │   │
│  │ • Prime Day/黑五等大促节奏规划                  │   │
│  │ • 站外推广计划（社媒/红人/Deal站）              │   │
│  │ • 促销效果复盘                                 │   │
│  │ 工具：SP-API(Promotions), 社媒API              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

### 🟣 模块 5：数据分析与财务 (Analytics & Finance)

```
┌─────────────────────────────────────────────────────┐
│              财务总监 Agent (L1)                      │
│  职责：数据看板、财务核算、经营决策支持                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Sub-Agent 5.1 ─ 数据分析师                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 销售数据看板（日/周/月）                     │   │
│  │ • 转化率漏斗分析                               │   │
│  │   (曝光→点击→加购→购买 每环节转化率)            │   │
│  │ • 关键词排名追踪                               │   │
│  │ • 竞品数据对标                                 │   │
│  │ • 异常数据告警（销量骤降/排名下跌）             │   │
│  │ 工具：SP-API(Reports), BI工具                  │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 5.2 ─ 财务核算员                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • SKU级别利润核算                              │   │
│  │ • 亚马逊费用明细拆解                           │   │
│  │   (佣金/FBA/仓储/广告/退货/其他)               │   │
│  │ • 月度P&L报表                                  │   │
│  │ • 现金流预测                                   │   │
│  │ • 亏损ASIN预警                                 │   │
│  │ 工具：SP-API(Financial), 财务模型               │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  Sub-Agent 5.3 ─ 决策支持官                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ • 汇总所有Agent数据 → 经营仪表盘               │   │
│  │ • ASIN生命周期评估（成长/成熟/衰退）            │   │
│  │ • 弃品建议（连续亏损/低周转）                   │   │
│  │ • 扩品方向建议（联动选品Agent）                 │   │
│  │ • 年度经营规划辅助                             │   │
│  │ 工具：全部数据源的只读权限                      │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 四、不同规模卖家的分配策略

> **不是每个卖家都需要全部 Agent，根据规模按需部署**

```
┌────────────────────────────────────────────────────────────────┐
│                    按卖家规模分配                                │
├────────────┬──────────────┬──────────────┬─────────────────────┤
│  Agent     │  小卖家       │  中型卖家     │  大卖家/品牌卖家    │
│            │ (月销<$10K)   │ ($10K-$100K) │  (月销>$100K)      │
├────────────┼──────────────┼──────────────┼─────────────────────┤
│ 选品       │              │              │                     │
│  市场扫描   │  ✅ 合并为    │  ✅           │  ✅                │
│  市场验证   │  1个选品Agent │  ✅           │  ✅                │
│  竞品解剖   │              │  ✅           │  ✅                │
│  合规检查   │  ❌ 人工      │  ⚠️ 半自动    │  ✅                │
├────────────┼──────────────┼──────────────┼─────────────────────┤
│ 供应链     │              │              │                     │
│  供应商     │  ❌ 人工      │  ✅ 合并为    │  ✅                │
│  成本核算   │  ✅ 用Excel   │  1个供应链    │  ✅                │
│  物流调度   │  ❌ 人工      │  Agent       │  ✅                │
│  库存管家   │  ✅ 简版      │  ✅           │  ✅                │
├────────────┼──────────────┼──────────────┼─────────────────────┤
│ 运营       │              │              │                     │
│  Listing   │  ✅ 合并为    │  ✅           │  ✅                │
│  定价      │  1个运营Agent │  ✅           │  ✅                │
│  评论管理   │              │  ✅           │  ✅                │
│  客服      │  ❌ 人工      │  ⚠️ 半自动    │  ✅                │
│  账号健康   │  ⚠️ 简单监控  │  ✅           │  ✅                │
├────────────┼──────────────┼──────────────┼─────────────────────┤
│ 营销       │              │              │                     │
│  SP广告    │  ✅ 合并为    │  ✅           │  ✅                │
│  SB/SD广告 │  1个广告Agent │  ✅           │  ✅                │
│  预算管控   │              │  ✅           │  ✅                │
│  促销策划   │  ❌ 人工      │  ⚠️ 半自动    │  ✅                │
├────────────┼──────────────┼──────────────┼─────────────────────┤
│ 数据/财务  │              │              │                     │
│  数据分析   │  ✅ 合并为    │  ✅           │  ✅                │
│  财务核算   │  1个报表Agent │  ✅           │  ✅                │
│  决策支持   │              │  ⚠️ 半自动    │  ✅                │
├────────────┼──────────────┼──────────────┼─────────────────────┤
│ Agent总数   │  4个          │  8-12个       │  16-20个           │
│ 月成本预估  │  $50-100      │  $200-500     │  $1000+            │
│ (API+LLM)  │              │              │                     │
└────────────┴──────────────┴──────────────┴─────────────────────┘
```

---

## 五、小卖家最小可行方案 (4 Agent)

```python
# 小卖家配置 — 4个合并Agent，覆盖核心需求

agents = {
    "scout": {
        "name": "选品Scout",
        "covers": ["市场扫描", "市场验证", "竞品分析", "成本核算"],
        "prompt": """
        你同时负责选品调研和成本核算：
        1. 分析关键词搜索量和竞争度
        2. 拆解竞品差评找机会
        3. 计算采购成本+FBA费用+目标利润
        4. 给出Go/No-Go建议
        """,
        "schedule": "按需触发",
    },

    "operator": {
        "name": "运营管家",
        "covers": ["Listing优化", "定价监控", "评论监控", "库存提醒"],
        "prompt": """
        你是全能运营管家：
        1. 优化Listing文案和关键词
        2. 每日检查竞品价格变化
        3. 监控新评论，差评立即告警
        4. 库存低于安全线时提醒补货
        """,
        "schedule": "每日早8点",
    },

    "advertiser": {
        "name": "广告管家",
        "covers": ["SP广告管理", "竞价优化", "关键词收割", "预算管理"],
        "prompt": """
        你负责全部PPC广告：
        1. 管理自动和手动广告
        2. 每日检查ACoS异常词
        3. 每周从自动广告收割关键词
        4. 控制总广告预算不超标
        """,
        "schedule": "每日早9点",
    },

    "analyst": {
        "name": "数据助手",
        "covers": ["销售报表", "利润核算", "异常告警"],
        "prompt": """
        你负责数据和财务：
        1. 每日出销售简报
        2. 每周出利润报表
        3. 发现异常立即告警
        """,
        "schedule": "每日晚8点",
    },
}
```

---

## 六、Agent 间协作的信息流

```
关键协作场景及数据传递关系：

场景A：新品从0到1
═══════════════════════════════════════════════════

选品Scout ──→ "这个品类OK，目标关键词是xxx，建议售价$29.99"
    │
    ▼
供应链Agent ──→ "供应商找到了，单价$5.2，头程$1.8，FBA费$4.5"
    │
    ▼
运营管家 ──→ "Listing写好了，ASIN: B0XXXXX，已上架"
    │
    ▼
广告管家 ──→ "广告架构搭好了：
              自动Campaign $20/day
              手动广泛 $15/day
              首周预算共$245"
    │
    ▼
数据助手 ──→ "第7天报告：
              销量12单/天，BSR #45,000
              广告ACoS 45%（新品正常）
              建议继续，第14天复盘"


场景B：日常运营闭环（每日自动执行）
═══════════════════════════════════════════════════

08:00  运营管家 ──→ 检查账号健康 ✅
                    检查库存 ⚠️ SKU-A需补货
                    检查评论 🔴 新增1条差评

08:30  广告管家 ──→ 昨日广告数据正常 ✅
                    关键词"xxx"ACoS过高 → 降价
                    预算使用率85% ✅

20:00  数据助手 ──→ 汇总今日数据：
                    总销售$1,234 (+5%)
                    总利润$387 (31.4%)
                    行动项：
                    ① 补货SKU-A（运营管家已提醒）
                    ② 回复差评（运营管家已起草）
                    ③ 关键词竞价已调整（广告管家已执行）


场景C：危机响应（事件驱动）
═══════════════════════════════════════════════════

                    ┌──────────────┐
                    │  触发事件：    │
                    │ 销量骤降50%   │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         运营管家      广告管家      数据助手
         检查：        检查：        检查：
         ·Listing被    ·广告是否     ·是否全品类
          篡改？        暂停？        下降？
         ·是否被跟      ·竞价是否     ·竞品是否
          卖？          被超？        大促？
         ·Buy Box      ·预算是否     ·是否季节
          丢了？        花完？        性因素？
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │  汇总诊断：    │
                    │ Buy Box被抢   │
                    │ 原因：竞品降价  │
                    │ 建议：跟价至   │
                    │ $24.99 + 加   │
                    │ Coupon 10%    │
                    └──────────────┘
```

---

## 七、实际部署代码框架

```python
# main.py — 完整部署框架

from dataclasses import dataclass
from enum import Enum
from typing import Optional

class AgentPriority(Enum):
    CRITICAL = 1   # 账号健康、危机
    HIGH = 2       # 库存告急、差评
    NORMAL = 3     # 日常报表
    LOW = 4        # 选品扫描

@dataclass
class AgentMessage:
    """Agent间通信的标准消息格式"""
    from_agent: str
    to_agent: str
    action: str
    data: dict
    priority: AgentPriority

class AmazonAgentOrchestrator:
    """亚马逊卖家Agent总调度"""

    def __init__(self, seller_tier: str = "small"):
        self.seller_tier = seller_tier
        self.agents = self._init_agents(seller_tier)
        self.message_queue = []

    def _init_agents(self, tier: str) -> dict:
        if tier == "small":
            return {
                "scout": ProductScoutAgent(),
                "operator": OperationsAgent(),
                "advertiser": AdvertisingAgent(),
                "analyst": AnalyticsAgent(),
            }
        elif tier == "medium":
            return {
                # 选品拆分
                "market_scanner": MarketScannerAgent(),
                "market_validator": MarketValidatorAgent(),
                "competitor_analyzer": CompetitorAgent(),
                # 供应链
                "supply_chain": SupplyChainAgent(),
                "inventory": InventoryAgent(),
                # 运营拆分
                "listing_writer": ListingAgent(),
                "pricing": PricingAgent(),
                "review_manager": ReviewAgent(),
                # 广告拆分
                "sp_ads": SPAdsAgent(),
                "sb_sd_ads": SBSDAdsAgent(),
                "budget_manager": BudgetAgent(),
                # 数据
                "analyst": AnalyticsAgent(),
                "finance": FinanceAgent(),
            }
        elif tier == "large":
            # ... 全部20个Agent
            pass

    async def run_daily_routine(self):
        """每日自动例行任务"""
        results = {}

        # Step 1: 健康检查（最高优先级）
        results["health"] = await self.agents["operator"].check_account_health()
        if results["health"]["status"] == "danger":
            await self._alert_boss("🚨 账号健康异常!", results["health"])
            return  # 优先处理危机

        # Step 2: 库存检查
        results["inventory"] = await self.agents["operator"].check_inventory()

        # Step 3: 评论检查
        results["reviews"] = await self.agents["operator"].check_reviews()

        # Step 4: 广告优化
        results["ads"] = await self.agents["advertiser"].daily_optimize()

        # Step 5: 汇总报告
        daily_report = await self.agents["analyst"].generate_daily_report(results)
        await self._send_report(daily_report)

    async def handle_user_query(self, query: str):
        """处理卖家的即时问题"""
        # 意图识别 → 路由到对应Agent
        intent = self._classify_intent(query)

        routing = {
            "选品": "scout",
            "listing": "operator",
            "广告": "advertiser",
            "库存": "operator",
            "利润": "analyst",
            "价格": "operator",
            "评论": "operator",
            "销量": "analyst",
        }

        target_agent = routing.get(intent, "analyst")
        return await self.agents[target_agent].handle(query)

    async def launch_new_product(self, product_idea: str):
        """新品上架全流程（多Agent协作）"""

        # Phase 1: 选品评估
        research = await self.agents["scout"].full_analysis(product_idea)
        if research["score"] < 60:
            return {"decision": "不推荐", "report": research}

        # Phase 2: 运营准备
        listing = await self.agents["operator"].create_listing(
            keywords=research["keywords"],
            selling_points=research["differentiators"],
            price=research["suggested_price"],
        )

        # Phase 3: 广告计划
        ads_plan = await self.agents["advertiser"].create_launch_plan(
            asin=listing["asin"],
            keywords=research["keywords"],
            budget=research["suggested_ad_budget"],
        )

        return {
            "decision": "Go",
            "research": research,
            "listing": listing,
            "ads_plan": ads_plan,
        }


# ====== 启动 ======
if __name__ == "__main__":
    # 小卖家用4个Agent
    amazon = AmazonAgentOrchestrator(seller_tier="small")

    # 每日自动运行
    scheduler.add_job(amazon.run_daily_routine, 'cron', hour=8)

    # 交互式问答
    # amazon.handle_user_query("帮我看看这个ASIN值不值得做")
    # amazon.launch_new_product("便携式搅拌杯")
```

---

## 八、总结：合理分配的核心原则

```
┌──────────────────────────────────────────────────────────┐
│                   分配原则总结                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. 按职责边界拆分，而非按功能堆叠                          │
│     ✅ "广告竞价优化" 归广告Agent                          │
│     ❌  让运营Agent又管库存又管广告                         │
│                                                          │
│  2. 每个Agent的Prompt要足够专精                            │
│     ✅ "你是SP广告专家，只关注ACoS和ROAS"                  │
│     ❌ "你什么都懂" → 什么都不精                           │
│                                                          │
│  3. 先少后多，按需扩展                                     │
│     小卖家 4个 → 中卖家 8-12个 → 大卖家 16-20个            │
│     先跑通核心链路，再拆分细化                              │
│                                                          │
│  4. 自动化程度逐步提升                                     │
│     Level 1: Agent建议 → 人工审批 → 人工执行                │
│     Level 2: Agent建议 → 人工审批 → 自动执行                │
│     Level 3: Agent决策 → 自动执行 → 人工复盘                │
│                                                          │
│  5. 数据打通是关键                                        │
│     所有Agent共享统一数据层                                │
│     Agent间通过标准消息格式通信                             │
│     避免数据孤岛                                          │
│                                                          │
│  6. 人在关键节点（Human-in-the-loop）                      │
│     ⚡ 选品Go/No-Go → 人决定                              │
│     ⚡ Listing发布 → 人审核                                │
│     ⚡ 大额预算调整 → 人批准                               │
│     🤖 竞价微调 → Agent自动                                │
│     🤖 日常报表 → Agent自动                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

根据你的实际情况（卖家规模、SKU数量、预算），我可以进一步帮你细化某个具体模块的 Agent 配置和 Prompt 设计。需要深入哪一块？

亚马逊广告计划（就是针对新品精铺广告投放策略），针对新品精铺广告投放策略（新品-精铺-正常价格-保守广告版），推新的完整方案流程落地,背景介绍：属于标品，没有季节性（季节性的没有）大部分产品的类目是宠物，客单价在20美金左右（宠物类目，还有一些杂货，20 美金左右客单）精铺的模式


# 亚马逊宠物类目 新品精铺广告投放全链路方案

> **适用场景**：宠物标品 | 客单价 ~$20 | 精铺模式 | 正常定价 | 保守广告
> **核心原则**：以小博大，用最少的广告预算跑出有效数据，稳步推进

---

## 一、先算清楚账：$20 客单价的利润结构

```
┌──────────────────────────────────────────────────────┐
│         $20 宠物产品 利润拆解（决定广告天花板）          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  售价                              $20.00   100%     │
│  ─────────────────────────────────────────────       │
│  亚马逊佣金 (15%)                  -$3.00            │
│  FBA配送费 (小标准件≈)             -$3.50            │
│  FBA仓储费 (月均≈)                 -$0.30            │
│  ─────────────────────────────────────────────       │
│  亚马逊费用小计                     -$6.80   34%     │
│  ─────────────────────────────────────────────       │
│  采购成本 (含包装)                  -$3.50            │
│  头程运费 (海运均摊)                -$1.50            │
│  ─────────────────────────────────────────────       │
│  货物成本小计                       -$5.00   25%     │
│  ─────────────────────────────────────────────       │
│  退货预留 (5%)                     -$1.00            │
│  ─────────────────────────────────────────────       │
│                                                      │
│  ★ 广告前毛利                       $7.20   36%     │
│                                                      │
│  ─────────────────── 关键线 ──────────────────       │
│                                                      │
│  广告预算 (目标TACoS 15%)          -$3.00            │
│  ─────────────────────────────────────────────       │
│  ★ 净利润                           $4.20   21%     │
│                                                      │
│  ═══════════════════════════════════════════════     │
│  关键指标推导：                                       │
│  • 广告前毛利 $7.20 → 最高可承受ACoS = 36%           │
│  • 盈亏平衡ACoS = 36%（超过这个就亏钱）               │
│  • 目标ACoS = 20-25%（保守策略）                     │
│  • 长期目标TACoS = 10-15%                           │
│  • CPC预估 = $0.60-$1.20（宠物类目）                 │
│  • 目标CVR ≥ 10%（标品正常水平）                      │
│                                                      │
│  每单最多能花在广告上的钱 = $7.20                      │
│  如果CPC=$0.80, 需要≤9次点击出1单 → CVR≥11%          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

> ⚠️ **$20客单价 + 保守策略 = 每一分钱广告费都要精打细算**

---

## 二、完整时间线总览

```
         新品上架
            │
Day 1───────┤  阶段一：数据收集期（冷启动）
            │  目标：让亚马逊认识你的产品
            │  预算：$10-15/天
            │  重点：自动广告 + 基础手动
Day 14──────┤
            │  阶段二：数据优化期（调整打磨）
            │  目标：找出赚钱的词，砍掉烧钱的词
            │  预算：$15-20/天
            │  重点：关键词收割 + 否定词
Day 30──────┤
            │  阶段三：放量冲刺期（加速跑）
            │  目标：核心词上首页，稳定出单
            │  预算：$20-30/天
            │  重点：精确词加码 + 竞品ASIN投放
Day 60──────┤
            │  阶段四：稳定收割期（降本增效）
            │  目标：降ACoS，提自然单占比
            │  预算：$15-25/天（效率优先）
            │  重点：TACoS持续下降
Day 90──────┤
            │  阶段五：长期维护期（自动驾驶）
            │  目标：TACoS<12%，广告利润双正
            │  预算：按ROI动态调整
            │
            ▼  产品进入成熟期
```

---

## 三、阶段一：数据收集期（Day 1-14）

### 3.1 上架前准备（Day 0 必须完成）

```
┌──────────────────────────────────────────────────────┐
│                上架前检查清单                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ✅ Listing质量达标（广告效果的前提！）                  │
│  ┌────────────────────────────────────────────┐     │
│  │ □ 主图白底高清，点击率>0.4%的标准              │     │
│  │ □ 6张副图：场景图+功能图+尺寸图+对比图         │     │
│  │ □ 标题：核心词前置，包含品牌+核心功能+材质       │     │
│  │   示例：BrandX Dog Leash, 6FT Heavy Duty      │     │
│  │   Nylon Leash with Padded Handle for          │     │
│  │   Medium Large Dogs, Reflective & Durable     │     │
│  │ □ 五点：每点一个核心卖点，嵌入2-3个关键词        │     │
│  │ □ A+页面已上传（品牌备案前提下）                │     │
│  │ □ 价格设置 $19.99（正常定价，不搞低价冲量）     │     │
│  │ □ 至少15个Review或开通Vine                    │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ✅ 关键词库准备好（开广告前就要整理好）                 │
│  ┌────────────────────────────────────────────┐     │
│  │ 第一梯队（核心大词，3-5个）                     │     │
│  │   dog leash / dog lead / pet leash              │     │
│  │                                                │     │
│  │ 第二梯队（精准长尾，10-15个）                    │     │
│  │   heavy duty dog leash large breed              │     │
│  │   reflective dog leash 6ft                      │     │
│  │   nylon dog leash with padded handle            │     │
│  │                                                │     │
│  │ 第三梯队（场景/属性词，10-20个）                  │     │
│  │   dog walking leash / training leash for dogs   │     │
│  │   no pull dog leash / strong dog leash          │     │
│  │                                                │     │
│  │ 竞品ASIN（5-10个同价位竞品）                     │     │
│  │   B0XXXXXX, B0YYYYYY ...                       │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ❌ 不要做的事：                                       │
│  │  × 低价上架再提价                                  │
│  │  × 一上来就开大量广告                               │
│  │  × 没有Review就猛砸广告                             │
│  │  × Listing没优化好就开广告（浪费钱）                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 3.2 广告架构搭建（Day 1 开启）

```
Day 1 开启的广告活动（共4个Campaign）
══════════════════════════════════════════════════════

Campaign 1: [AUTO] 产品名-自动广告
─────────────────────────────────────
├── 目的：让亚马逊给你匹配流量，收集搜索词数据
├── 竞价策略：固定竞价（Dynamic bids - fixed）
├── 日预算：$5/天
├── 默认竞价：$0.55（保守，宠物类目CPC约$0.6-1.2）
├── 4个投放组设置：
│   ├── 紧密匹配 (Close Match)    竞价 $0.55
│   ├── 宽泛匹配 (Loose Match)    竞价 $0.45
│   ├── 同类商品 (Substitutes)    竞价 $0.50
│   └── 关联商品 (Complements)    竞价 $0.35
│
├── 否定关键词（上来就加！避免浪费）：
│   ├── 否定精确：cat leash（如果你只做狗的）
│   ├── 否定精确：retractable leash（如果你不是伸缩的）
│   ├── 否定精确：leash holder / leash hook（不相关）
│   └── 否定词组：free / cheap / wholesale / used
│
└── 注意：不要开自动广告的 "仅降低" 模式
         新品没数据，用 "固定" 模式


Campaign 2: [SP-Manual-Broad] 产品名-手动广泛
─────────────────────────────────────
├── 目的：用广泛匹配拓展更多长尾词
├── 竞价策略：固定竞价
├── 日预算：$5/天
├── 关键词（广泛匹配）：选5-8个第二梯队词
│   ├── heavy duty dog leash         $0.60
│   ├── dog leash large breed        $0.60
│   ├── nylon dog leash              $0.55
│   ├── reflective dog leash         $0.55
│   ├── dog leash with handle        $0.50
│   └── dog walking leash            $0.50
│
├── 否定精确：把核心大词先否掉（大词放精确Campaign）
│   ├── dog leash
│   └── pet leash
│
└── 为什么不上精确？
    新品没数据不知道哪个词转化好，先用广泛探路


Campaign 3: [SP-Manual-Exact] 产品名-手动精确
─────────────────────────────────────
├── 目的：精准打核心关键词
├── 竞价策略：固定竞价
├── 日预算：$3/天（先少量，等数据验证）
├── 关键词（精确匹配）：只放2-3个最核心的词
│   ├── dog leash                    $0.75
│   ├── dog leash for large dogs     $0.65
│   └── heavy duty dog leash         $0.65
│
└── 注意：精确词竞价比广泛高15-20%
         因为精确匹配的竞争更直接


Campaign 4: [SP-Manual-ASIN] 产品名-竞品ASIN定向
─────────────────────────────────────
├── 目的：抢竞品的流量（出现在竞品详情页）
├── 竞价策略：固定竞价
├── 日预算：$2/天
├── 定向ASIN：选5个同价位、评论数<500的竞品
│   ├── B0XXXXXX（$19.99, 200 reviews, 4.2星）
│   ├── B0YYYYYY（$21.99, 150 reviews, 4.0星）
│   ├── B0ZZZZZZ（$18.99, 300 reviews, 4.3星）
│   ├── B0AAAAAA（$22.99, 100 reviews, 4.1星）
│   └── B0BBBBBB（$19.99, 250 reviews, 4.0星）
│
├── 选ASIN标准：
│   ✅ 价格接近你的（±$5）
│   ✅ 评论数不超过你太多
│   ✅ 评分≤4.3（你有差异化空间）
│   ✅ Listing质量一般（图片/文案不如你）
│   ❌ 不投大牌/超高评论数（打不过浪费钱）
│
└── 保守起见，日预算低，先看转化


═══════════════════════════════════════════════════
Day 1 广告预算汇总：
  自动广告:     $5/天
  手动广泛:     $5/天
  手动精确:     $3/天
  ASIN定向:     $2/天
  ─────────────────
  合计:         $15/天 ≈ $450/月
  
  占售价比：如果日出3单 → TACoS = $15/($60) = 25%
  可接受：新品前期TACoS 25-35% 是正常的
═══════════════════════════════════════════════════
```

### 3.3 Day 1-14 每日操作清单

```
┌──────────────────────────────────────────────────────┐
│              Day 1-14 每日检查动作                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  每天花15分钟做这些事：                                 │
│                                                      │
│  □ 1. 检查预算是否花完                                 │
│     ├── 如果中午就花完 → 不急着加，说明竞价可能偏高      │
│     ├── 如果花不到50% → 竞价可能偏低，加$0.05          │
│     └── 理想状态：每天花掉70-90%的预算                  │
│                                                      │
│  □ 2. 检查点击和花费                                   │
│     ├── 有展现无点击 → 主图或价格有问题                  │
│     ├── 有点击无转化 → Listing或Review不够               │
│     └── 前7天不要急着调，让数据跑出来                    │
│                                                      │
│  □ 3. 添加否定词（这个要每天做！）                       │
│     ├── 进搜索词报告（72h延迟，从Day 4开始看）           │
│     ├── 找到明显不相关的词 → 加否定精确                  │
│     │   例如："cat leash" "leash for small dogs"       │
│     │   （如果你产品是大狗用的）                        │
│     └── 不要否定太激进！有点击无转化不代表词不好           │
│         （前14天数据量不够，不要过早下结论）               │
│                                                      │
│  □ 4. 记录数据（Excel或飞书表格）                       │
│     日期 | 花费 | 点击 | 订单 | 销售额 | ACoS          │
│                                                      │
│  ❌ Day 1-14 不要做的事：                               │
│     × 不要频繁调竞价（至少3天调一次）                    │
│     × 不要看到ACoS高就慌（新品高是正常的）               │
│     × 不要关掉自动广告（它在帮你收集数据）               │
│     × 不要加太多关键词（先把少量词跑出数据）              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 四、阶段二：数据优化期（Day 15-30）

### 4.1 关键词收割（最重要的动作！）

```
Day 14 数据回顾 → 执行收割
══════════════════════════════════════════════════════

Step 1: 导出搜索词报告（过去14天）
─────────────────────────────────────
从自动广告和手动广泛中导出所有搜索词

Step 2: 用这张表分类每个搜索词
─────────────────────────────────────

┌──────────────────┬────────┬──────┬──────┬─────────────────────┐
│ 搜索词            │ 点击数  │ 订单 │ ACoS │ 动作                │
├──────────────────┼────────┼──────┼──────┼─────────────────────┤
│ 高转化词          │        │      │      │                     │
│ heavy duty dog   │ 45     │ 6    │ 18%  │ ✅ 收割到手动精确     │
│ leash            │        │      │      │   竞价$0.75          │
│                  │        │      │      │   自动中加精确否定    │
├──────────────────┼────────┼──────┼──────┼─────────────────────┤
│ 有潜力词          │        │      │      │                     │
│ strong dog leash │ 22     │ 2    │ 28%  │ ⚠️ 再观察1周         │
│ for pulling      │        │      │      │   ACoS偏高但有转化    │
│                  │        │      │      │   不急着收割          │
├──────────────────┼────────┼──────┼──────┼─────────────────────┤
│ 烧钱无效词        │        │      │      │                     │
│ retractable dog  │ 35     │ 0    │ ∞    │ 🔴 加否定精确！       │
│ leash            │        │      │      │  （你不是伸缩牵引绳）  │
├──────────────────┼────────┼──────┼──────┼─────────────────────┤
│ 不相关词          │        │      │      │                     │
│ cat harness      │ 12     │ 0    │ ∞    │ 🔴 加否定精确！       │
├──────────────────┼────────┼──────┼──────┼─────────────────────┤
│ 数据不足词        │        │      │      │                     │
│ training leash   │ 5      │ 0    │ -    │ ⏳ 数据太少，继续跑   │
│ for dogs         │        │      │      │                     │
└──────────────────┴────────┴──────┴──────┴─────────────────────┘

收割标准（保守版）：
  ✅ 收割条件：点击 ≥ 15 且 订单 ≥ 2 且 ACoS ≤ 30%
  🔴 否定条件：点击 ≥ 20 且 订单 = 0
  ⏳ 继续观察：其他情况再跑一周

Step 3: 执行收割操作
─────────────────────────────────────
把高转化词从自动/广泛 → 手动精确Campaign

┌─────────┐        ┌─────────┐        ┌─────────┐
│ 自动广告 │──收割──▶│ 手动广泛 │──收割──▶│ 手动精确 │
│ (探索)   │        │ (验证)   │        │ (收割)   │
└─────────┘        └─────────┘        └─────────┘
     │                  │
     │   同时在源头       │   同时在源头
     ▼   加否定精确       ▼   加否定精确
  避免重复投放          避免重复投放
```

### 4.2 竞价调整规则

```
┌──────────────────────────────────────────────────────┐
│          Day 15-30 竞价调整规则（保守版）               │
├──────────────────────────────────────────────────────┤
│                                                      │
│  规则1: 高转化低ACoS → 温和加价                        │
│  ┌────────────────────────────────────────────┐     │
│  │ 条件：ACoS < 20% 且 订单 ≥ 3（过去7天）      │     │
│  │ 动作：竞价 + 10%                             │     │
│  │ 上限：不超过 $1.20                           │     │
│  │ 举例：$0.65 → $0.72                         │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  规则2: ACoS偏高但有转化 → 小幅降价                    │
│  ┌────────────────────────────────────────────┐     │
│  │ 条件：25% < ACoS < 36% 且 订单 ≥ 2           │     │
│  │ 动作：竞价 - 10%                             │     │
│  │ 举例：$0.80 → $0.72                         │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  规则3: ACoS>盈亏线 → 大幅降价或暂停                   │
│  ┌────────────────────────────────────────────┐     │
│  │ 条件：ACoS > 36%（盈亏平衡线）                │     │
│  │ 动作A（有转化）：竞价 - 20%                   │     │
│  │ 动作B（无转化，点击>25）：暂停该关键词          │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  规则4: 有曝光无点击 → 检查Listing再决定               │
│  ┌────────────────────────────────────────────┐     │
│  │ 条件：展现 > 1000 且 CTR < 0.3%              │     │
│  │ 动作：先优化主图和价格，不要盲目加竞价           │     │
│  │ 原因：不是竞价问题，是Listing吸引力问题         │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ⚠️ 保守原则：                                       │
│  • 每次调整幅度不超过15-20%                           │
│  • 调完等3-5天再看效果，不要天天调                     │
│  • 每周集中调1-2次就够了                              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### 4.3 Day 15-30 广告架构升级

```
Day 15-30 广告活动调整后的样子：
══════════════════════════════════════════════════════

Campaign 1: [AUTO] 自动广告
├── 日预算：维持$5 或降到$3（如果已收割很多词）
├── 角色转变：从主力 → 探索器（持续发现新词）
├── 新增否定词：把已收割的词都加否定精确
└── 竞价：可降$0.05（因为好词已经被精确Campaign承接）

Campaign 2: [SP-Broad] 手动广泛
├── 日预算：维持$5
├── 角色：继续拓展长尾词
├── 新增：加入自动广告中发现的好词（广泛匹配）
├── 新增否定：已收割到精确的词加否定精确
└── 可加入新的中长尾词测试

Campaign 3: [SP-Exact] 手动精确 ← 主力Campaign！
├── 日预算：提升到 $5-8/天
├── 角色：核心出单主力
├── 关键词：从原来的3个 → 扩展到8-12个
│   ├── 原有词（数据验证OK的）
│   └── 新收割的高转化词
├── 竞价：按词表现分层
│   ├── A级词（ACoS<20%）：$0.75-0.90
│   ├── B级词（ACoS 20-30%）：$0.55-0.70
│   └── C级词（ACoS 30-36%）：$0.45-0.55
└── 这个Campaign要最关注！

Campaign 4: [SP-ASIN] 竞品定向
├── 日预算：维持$2-3
├── 调整：淘汰无转化的ASIN，换新的测试
└── 如果整体ASIN定向效果差（ACoS>40%），缩减预算

【新增】Campaign 5: [SP-Exact-Defense] 品牌词精确（如果有品牌）
├── 日预算：$1-2
├── 关键词：品牌名精确匹配
├── 竞价：$0.25-0.35（品牌词CPC很低）
└── 目的：防止竞品抢你的品牌流量

═══════════════════════════════════════════════════
Day 15-30 预算汇总：
  自动广告:     $3-5/天
  手动广泛:     $5/天
  手动精确:     $5-8/天  ← 加预算！
  ASIN定向:     $2-3/天
  品牌防守:     $1-2/天
  ─────────────────
  合计:         $16-23/天 ≈ $500-700/月
═══════════════════════════════════════════════════
```

---

## 五、阶段三：放量冲刺期（Day 31-60）

```
┌──────────────────────────────────────────────────────┐
│            Day 31-60 冲刺期目标和策略                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  前提条件（如果没达到，继续在阶段二打磨）：               │
│  ✅ 手动精确Campaign ACoS ≤ 25%                      │
│  ✅ 核心关键词CVR ≥ 10%                               │
│  ✅ Review ≥ 15个，评分 ≥ 4.2                         │
│  ✅ 日均出单 ≥ 3单                                    │
│                                                      │
│  如果没达到上述指标 → 别着急放量！                       │
│  先回去优化Listing/主图/价格/Review                     │
│                                                      │
└──────────────────────────────────────────────────────┘

Day 31-60 升级动作：
══════════════════════════════════════════════════════

① 精确Campaign加预算
   $5-8/天 → $10-15/天
   只给ACoS<25%的验证词加预算
   不是盲目加，是"好词多给钱"

② 开词组匹配Campaign
   ┌─────────────────────────────────────────────┐
   │ 【新增】Campaign 6: [SP-Phrase] 手动词组      │
   │ 日预算：$5/天                                 │
   │ 关键词：从精确Campaign中验证的高转化词          │
   │        用词组匹配去拓展其变体                   │
   │ 例如：精确词 "heavy duty dog leash" 效果好     │
   │      → 词组匹配可以命中                        │
   │      "heavy duty dog leash for large breeds"  │
   │      "best heavy duty dog leash"              │
   └─────────────────────────────────────────────┘

③ 冲核心大词排名
   核心词（如 dog leash）如果在2-3页，可以短期：
   ├── 提高精确竞价到建议竞价的120%
   ├── 开 "提高和降低"竞价策略（仅对这个Campaign）
   ├── 目标：打到首页底部
   ├── 时间窗口：给2周，如果上不去就回撤
   └── 保守策略！不要无限制加价冲排名

④ 测试SB品牌推广（如果有品牌备案）
   ┌─────────────────────────────────────────────┐
   │ 【新增】Campaign 7: [SB] 品牌推广              │
   │ 日预算：$3-5/天                               │
   │ 类型：商品集合广告                              │
   │ 关键词：3-5个核心词（精确匹配）                  │
   │ 竞价：比SP精确低20%（SB流量便宜些）             │
   │ 着陆页：品牌旗舰店 或 产品列表页                 │
   └─────────────────────────────────────────────┘

⑤ 持续否定词管理
   每周导出一次搜索词报告
   继续否定无效词
   这个动作永远不能停！

═══════════════════════════════════════════════════
Day 31-60 预算汇总：
  自动广告:     $3/天（降为纯探索）
  手动广泛:     $5/天
  手动词组:     $5/天（新增）
  手动精确:     $10-15/天（主力，加预算）
  ASIN定向:     $3/天
  品牌防守:     $2/天
  SB品牌推广:   $3-5/天（新增）
  ─────────────────
  合计:         $31-38/天 ≈ $950-1150/月

  目标：日均出单5-8单 → TACoS降到20%以下
═══════════════════════════════════════════════════
```

---

## 六、阶段四：稳定收割期（Day 61-90）

```
┌──────────────────────────────────────────────────────┐
│            Day 61-90 核心目标：降本增效                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  此时你应该达到的状态：                                 │
│  • 日均出单 5-10单                                    │
│  • 核心词自然排名进入前2页                              │
│  • 广告单占比 < 60%（自然单开始增长）                    │
│  • Review 30+                                        │
│                                                      │
│  这个阶段的核心动作：                                   │
│                                                      │
│  ① 砍掉低效Campaign/关键词                             │
│  ┌────────────────────────────────────────────┐     │
│  │ 过去30天数据复盘：                           │     │
│  │ • 花费占比前80%的词 → 逐个审查                │     │
│  │ • ACoS>30%且趋势没好转的 → 降竞价或暂停       │     │
│  │ • 自动广告如果贡献<10%订单 → 降到$2/天         │     │
│  │ • ASIN定向如果整体ACoS>35% → 缩减到$1/天      │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ② 精确Campaign精细化分组                              │
│  ┌────────────────────────────────────────────┐     │
│  │ 把精确Campaign按ACoS分成2个：                 │     │
│  │                                              │     │
│  │ Campaign A - 高效词（ACoS<18%）               │     │
│  │ → 给充足预算，竞价可以激进一些                  │     │
│  │ → 目标：抢更多这些词的流量                     │     │
│  │                                              │     │
│  │ Campaign B - 一般词（ACoS 18-30%）            │     │
│  │ → 控制预算，竞价保守                          │     │
│  │ → 持续优化或等Listing提升后再观察              │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ③ 开始关注TACoS而非ACoS                              │
│  ┌────────────────────────────────────────────┐     │
│  │                                              │     │
│  │  TACoS = 广告花费 / 总销售额（含自然单）       │     │
│  │                                              │     │
│  │  ACoS可能还是25%，但如果自然单占40%，           │     │
│  │  那TACoS = 25% × 60% = 15% ← 这才是真实成本  │     │
│  │                                              │     │
│  │  目标：TACoS持续下降，说明自然流量在增长         │     │
│  │                                              │     │
│  │  TACoS趋势判断：                              │     │
│  │  📈 TACoS上升 → 广告依赖加重，需要优化         │     │
│  │  📉 TACoS下降 → 自然流量增长，良性发展          │     │
│  │  ─── TACoS不变 → 稳定状态，可以接受             │     │
│  │                                              │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ④ 竞价策略切换                                       │
│  ┌────────────────────────────────────────────┐     │
│  │ 精确Campaign：从"固定竞价"→"仅降低"           │     │
│  │ 原因：产品已有数据，让亚马逊根据转化             │     │
│  │       概率自动降低低转化场景的竞价               │     │
│  │                                              │     │
│  │ 但自动广告和广泛保持"固定竞价"                  │     │
│  │ 因为它们还在探索，不要让算法限制探索             │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
└──────────────────────────────────────────────────────┘

Day 61-90 预算调整：
═══════════════════════════════════════════════════
  自动广告:       $2/天（纯探索）
  手动广泛:       $3/天（缩减）
  手动词组:       $3/天（缩减）
  精确A-高效词:   $10-12/天（主力！）
  精确B-一般词:   $3-5/天（控制）
  ASIN定向:       $1-2/天（缩减）
  品牌防守:       $1/天
  SB品牌推广:     $3/天
  ─────────────────
  合计:           $26-31/天 ≈ $800-950/月

  预算下降但出单增长（因为效率提升了）
  目标：日均8-12单，TACoS 12-18%
═══════════════════════════════════════════════════
```

---

## 七、阶段五：长期维护期（Day 90+）

```
┌──────────────────────────────────────────────────────┐
│         Day 90+ 进入自动驾驶模式                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  理想状态指标：                                        │
│  ┌────────────────────────────────────────────┐     │
│  │ 日均出单：10-15单                            │     │
│  │ BSR：品类排名 Top 5000-10000                 │     │
│  │ 核心词排名：首页（Top 20）                    │     │
│  │ ACoS：18-22%                                │     │
│  │ TACoS：10-15%                               │     │
│  │ 广告单占比：30-50%                           │     │
│  │ 自然单占比：50-70%                           │     │
│  │ Review：50+, 评分4.3+                       │     │
│  │ 净利润率：18-22%                             │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  每周只需做：                                         │
│  ┌────────────────────────────────────────────┐     │
│  │ □ 周一：检查搜索词报告，加否定词（15分钟）     │     │
│  │ □ 周三：检查ACoS异常，微调竞价（10分钟）       │     │
│  │ □ 周五：看周报，确认TACoS趋势（10分钟）       │     │
│  │                                              │     │
│  │ 每月做一次：                                  │     │
│  │ □ 大扫除：暂停所有30天无转化的词               │     │
│  │ □ 新词测试：加2-3个新词到广泛测试              │     │
│  │ □ 竞品检查：看竞品是否有新变化                 │     │
│  │ □ 利润复盘：确认还在赚钱                      │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
│  ⚠️ 触发重新优化的信号：                               │
│  ┌────────────────────────────────────────────┐     │
│  │ 🔴 TACoS连续2周上升 → 检查是否自然排名下降     │     │
│  │ 🔴 ACoS突然飙升 → 检查竞品是否降价/新品涌入    │     │
│  │ 🔴 销量骤降 → 检查Buy Box/库存/Listing变化     │     │
│  │ 🔴 CPC明显上涨 → 竞争加剧，考虑调整策略        │     │
│  └────────────────────────────────────────────┘     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 八、精铺模式的多SKU广告管理

```
精铺模式下你有多个SKU，广告怎么分配？
══════════════════════════════════════════════════════

原则：不是每个SKU都值得花同样多的广告费

┌──────────────────────────────────────────────────────┐
│                                                      │
│  SKU分级管理：                                        │
│                                                      │
│  ⭐ A级SKU（潜力款，2-3个）                            │
│  ├── 特征：市场大、利润OK、有差异化                     │
│  ├── 广告预算：占总预算60%                             │
│  ├── 策略：完整5阶段推广流程                           │
│  └── 目标：做到品类Top 50-100                         │
│                                                      │
│  📦 B级SKU（常规款，3-5个）                            │
│  ├── 特征：稳定出单、利润适中                          │
│  ├── 广告预算：占总预算30%                             │
│  ├── 策略：只开自动+精确2个Campaign                    │
│  └── 目标：保持稳定出单和利润                          │
│                                                      │
│  📉 C级SKU（测试款/尾货）                              │
│  ├── 特征：销量低、不确定性高                          │
│  ├── 广告预算：占总预算10%或不开广告                    │
│  ├── 策略：只开$3/天自动广告探路                       │
│  └── 目标：测试3个月，达不到B级就清货                   │
│                                                      │
│  示例（月广告预算$1500的分配）：                        │
│  ┌──────────┬────────┬──────────────┬───────────┐    │
│  │ SKU      │ 等级   │ 月预算        │ Campaign数│    │
│  ├──────────┼────────┼──────────────┼───────────┤    │
│  │ 狗牵引绳  │ A级    │ $450 (30%)   │ 5-7个     │    │
│  │ 狗碗      │ A级    │ $450 (30%)   │ 5-7个     │    │
│  │ 狗玩具    │ B级    │ $225 (15%)   │ 2-3个     │    │
│  │ 猫抓板    │ B级    │ $225 (15%)   │ 2-3个     │    │
│  │ 宠物毛巾  │ C级    │ $100 (7%)    │ 1个       │    │
│  │ 宠物指甲剪│ C级    │ $50 (3%)     │ 1个       │    │
│  ├──────────┼────────┼──────────────┼───────────┤    │
│  │ 合计      │        │ $1500        │ 16-23个   │    │
│  └──────────┴────────┴──────────────┴───────────┘    │
│                                                      │
│  动态调整规则：                                        │
│  • B级SKU连续4周ACoS<20% → 升级为A级，加预算           │
│  • A级SKU连续4周ACoS>35% → 降级为B级，砍预算           │
│  • C级SKU3个月无起色 → 关停广告，清货                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 九、广告命名规范（精铺必须做！）

```
多SKU管理，命名不规范 = 混乱噩梦

推荐命名格式：
[广告类型]-[匹配方式]-[产品简称]-[用途标记]-[日期]

示例：
═══════════════════════════════════════════════════

SP-AUTO-DogLeash-Discovery-20240115
SP-BROAD-DogLeash-KWExpand-20240115
SP-PHRASE-DogLeash-MidFunnel-20240201
SP-EXACT-DogLeash-TopKW-20240115
SP-EXACT-DogLeash-HighPerf-20240215     (高效词独立出来)
SP-ASIN-DogLeash-CompTarget-20240115
SP-EXACT-DogLeash-BrandDefense-20240201
SB-DogLeash-BrandAd-20240301

SP-AUTO-DogBowl-Discovery-20240120
SP-EXACT-DogBowl-TopKW-20240120
...

Portfolio分组（按产品线）：
├── Portfolio: Dog Leash 系列
│   ├── SP-AUTO-DogLeash-...
│   ├── SP-BROAD-DogLeash-...
│   ├── SP-EXACT-DogLeash-...
│   └── ...
├── Portfolio: Dog Bowl 系列
│   ├── SP-AUTO-DogBowl-...
│   └── ...
└── Portfolio: Cat Products 系列
    └── ...

好处：
✅ 一眼看出是什么产品、什么匹配方式
✅ 按Portfolio看每个产品线的广告总花费和ROAS
✅ 多人协作不会搞混
```

---

## 十、$20 客单价的特殊注意事项

```
┌──────────────────────────────────────────────────────┐
│        低客单价保守广告的「红线」和「底线」              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  🔴 红线（触碰就必须行动）：                            │
│                                                      │
│  1. 单个关键词花费 > $10 无转化 → 立即暂停              │
│     （$20售价，$10就是半个产品价了）                     │
│                                                      │
│  2. 单日广告花费 > 当日销售额 → ACoS>100%              │
│     当天就要检查原因                                   │
│                                                      │
│  3. 连续7天TACoS > 30% → 必须全面复盘                  │
│     可能是Listing或产品竞争力的问题                     │
│                                                      │
│  4. CPC持续上涨超过$1.20 → 考虑是否要继续               │
│     这个品类竞价如果 > $1.2，$20客单价很难赚钱           │
│                                                      │
│  ─────────────────────────────────────────────       │
│                                                      │
│  💡 低客单价广告的关键心法：                             │
│                                                      │
│  1.「宁可少花也不能乱花」                               │
│     $20客单价，每一次无效点击都心疼                      │
│     否定词管理比加关键词更重要                           │
│                                                      │
│  2.「转化率是王道」                                     │
│     CPC你控制不了太多（市场决定）                       │
│     但CVR你可以通过优化Listing来提升                    │
│     CVR从8%提到12% = ACoS自动降33%                    │
│                                                      │
│  3.「自然单占比才是终极目标」                            │
│     广告是手段不是目的                                  │
│     如果一个产品永远离不开广告 → 可能这个品选错了          │
│                                                      │
│  4.「精铺不是铺货，不值得推的果断放弃」                   │
│     一个SKU推3个月，TACoS > 25%下不来                   │
│     自然排名上不去 → 考虑清货退出                       │
│     把预算给更有潜力的SKU                               │
│                                                      │
│  5.「别和大卖硬碰硬」                                   │
│     大词CPC太贵 → 打长尾词                              │
│     大牌垄断的词 → 避开，找差异化的词                    │
│     例如不打 "dog leash" → 打 "heavy duty              │
│     nylon dog leash reflective"                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 十一、完整执行CheckList

```
把整个方案浓缩为一张可打印的执行表：

╔══════════════════════════════════════════════════════╗
║            新品广告投放 完整Checklist                  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  上架前（Day -7 to 0）                                ║
║  □ Listing文案优化完成（标题/五点/描述/ST）              ║
║  □ 7张图片到位（主图+6副图）                           ║
║  □ A+页面上传（如有品牌备案）                           ║
║  □ 定价确定：$19.99                                   ║
║  □ 关键词库整理好（3个梯队）                            ║
║  □ 竞品ASIN清单（5-10个）                              ║
║  □ 否定词预备清单                                      ║
║  □ 利润计算表做好，确认盈亏ACoS=36%                     ║
║  □ 至少开通Vine或有计划获取首批Review                    ║
║                                                      ║
║  ─────────────────────────────────────────────       ║
║                                                      ║
║  阶段一 Day 1-14（数据收集）                           ║
║  □ Day 1: 开4个Campaign（自动+广泛+精确+ASIN）         ║
║  □ Day 1: 总预算$15/天                                ║
║  □ Day 1-3: 只观察，不调整                             ║
║  □ Day 4: 开始看搜索词报告，加否定词                    ║
║  □ Day 7: 第一次数据复盘，微调竞价                      ║
║  □ Day 7-14: 每天加否定词，每3天调一次竞价               ║
║  □ Day 14: 记录所有数据到Excel                         ║
║                                                      ║
║  ─────────────────────────────────────────────       ║
║                                                      ║
║  阶段二 Day 15-30（数据优化）                          ║
║  □ Day 14: 执行第一次关键词收割                         ║
║  □ Day 15: 精确Campaign加入收割的词                     ║
║  □ Day 15: 源头Campaign加否定                          ║
║  □ Day 15: 精确Campaign预算提到$5-8/天                  ║
║  □ Day 21: 第二次关键词收割                             ║
║  □ Day 21: 按规则调整竞价                              ║
║  □ Day 28: 第三次收割 + 竞价调整                        ║
║  □ Day 30: 全面数据复盘，算清楚每个词的真实ROI           ║
║                                                      ║
║  ─────────────────────────────────────────────       ║
║                                                      ║
║  阶段三 Day 31-60（放量冲刺）前提：ACoS≤25%            ║
║  □ Day 31: 精确Campaign加预算到$10-15/天               ║
║  □ Day 31: 新增词组匹配Campaign                        ║
║  □ Day 35: 测试SB品牌推广                              ║
║  □ Day 35-60: 每周收割+否定+竞价调整                    ║
║  □ Day 45: 中期复盘，是否需要调整节奏                   ║
║  □ Day 60: 全面复盘                                   ║
║                                                      ║
║  ─────────────────────────────────────────────       ║
║                                                      ║
║  阶段四 Day 61-90（稳定收割）                          ║
║  □ 砍低效Campaign/关键词                               ║
║  □ 精确Campaign分为高效组/普通组                        ║
║  □ 切换竞价策略为"仅降低"（精确Campaign）               ║
║  □ 开始重点关注TACoS                                   ║
║  □ 目标TACoS < 15%                                    ║
║                                                      ║
║  ─────────────────────────────────────────────       ║
║                                                      ║
║  阶段五 Day 90+（长期维护）                            ║
║  □ 每周：否定词 + 竞价微调（30分钟）                    ║
║  □ 每月：大扫除 + 新词测试 + 利润复盘                   ║
║  □ 持续：监控TACoS趋势和竞品动态                       ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

---

## 十二、数据追踪模板

```
建一个这样的Excel/飞书表格，每周更新：

Sheet 1: 每日数据
┌──────┬──────┬──────┬─────┬──────┬──────┬──────┬──────┬───────┐
│ 日期  │总销售│总订单│广告费│广告单│自然单│ACoS  │TACoS │自然占比│
├──────┼──────┼──────┼─────┼──────┼──────┼──────┼──────┼───────┤
│ 1/15 │$80   │4     │$15  │2     │2     │37%   │19%   │50%    │
│ 1/16 │$100  │5     │$14  │3     │2     │23%   │14%   │40%    │
│ ...  │      │      │     │      │      │      │      │       │
└──────┴──────┴──────┴─────┴──────┴──────┴──────┴──────┴───────┘

Sheet 2: 每周关键词表现
┌──────────────┬─────┬──────┬────┬─────┬─────┬──────┬──────┐
│ 关键词        │匹配  │花费   │点击│转化  │ACoS │CPC   │动作   │
├──────────────┼─────┼──────┼────┼─────┼─────┼──────┼──────┤
│ dog leash    │精确  │$25   │32  │4    │31%  │$0.78 │降竞价 │
│ heavy duty   │精确  │$18   │28  │5    │18%  │$0.64 │加竞价 │
│ dog leash    │     │      │    │     │     │      │      │
│ nylon leash  │广泛  │$12   │20  │0    │∞    │$0.60 │否定   │
│ for cats     │     │      │    │     │     │      │      │
└──────────────┴─────┴──────┴────┴─────┴─────┴──────┴──────┘

Sheet 3: Campaign级别周报
┌──────────────┬──────┬──────┬─────┬─────┬──────┐
│ Campaign     │花费   │销售   │ACoS │订单  │趋势   │
├──────────────┼──────┼──────┼─────┼─────┼──────┤
│ AUTO         │$35   │$80   │44%  │4    │↓优化中│
│ BROAD        │$42   │$120  │35%  │6    │→稳定  │
│ EXACT        │$56   │$280  │20%  │14   │↑增长  │
│ ASIN         │$15   │$40   │38%  │2    │↓考虑砍│
├──────────────┼──────┼──────┼─────┼─────┼──────┤
│ 合计          │$148  │$520  │28%  │26   │      │
│ TACoS        │      │$780* │19%  │39*  │↓良性  │
│ (*含自然单)   │      │      │     │     │      │
└──────────────┴──────┴──────┴─────┴─────┴──────┘
```

---

## 十三、常见问题决策树

```
遇到问题时，按这个决策树处理：

问题1: ACoS一直很高（>35%）
─────────────────────────────────
                ACoS > 35%
                    │
        ┌───────────┴───────────┐
        有转化                  无转化
        │                       │
   CVR是多少？             点击>30了吗？
        │                       │
   ┌────┴────┐            ┌────┴────┐
  CVR<8%   CVR≥8%         是        否
   │         │            │         │
 Listing   CPC太高        否定      继续跑
 有问题     │           这个词      等数据
 先优化    降竞价
 Listing   或换长尾词


问题2: 花不出去（预算用不完）
─────────────────────────────────
             花不出去
                │
        ┌───────┴───────┐
     有展现无点击      无展现
        │                │
     主图/价格         竞价太低
     不够吸引人          │
        │             加竞价
     优化主图         $0.10/次
     检查价格
     竞争力


问题3: 有点击无转化
─────────────────────────────────
            点击多但不转化
                │
        ┌───────┼───────┐
     流量不精准  │     Listing问题
     （搜索词   │     （Review太少/
      不对）    │      图片差/
        │       │      价格高）
     加否定词   │         │
              Review   优化Listing
              太少      再观察
              (< 10)
                │
            先暂停广告
            等Review
            到15个再开


问题4: 销量突然下跌
─────────────────────────────────
              销量突然下跌
                   │
    ┌──────┬───────┼───────┬──────┐
  Buy Box  库存   Listing  竞品   季节性
  被抢     断了   被改了   降价    因素
    │       │      │       │      │
  检查是   紧急   查变动   查竞   等待
  否被跟   补货   记录     品价   (宠物品
  卖             恢复     格     不太有)
```

---

## 最后总结：$20宠物标品精铺广告的核心数字

```
┌──────────────────────────────────────────────────────┐
│                  核心数字记住这些就够了                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  💰 盈亏平衡ACoS = 36%（超过就亏，绝对红线）           │
│  🎯 目标ACoS = 20-25%（保守稳健）                     │
│  📊 目标TACoS = 10-15%（长期目标）                    │
│  🖱️ CPC预算 = $0.50-0.90（宠物类目，保守竞价）        │
│  📈 目标CVR ≥ 10%（低于8%先优化Listing）               │
│  💵 新品首月广告预算 ≈ $450（$15/天）                  │
│  💵 推广期3个月总预算 ≈ $2000-2500                     │
│  ⏰ 每天花15分钟管广告就够了                            │
│  📅 关键词收割每2周做一次                               │
│  🎯 90天后TACoS应稳定在12-18%                         │
│  ✂️ 自然单占比目标 > 50%（说明推广成功）                │
│                                                      │
│  一句话总结：                                         │
│  「先用自动广告探路 → 收割好词到精确 → 精确出单为主      │
│    → 自然单逐步增长 → TACoS持续下降 → 赚钱」           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

这套方案每一步都可以直接执行，需要我针对某个具体产品（比如你实际在卖的宠物产品）做一份更具体的广告计划吗？

亚马逊广告计划（就是针对新品精铺广告投放策略），针对新品精铺广告投放策略（新品-精铺-正常价格-保守广告版），推新的完整方案流程落地,背景介绍：属于标品，没有季节性（季节性的没有）大部分产品的类目是宠物，客单价在20美金左右（宠物类目，还有一些杂货，20 美金左右客单）精铺的模式

# 宠物类目 $20 客单价新品精铺 — 周级广告落地计划

> **基于你的推广计划模板，针对 $20 宠物标品 重新适配**
> 以"宠物狗牵引绳"（Dog Leash）为产品示例

---

## 一、你的计划模板 vs $20 产品适配对比

```
┌──────────────────────────────────────────────────────────┐
│          你的原始计划（$109产品）vs $20产品 关键差异       │
├──────────────┬──────────────────┬─────────────────────────┤
│  指标         │ 你的计划($109)   │ $20宠物标品适配          │
├──────────────┼──────────────────┼─────────────────────────┤
│ 售价          │ $109→$119        │ $19.99→$21.99           │
│ Coupon        │ $20→$10→$0      │ $2→$1→$0               │
│ 目标日销       │ 6→17单/天       │ 3→12单/天               │
│ CPC           │ ~$1.00          │ $0.50-0.80              │
│ CVR           │ 未标注            │ 目标 10-15%             │
│ 广告日预算     │ $48→$13         │ $10→$25                 │
│ 盈亏ACoS      │ ~35%            │ ~36%                    │
│ 目标ACoS      │ 未明确           │ 20-25%                  │
│ 推广周期       │ 25周+           │ 12-16周                 │
│ Review起点     │ 136个, 4星      │ 0个, 需要积累            │
│ 排名目标       │ #60→#20→首页    │ #100→#30→首页           │
│ Campaign数     │ 6个             │ 4个→6个（渐进）          │
│ 广告类型占比    │ SP70/SD15/SB15  │ SP80/SD10/SB10          │
│               │ →SP60/SD20/SB20 │ →SP65/SD15/SB20         │
└──────────────┴──────────────────┴─────────────────────────┘

关键区别说明：
━━━━━━━━━━━━━
① $20产品利润薄，广告容错空间极小
   $109产品每单可承受$38广告费
   $20产品每单只能承受$7.2广告费
   → 必须更保守，更精准

② $20产品CPC更低，但利润也低
   CPC $0.65 + CVR 10% = 每单广告成本$6.50 → ACoS=32.5%
   CPC $0.65 + CVR 12% = 每单广告成本$5.42 → ACoS=27.1%
   CPC $0.65 + CVR 15% = 每单广告成本$4.33 → ACoS=21.7% ✅
   → CVR是生死线，Listing质量决定一切

③ $20宠物标品竞争激烈但CPC相对温和
   不像$109产品有价格壁垒
   → 靠长尾词+精准投放取胜
```

---

## 二、利润测算表（$20产品版）

```
┌──────────────────────────────────────────────────────────────┐
│                    价格利润测算 — $20宠物产品                   │
├────────────────┬───────────┬───────────┬───────────┬─────────┤
│ 细分项          │ Phase 1   │ Phase 2   │ Phase 3   │ 达标稳态│
│                │ Coupon期   │ 提价期     │ 去Coupon   │         │
├────────────────┼───────────┼───────────┼───────────┼─────────┤
│ 售价            │ $19.99    │ $20.99    │ $21.99    │ $21.99  │
│ Coupon          │ -$2.00    │ -$1.00    │ $0        │ $0      │
│ 实际成交价       │ $17.99    │ $19.99    │ $21.99    │ $21.99  │
├────────────────┼───────────┼───────────┼───────────┼─────────┤
│ 佣金(15%)       │ -$2.70    │ -$3.00    │ -$3.30    │ -$3.30  │
│ FBA配送费       │ -$3.50    │ -$3.50    │ -$3.50    │ -$3.50  │
│ FBA仓储费       │ -$0.30    │ -$0.30    │ -$0.30    │ -$0.30  │
│ 采购成本+包装    │ -$3.50    │ -$3.50    │ -$3.50    │ -$3.50  │
│ 头程运费(海运)   │ -$1.50    │ -$1.50    │ -$1.50    │ -$1.50  │
│ 退货预留(5%)    │ -$0.90    │ -$1.00    │ -$1.10    │ -$1.10  │
├────────────────┼───────────┼───────────┼───────────┼─────────┤
│ ★ 广告前毛利    │ $5.59     │ $7.19     │ $8.79     │ $8.79   │
│ ★ 广告前毛利率  │ 31.1%     │ 36.0%     │ 40.0%     │ 40.0%   │
├────────────────┼───────────┼───────────┼───────────┼─────────┤
│ 盈亏平衡ACoS    │ 31.1%     │ 36.0%     │ 40.0%     │ 40.0%   │
│ 目标ACoS        │ 25-30%    │ 20-25%    │ 18-22%    │ 15-20%  │
│ 目标TACoS       │ 25-30%    │ 15-20%    │ 12-15%    │ 8-12%   │
├────────────────┼───────────┼───────────┼───────────┼─────────┤
│ 广告费/单(目标)  │ $4.50     │ $4.00     │ $3.96     │ $3.30   │
│ ★ 净利润/单     │ $1.09     │ $3.19     │ $4.83     │ $5.49   │
│ ★ 净利润率      │ 6.1%      │ 16.0%     │ 22.0%     │ 25.0%   │
└────────────────┴───────────┴───────────┴───────────┴─────────┘

CPC与CVR对应的ACoS速查表（$20售价）：
┌────────┬────────┬────────┬────────┬────────┬────────┐
│ CPC\CVR│  8%    │ 10%    │ 12%    │ 15%    │ 20%    │
├────────┼────────┼────────┼────────┼────────┼────────┤
│ $0.40  │ 25.0%  │ 20.0%  │ 16.7%  │ 13.3%  │ 10.0%  │
│ $0.50  │ 31.3%  │ 25.0%✅│ 20.8%  │ 16.7%  │ 12.5%  │
│ $0.60  │ 37.5%🔴│ 30.0%  │ 25.0%✅│ 20.0%  │ 15.0%  │
│ $0.70  │ 43.8%🔴│ 35.0%  │ 29.2%  │ 23.3%✅│ 17.5%  │
│ $0.80  │ 50.0%🔴│ 40.0%🔴│ 33.3%  │ 26.7%  │ 20.0%✅│
│ $0.90  │ 56.3%🔴│ 45.0%🔴│ 37.5%🔴│ 30.0%  │ 22.5%  │
│ $1.00  │ 62.5%🔴│ 50.0%🔴│ 41.7%🔴│ 33.3%  │ 25.0%  │
└────────┴────────┴────────┴────────┴────────┴────────┘
  🔴=亏损  ✅=目标区间

  → CPC必须控制在$0.70以下！CVR必须>10%！
```

---

## 三、关键词库准备

```
┌──────────────────────────────────────────────────────────────┐
│         关键词库 — 宠物狗牵引绳（示例产品）                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  关键词              翻译           流量占比  预估周曝光  类型  │
│  ─────────────────────────────────────────────────────────  │
│  dog leash           狗牵引绳        28%     52,000   主词  │
│  dog leashes         狗牵引绳(复数)   15%     28,000   主词  │
│  leash for dogs      狗用牵引绳       8%      14,800   主词  │
│  heavy duty dog      重型狗牵引绳     6%      11,200   精准  │
│   leash                                              长尾  │
│  dog leash large     大狗牵引绳       5%       9,300   精准  │
│   breed                                              长尾  │
│  nylon dog leash     尼龙狗牵引绳     4%       7,400   精准  │
│                                                      长尾  │
│  reflective dog      反光狗牵引绳     3%       5,600   精准  │
│   leash                                              长尾  │
│  dog walking leash   遛狗牵引绳       3%       5,600   场景  │
│  6ft dog leash       6英尺狗牵引绳    2%       3,700   属性  │
│  padded handle dog   加厚手柄狗绳     2%       3,700   属性  │
│   leash                                              长尾  │
│  training leash      训练牵引绳       2%       3,700   场景  │
│   for dogs                                                  │
│  no pull dog leash   防拉扯牵引绳     1.5%     2,800   功能  │
│  strong dog leash    加固狗牵引绳     1%       1,900   属性  │
│                                                              │
│  ─────────────────────────────────────────────────────────  │
│  核心主推词（2-3个）：                                         │
│  ① dog leash                                                │
│  ② heavy duty dog leash                                     │
│  ③ dog leash large breed                                    │
│                                                              │
│  广泛测试词（5-8个）：                                         │
│  ① nylon dog leash                                          │
│  ② reflective dog leash                                     │
│  ③ dog walking leash                                        │
│  ④ 6ft dog leash                                            │
│  ⑤ padded handle dog leash                                  │
│  ⑥ training leash for dogs                                  │
│                                                              │
│  竞品ASIN（5-8个，选$15-25价位，评论<500的）：                  │
│  B0AAAAAA  $19.99  280 reviews  4.2★                        │
│  B0BBBBBB  $21.99  150 reviews  4.0★                        │
│  B0CCCCCC  $18.99  320 reviews  4.3★                        │
│  B0DDDDDD  $22.99   95 reviews  4.1★                        │
│  B0EEEEEE  $17.99  200 reviews  4.0★                        │
│                                                              │
│  预设否定词：                                                  │
│  cat leash / retractable leash / leash holder /              │
│  leash hook / harness / collar / free / cheap /              │
│  wholesale / used / leather（如果你是尼龙的）                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 四、广告结构定义（对标你的Campaign命名）

```
┌──────────────────────────────────────────────────────────────┐
│         广告Campaign结构 — 按阶段渐进开启                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ===== WEEK 1-2 开启（4个Campaign）=====                      │
│                                                              │
│ Campaign 1: SP-AUTO-DogLeash-Discovery                       │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 类型：SP 自动广告                                      │    │
│ │ 目的：数据收集，让亚马逊给你匹配流量                     │    │
│ │ 竞价策略：固定竞价                                     │    │
│ │ 日预算：$5                                            │    │
│ │ 竞价设置：                                            │    │
│ │   Close Match:    $0.45                               │    │
│ │   Loose Match:    $0.35                               │    │
│ │   Substitutes:    $0.40                               │    │
│ │   Complements:    $0.25                               │    │
│ │ 预设否定：cat leash / retractable / harness / collar  │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
│ Campaign 2: SP-BROAD-DogLeash-KWTest                         │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 类型：SP 手动广告 - 广泛匹配（= 你的测试组B）           │    │
│ │ 目的：拓展长尾词，验证关键词                            │    │
│ │ 竞价策略：固定竞价                                     │    │
│ │ 日预算：$3                                            │    │
│ │ 关键词：                                              │    │
│ │   nylon dog leash          $0.50 广泛                 │    │
│ │   reflective dog leash     $0.45 广泛                 │    │
│ │   dog walking leash        $0.45 广泛                 │    │
│ │   6ft dog leash            $0.40 广泛                 │    │
│ │   padded handle dog leash  $0.40 广泛                 │    │
│ │ 否定精确：dog leash / dog leashes（大词放精确组）       │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
│ Campaign 5: SP-EXACT-DogLeash-CoreKW                         │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 类型：SP 手动广告 - 精确匹配（= 你的核心关键词E）        │    │
│ │ 目的：精准打核心词，冲排名                              │    │
│ │ 竞价策略：固定竞价                                     │    │
│ │ 日预算：$3                                            │    │
│ │ 关键词：                                              │    │
│ │   dog leash                $0.60 精确                 │    │
│ │   heavy duty dog leash     $0.55 精确                 │    │
│ │   dog leash large breed    $0.50 精确                 │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
│ Campaign 4: SP-PT-DogLeash-CompASIN                          │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 类型：SP 手动广告 - 商品定向（= 你的PT）                │    │
│ │ 目的：抢竞品流量                                       │    │
│ │ 竞价策略：固定竞价                                     │    │
│ │ 日预算：$2                                            │    │
│ │ 定向ASIN：5个竞品                                     │    │
│ │   B0AAAAAA  $0.40                                    │    │
│ │   B0BBBBBB  $0.40                                    │    │
│ │   B0CCCCCC  $0.35                                    │    │
│ │   B0DDDDDD  $0.35                                    │    │
│ │   B0EEEEEE  $0.35                                    │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
│ WEEK 1-2 总日预算：$13/天                                    │
│ 广告类型占比：SP 100%（新品先不开SD/SB）                      │
│                                                              │
│ ===== WEEK 5 新增（1个Campaign）=====                        │
│                                                              │
│ Campaign 3: SD-CAT-DogLeash-Categories                       │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 类型：SD 展示广告 - 品类定向（= 你的SD-categories）     │    │
│ │ 目的：品类曝光，再营销                                  │    │
│ │ 日预算：$2                                            │    │
│ │ 定向：Pet Supplies > Dogs > Leashes                   │    │
│ │ 竞价：$0.30                                          │    │
│ │ 注意：$20产品SD效果可能一般，先小预算测试               │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
│ ===== WEEK 7 新增（1个Campaign）=====                        │
│                                                              │
│ Campaign 6: SBV-DogLeash-Video                               │
│ ┌──────────────────────────────────────────────────────┐    │
│ │ 类型：SB 品牌视频广告（= 你的SBV-KT）                  │    │
│ │ 前提：品牌备案 + 有产品视频                             │    │
│ │ 目的：视频广告CTR高，提升点击和转化                      │    │
│ │ 日预算：$2                                            │    │
│ │ 关键词：2-3个核心词精确匹配                             │    │
│ │   dog leash              $0.45 精确                   │    │
│ │   heavy duty dog leash   $0.40 精确                   │    │
│ │ 注意：SBV的CPC通常比SP低20-30%，性价比高               │    │
│ └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 五、完整 16 周推广计划（核心表）

```
参考你的模板格式，完全适配 $20 宠物产品
产品：宠物狗牵引绳   SKU: PET-DL-001   ASIN: B0XXXXXX
上架时间：2025.4.1   推广周期：4月1日 - 7月22日 (16周)
对标竞品：B0AAAAAA, B0BBBBBB
目标排名：dog leash → 首页(#1-48)
目标日销：8-12单/天（稳态）
```

### WEEK 1 — 冷启动·数据收集

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 1   4.1 - 4.7   冷启动期                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  基础信息                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 售价：$19.99    Coupon：$2.00     实际成交：$17.99     │  ║
║  │ Review：0个     Vine：已开通，等待                     │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  目标设定                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 目标日均单：2-3单    周目标：15-20单                    │  ║
║  │ 目标排名：主词进入前10页（#200-480）                    │  ║
║  │ 目标ACoS：不设硬性目标（数据收集期）                    │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 竞价    │ 匹配   │ 词数    │  ║
║  │ ─────────────── │ ────── │ ─────── │ ────── │ ─────  │  ║
║  │ C1-AUTO         │ $5.00  │ $0.45   │ 自动   │ -      │  ║
║  │ C2-BROAD        │ $3.00  │ $0.40-  │ 广泛   │ 5个    │  ║
║  │                 │        │  0.50   │        │        │  ║
║  │ C5-EXACT        │ $3.00  │ $0.50-  │ 精确   │ 3个    │  ║
║  │                 │        │  0.60   │        │        │  ║
║  │ C4-PT           │ $2.00  │ $0.35-  │ ASIN   │ 5个    │  ║
║  │                 │        │  0.40   │        │        │  ║
║  │ ─────────────── │ ────── │ ─────── │ ────── │ ─────  │  ║
║  │ 日预算合计       │ $13.00 │         │        │        │  ║
║  │ 广告类型占比      │ SP:100%│         │        │        │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 广告日预算  │ 每日点击 │ CPC    │ CVR   │ 广告日订单  │  ║
║  │ $13        │ 22      │ $0.59  │ 8%    │ 1.8       │  ║
║  │                                                       │  ║
║  │ 周花费    │ 周点击 │ 周广告单│ 周自然单│ 周总单│ 周销售额│  ║
║  │ $91      │ 154   │ 13     │ 5      │ 18   │ $324  │  ║
║  │                                                       │  ║
║  │ 广告ACoS │ TACoS  │ 广告占比  │ 自然占比                │  ║
║  │ 35%      │ 28%    │ 72%      │ 28%                    │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  本周行动 Action                                             ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ ✅ Day 1: 开启4个Campaign                              │  ║
║  │ ✅ Day 1: 确认Listing所有内容已优化                      │  ║
║  │ ✅ Day 1: Vine计划已开通                                │  ║
║  │ ✅ Day 1-3: 只观察，不调整竞价                           │  ║
║  │ ✅ Day 4: 开始看搜索词报告，加否定词                      │  ║
║  │ ✅ Day 5: 检查预算消耗情况                               │  ║
║  │    └ 花不完50% → 竞价+$0.05                            │  ║
║  │    └ 中午花完 → 竞价偏高，不急着加预算                    │  ║
║  │ ✅ Day 7: 记录本周数据到Excel                            │  ║
║  │ ❌ 不做：不频繁调竞价，不慌ACoS高                        │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  Review计划                                                  ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Vine送出：5个                                          │  ║
║  │ Request a Review：每个自然订单都发                       │  ║
║  │ 本周预计获评：0-1个（Vine有延迟）                        │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  库存计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ FBA库存：500    中仓：300    在途：0    消耗：18        │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 2 — 继续收集·开始否定

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 2   4.8 - 4.14   数据积累期                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$19.99    Coupon：$2.00    Review：1-2个, 4.5★        ║
║                                                              ║
║  目标：日均3单 | 周21单 | 排名进前5页(#100-240)               ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 竞价调整      │ 变化        │  ║
║  │ ─────────────── │ ────── │ ──────────── │ ─────────── │  ║
║  │ C1-AUTO         │ $5.00  │ 按表现微调    │ 加否定词3-5个│  ║
║  │ C2-BROAD        │ $3.00  │ 维持         │ 加否定词2-3个│  ║
║  │ C5-EXACT        │ $3.00  │ 维持         │ 不动        │  ║
║  │ C4-PT           │ $2.00  │ 维持         │ 不动        │  ║
║  │ ─────────────── │ ────── │              │             │  ║
║  │ 日预算合计       │ $13.00 │              │             │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 广告日预算│ 每日点击│ CPC    │ CVR    │ 广告日订单     │  ║
║  │ $13      │ 24     │ $0.54  │ 9%     │ 2.2           │  ║
║  │                                                       │  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $91    │ 168  │ 15     │ 6      │ 21   │ $378      │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 34%    │ 24%   │ 71%     │ 29%                      │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  关键动作                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ ✅ 导出WEEK1搜索词报告（72h延迟，Day 4才有完整数据）     │  ║
║  │ ✅ 识别不相关搜索词 → 加否定精确                         │  ║
║  │    └ 示例：cat leash, leash rack, leash wall hook      │  ║
║  │ ✅ 识别有潜力的搜索词 → 记录但不急着动                    │  ║
║  │ ✅ Day 14（周末）：完成2周数据汇总                       │  ║
║  │ ✅ 准备WEEK3的第一次关键词收割                           │  ║
║  │ ❌ 不做：不大幅调竞价（数据量不够）                       │  ║
║  │ ❌ 不做：不因为ACoS高就砍预算                            │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  Review：Vine陆续到评，目标本周末3-5个Review                  ║
║  库存：FBA 482 | 消耗21 | 安全                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 3 — 首次收割·竞价优化

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 3   4.15 - 4.21   ★ 首次关键词收割 ★                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$19.99    Coupon：$2.00    Review：5-8个, 4.3★        ║
║                                                              ║
║  目标：日均4单 | 周28单 | 排名进前3页(#50-150)                ║
║                                                              ║
║  ★ 本周核心动作：第一次关键词收割                              ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │                                                       │  ║
║  │  从自动广告/广泛 → 精确Campaign 的收割标准：             │  ║
║  │                                                       │  ║
║  │  搜索词分析表（过去14天汇总）：                          │  ║
║  │  ┌──────────────────┬────┬───┬─────┬────────────────┐│  ║
║  │  │ 搜索词            │点击│单 │ACoS │ 动作           ││  ║
║  │  ├──────────────────┼────┼───┼─────┼────────────────┤│  ║
║  │  │heavy duty dog    │ 28 │ 4 │ 20% │✅收割到C5精确   ││  ║
║  │  │leash             │    │   │     │  源头加否定精确 ││  ║
║  │  ├──────────────────┼────┼───┼─────┼────────────────┤│  ║
║  │  │nylon dog leash   │ 22 │ 3 │ 22% │✅收割到C5精确   ││  ║
║  │  │for large dogs    │    │   │     │  源头加否定精确 ││  ║
║  │  ├──────────────────┼────┼───┼─────┼────────────────┤│  ║
║  │  │reflective dog    │ 18 │ 2 │ 27% │⚠️再观察1周      ││  ║
║  │  │leash 6ft         │    │   │     │  有转化但偏高   ││  ║
║  │  ├──────────────────┼────┼───┼─────┼────────────────┤│  ║
║  │  │dog rope leash    │ 15 │ 1 │ 45% │⚠️再观察         ││  ║
║  │  │                  │    │   │     │  数据不足       ││  ║
║  │  ├──────────────────┼────┼───┼─────┼────────────────┤│  ║
║  │  │retractable dog   │ 25 │ 0 │ ∞   │🔴否定精确!      ││  ║
║  │  │leash             │    │   │     │  完全不相关     ││  ║
║  │  ├──────────────────┼────┼───┼─────┼────────────────┤│  ║
║  │  │small dog leash   │ 20 │ 0 │ ∞   │🔴否定精确!      ││  ║
║  │  │                  │    │   │     │ （产品是大狗用） ││  ║
║  │  └──────────────────┴────┴───┴─────┴────────────────┘│  ║
║  │                                                       │  ║
║  │  收割标准：                                            │  ║
║  │  ✅ 收割：clicks ≥15 且 orders ≥2 且 ACoS ≤30%        │  ║
║  │  🔴 否定：clicks ≥20 且 orders = 0                    │  ║
║  │  ⏳ 观察：其他情况                                     │  ║
║  │                                                       │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  广告计划调整                                                 ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 调整说明                    │  ║
║  │ ─────────────── │ ────── │ ────────────────────────── │  ║
║  │ C1-AUTO         │ $5→$4  │ 好词已收割，降$1            │  ║
║  │ C2-BROAD        │ $3    │ 维持，继续拓词               │  ║
║  │ C5-EXACT        │ $3→$5  │ 加入收割词，加预算！         │  ║
║  │ C4-PT           │ $2    │ 淘汰无效ASIN，换新的测试      │  ║
║  │ ─────────────── │ ────── │                            │  ║
║  │ 日预算合计       │ $14.00 │                            │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  竞价调整                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ C5-EXACT 精确Campaign词级别竞价：                       │  ║
║  │ dog leash               $0.60 → $0.60 维持            │  ║
║  │ heavy duty dog leash    $0.55 → $0.62 ↑ (ACoS<25%)   │  ║
║  │ dog leash large breed   $0.50 → $0.50 维持            │  ║
║  │ 【新收割】nylon dog leash for large dogs  $0.55 新增   │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 广告日预算│ 每日点击│ CPC    │ CVR    │ 广告日订单     │  ║
║  │ $14      │ 26     │ $0.54  │ 10%    │ 2.6           │  ║
║  │                                                       │  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $98    │ 182  │ 18     │ 10     │ 28   │ $504      │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 30%    │ 19%   │ 64%     │ 36%                      │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  库存：FBA 461 | 周消耗28 | 可售16周 ✅                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 4 — 第二次收割·初步放量

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 4   4.22 - 4.28   二次收割+放量测试                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$19.99    Coupon：$2.00    Review：8-12个, 4.3★       ║
║  目标：日均5单 | 周35单 | 排名进前2页(#30-96)                 ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 竞价    │ 变化              │  ║
║  │ ─────────────── │ ────── │ ─────── │ ──────────────── │  ║
║  │ C1-AUTO         │ $3.00  │ $0.40   │ 缩减，纯探索     │  ║
║  │ C2-BROAD        │ $3.00  │ $0.40-  │ 二次收割后加否定   │  ║
║  │                 │        │  0.50   │                  │  ║
║  │ C5-EXACT        │ $5→$7  │ $0.50-  │ ★主力！加预算    │  ║
║  │                 │        │  0.65   │  词从4→6个       │  ║
║  │ C4-PT           │ $2.00  │ $0.35   │ 保留有效ASIN     │  ║
║  │ ─────────────── │ ────── │ ─────── │                  │  ║
║  │ 日预算合计       │ $15.00 │         │                  │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 广告日预算│ 每日点击│ CPC    │ CVR    │ 广告日订单     │  ║
║  │ $15      │ 28     │ $0.54  │ 11%    │ 3.1           │  ║
║  │                                                       │  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $105   │ 196  │ 22     │ 13     │ 35   │ $630      │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 27%    │ 17%   │ 63%     │ 37%                      │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  关键动作                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ ✅ 执行第二次关键词收割                                  │  ║
║  │ ✅ C5精确Campaign加到6-8个关键词                         │  ║
║  │ ✅ 如果精确ACoS < 25%，开始考虑WEEK5加Campaign           │  ║
║  │ ✅ Coupon保持$2（还在积累Review阶段）                    │  ║
║  │ ✅ 7Day Deal评估（如果可以报名且划算）                    │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  ⚠️ 决策节点：4周复盘                                        ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 如果4周数据如下 → 继续推进：                             │  ║
║  │   精确Campaign ACoS ≤ 28%  ✅                          │  ║
║  │   CVR ≥ 10%  ✅                                        │  ║
║  │   日均≥3单  ✅                                          │  ║
║  │   Review ≥ 8个  ✅                                      │  ║
║  │                                                       │  ║
║  │ 如果4周数据如下 → 暂停放量，回头优化Listing：             │  ║
║  │   精确Campaign ACoS > 35%  🔴                          │  ║
║  │   CVR < 8%  🔴                                         │  ║
║  │   日均<2单  🔴                                          │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 5-6 — 加入SD·精确放量

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 5   4.29 - 5.5   新增SD + Coupon调整                  ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$19.99→$20.99  Coupon：$2→$1  Review：12-15个, 4.3★  ║
║  目标：日均5-6单 | 周38单 | 主词排名#30-50                    ║
║  行动：提价$1 + 降Coupon$1（净价不变，利润增加）               ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 竞价    │ 变化              │  ║
║  │ ─────────────── │ ────── │ ─────── │ ──────────────── │  ║
║  │ C1-AUTO         │ $3.00  │ $0.38   │ 继续探索         │  ║
║  │ C2-BROAD        │ $3.00  │ $0.42   │ 维持             │  ║
║  │ C5-EXACT        │ $7.00  │ $0.50-  │ 主力，8个词      │  ║
║  │                 │        │  0.68   │                  │  ║
║  │ C4-PT           │ $2.00  │ $0.35   │ 维持             │  ║
║  │ C3-SD【新增】    │ $2.00  │ $0.30   │ ★品类定向测试    │  ║
║  │ ─────────────── │ ────── │ ─────── │                  │  ║
║  │ 日预算合计       │ $17.00 │         │                  │  ║
║  │ 广告类型占比      │ SP:88% │ SD:12%  │                  │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 广告日预算│ 每日点击│ CPC    │ CVR    │ 广告日订单     │  ║
║  │ $17      │ 32     │ $0.53  │ 11%    │ 3.5           │  ║
║  │                                                       │  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $119   │ 224  │ 25     │ 17     │ 42   │ $839      │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 24%    │ 14%   │ 60%     │ 40%                      │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║  WEEK 6   5.6 - 5.12   稳定期+7DD测试                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$20.99    Coupon：$1.00    Review：15-18个, 4.3★      ║
║  目标：日均6单 | 周42单 | 主词排名#25-40                      ║
║  行动：报名7Day Deal（如果可报名）                            ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 变化                        │  ║
║  │ ─────────────── │ ────── │ ────────────────────────── │  ║
║  │ C1-AUTO         │ $3.00  │ 维持                       │  ║
║  │ C2-BROAD        │ $3.00  │ 维持                       │  ║
║  │ C5-EXACT        │ $8.00  │ ↑ 精确加$1（好词给更多预算）│  ║
║  │ C4-PT           │ $2.00  │ 维持                       │  ║
║  │ C3-SD           │ $2.00  │ 评估效果，不好则砍到$1      │  ║
║  │ ─────────────── │ ────── │                            │  ║
║  │ 日预算合计       │ $18.00 │                            │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $126   │ 240  │ 27     │ 18     │ 45   │ $944      │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 22%    │ 13%   │ 60%     │ 40%                      │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  关键动作                                                    ║
║  ✅ 第三次关键词收割                                          ║
║  ✅ 评估SD效果：ACoS>40% → 砍到$1；ACoS<30% → 维持          ║
║  ✅ 准备SBV视频素材（下周开SBV）                              ║
║  ✅ 如有7DD，广告配合加预算$3-5/天（仅Deal期间）               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 7-8 — 加入SBV·冲排名

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 7   5.13 - 5.19   ★ 开启SBV + 冲排名 ★               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$20.99    Coupon：$1.00    Review：18-22个, 4.3★      ║
║  目标：日均7单 | 周49单 | 主词排名进首页底部(#25-48)           ║
║                                                              ║
║  广告计划 — 完整6个Campaign已齐                               ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 竞价    │ 状态              │  ║
║  │ ─────────────── │ ────── │ ─────── │ ──────────────── │  ║
║  │ C1-AUTO         │ $3.00  │ $0.38   │ 探索（缩减）     │  ║
║  │ C2-BROAD        │ $3.00  │ $0.42   │ 拓词             │  ║
║  │ C3-SD           │ $1.50  │ $0.28   │ 辅助曝光         │  ║
║  │ C4-PT           │ $2.00  │ $0.35   │ 竞品定向         │  ║
║  │ C5-EXACT        │ $8.00  │ $0.50-  │ ★★★ 主力        │  ║
║  │                 │        │  0.70   │                  │  ║
║  │ C6-SBV【新增】   │ $2.50  │ $0.40   │ ★ 视频广告      │  ║
║  │ ─────────────── │ ────── │ ─────── │                  │  ║
║  │ 日预算合计       │ $20.00 │         │                  │  ║
║  │ 广告类型占比      │SP:80%  │SD:7.5% │ SB:12.5%         │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  C6-SBV 视频广告详细设置                                      ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 类型：Sponsored Brands Video                          │  ║
║  │ 关键词：                                              │  ║
║  │   dog leash             $0.45 精确                   │  ║
║  │   heavy duty dog leash  $0.40 精确                   │  ║
║  │   dog leash large breed $0.38 精确                   │  ║
║  │                                                       │  ║
║  │ 视频要求：                                            │  ║
║  │   • 15-30秒                                          │  ║
║  │   • 前3秒展示产品核心卖点                              │  ║
║  │   • 使用场景：狗主人遛狗实拍                            │  ║
║  │   • 突出差异化：反光条/加厚手柄/耐咬                    │  ║
║  │                                                       │  ║
║  │ 为什么开SBV：                                         │  ║
║  │   • CPC比SP低20-30%（$0.40 vs $0.55）                │  ║
║  │   • CTR比普通广告高2-3倍                              │  ║
║  │   • 视频在搜索结果中非常醒目                           │  ║
║  │   • $20产品用视频展示性价比非常高                       │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 广告日预算│ 每日点击│ CPC    │ CVR    │ 广告日订单     │  ║
║  │ $20      │ 38     │ $0.53  │ 12%    │ 4.6           │  ║
║  │                                                       │  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $140   │ 266  │ 32     │ 21     │ 53   │ $1112     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 21%    │ 13%   │ 60%     │ 40%                      │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  冲排名策略（保守版）                                         ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 核心词 "dog leash" 如果在第2-3页：                     │  ║
║  │   1. C5精确中该词竞价 → 建议竞价的110%                  │  ║
║  │   2. 给2周时间观察排名变化                              │  ║
║  │   3. 如果排名稳步上升 → 维持                           │  ║
║  │   4. 如果排名不动 → 不要无限加价，换长尾策略             │  ║
║  │                                                       │  ║
║  │ ❌ 不做：                                              │  ║
║  │   × 不开 "提高和降低" 竞价模式（$20产品承受不了）        │  ║
║  │   × 不设置Top of Search加价（烧钱太快）                 │  ║
║  │   × 不盲目加预算冲排名                                 │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║  WEEK 8   5.20 - 5.26   持续优化                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$20.99    Coupon：$1.00    Review：22-28个, 4.3★      ║
║  目标：日均7-8单 | 周52单 | 主词排名#20-35                    ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 变化                        │  ║
║  │ ─────────────── │ ────── │ ────────────────────────── │  ║
║  │ C1-AUTO         │ $2.00  │ ↓ 继续缩减                 │  ║
║  │ C2-BROAD        │ $2.00  │ ↓ 好词已收割完，缩减        │  ║
║  │ C3-SD           │ $1.50  │ 维持                       │  ║
║  │ C4-PT           │ $2.00  │ 维持                       │  ║
║  │ C5-EXACT        │ $10.00 │ ↑ 继续加！（ACoS<22%）     │  ║
║  │ C6-SBV          │ $3.00  │ ↑ SBV效果好，加预算        │  ║
║  │ ─────────────── │ ────── │                            │  ║
║  │ 日预算合计       │ $20.50 │                            │  ║
║  │ 广告类型占比      │SP:78%  │SD:7%   │ SB:15%           │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $144   │ 278  │ 33     │ 25     │ 58   │ $1218     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 21%    │ 12%   │ 57%     │ 43% ✅ 自然占比提升       │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 9-10 — 提价去Coupon·利润优化

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 9   5.27 - 6.2   ★ 去Coupon + 提价 ★                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ★ 重要调整：去掉Coupon，售价调至$21.99                       ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 理由：                                                │  ║
║  │ • Review已积累25+，有足够社会证明                       │  ║
║  │ • 自然排名已进入前2页，流量稳定                         │  ║
║  │ • Coupon的引流作用递减                                  │  ║
║  │ • 去Coupon后毛利从$7.19 → $8.79（+22%！）               │  ║
║  │                                                       │  ║
║  │ 风险控制：                                             │  ║
║  │ • 不一次性提价太多（$20.99→$21.99 只+$1）               │  ║
║  │ • 观察1周，如果销量降>20%，恢复Coupon                    │  ║
║  │ • 同时加大广告曝光弥补Coupon取消的转化下降               │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  售价：$21.99    Coupon：$0    Review：28-32个, 4.3★         ║
║  目标：日均7-8单（去Coupon后可能短暂回落）| 排名#20-30         ║
║                                                              ║
║  广告计划                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign        │ 日预算 │ 变化                        │  ║
║  │ ─────────────── │ ────── │ ────────────────────────── │  ║
║  │ C1-AUTO         │ $2.00  │ 维持                       │  ║
║  │ C2-BROAD        │ $2.00  │ 维持                       │  ║
║  │ C3-SD           │ $2.00  │ ↑ 提价后加$0.5曝光补偿     │  ║
║  │ C4-PT           │ $2.00  │ 维持                       │  ║
║  │ C5-EXACT        │ $10.00 │ 维持                       │  ║
║  │ C6-SBV          │ $3.00  │ 维持                       │  ║
║  │ ─────────────── │ ────── │                            │  ║
║  │ 日预算合计       │ $21.00 │                            │  ║
║  │ 广告类型占比      │SP:76%  │SD:10%  │ SB:14%           │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据（去Coupon后保守估计）                                ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $147   │ 280  │ 30     │ 22     │ 52   │ $1143     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 22%    │ 13%   │ 58%     │ 42%                      │  ║
║  │                                                       │  ║
║  │ ★ 单位利润变化：                                       │  ║
║  │ 去Coupon前：$3.19/单 → 去Coupon后：$4.83/单 (+51%!)   │  ║
║  │ 即使销量降10%，总利润反而增加！                          │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║  WEEK 10   6.3 - 6.9   稳定验证                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$21.99    Coupon：$0    Review：32-38个, 4.3★         ║
║  目标：日均8单 | 周56单 | 确认去Coupon后销量稳定               ║
║                                                              ║
║  广告计划：与WEEK 9相同，观察去Coupon的影响                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 日预算合计       │ $21.00 │ 维持不变                    │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据（去Coupon1周后恢复）                                ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $147   │ 284  │ 32     │ 26     │ 58   │ $1275     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 21%    │ 12%   │ 55%     │ 45% ✅                    │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  关键动作                                                    ║
║  ✅ 确认去Coupon后销量没有大幅下滑                             ║
║  ✅ 如果销量恢复 → 继续当前策略                                ║
║  ✅ C5-EXACT精确Campaign分组（下周执行）：                     ║
║     → 高效词 (ACoS<18%) 独立到 C5A                           ║
║     → 一般词 (ACoS 18-28%) 留在 C5B                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 11-12 — 精确分组·降本增效

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 11   6.10 - 6.16   ★ 精确Campaign分组 ★               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$21.99    Coupon：$0    Review：38-42个, 4.3★         ║
║  目标：日均8-9单 | 周60单 | 主词稳定首页#15-30                 ║
║                                                              ║
║  ★ 结构调整：精确Campaign一分为二                              ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │                                                       │  ║
║  │  原 C5-EXACT（8个词混在一起）                           │  ║
║  │       │                                               │  ║
║  │       ├──→ C5A-EXACT-HighPerf（高效词）                 │  ║
║  │       │    日预算：$8                                   │  ║
║  │       │    关键词（ACoS<18%的词）：                      │  ║
║  │       │      heavy duty dog leash     $0.65            │  ║
║  │       │      nylon dog leash large    $0.60            │  ║
║  │       │      reflective dog leash 6ft $0.58            │  ║
║  │       │    策略：给够预算，让它跑满                      │  ║
║  │       │                                               │  ║
║  │       └──→ C5B-EXACT-Normal（一般词）                   │  ║
║  │            日预算：$4                                   │  ║
║  │            关键词（ACoS 18-28%的词）：                   │  ║
║  │              dog leash               $0.55             │  ║
║  │              dog leash large breed   $0.50             │  ║
║  │              dog walking leash       $0.48             │  ║
║  │              padded handle dog leash $0.45             │  ║
║  │              training leash for dogs $0.42             │  ║
║  │            策略：控制预算，持续优化竞价                   │  ║
║  │                                                       │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  完整广告计划                                                 ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign          │ 日预算 │ 角色                      │  ║
║  │ ───────────────── │ ────── │ ──────────────────────── │  ║
║  │ C1-AUTO           │ $2.00  │ 纯探索，发现新词          │  ║
║  │ C2-BROAD          │ $2.00  │ 拓展长尾                  │  ║
║  │ C3-SD             │ $1.50  │ 品类曝光                  │  ║
║  │ C4-PT             │ $2.00  │ 竞品防守+进攻             │  ║
║  │ C5A-EXACT-High    │ $8.00  │ ★★★ 印钞机              │  ║
║  │ C5B-EXACT-Normal  │ $4.00  │ ★ 持续优化               │  ║
║  │ C6-SBV            │ $3.00  │ 品牌视频                  │  ║
║  │ ───────────────── │ ────── │                          │  ║
║  │ 日预算合计         │ $22.50 │                          │  ║
║  │ 广告类型占比        │SP:80%  │SD:7%  │ SB:13%          │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  同时：竞价策略切换                                           ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ C5A-EXACT-High  →  "仅降低" (Down only)               │  ║
║  │ 原因：高效词已验证，让亚马逊在低转化时段自动降竞价        │  ║
║  │                                                       │  ║
║  │ C5B、C1、C2     →  维持 "固定竞价"                      │  ║
║  │ 原因：还在探索和优化中                                  │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $158   │ 302  │ 35     │ 30     │ 65   │ $1430     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 20%    │ 11%   │ 54%     │ 46% ✅ 接近平衡           │  ║
║  │                                                       │  ║
║  │ ★ 周利润：65单 × $4.83 = $314                         │  ║
║  │   （$20产品也能赚钱了！）                                │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║  WEEK 12   6.17 - 6.23   确认分组效果                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$21.99  Coupon：$0  Review：42-48个, 4.3★             ║
║  目标：日均9单 | 周63单 | 主词稳定首页                         ║
║  广告日预算：$22.50 维持                                      ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $158   │ 310  │ 36     │ 33     │ 69   │ $1518     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 20%    │ 10%   │ 52%     │ 48% ✅                    │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  关键评估                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ C5A高效组 → ACoS 15-18% → 效果很好，维持              │  ║
║  │ C5B一般组 → ACoS 22-28% → 继续优化竞价               │  ║
║  │ C6-SBV   → ACoS 18-22% → SBV性价比高，考虑加预算     │  ║
║  │ C3-SD    → ACoS 30-35% → 可以接受，品牌曝光价值      │  ║
║  │ C1-AUTO  → 还在发现新词 → 维持$2                     │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 13-14 — 收割稳定期

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 13-14   6.24 - 7.7   ★ 稳定收割期 ★                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$21.99    Coupon：$0    Review：48-55个, 4.3★         ║
║  目标：日均10单 | 周70单 | 主词首页稳定                        ║
║                                                              ║
║  广告策略：从"推广"转向"收割"                                  ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │                                                       │  ║
║  │  策略转变：                                            │  ║
║  │  推广期 → "花钱买排名"                                 │  ║
║  │  收割期 → "用最少的钱维持排名，最大化利润"               │  ║
║  │                                                       │  ║
║  │  具体操作：                                            │  ║
║  │  ① C5B一般组：ACoS>25%的词 → 降竞价15%或暂停           │  ║
║  │  ② C4-PT：整体ACoS>30% → 砍到$1/天                    │  ║
║  │  ③ C5A高效组：维持或微调，这是利润来源                   │  ║
║  │  ④ C6-SBV：效果好 → 加到$4/天                          │  ║
║  │  ⑤ C2-BROAD：缩减到$1.50/天                            │  ║
║  │                                                       │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  广告计划 — 收割期配置                                        ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign          │ 日预算 │ 角色        │ 占比        │  ║
║  │ ───────────────── │ ────── │ ─────────── │ ────────── │  ║
║  │ C1-AUTO           │ $2.00  │ 探索        │ 10%        │  ║
║  │ C2-BROAD          │ $1.50  │ 拓展(缩减)   │ 8%         │  ║
║  │ C3-SD             │ $1.50  │ 再营销       │ 8%         │  ║
║  │ C4-PT             │ $1.00  │ 竞品(缩减)   │ 5%         │  ║
║  │ C5A-EXACT-High    │ $7.00  │ ★ 利润中心  │ 35%        │  ║
║  │ C5B-EXACT-Normal  │ $3.00  │ 优化(缩减)   │ 15%        │  ║
║  │ C6-SBV            │ $4.00  │ ★ 性价比高  │ 20%        │  ║
║  │ ───────────────── │ ────── │ ─────────── │ ────────── │  ║
║  │ 日预算合计         │ $20.00 │             │ 100%       │  ║
║  │ 类型占比           │SP:73%  │SD:7.5%      │SB:20%     │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  注意：总预算从$22.50降到$20（但效率更高了）                    ║
║                                                              ║
║  预估数据                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │                   │ WEEK 13     │ WEEK 14              │  ║
║  │ 周花费             │ $140        │ $140                 │  ║
║  │ 周广告单           │ 34          │ 35                   │  ║
║  │ 周自然单           │ 36          │ 40                   │  ║
║  │ 周总单             │ 70          │ 75                   │  ║
║  │ 周销售额           │ $1540       │ $1650                │  ║
║  │ 广告ACoS          │ 19%         │ 18%                  │  ║
║  │ TACoS             │ 9%          │ 8.5%                 │  ║
║  │ 广告占比           │ 49%         │ 47%                  │  ║
║  │ 自然占比           │ 51% ✅      │ 53% ✅✅             │  ║
║  │ 周利润             │ $338        │ $362                 │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  ★ 里程碑：自然单 > 广告单！推广成功的标志！                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### WEEK 15-16 — 长期维护·自动驾驶

```
╔══════════════════════════════════════════════════════════════╗
║  WEEK 15-16   7.8 - 7.22   长期维护模式                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  售价：$21.99    Coupon：$0    Review：55-65个, 4.3★         ║
║  目标：日均10-12单 | TACoS < 10% | 净利润率 > 20%             ║
║                                                              ║
║  广告配置（长期稳态）                                         ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ Campaign          │ 日预算 │ 角色                      │  ║
║  │ ───────────────── │ ────── │ ──────────────────────── │  ║
║  │ C1-AUTO           │ $2.00  │ 持续探索新词              │  ║
║  │ C2-BROAD          │ $1.00  │ 最小化维持                │  ║
║  │ C3-SD             │ $1.50  │ 再营销维持                │  ║
║  │ C4-PT             │ $1.00  │ 竞品防守                  │  ║
║  │ C5A-EXACT-High    │ $7.00  │ ★ 核心利润源              │  ║
║  │ C5B-EXACT-Normal  │ $2.50  │ 辅助                     │  ║
║  │ C6-SBV            │ $4.00  │ ★ 高性价比                │  ║
║  │ ───────────────── │ ────── │                          │  ║
║  │ 日预算合计         │ $19.00 │                          │  ║
║  │ 类型占比           │SP:71%  │SD:8%  │SB:21%            │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  最终稳态数据                                                 ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 周花费  │ 周点击│ 周广告单│ 周自然单│ 周总单│ 周销售额  │  ║
║  │ $133   │ 260  │ 33     │ 47     │ 80   │ $1760     │  ║
║  │                                                       │  ║
║  │ 广告ACoS│ TACoS │ 广告占比 │ 自然占比                  │  ║
║  │ 18%    │ 7.6%  │ 41%     │ 59% ✅✅✅                │  ║
║  │                                                       │  ║
║  │ 周利润：80单 × $5.49 = $439                            │  ║
║  │ 周利润减广告费：$439 - $133 = $306 净利润               │  ║
║  │ 月利润预估：$1,224                                     │  ║
║  │ 月销售额预估：$7,040                                   │  ║
║  │ 净利润率：17.4%（含广告费后的真实利润）                   │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
║  维护节奏                                                    ║
║  ┌───────────────────────────────────────────────────────┐  ║
║  │ 每周一 (15min)：                                       │  ║
║  │   □ 导出搜索词报告 → 加否定词                          │  ║
║  │   □ 检查是否有新的高潜力词                              │  ║
║  │                                                       │  ║
║  │ 每周三 (10min)：                                       │  ║
║  │   □ 检查ACoS异常 → 微调竞价（±5-10%）                  │  ║
║  │   □ 检查预算消耗                                       │  ║
║  │                                                       │  ║
║  │ 每周五 (10min)：                                       │  ║
║  │   □ 看周数据 → 确认TACoS趋势                           │  ║
║  │   □ 记录到Excel                                        │  ║
║  │                                                       │  ║
║  │ 每月1号 (30min)：                                      │  ║
║  │   □ 月度大扫除：暂停30天无转化的词                      │  ║
║  │   □ 利润复盘：确认每个SKU还在赚钱                       │  ║
║  │   □ 竞品检查：有无新强竞品进入                          │  ║
║  └───────────────────────────────────────────────────────┘  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 六、16 周汇总数据看板

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                              16周完整数据追踪表                                              │
├──────┬───────┬───────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────────────┤
│ WEEK │ 售价   │Coupon │日预算 │周花费 │周广告│周自然│周总单│周销售│ACoS  │TACoS │主词排名      │
│      │       │       │      │      │单    │单    │      │额    │      │      │              │
├──────┼───────┼───────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────────────┤
│ W1   │$19.99 │$2.00  │$13   │$91   │13    │5     │18    │$324  │35%   │28%   │#200+         │
│ W2   │$19.99 │$2.00  │$13   │$91   │15    │6     │21    │$378  │34%   │24%   │#120-200      │
│ W3   │$19.99 │$2.00  │$14   │$98   │18    │10    │28    │$504  │30%   │19%   │#60-120  ★收割│
│ W4   │$19.99 │$2.00  │$15   │$105  │22    │13    │35    │$630  │27%   │17%   │#40-80   ★收割│
├──────┼───────┼───────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────────────┤
│ W5   │$20.99 │$1.00  │$17   │$119  │25    │17    │42    │$839  │24%   │14%   │#30-50  +SD   │
│ W6   │$20.99 │$1.00  │$18   │$126  │27    │18    │45    │$944  │22%   │13%   │#25-40  +7DD  │
│ W7   │$20.99 │$1.00  │$20   │$140  │32    │21    │53    │$1112 │21%   │13%   │#20-35  +SBV  │
│ W8   │$20.99 │$1.00  │$20.5 │$144  │33    │25    │58    │$1218 │21%   │12%   │#15-30        │
├──────┼───────┼───────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────────────┤
│ W9   │$21.99 │$0     │$21   │$147  │30    │22    │52    │$1143 │22%   │13%   │#20-35 去Cpn  │
│ W10  │$21.99 │$0     │$21   │$147  │32    │26    │58    │$1275 │21%   │12%   │#18-30  恢复   │
│ W11  │$21.99 │$0     │$22.5 │$158  │35    │30    │65    │$1430 │20%   │11%   │#15-25  分组   │
│ W12  │$21.99 │$0     │$22.5 │$158  │36    │33    │69    │$1518 │20%   │10%   │#12-22        │
├──────┼───────┼───────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────────────┤
│ W13  │$21.99 │$0     │$20   │$140  │34    │36    │70    │$1540 │19%   │9%    │#10-20  收割   │
│ W14  │$21.99 │$0     │$20   │$140  │35    │40    │75    │$1650 │18%   │8.5%  │#8-18   ★首页 │
│ W15  │$21.99 │$0     │$19   │$133  │33    │45    │78    │$1716 │18%   │7.8%  │#5-15   稳定   │
│ W16  │$21.99 │$0     │$19   │$133  │33    │47    │80    │$1760 │18%   │7.6%  │#5-15   维护   │
├──────┴───────┴───────┴──────┼──────┼──────┼──────┼──────┼──────┤      │      │              │
│ 16周累计                     │$2070 │472   │394   │866   │$17981│      │      │              │
│ 16周平均                     │$129/w│29.5/w│24.6/w│54.1/w│$1124 │23.3% │13.5% │              │
└─────────────────────────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────────────┘

趋势图（用文字画）：

ACoS 趋势：
35% ██████████████████
34% █████████████████
30% ███████████████
27% █████████████▌
24% ████████████
22% ███████████
21% ██████████▌
21% ██████████▌
22% ███████████      ← 去Coupon短暂回升
21% ██████████▌
20% ██████████
20% ██████████
19% █████████▌
18% █████████        ← 目标达成 ✅
18% █████████
18% █████████

TACoS 趋势：
28% ██████████████
24% ████████████
19% █████████▌
17% ████████▌
14% ███████
13% ██████▌
13% ██████▌
12% ██████
13% ██████▌          ← 去Coupon短暂回升
12% ██████
11% █████▌
10% █████
9%  ████▌
8.5%████▎            ← 目标达成 ✅
7.8%████
7.6%███▊

自然单占比趋势：
28% ████████
29% ████████▌
36% ██████████
37% ██████████▌
40% ███████████
40% ███████████
40% ███████████
43% ████████████
42% ███████████▌
45% ████████████▌
46% █████████████
48% █████████████▌
51% ██████████████▎  ← ★ 突破50%！
53% ██████████████▊
58% ████████████████
59% ████████████████▌ ← 目标达成 ✅
```

---

## 七、财务汇总（对标你的模板格式）

```
┌──────────────────────────────────────────────────────────────┐
│              财务汇总 — 4个月分阶段                             │
├──────────────┬──────────┬──────────┬──────────┬──────────────┤
│ 细分项        │ 4月      │ 5月      │ 6月      │ 7月(稳态)    │
│              │ (冷启动)  │ (放量)   │ (优化)   │ (收割)       │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 月销量        │ 102      │ 198      │ 252      │ 303          │
│ 售价          │ $19.99   │ $20.99   │ $21.99   │ $21.99       │
│ 月销售额      │ $1,836   │ $4,113   │ $5,506   │ $6,666       │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 佣金(15%)    │ -$275    │ -$617    │ -$826    │ -$1,000      │
│ FBA配送费     │ -$357    │ -$693    │ -$882    │ -$1,061      │
│ FBA仓储费     │ -$31     │ -$59     │ -$76     │ -$91         │
│ 退货分摊(5%)  │ -$92     │ -$206    │ -$275    │ -$333        │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 亚马逊费用小计 │ -$755    │ -$1,575  │ -$2,059  │ -$2,485      │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 采购成本      │ -$357    │ -$693    │ -$882    │ -$1,061      │
│ 头程运费(海运) │ -$153    │ -$297    │ -$378    │ -$455        │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 货物成本小计   │ -$510    │ -$990    │ -$1,260  │ -$1,516      │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ ★ 广告前毛利  │ $571     │ $1,548   │ $2,187   │ $2,665       │
│ ★ 广告前毛利率│ 31.1%    │ 37.6%    │ 39.7%    │ 40.0%        │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 广告费        │ -$385    │ -$529    │ -$603    │ -$546        │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ ★ 净毛利      │ $186     │ $1,019   │ $1,584   │ $2,119       │
│ ★ 净毛利率    │ 10.1%    │ 24.8%    │ 28.8%    │ 31.8%        │
│ 广告费占比     │ 21.0%    │ 12.9%    │ 11.0%    │ 8.2%         │
│ (TACoS)      │          │          │          │              │
├──────────────┼──────────┼──────────┼──────────┼──────────────┤
│ 累计净毛利     │ $186     │ $1,205   │ $2,789   │ $4,908       │
│ 累计广告费     │ $385     │ $914     │ $1,517   │ $2,063       │
│ 累计ROI       │ 0.48x    │ 1.32x    │ 1.84x    │ 2.38x        │
└──────────────┴──────────┴──────────┴──────────┴──────────────┘

  4月：投入期，微利，这是正常的
  5月：开始盈利，毛利覆盖广告费
  6月：利润稳步增长
  7月：进入稳态，月净利$2,100+ ✅
  
  16周总投入广告费：$2,063
  16周总净毛利：$4,908
  投资回报：2.38倍 ✅
```

---

## 八、库存计划（对标你的模板）

```
┌─────────────────────────────────────────────────────────────────────┐
│                      库存 & 采购计划                                  │
├──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────────────────┤
│ WEEK │FBA库 │中仓  │在途  │周消耗│可售  │采购  │ 备注                 │
│      │存    │      │      │      │周数  │计划  │                     │
├──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────────┤
│ W1   │ 500  │ 300  │ 0    │ 18   │ 28w  │      │ 首批FBA 500入仓     │
│ W2   │ 482  │ 300  │ 0    │ 21   │ 23w  │      │                     │
│ W3   │ 461  │ 300  │ 0    │ 28   │ 16w  │      │                     │
│ W4   │ 433  │ 300  │ 0    │ 35   │ 12w  │      │ ⚠️开始关注补货      │
├──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────────┤
│ W5   │ 398  │ 300  │ 0    │ 42   │ 9w   │ 下单 │ 翻单1: 1000个       │
│      │      │      │      │      │      │1000  │ 交期30天，走海运     │
│ W6   │ 356  │ 300  │ 0    │ 45   │ 8w   │      │                     │
│ W7   │ 311  │ 300  │ 0    │ 53   │ 6w   │      │ 中仓调拨200→FBA     │
│ W8   │ 453  │ 100  │ 0    │ 58   │ 8w   │      │ FBA=311-53+200=458  │
├──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────────┤
│ W9   │ 400  │ 100  │1000  │ 52   │ 8w   │      │ 翻单1在途           │
│ W10  │ 348  │ 100  │1000  │ 58   │ 6w   │      │                     │
│ W11  │ 290  │ 100  │1000  │ 65   │ 4.5w │ 下单 │ 翻单2: 1500个       │
│      │      │      │      │      │      │1500  │ 交期30天            │
│ W12  │ 225  │1100  │ 0    │ 69   │ 3.3w │      │ 翻单1到中仓！       │
│      │      │      │      │      │      │      │ 调拨500→FBA         │
├──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────────────────┤
│ W13  │ 656  │ 600  │ 0    │ 70   │ 9w   │      │ FBA=225-69+500=656  │
│ W14  │ 586  │ 600  │1500  │ 75   │ 8w   │      │ 翻单2在途           │
│ W15  │ 511  │ 600  │1500  │ 78   │ 6.5w │      │                     │
│ W16  │ 433  │ 600  │1500  │ 80   │ 5.4w │      │ 翻单2即将到中仓     │
├──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────────────────────┤
│                                                                     │
│ 补货规则（$20产品海运为主）：                                          │
│ ┌─────────────────────────────────────────────────────────────┐    │
│ │ • 安全库存 = 6周销量（海运4周+缓冲2周）                       │    │
│ │ • FBA可售周数 < 8周 → 启动中仓调拨                            │    │
│ │ • FBA可售周数 < 6周 → 下翻单                                 │    │
│ │ • 首批500个（保守，测试市场）                                  │    │
│ │ • 翻单1: 1000个（销量验证后加量）                              │    │
│ │ • 翻单2: 1500个（稳态后按月销300备）                           │    │
│ │ • 安全库存300个在中仓（防断货/账号异常）                        │    │
│ └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│ 采购汇总：                                                          │
│ ┌──────────┬──────┬──────────┬────────┬──────────┬──────────┐     │
│ │ 批次      │ 数量 │ 下单日期  │ 入仓日期│ 物流方式  │ 金额      │     │
│ ├──────────┼──────┼──────────┼────────┼──────────┼──────────┤     │
│ │ 首单      │ 800  │ 3月1日   │ 4月1日  │ 海运      │ $4,000   │     │
│ │ (500FBA   │      │          │        │          │          │     │
│ │  300中仓)  │      │          │        │          │          │     │
│ │ 翻单1     │1000  │ 4月29日  │ 6月15日 │ 海运      │ $5,000   │     │
│ │ 翻单2     │1500  │ 6月10日  │ 7月25日 │ 海运      │ $7,500   │     │
│ └──────────┴──────┴──────────┴────────┴──────────┴──────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 九、每周广告操作SOP

```
┌──────────────────────────────────────────────────────────────┐
│           每周广告操作SOP（可直接打印贴墙上）                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ╔══════════════════════════════════════╗                    │
│  ║  周一 (15分钟) — 搜索词清洗          ║                    │
│  ╠══════════════════════════════════════╣                    │
│  ║                                      ║                    │
│  ║  □ 1. 下载搜索词报告（过去7天）       

继续完成每周操作SOP及剩余部分：

---

## 九、每周广告操作SOP（续）

```
┌──────────────────────────────────────────────────────────────┐
│           每周广告操作SOP（可直接打印贴墙上）                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ╔══════════════════════════════════════════════════════╗    │
│  ║  周一 (15分钟) — 搜索词清洗                          ║    │
│  ╠══════════════════════════════════════════════════════╣    │
│  ║                                                      ║    │
│  ║  □ 1. 下载搜索词报告（过去7天）                       ║    │
│  ║     广告后台 → Reports → Search Term Report          ║    │
│  ║                                                      ║    │
│  ║  □ 2. 按花费从高到低排序                              ║    │
│  ║                                                      ║    │
│  ║  □ 3. 逐行检查，标记3类词：                           ║    │
│  ║     🔴 否定词：不相关 或 (点击≥15 且 订单=0)          ║    │
│  ║        → 加到对应Campaign的否定精确                   ║    │
│  ║                                                      ║    │
│  ║     ✅ 收割词：(点击≥15 且 订单≥2 且 ACoS≤28%)       ║    │
│  ║        → 加到C5精确Campaign                          ║    │
│  ║        → 在源头Campaign加否定精确                     ║    │
│  ║                                                      ║    │
│  ║     ⏳ 观察词：数据不足，继续跑                       ║    │
│  ║        → 不动，下周再看                               ║    │
│  ║                                                      ║    │
│  ║  □ 4. 在Excel记录本周否定/收割的词                    ║    │
│  ║                                                      ║    │
│  ║  操作记录模板：                                       ║    │
│  ║  ┌──────────┬──────┬──────┬──────┬──────────┐       ║    │
│  ║  │日期       │搜索词 │来源   │动作   │目标       │       ║    │
│  ║  ├──────────┼──────┼──────┼──────┼──────────┤       ║    │
│  ║  │4/7       │cat   │C1自动│否定   │C1否定精确 │       ║    │
│  ║  │          │leash │      │      │          │       ║    │
│  ║  │4/7       │nylon │C2广泛│收割   │C5精确    │       ║    │
│  ║  │          │dog   │      │      │+C2否定   │       ║    │
│  ║  │          │leash │      │      │          │       ║    │
│  ║  └──────────┴──────┴──────┴──────┴──────────┘       ║    │
│  ║                                                      ║    │
│  ╚══════════════════════════════════════════════════════╝    │
│                                                              │
│  ╔══════════════════════════════════════════════════════╗    │
│  ║  周三 (10分钟) — 竞价调整                            ║    │
│  ╠══════════════════════════════════════════════════════╣    │
│  ║                                                      ║    │
│  ║  □ 1. 打开广告后台，查看每个Campaign过去7天数据       ║    │
│  ║                                                      ║    │
│  ║  □ 2. 按规则调整竞价：                                ║    │
│  ║                                                      ║    │
│  ║  ┌──────────────────────────────────────────────┐   ║    │
│  ║  │          $20产品竞价调整决策表                 │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  情况A: ACoS < 18% 且 订单≥3                  │   ║    │
│  ║  │  → 竞价 + 10%（最高不超$0.85）                 │   ║    │
│  ║  │  → 给这个词更多流量，它在赚钱                   │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  情况B: ACoS 18-25%                           │   ║    │
│  ║  │  → 维持不变 ✅ 这是理想区间                    │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  情况C: ACoS 25-35%                           │   ║    │
│  ║  │  → 竞价 - 10%                                 │   ║    │
│  ║  │  → 还有转化但成本偏高                          │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  情况D: ACoS > 36%（盈亏线）                   │   ║    │
│  ║  │  → 竞价 - 20%                                 │   ║    │
│  ║  │  → 如果连续2周>36% → 暂停该词                  │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  情况E: 点击>20 无转化                         │   ║    │
│  ║  │  → 暂停关键词 或 加否定                        │   ║    │
│  ║  │  → $20产品，20次点击≈$12，亏不起                │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  情况F: 曝光多但CTR<0.3%                       │   ║    │
│  ║  │  → 不调竞价！先检查主图和价格                   │   ║    │
│  ║  │  → 这是Listing问题不是竞价问题                  │   ║    │
│  ║  └──────────────────────────────────────────────┘   ║    │
│  ║                                                      ║    │
│  ║  □ 3. 检查预算消耗                                   ║    │
│  ║     每天预算花不到60% → 整体竞价偏低                  ║    │
│  ║     每天下午2点花完 → 可以加$2日预算                   ║    │
│  ║     不要一次性加太多预算                               ║    │
│  ║                                                      ║    │
│  ║  □ 4. 记录调整动作                                   ║    │
│  ║  ┌──────────┬────────┬──────────┬──────────────┐    ║    │
│  ║  │日期       │关键词    │调整前     │调整后+原因     │    ║    │
│  ║  ├──────────┼────────┼──────────┼──────────────┤    ║    │
│  ║  │4/9       │dog     │$0.60     │$0.54 ACoS28% │    ║    │
│  ║  │          │leash   │          │降10%         │    ║    │
│  ║  │4/9       │heavy   │$0.55     │$0.61 ACoS15% │    ║    │
│  ║  │          │duty..  │          │加10%         │    ║    │
│  ║  └──────────┴────────┴──────────┴──────────────┘    ║    │
│  ║                                                      ║    │
│  ╚══════════════════════════════════════════════════════╝    │
│                                                              │
│  ╔══════════════════════════════════════════════════════╗    │
│  ║  周五 (10分钟) — 周报总结                            ║    │
│  ╠══════════════════════════════════════════════════════╣    │
│  ║                                                      ║    │
│  ║  □ 1. 填写周数据追踪表                                ║    │
│  ║                                                      ║    │
│  ║  ┌──────────────────────────────────────────────┐   ║    │
│  ║  │              本周数据卡                       │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  日期：W___  ____月____日 至 ____月____日     │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  售价：$______    Coupon：$______             │   ║    │
│  ║  │  Review数：______  评分：______★             │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  ── 销售数据 ──                               │   ║    │
│  ║  │  总订单：____单    日均：____单               │   ║    │
│  ║  │  总销售额：$______                            │   ║    │
│  ║  │  广告单：____单    自然单：____单             │   ║    │
│  ║  │  广告占比：____%    自然占比：____%           │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  ── 广告数据 ──                               │   ║    │
│  ║  │  广告花费：$______  日均：$______             │   ║    │
│  ║  │  总点击：______    CPC：$______              │   ║    │
│  ║  │  CVR：______%                                │   ║    │
│  ║  │  ACoS：______%     TACoS：______%            │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  ── 排名 ──                                   │   ║    │
│  ║  │  dog leash 排名：#______                     │   ║    │
│  ║  │  heavy duty dog leash 排名：#______          │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  ── 趋势判断 ──                               │   ║    │
│  ║  │  □ 销量趋势：↑上升 / →持平 / ↓下降           │   ║    │
│  ║  │  □ ACoS趋势：↑上升 / →持平 / ↓下降           │   ║    │
│  ║  │  □ TACoS趋势：↑上升 / →持平 / ↓下降          │   ║    │
│  ║  │  □ 自然占比：↑上升 / →持平 / ↓下降            │   ║    │
│  ║  │                                              │   ║    │
│  ║  │  ── 下周计划 ──                               │   ║    │
│  ║  │  1. ________________________________         │   ║    │
│  ║  │  2. ________________________________         │   ║    │
│  ║  │  3. ________________________________         │   ║    │
│  ║  │                                              │   ║    │
│  ║  └──────────────────────────────────────────────┘   ║    │
│  ║                                                      ║    │
│  ║  □ 2. 对比上周数据，判断趋势                          ║    │
│  ║                                                      ║    │
│  ║  □ 3. 确定下周是否需要：                              ║    │
│  ║     □ 调整预算分配？                                  ║    │
│  ║     □ 新增/暂停Campaign？                             ║    │
│  ║     □ 调整售价/Coupon？                               ║    │
│  ║     □ 优化Listing内容？                               ║    │
│  ║     □ 补货？                                          ║    │
│  ║                                                      ║    │
│  ╚══════════════════════════════════════════════════════╝    │
│                                                              │
│  ╔══════════════════════════════════════════════════════╗    │
│  ║  每月1号 (30分钟) — 月度大复盘                       ║    │
│  ╠══════════════════════════════════════════════════════╣    │
│  ║                                                      ║    │
│  ║  □ 1. Campaign级别扫除                                ║    │
│  ║     ┌────────────────────────────────────────────┐   ║    │
│  ║     │ 对每个Campaign做体检：                      │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ C1-AUTO：                                  │   ║    │
│  ║     │  □ 本月发现了几个新词？ ____个              │   ║    │
│  ║     │  □ 贡献了多少订单？ ____单                  │   ║    │
│  ║     │  □ ACoS：____%                             │   ║    │
│  ║     │  → 如果1个月没发现新词且ACoS>40%            │   ║    │
│  ║     │    → 考虑暂停或降到$1/天                    │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ C2-BROAD：                                 │   ║    │
│  ║     │  □ 本月收割了几个词？ ____个                │   ║    │
│  ║     │  □ ACoS：____%                             │   ║    │
│  ║     │  → 好词都收割完了 → 缩减预算               │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ C5-EXACT（A组/B组）：                       │   ║    │
│  ║     │  □ A组ACoS：____% → 维持/加预算            │   ║    │
│  ║     │  □ B组ACoS：____% → 优化/砍低效词          │   ║    │
│  ║     │  □ 有没有B组词表现提升可以移到A组？          │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ C4-PT：                                    │   ║    │
│  ║     │  □ 哪些ASIN有转化？ 保留                   │   ║    │
│  ║     │  □ 哪些ASIN烧钱？ 替换                     │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ C6-SBV：                                   │   ║    │
│  ║     │  □ ACoS：____%                             │   ║    │
│  ║     │  □ CTR：____%（SBV正常CTR应>0.5%）         │   ║    │
│  ║     │  → 效果好加预算，效果差检查视频质量          │   ║    │
│  ║     └────────────────────────────────────────────┘   ║    │
│  ║                                                      ║    │
│  ║  □ 2. 关键词级别扫除                                  ║    │
│  ║     ┌────────────────────────────────────────────┐   ║    │
│  ║     │ 导出30天关键词报告，找出：                   │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ 🔴 30天无转化但花费>$10的词 → 暂停          │   ║    │
│  ║     │ 🔴 30天ACoS>40%的词 → 降竞价20%或暂停       │   ║    │
│  ║     │ ✅ 表现上升的词 → 考虑从B组移到A组           │   ║    │
│  ║     │ ⏳ 新加入的词 → 给足够时间跑数据             │   ║    │
│  ║     └────────────────────────────────────────────┘   ║    │
│  ║                                                      ║    │
│  ║  □ 3. 利润核算                                       ║    │
│  ║     ┌────────────────────────────────────────────┐   ║    │
│  ║     │ 本月销售额：$______                        │   ║    │
│  ║     │ 本月广告费：$______                        │   ║    │
│  ║     │ TACoS：______%                             │   ║    │
│  ║     │ 本月净利润：$______                        │   ║    │
│  ║     │ 净利润率：______%                           │   ║    │
│  ║     │                                            │   ║    │
│  ║     │ 这个SKU还值得继续推吗？                     │   ║    │
│  ║     │ ✅ 净利润为正 + TACoS下降趋势 → 继续        │   ║    │
│  ║     │ ⚠️ 净利润为正 + TACoS不降 → 优化但不加投入  │   ║    │
│  ║     │ 🔴 持续亏损3个月 → 考虑退出                 │   ║    │
│  ║     └────────────────────────────────────────────┘   ║    │
│  ║                                                      ║    │
│  ║  □ 4. 竞品检查                                       ║    │
│  ║     ┌────────────────────────────────────────────┐   ║    │
│  ║     │ □ 竞品价格有无变化？                        │   ║    │
│  ║     │ □ 有无新的强竞品上架？                       │   ║    │
│  ║     │ □ 竞品Review有无大幅增长？                   │   ║    │
│  ║     │ □ 你的排名相对竞品是进步还是退步？            │   ║    │
│  ║     └────────────────────────────────────────────┘   ║    │
│  ║                                                      ║    │
│  ╚══════════════════════════════════════════════════════╝    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 十、异常处理手册

```
┌──────────────────────────────────────────────────────────────┐
│             遇到问题怎么办 — 按场景速查                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  场景1: ACoS突然飙升（从22%→40%+）                            │
│  ═══════════════════════════════════════                      │
│                                                              │
│  ┌── 排查步骤 ──────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Step 1: 是所有Campaign都高还是个别？                   │   │
│  │  ├── 个别Campaign高                                    │   │
│  │  │   → 检查该Campaign是否有新的低效搜索词匹配进来       │   │
│  │  │   → 加否定词解决                                    │   │
│  │  │                                                     │   │
│  │  └── 所有Campaign都高                                   │   │
│  │      → 继续Step 2                                      │   │
│  │                                                        │   │
│  │  Step 2: CVR是否下降？                                  │   │
│  │  ├── CVR下降了                                         │   │
│  │  │   → 检查Listing是否被改（标题/图片/价格）             │   │
│  │  │   → 检查差评是否增加                                 │   │
│  │  │   → 检查竞品是否降价/做Deal                          │   │
│  │  │   → 检查Buy Box是否丢失                              │   │
│  │  │                                                     │   │
│  │  └── CVR没变，CPC上升了                                 │   │
│  │      → 竞争加剧，更多卖家在投这些词                      │   │
│  │      → 不要跟着加价！保守降竞价10%                       │   │
│  │      → 把预算转移到长尾词和SBV                           │   │
│  │                                                        │   │
│  │  Step 3: 如果2-3天后没改善                               │   │
│  │  → 先把高ACoS的词暂停（止血）                            │   │
│  │  → 只保留ACoS<25%的词继续跑                              │   │
│  │  → 排查完原因后再恢复                                    │   │
│  │                                                        │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                              │
│                                                              │
│  场景2: 广告花不出去                                          │
│  ═══════════════════════════════════════                      │
│                                                              │
│  ┌── 排查步骤 ──────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  原因A: 竞价太低                                       │   │
│  │  → 每次加$0.05，观察2天                                │   │
│  │  → 但注意：$20产品CPC上限建议$0.85                      │   │
│  │  → 如果加到$0.85还花不出去 → 这个词竞争太激烈，换词      │   │
│  │                                                        │   │
│  │  原因B: 关键词太少/太窄                                 │   │
│  │  → 精确匹配天然曝光少                                   │   │
│  │  → 加几个广泛/词组匹配的词测试                           │   │
│  │                                                        │   │
│  │  原因C: Listing质量分低                                 │   │
│  │  → 亚马逊会给质量分低的Listing更少曝光                   │   │
│  │  → 检查Listing完整度：图片7张、五点5条、A+完整           │   │
│  │                                                        │   │
│  │  原因D: 新品无权重                                      │   │
│  │  → 正常现象，新品前1-2周曝光会比较少                     │   │
│  │  → 耐心等待，同时确保自动广告在跑                        │   │
│  │                                                        │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                              │
│                                                              │
│  场景3: 有点击但CVR一直低于8%                                  │
│  ═══════════════════════════════════════                      │
│                                                              │
│  ┌── 排查步骤 ──────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  ❶ 检查流量是否精准                                    │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 导出搜索词报告：                                │  │   │
│  │  │ • 是否有大量不相关词在消耗点击？                  │  │   │
│  │  │ • 是否自动广告跑偏了？                           │  │   │
│  │  │ → 加否定词 + 缩减自动广告预算                    │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ❷ 检查Listing转化要素                                 │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ □ 主图是否清晰、吸引人？                        │  │   │
│  │  │ □ 价格是否有竞争力？（对比竞品±10%）             │  │   │
│  │  │ □ Review是否足够？（<10个很难转化）              │  │   │
│  │  │ □ 评分是否>=4.0？（<4.0严重影响转化）            │  │   │
│  │  │ □ 五点描述是否突出卖点？                        │  │   │
│  │  │ □ A+页面是否有？                                │  │   │
│  │  │ □ 是否有Coupon标签？（绿色标签提升CTR和CVR）     │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  ❸ 如果Listing都OK但CVR还是低                          │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ → 可能是产品本身竞争力不够                       │  │   │
│  │  │ → 对比竞品：你的图片/卖点/价格是否有优势？        │  │   │
│  │  │ → 如果无明显优势 → 降低广告投入，不强推            │  │   │
│  │  │ → $20产品CVR<8%基本无法盈利（参考速查表）         │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                              │
│                                                              │
│  场景4: 排名上去了又掉了                                      │
│  ═══════════════════════════════════════                      │
│                                                              │
│  ┌── 排查步骤 ──────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Step 1: 是否断货了？                                  │   │
│  │  → 断货=排名直接清零，最致命的事情                      │   │
│  │  → 永远保持6周以上库存                                  │   │
│  │                                                        │   │
│  │  Step 2: 广告是否暂停了？                               │   │
│  │  → 预算花完导致下午无广告 → 排名下滑                    │   │
│  │  → 解决：加预算 或 降竞价让预算撑到全天                  │   │
│  │                                                        │   │
│  │  Step 3: 竞品是否在做Deal？                             │   │
│  │  → 竞品做7DD/Lightning Deal会短暂抢走你的排名           │   │
│  │  → 不要慌，Deal结束后排名会恢复                         │   │
│  │  → 不要因为竞品做Deal就盲目降价                         │   │
│  │                                                        │   │
│  │  Step 4: 差评影响？                                     │   │
│  │  → 新增差评会降低CVR → 影响排名                         │   │
│  │  → 回复差评 + 联系买家解决 + 请好评客户留评              │   │
│  │                                                        │   │
│  │  Step 5: 算法波动                                      │   │
│  │  → 亚马逊排名本身就有±5位的正常波动                     │   │
│  │  → 不要因为排名波动1-2位就紧张                          │   │
│  │  → 连续下跌7天以上才需要干预                            │   │
│  │                                                        │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                              │
│                                                              │
│  场景5: 竞品大幅降价                                          │
│  ═══════════════════════════════════════                      │
│                                                              │
│  ┌── 应对策略 ──────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  $20产品的价格战底线：                                  │   │
│  │                                                       │   │
│  │  ❌ 不要盲目跟着降价！                                  │   │
│  │  $20产品利润薄，降$2就少了30%利润                       │   │
│  │                                                       │   │
│  │  ✅ 正确做法：                                         │   │
│  │  ① 先观察竞品降价是短期促销还是永久调价                 │   │
│  │     → 短期促销：不跟，等它恢复                         │   │
│  │     → 永久降价：继续看Step ②                          │   │
│  │                                                       │   │
│  │  ② 用Coupon应对而非直接降售价                          │   │
│  │     → 加$1-2 Coupon = 显示"已优惠"标签                │   │
│  │     → 保持标价不变，Coupon可以随时取消                  │   │
│  │     → 比直接降价灵活得多                               │   │
│  │                                                       │   │
│  │  ③ 如果你的Review和评分更好 → 可以保持高价              │   │
│  │     → 消费者愿意为好评分多付$1-2                       │   │
│  │                                                       │   │
│  │  ④ 极端情况：竞品降到$12-14 持续大甩卖                  │   │
│  │     → 不跟！这个价格不可能赚钱                         │   │
│  │     → 说明竞品在清货，等它清完市场恢复                  │   │
│  │                                                       │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 十一、精铺多SKU统一管理看板

```
如果你同时推3-5个宠物产品，用这张表统一管理：

┌──────────────────────────────────────────────────────────────────────┐
│                    多SKU广告统一管理看板 — 周度更新                     │
├──────────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬─────────┤
│ SKU      │ 级别 │日预算 │周单量│ ACoS │TACoS │自然% │利润/单│ 状态    │
├──────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────┤
│ 狗牵引绳  │ A    │$20   │80    │18%   │7.6%  │59%   │$5.49 │稳态运转 │
│ 狗碗      │ A    │$18   │65    │20%   │9%    │55%   │$4.80 │放量中   │
│ 宠物梳子  │ B    │$8    │30    │25%   │14%   │43%   │$3.20 │优化中   │
│ 猫玩具    │ B    │$6    │22    │28%   │18%   │35%   │$2.10 │观察中   │
│ 宠物指甲剪│ C    │$3    │8     │35%   │28%   │20%   │$0.80 │考虑退出 │
├──────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼─────────┤
│ 合计      │      │$55   │205   │22%   │11%   │48%   │      │         │
│ 月预算    │      │$1650 │      │      │      │      │      │         │
│ 月利润    │      │      │      │      │      │      │$3456 │         │
└──────────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┴─────────┘

预算分配原则：
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  A级SKU拿60%预算 → $33/天                                   │
│  ├── 这些是利润贡献主力                                     │
│  ├── ACoS<22%, TACoS<10%, 自然占比>50%                     │
│  └── 已验证的赚钱产品，给够子弹                              │
│                                                            │
│  B级SKU拿30%预算 → $14/天                                   │
│  ├── 还在优化中，有潜力但未验证                              │
│  ├── ACoS 22-30%, TACoS 12-20%                             │
│  └── 给一定预算跑数据，但不大投                              │
│                                                            │
│  C级SKU拿10%预算 → $3/天                                    │
│  ├── 表现不佳，给最后机会                                   │
│  ├── ACoS>30%, TACoS>25%                                   │
│  └── 跑4周无改善 → 关广告清货                               │
│                                                            │
│  动态调整：每月1号根据上月数据重新分级                        │
│  B→A：连续4周ACoS<22% + 自然占比>45%                        │
│  A→B：连续4周ACoS>28% 或 TACoS上升趋势                      │
│  B→C：连续4周ACoS>35% 或 持续亏损                           │
│  C→退出：3个月无起色                                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 十二、16周后的长期运营节奏

```
┌──────────────────────────────────────────────────────────────┐
│         产品进入成熟期后的广告运营年历                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────── 常规月份 ──────────────────────────────────────┐  │
│  │                                                       │  │
│  │  月初：                                                │  │
│  │  □ 月度大复盘（30分钟）                                │  │
│  │  □ Campaign/关键词清洗                                 │  │
│  │  □ 预算重新分配                                        │  │
│  │  □ 利润核算                                            │  │
│  │                                                       │  │
│  │  月中：                                                │  │
│  │  □ 竞品价格和Listing检查                               │  │
│  │  □ 新关键词测试（加2-3个到广泛Campaign）                │  │
│  │  □ 评估是否需要更新主图或A+                             │  │
│  │                                                       │  │
│  │  每周：                                                │  │
│  │  □ 周一搜索词清洗 → 周三竞价调整 → 周五周报             │  │
│  │  □ 每周总耗时：35分钟/SKU                              │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─────── 大促月份特殊操作 ─────────────────────────────┐   │
│  │                                                       │   │
│  │  🏷️ Prime Day (7月)                                   │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 大促前2周：                                     │  │   │
│  │  │  □ 精确Campaign预算 +50%                        │  │   │
│  │  │  □ 竞价提高15-20%（大促CPC会上涨）              │  │   │
│  │  │  □ 确保库存充足（大促期间日销可能翻2-3倍）       │  │   │
│  │  │  □ 报名7DD/Lightning Deal                      │  │   │
│  │  │  □ 设置Coupon叠加                               │  │   │
│  │  │                                                │  │   │
│  │  │ 大促期间：                                      │  │   │
│  │  │  □ 每天检查预算消耗（可能中午就花完）            │  │   │
│  │  │  □ 按需加预算                                   │  │   │
│  │  │  □ 不要在大促期间调低竞价！                      │  │   │
│  │  │                                                │  │   │
│  │  │ 大促后1周：                                     │  │   │
│  │  │  □ 预算恢复正常                                 │  │   │
│  │  │  □ 竞价恢复原水平                               │  │   │
│  │  │  □ 分析大促数据（哪些词爆了）                    │  │   │
│  │  │  □ 预期销量短暂下滑（正常回调）                  │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  │  🎄 Q4旺季 (10-12月)                                  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │ 宠物产品Q4策略：                                │  │   │
│  │  │                                                │  │   │
│  │  │ 宠物品类Q4增长适中（不像玩具/电子那么疯狂）       │  │   │
│  │  │ 但"宠物礼品"类关键词会暴增：                     │  │   │
│  │  │  → dog gifts / pet stocking stuffers            │  │   │
│  │  │  → gifts for dog lovers / christmas dog leash   │  │   │
│  │  │                                                │  │   │
│  │  │ 操作：                                          │  │   │
│  │  │  □ 10月：加入礼品类关键词测试                    │  │   │
│  │  │  □ 11月：黑五/网一提前加预算30%                   │  │   │
│  │  │  □ 12月：圣诞前2周是宠物品高峰                   │  │   │
│  │  │  □ 12月20日后：降预算（圣诞后宠物品需求回落）     │  │   │
│  │  │  □ 库存：10月初确保有10周库存                     │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────── Listing迭代周期 ──────────────────────────────┐   │
│  │                                                       │   │
│  │  每3个月做一次Listing体检：                            │   │
│  │                                                       │   │
│  │  □ 标题：是否需要调整关键词权重？                      │   │
│  │    → 看搜索词报告中哪些词转化最好 → 放标题前面          │   │
│  │                                                       │   │
│  │  □ 主图：是否可以优化？                                │   │
│  │    → 对比竞品新上的图片                                │   │
│  │    → CTR<0.4% → 换主图测试                            │   │
│  │                                                       │   │
│  │  □ 副图：是否需要更新使用场景？                        │   │
│  │    → 分析差评找到的痛点 → 用图片回应                   │   │
│  │                                                       │   │
│  │  □ A+页面：是否需要迭代？                              │   │
│  │    → 每半年更新一次A+内容                              │   │
│  │                                                       │   │
│  │  □ 五点描述：根据新积累的Review优化卖点                 │   │
│  │    → 把买家最频繁提到的优点放进五点                     │   │
│  │                                                       │   │
│  │  ⚠️ 注意：不要在销量高峰期改Listing！                  │   │
│  │     改Listing会短暂影响排名                            │   │
│  │     选在销售淡季做调整                                 │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 十三、一页纸总结 — 贴在电脑旁边

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       $20 宠物标品 · 精铺 · 保守广告 · 一页纸总结             ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  💰 关键数字                                                  ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ 盈亏ACoS = 36%    →  超过就亏钱的红线                │   ║
║  │ 目标ACoS = 18-22%  →  舒适盈利区间                   │   ║
║  │ 目标TACoS = 8-12%  →  长期健康指标                   │   ║
║  │ CPC上限 = $0.85    →  超过不要追                     │   ║
║  │ CVR底线 = 10%      →  低于先修Listing                │   ║
║  │ 否定标准 = 20次点击0单 → 立即否定                    │   ║
║  │ 收割标准 = 15次点击+2单+ACoS<28% → 收到精确          │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  📅 节奏                                                     ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ W1-2:   数据收集    $13/天   只加否定不调竞价          │   ║
║  │ W3-4:   首次收割    $14-15   收割好词到精确           │   ║
║  │ W5-8:   放量冲刺    $17-21   +SD +SBV 冲排名         │   ║
║  │ W9-12:  降本增效    $21-23   去Coupon 提价 分组       │   ║
║  │ W13-16: 稳定收割    $19-20   TACoS<10% 自然>50%      │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  🎯 每周3件事                                                ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ 周一：搜索词报告 → 加否定 + 收割（15分钟）             │   ║
║  │ 周三：竞价调整 + 预算检查（10分钟）                     │   ║
║  │ 周五：填周报 + 确认趋势（10分钟）                       │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  🚫 绝对不做的事                                             ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ × 不天天调竞价（至少隔3天）                            │   ║
║  │ × 不因为ACoS高就砍预算（先找原因）                     │   ║
║  │ × 不和大牌硬碰核心大词（打长尾）                       │   ║
║  │ × 不在Review<10时猛砸广告（先积评）                    │   ║
║  │ × 不盲目跟竞品降价（用Coupon应对）                     │   ║
║  │ × 不开"提高和降低"竞价模式（$20产品扛不住）            │   ║
║  │ × 不让库存断（断货=排名清零=前功尽弃）                 │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  ✅ 成功标志                                                  ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ □ 核心词排名稳定首页                                   │   ║
║  │ □ 自然单 > 广告单（自然占比>50%）                       │   ║
║  │ □ TACoS 持续下降趋势                                   │   ║
║  │ □ 每周只花35分钟管广告                                  │   ║
║  │ □ 月净利润稳定为正                                     │   ║
║  │ → 全部达成 = 这个产品推成功了 🎉                       │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

> 这套方案是完全按照你提供的推广计划模板格式（周维度、Campaign结构、库存联动、财务测算）重新为 **$20宠物标品** 量身定制的。每一周的预算、竞价、关键词动作、预期数据都可以直接拿去执行。
> 
> 需要我针对你手上某个具体宠物SKU（比如真实的关键词和竞品ASIN）做一份更精确的版本吗？





针对你具体某个宠物SKU（提供真实关键词和竞品ASIN）做一份实操版计划吗？




















# OpenClaw 全景总结：功能·技术·路径·风控策略

---

## 一、OpenClaw 是什么

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   OpenClaw = 开源AI Agent框架 + 计算机操控能力 + 任务自动化引擎        │
│                                                                      │
│   核心定位:                                                           │
│   "人在电脑上能做的事，OpenClaw 基本上都可以做"                         │
│                                                                      │
│   技术本质:                                                           │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│   │  视觉理解  │ + │ 浏览器操控 │ + │ 决策推理  │ + │ 工具调用  │        │
│   │  (看屏幕)  │   │ (点击/输入)│   │ (思考判断)│   │ (API/CLI) │        │
│   └──────────┘   └──────────┘   └──────────┘   └──────────┘        │
│         │              │              │              │                │
│         ▼              ▼              ▼              ▼                │
│   ┌────────────────────────────────────────────────────────┐         │
│   │          完整模拟人类操作电脑的全过程                      │         │
│   └────────────────────────────────────────────────────────┘         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 二、OpenClaw 全部核心技术栈

### 2.1 底层能力

```
┌──────────────────────────────────────────────────────────────────┐
│                    技术架构全景                                    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   应用层 (Application)                    │     │
│  │  任务编排引擎 │ 工作流定义 │ 多Agent协作 │ 人机协同界面      │     │
│  └─────────────────────────────────────────────────────────┘     │
│                            ▲                                      │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   智能层 (Intelligence)                   │     │
│  │  LLM推理(GPT-4o/Claude) │ 视觉理解 │ 上下文记忆 │ 规划能力 │     │
│  └─────────────────────────────────────────────────────────┘     │
│                            ▲                                      │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   操控层 (Control)                        │     │
│  │  浏览器自动化  │  桌面GUI操控  │  键盘鼠标模拟  │  截图识别  │     │
│  │  (Playwright)  │  (PyAutoGUI)  │  (人类化轨迹)  │  (OCR)   │     │
│  └─────────────────────────────────────────────────────────┘     │
│                            ▲                                      │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │                   基础层 (Infrastructure)                 │     │
│  │  沙盒环境 │ 容器隔离 │ 网络管理 │ 存储 │ 日志 │ 安全认证    │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 关键技术能力详解

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  ① 计算机视觉 (Computer Use)                                        │
│  ┌───────────────────────────────────────────────────┐               │
│  │ · 截屏 → LLM 理解当前页面状态                       │               │
│  │ · 识别按钮/输入框/下拉菜单/表格等UI元素              │               │
│  │ · 理解弹窗/错误提示/验证码等异常状态                 │               │
│  │ · 多语言界面识别（中英日德法西等）                    │               │
│  └───────────────────────────────────────────────────┘               │
│                                                                      │
│  ② 浏览器自动化 (Browser Automation)                                 │
│  ┌───────────────────────────────────────────────────┐               │
│  │ · 基于Playwright/Puppeteer的无头/有头浏览器控制      │               │
│  │ · DOM操作 + CSS选择器定位                           │               │
│  │ · Cookie/Session管理                               │               │
│  │ · 多标签页/多窗口管理                               │               │
│  │ · 文件上传/下载处理                                 │               │
│  │ · 表单自动填充                                      │               │
│  └───────────────────────────────────────────────────┘               │
│                                                                      │
│  ③ LLM 推理与决策 (Reasoning)                                       │
│  ┌───────────────────────────────────────────────────┐               │
│  │ · 任务分解：复杂任务→子任务序列                      │               │
│  │ · 状态判断：当前在哪一步？成功还是失败？              │               │
│  │ · 异常处理：页面加载失败、元素找不到时的自愈           │               │
│  │ · 多步推理：跨页面的复杂操作链路                      │               │
│  │ · 上下文记忆：记住之前的操作结果和状态                │               │
│  └───────────────────────────────────────────────────┘               │
│                                                                      │
│  ④ 工具调用 (Tool Use / Function Calling)                            │
│  ┌───────────────────────────────────────────────────┐               │
│  │ · API直接调用（Amazon SP-API/Advertising API）       │               │
│  │ · 命令行工具执行                                     │               │
│  │ · 数据库读写                                        │               │
│  │ · 文件系统操作（Excel/CSV/PDF生成与解析）             │               │
│  │ · 第三方SaaS工具操作（Helium10/JungleScout等）       │               │
│  └───────────────────────────────────────────────────┘               │
│                                                                      │
│  ⑤ 多Agent协作 (Multi-Agent)                                        │
│  ┌───────────────────────────────────────────────────┐               │
│  │ · 选品Agent + Listing Agent + 广告Agent 并行工作     │               │
│  │ · Agent间消息传递与任务交接                          │               │
│  │ · 中央调度器统一管理                                 │               │
│  │ · 冲突检测与解决                                     │               │
│  └───────────────────────────────────────────────────┘               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 三、OpenClaw 在跨境电商中的全部功能清单

### 总览矩阵

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                    │
│              能力域                     功能数    当前成熟度        │
│  ─────────────────────────────────────────────────────────        │
│  🔍 选品与市场调研                        8项      ████████ 90%    │
│  📝 Listing内容创建                       8项      ███████░ 85%    │
│  🎯 活动与促销管理                        7项      ██████░░ 70%    │
│  💬 客服与买家沟通                        7项      ██████░░ 75%    │
│  📦 库存与供应链                          7项      █████░░░ 60%    │
│  📢 广告投放与优化                        9项      ██████░░ 70%    │
│  💰 财务与结算                            7项      █████░░░ 55%    │
│  🛡️ 账号健康与合规                        6项      ██████░░ 70%    │
│  🔄 刊登与产品上架                        5项      █████░░░ 60%    │
│  📊 数据分析与BI                          6项      ███████░ 85%    │
│  🏪 多店铺管理                            5项      ████░░░░ 45%    │
│  ─────────────────────────────────────────────────────────        │
│  总计                                    75项                      │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

### 3.1 全功能详细列表（按风险等级排序）

#### 🟢 绿色区 — 零风险（35项）| 自由执行

```
┌──────────────────────────────────────────────────────────────────────┐
│ 编号  │ 模块        │ 功能                  │ 操作性质 │ 权限   │ 说明  │
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-01  │ 选品        │ 市场容量分析            │ 只读    │ L1    │ 公开数据│
│ G-02  │ 选品        │ 竞品Listing分析         │ 只读    │ L1    │ 前台抓取│
│ G-03  │ 选品        │ 关键词挖掘与搜索量       │ 只读    │ L1    │ 工具API │
│ G-04  │ 选品        │ FBA利润测算             │ 计算    │ L1    │ 离线计算│
│ G-05  │ 选品        │ 供应商初筛(1688浏览)     │ 只读    │ L1    │ 仅浏览  │
│ G-06  │ 选品        │ 专利/商标风险排查        │ 只读    │ L1    │ 公开库  │
│ G-07  │ 选品        │ 季节性趋势预测           │ 分析    │ L1    │ 历史数据│
│ G-08  │ 选品        │ 差评挖掘与产品改进       │ 只读    │ L1    │ 公开Review│
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-09  │ Listing     │ 标题撰写(草稿)          │ 生成    │ L1    │ 不提交  │
│ G-10  │ Listing     │ 五行卖点撰写(草稿)       │ 生成    │ L1    │ 不提交  │
│ G-11  │ Listing     │ 产品描述/A+文案          │ 生成    │ L1    │ 不提交  │
│ G-12  │ Listing     │ Search Terms优化建议     │ 生成    │ L1    │ 不提交  │
│ G-13  │ Listing     │ 多语言翻译本地化          │ 生成    │ L1    │ 不提交  │
│ G-14  │ Listing     │ Listing质量评分监控      │ 只读    │ L1    │ 后台读取│
│ G-15  │ Listing     │ 竞品Listing变动追踪      │ 监控    │ L1    │ 定时比对│
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-16  │ 活动        │ LD/BD推荐活动查看        │ 只读    │ L1    │ 后台读取│
│ G-17  │ 活动        │ 活动利润模拟计算          │ 计算    │ L1    │ 离线    │
│ G-18  │ 活动        │ 促销效果实时数据          │ 监控    │ L1    │ 数据面板│
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-19  │ 客服        │ 买家消息自动分类          │ 分析    │ L1    │ 不回复  │
│ G-20  │ 客服        │ Review请求(官方RTV)      │ 执行    │ L1    │ 合规功能│
│ G-21  │ 客服        │ 24小时响应率监控          │ 监控    │ L1    │ 超时告警│
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-22  │ 库存        │ FBA库存水位监控           │ 监控    │ L1    │ 阈值告警│
│ G-23  │ 库存        │ 智能补货计划生成          │ 建议    │ L1    │ 仅建议  │
│ G-24  │ 库存        │ 多仓库存分布分析          │ 分析    │ L1    │ 数据分析│
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-25  │ 广告        │ 广告数据报表下载          │ 只读    │ L1    │ 导出数据│
│ G-26  │ 广告        │ 关键词表现深度分析        │ 分析    │ L1    │ 数据分析│
│ G-27  │ 广告        │ 广告异常监控告警          │ 监控    │ L1    │ 实时告警│
│ G-28  │ 广告        │ 竞品广告策略分析          │ 分析    │ L1    │ 推测分析│
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-29  │ 财务        │ 结算报告下载与解读        │ 只读    │ L1    │ 导出数据│
│ G-30  │ 财务        │ SKU级利润计算            │ 计算    │ L1    │ 数据整合│
│ G-31  │ 财务        │ 异常扣费监控             │ 监控    │ L1    │ 自动告警│
│ G-32  │ 财务        │ 汇率监控与换汇建议        │ 监控    │ L1    │ 仅建议  │
│ G-33  │ 财务        │ 税务合规日历提醒          │ 监控    │ L1    │ 仅提醒  │
│───────┼────────────┼──────────────────────┼─────────┼───────┼──────│
│ G-34  │ 合规        │ Account Health监控      │ 监控    │ L1    │ 实时告警│
│ G-35  │ 合规        │ Policy违规预警           │ 监控    │ L1    │ 实时告警│
│───────┴────────────┴──────────────────────┴─────────┴───────┴──────│
│ 这35项可以立即部署，零风险，为运营团队节省大量重复劳动                     │
└──────────────────────────────────────────────────────────────────────┘
```

#### 🟡 黄色区 — 低/中风险（28项）| 需确认机制

```
┌──────────────────────────────────────────────────────────────────────┐
│ 编号  │ 模块        │ 功能                  │ 风险点         │ 权限  │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-01  │ Listing     │ Listing提交到后台      │ 内容错误       │ L2   │
│ Y-02  │ Listing     │ 批量Flat File上传      │ 批量错误扩散    │ L2   │
│ Y-03  │ Listing     │ 变体创建/合并/拆分      │ 结构混乱       │ L2   │
│ Y-04  │ Listing     │ 多站点同步上架          │ 合规差异       │ L2   │
│ Y-05  │ Listing     │ 类目审核材料提交        │ 材料不合格     │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-06  │ 活动        │ LD/7DD秒杀报名         │ 亏损风险       │ L2   │
│ Y-07  │ 活动        │ Coupon创建             │ 预算失控       │ L2   │
│ Y-08  │ 活动        │ Prime Exclusive折扣    │ 价格设错       │ L2   │
│ Y-09  │ 活动        │ 站外折扣码创建          │ 薅羊毛风险     │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-10  │ 客服        │ 标准问题模板回复        │ 回复不当       │ L2   │
│ Y-11  │ 客服        │ 差评买家主动联系        │ 违规诱导       │ L2   │
│ Y-12  │ 客服        │ A-to-Z申诉材料         │ 申诉失败       │ L2   │
│ Y-13  │ 客服        │ 退货退款审批(≤$30)      │ 资金损失       │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-14  │ 库存        │ 创建FBA发货计划         │ 数量错误       │ L2   │
│ Y-15  │ 库存        │ 库龄清货方案执行        │ 亏损处理       │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-16  │ 广告        │ 否定关键词批量添加       │ 误否高效词     │ L2   │
│ Y-17  │ 广告        │ 关键词竞价调整(±30%)    │ 花费变化       │ L2   │
│ Y-18  │ 广告        │ 新建SP广告活动          │ 预算风险       │ L2   │
│ Y-19  │ 广告        │ 新建SB/SD广告活动       │ 预算风险       │ L2   │
│ Y-20  │ 广告        │ 日预算动态调控          │ 花费波动       │ L2   │
│ Y-21  │ 广告        │ 分时竞价策略            │ 策略失效       │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-22  │ 财务        │ FBA丢件/损件索赔        │ 证据不足       │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-23  │ 合规        │ 申诉信(POA)生成+提交    │ 申诉策略错误    │ L2   │
│ Y-24  │ 合规        │ 跟卖警告信发送          │ 误判           │ L2   │
│ Y-25  │ 合规        │ 知识产权投诉提交        │ 证据链不完整    │ L2   │
│ Y-26  │ 合规        │ 品牌备案维护            │ 信息错误       │ L2   │
│───────┼────────────┼──────────────────────┼───────────────┼──────│
│ Y-27  │ 运营        │ 价格自动调整            │ 价格战/亏损     │ L2   │
│ Y-28  │ 运营        │ 退货退款审批(>$30)      │ 较大资金损失    │ L2   │
│───────┴────────────┴──────────────────────┴───────────────┴──────│
│ 这28项需要"AI建议 → 人工确认 → 执行"的工作流                          │
└──────────────────────────────────────────────────────────────────────┘
```

#### 🔴 红色区 — 高风险（7项）| 多级审批

```
┌──────────────────────────────────────────────────────────────────────┐
│ 编号  │ 模块        │ 功能                  │ 风险说明        │ 权限  │
│───────┼────────────┼──────────────────────┼────────────────┼──────│
│ R-01  │ 供应链      │ 采购订单下达(1688)     │ 资金占用大       │ L3   │
│ R-02  │ 供应链      │ 物流头程下单           │ 费用高/不可逆    │ L3   │
│ R-03  │ 广告        │ DSP程序化广告投放      │ 预算极大        │ L3   │
│ R-04  │ 广告        │ 全自动广告闭环         │ 失控风险        │ L3   │
│ R-05  │ 客服        │ 全自动客服(含售后)      │ 客诉升级        │ L3   │
│ R-06  │ 运营        │ 多店铺批量操作         │ 关联风险        │ L3   │
│ R-07  │ 运营        │ 店铺设置修改           │ 配置错误        │ L3   │
│───────┴────────────┴──────────────────────┴────────────────┴──────│
│ 这7项需要"AI建议 → 运营确认 → 主管审批 → 执行"                         │
└──────────────────────────────────────────────────────────────────────┘
```

#### ⛔ 禁止区 — 永远人工（5项）| AI零执行权

```
┌──────────────────────────────────────────────────────────────────────┐
│ 编号  │ 模块        │ 功能                  │ 为什么禁止                │
│───────┼────────────┼──────────────────────┼──────────────────────── │
│ X-01  │ 资金        │ 收款账户操作(提现)     │ 资金安全，不可逆            │
│ X-02  │ 账号        │ 店铺注册/注销          │ 身份认证，法律责任          │
│ X-03  │ 法务        │ 品牌授权/转让签署      │ 法律文件，需本人签字        │
│ X-04  │ 税务        │ 税务申报正式提交       │ 法律责任，错误罚款巨大      │
│ X-05  │ 账号        │ 银行/支付方式变更      │ 资金安全，高诈骗目标        │
│───────┴────────────┴──────────────────────┴──────────────────────── │
│ AI仅提供信息整理和建议，所有执行必须由人类亲自完成                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 四、发展路径（四阶段演进）

```
时间轴 ──────────────────────────────────────────────────────────────▶

  Phase 1                Phase 2              Phase 3            Phase 4
  [0-3个月]              [3-6个月]            [6-12个月]         [12个月+]
  
  ┌──────────┐         ┌──────────┐        ┌──────────┐      ┌──────────┐
  │          │         │          │        │          │      │          │
  │  数据眼睛 │ ──────▶ │  操作双手 │ ─────▶ │  运营大脑 │ ───▶ │  运营公司 │
  │          │         │          │        │          │      │          │
  │ 看得懂    │         │ 做得了    │        │ 想得到    │      │ 管得住    │
  │ 说得出    │         │ 改得动    │        │ 判断准    │      │ 跑得好    │
  │          │         │          │        │          │      │          │
  └──────────┘         └──────────┘        └──────────┘      └──────────┘
  
  能力:                  能力:                能力:              能力:
  ·全域数据采集          ·Listing上传         ·采购决策+执行      ·全链路闭环
  ·智能分析报告          ·客服回复            ·广告全自动         ·多店铺矩阵
  ·选品建议             ·活动报名            ·供应链管理         ·基础运营公司
  ·文案生成             ·广告调整            ·财务分析          ·策略自迭代
  ·竞品监控             ·库存操作            ·全自动客服        
  
  风控:                  风控:                风控:              风控:
  ·零风险               ·单次确认机制         ·多级审批链        ·AI自我风控
  ·纯只读               ·操作金额阈值         ·异常自动熔断      ·全链路审计
  ·无需权限             ·可回滚保障          ·人工兜底开关      ·自适应策略
  
  人效:                  人效:                人效:              人效:
  1人管3-5店 ──▶        1人管5-10店 ──▶      1人管10-20店 ──▶   1人管20-50店
  节省40%时间           节省60%时间           节省80%时间        节省90%时间
```

### 阶段转换的前置条件

```
┌──────────────────────────────────────────────────────────────────┐
│                    阶段晋升检查清单                                │
│                                                                   │
│  Phase 1 → Phase 2 的前提:                                       │
│  ☐ 环境隔离方案已部署并验证                                       │
│  ☐ 操作日志系统100%覆盖                                           │
│  ☐ 确认+回滚工作流已测试通过                                      │
│  ☐ 金额阈值规则已配置                                             │
│  ☐ Phase 1功能稳定运行>30天无重大bug                               │
│                                                                   │
│  Phase 2 → Phase 3 的前提:                                       │
│  ☐ Phase 2功能稳定运行>90天                                       │
│  ☐ 多级审批链已部署                                               │
│  ☐ 异常熔断机制已测试通过（模拟演练>3次）                           │
│  ☐ 多店铺隔离架构已上线并通过安全审计                               │
│  ☐ 关联检测系统已部署（IP/指纹/行为/业务四维检测）                   │
│  ☐ 人工兜底一键切换已验证                                         │
│                                                                   │
│  Phase 3 → Phase 4 的前提:                                       │
│  ☐ Phase 3功能稳定运行>180天                                      │
│  ☐ AI自我风控模型训练完成                                         │
│  ☐ 全链路审计通过第三方安全评估                                    │
│  ☐ 灾难恢复演练通过                                               │
│  ☐ 法律合规审查通过                                               │
│  ☐ 保险/兜底方案已建立                                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 五、风控权限策略体系（核心重点）

### 5.1 四层权限模型

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                          权限控制模型                                  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  L1 - 只读/建议层                                          │      │
│  │  ┌──────────────────────────────────────────────────────┐ │      │
│  │  │  规则:                                                 │ │      │
│  │  │  · 只允许GET请求，禁止POST/PUT/DELETE                   │ │      │
│  │  │  · 只读取数据，不修改任何后台设置                        │ │      │
│  │  │  · 生成的内容保存在本地，不提交到平台                    │ │      │
│  │  │  · 无需任何人工审批                                     │ │      │
│  │  │  · 24/7自由运行                                        │ │      │
│  │  │                                                        │ │      │
│  │  │  触发条件: 自动                                         │ │      │
│  │  │  回滚需求: 无（不修改任何内容）                          │ │      │
│  │  └──────────────────────────────────────────────────────┘ │      │
│  └────────────────────────────────────────────────────────────┘      │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  L2 - 确认执行层                                           │      │
│  │  ┌──────────────────────────────────────────────────────┐ │      │
│  │  │  规则:                                                 │ │      │
│  │  │  · AI生成操作方案 → 推送给运营人员 → 人工确认 → 执行    │ │      │
│  │  │  · 单笔操作金额上限: $200                              │ │      │
│  │  │  · 单日累计操作金额上限: $1,000                         │ │      │
│  │  │  · 批量操作先执行1条测试，确认后再批量                   │ │      │
│  │  │  · 每次操作前截图保存当前状态（用于回滚）                │ │      │
│  │  │  · 确认超时(30分钟)自动取消                             │ │      │
│  │  │                                                        │ │      │
│  │  │  触发条件: 人工一键确认(单人)                            │ │      │
│  │  │  回滚方案: 操作前快照 + 逆向操作脚本                     │ │      │
│  │  └──────────────────────────────────────────────────────┘ │      │
│  └────────────────────────────────────────────────────────────┘      │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  L3 - 多级审批层                                           │      │
│  │  ┌──────────────────────────────────────────────────────┐ │      │
│  │  │  规则:                                                 │ │      │
│  │  │  · AI生成方案 → 运营确认 → 主管审批 → 执行              │ │      │
│  │  │  · 单笔金额上限: $5,000                                │ │      │
│  │  │  · 执行前24小时预告期（重大操作）                        │ │      │
│  │  │  · 必须有完整回滚方案才允许提交                          │ │      │
│  │  │  · 执行全程录屏                                        │ │      │
│  │  │  · 高危操作仅在工作时间执行(9:00-18:00)                 │ │      │
│  │  │                                                        │ │      │
│  │  │  触发条件: 双人审批(运营+主管)                           │ │      │
│  │  │  回滚方案: 完整状态快照 + 应急预案 + 人工备份             │ │      │
│  │  └──────────────────────────────────────────────────────┘ │      │
│  └────────────────────────────────────────────────────────────┘      │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │  L4 - 人工专属层（AI禁入）                                  │      │
│  │  ┌──────────────────────────────────────────────────────┐ │      │
│  │  │  规则:                                                 │ │      │
│  │  │  · AI绝对不执行任何操作                                 │ │      │
│  │  │  · AI仅提供信息整理、数据汇总、建议参考                  │ │      │
│  │  │  · 涉及: 资金提现/账号注册注销/法律文件/税务申报          │ │      │
│  │  │  · 代码层面硬编码阻断，不可通过配置绕过                  │ │      │
│  │  │                                                        │ │      │
│  │  │  触发条件: 仅人类手动操作                                │ │      │
│  │  │  回滚方案: 不适用                                       │ │      │
│  │  └──────────────────────────────────────────────────────┘ │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 5.2 三大核心风控引擎

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  引擎一: 🔐 店铺安全引擎 (Account Security Engine)                    │
│  ═══════════════════════════════════════════════════                  │
│                                                                      │
│  ┌─ 登录环境守卫 ───────────────────────────────────┐               │
│  │                                                    │               │
│  │  检测项             标准              异常动作       │               │
│  │  ─────────────────────────────────────────────    │               │
│  │  IP地址             固定住宅IP白名单    立即断开     │               │
│  │  设备指纹            绑定设备Hash       阻断+告警   │               │
│  │  浏览器指纹          固定Profile        阻断+告警   │               │
│  │  操作时间            工作时间段         二次验证     │               │
│  │  地理位置            固定城市/国家       立即断开     │               │
│  │  Cookie状态          有效期内           重新认证     │               │
│  │  2FA状态             必须开启           禁止操作     │               │
│  │                                                    │               │
│  │  核心原则: 宁可误断，不可漏放                        │               │
│  └────────────────────────────────────────────────────┘               │
│                                                                      │
│  引擎二: 🏪 关联防控引擎 (Association Prevention Engine)               │
│  ═══════════════════════════════════════════════════                  │
│                                                                      │
│  ┌─ 六维关联检测 ───────────────────────────────────┐               │
│  │                                                    │               │
│  │  维度           检测内容            检测频率         │               │
│  │  ─────────────────────────────────────────────    │               │
│  │  网络层          IP/IP段/DNS/出口     每次操作前     │               │
│  │  设备层          MAC/硬盘ID/CPU/GPU   启动时检测     │               │
│  │  浏览器层        Canvas/WebGL/字体    启动时检测     │               │
│  │  账户层          邮箱/信用卡/收款户    每日扫描       │               │
│  │  行为层          操作时间/习惯/轨迹    持续监控       │               │
│  │  业务层          产品/品牌/供应商重叠   每周扫描       │               │
│  │                                                    │               │
│  │  隔离架构:                                          │               │
│  │  每个店铺 = 独立VM/容器 + 独立IP + 独立浏览器         │               │
│  │  店铺之间绝对零数据交叉                               │               │
│  │  中控层仅通过加密API通信，不直接访问店铺环境           │               │
│  └────────────────────────────────────────────────────┘               │
│                                                                      │
│  引擎三: 💰 操作风控引擎 (Operation Risk Engine)                      │
│  ═══════════════════════════════════════════════════                  │
│                                                                      │
│  ┌─ 多维限制规则 ───────────────────────────────────┐               │
│  │                                                    │               │
│  │  规则类型         具体规则            触发动作       │               │
│  │  ─────────────────────────────────────────────    │               │
│  │  金额限制         单笔>$200(L2)       需确认        │               │
│  │                   单笔>$5000(L3)      需双人审批    │               │
│  │  频率限制         同类操作>10次/小时    暂停+告警     │               │
│  │  时间限制         非工作时间           禁止L2+操作   │               │
│  │  变化幅度         价格变动>20%         需确认        │               │
│  │                   竞价变动>30%         需确认        │               │
│  │  累计限制         日花费>日预算80%      暂停广告      │               │
│  │  异常检测         ACoS突增>2倍         暂停+告警     │               │
│  │  黑名单           特定操作类型         硬编码阻断    │               │
│  │                                                    │               │
│  │  熔断机制:                                          │               │
│  │  任何风控规则触发 → 所有自动操作立即暂停              │               │
│  │  人工确认安全后 → 手动恢复                           │               │
│  └────────────────────────────────────────────────────┘               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 5.3 审计与日志体系

```
┌──────────────────────────────────────────────────────────────────┐
│                    全链路审计系统                                  │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  日志分级:                                                │     │
│  │                                                           │     │
│  │  Level 1 - 操作日志 (每一次操作)                           │     │
│  │  ├── 时间戳(毫秒级)                                       │     │
│  │  ├── 操作类型(读取/写入/删除/修改)                         │     │
│  │  ├── 操作目标(哪个店铺/哪个ASIN/哪个广告活动)              │     │
│  │  ├── 操作内容(修改前值 → 修改后值)                         │     │
│  │  ├── 操作结果(成功/失败/超时)                              │     │
│  │  └── 操作发起者(AI自动/人工确认/审批通过)                  │     │
│  │                                                           │     │
│  │  Level 2 - 截图快照 (关键操作)                             │     │
│  │  ├── 操作前页面截图                                       │     │
│  │  ├── 操作后页面截图                                       │     │
│  │  └── 异常状态截图                                         │     │
│  │                                                           │     │
│  │  Level 3 - 录屏记录 (高风险操作)                           │     │
│  │  ├── L3权限操作全程录屏                                   │     │
│  │  ├── 录屏自动上传到安全存储                                │     │
│  │  └── 保留期限: 180天                                      │     │
│  │                                                           │     │
│  │  Level 4 - 安全审计 (定期)                                 │     │
│  │  ├── 每日: 自动生成操作摘要报告                            │     │
│  │  ├── 每周: 安全扫描报告(关联检测/异常检测)                 │     │
│  │  └── 每月: 完整安全审计报告(人工Review)                    │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
│  日志存储:                                                        │
│  · 本地加密存储 + 异地备份                                        │
│  · 日志不可篡改(追加写入模式)                                     │
│  · 保留周期: 操作日志1年 / 截图6个月 / 录屏6个月                   │
│  · 敏感信息脱敏处理                                               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 六、应急响应预案

```
┌──────────────────────────────────────────────────────────────────────┐
│                        五大灾难场景预案                                │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │ 场景 1: 🚨 账号被异常登录                                    │      │
│  │                                                              │      │
│  │ 检测 → [<30秒] 断开所有Session                                │      │
│  │      → [<2分钟] 修改密码+重置2FA                              │      │
│  │      → [<5分钟] 检查后台设置是否被篡改                         │      │
│  │      → [<1小时] 通知所有相关人+完整安全审计                    │      │
│  │      → [<24小时] 出具安全报告+改进措施                         │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │ 场景 2: 🚨 疑似店铺关联                                      │      │
│  │                                                              │      │
│  │ 检测 → [<5分钟] 暂停所有可疑店铺的自动操作                     │      │
│  │      → [<30分钟] 隔离环境深度排查(六维检测)                    │      │
│  │      → [<2小时] 确认关联风险等级(高/中/低)                     │      │
│  │      → [<24小时] 执行关联切割方案(换IP/换设备/迁移)            │      │
│  │      → [持续] 关联监控频率提升至每小时一次                     │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │ 场景 3: 🚨 广告费用失控                                      │      │
│  │                                                              │      │
│  │ 检测 → [<1分钟] 自动暂停异常Campaign                          │      │
│  │      → [<10分钟] 花费归因分析(哪个词/ASIN/时段)               │      │
│  │      → [<1小时] 生成异常报告+恢复建议                         │      │
│  │      → [人工确认] 决定恢复/调整/永久暂停                       │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │ 场景 4: 🚨 Listing被劫持/篡改                                │      │
│  │                                                              │      │
│  │ 检测 → [<1分钟] 截图存证(篡改前后对比)                        │      │
│  │      → [<5分钟] 通知运营+自动开Case                           │      │
│  │      → [<30分钟] 准备Brand Registry投诉材料                   │      │
│  │      → [<2小时] 提交恢复申请                                  │      │
│  │      → [持续] 该ASIN监控频率提升至每10分钟                    │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │ 场景 5: 🚨 OpenClaw系统自身故障                               │      │
│  │                                                              │      │
│  │ 检测 → [<1分钟] 所有自动操作立即冻结                          │      │
│  │      → [<5分钟] 切换到纯人工模式(一键切换)                    │      │
│  │      → [<30分钟] 系统诊断+日志排查                            │      │
│  │      → [修复后] 渐进式恢复(先L1,再L2,最后L3)                  │      │
│  │                                                              │      │
│  │  核心原则: OpenClaw挂了，业务不能停                            │      │
│  │  人工备份方案必须始终保持可用                                  │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 七、核心策略总结

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│                    OpenClaw 战略方针                                   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │                                                              │      │
│  │              "功能激进，风控保守"                              │      │
│  │                                                              │      │
│  │   功能:  尽可能快地覆盖所有运营环节                            │      │
│  │   风控:  权限开放永远慢于功能开发一个阶段                      │      │
│  │   原则:  宁可少做一步，不可多错一步                            │      │
│  │                                                              │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │                                                              │      │
│  │              "渐进放权，随时收回"                              │      │
│  │                                                              │      │
│  │   L1 → L2:  验证准确率>99%后开放                              │      │
│  │   L2 → L3:  验证准确率>99.9%且运行>90天后开放                 │      │
│  │   任何时刻:  一键回退到上一权限等级                            │      │
│  │   任何异常:  自动降级到L1(只读模式)                            │      │
│  │                                                              │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │                                                              │      │
│  │              "AI做执行，人做决策"                              │      │
│  │                                                              │      │
│  │   AI擅长:  重复性工作 / 7x24监控 / 数据分析 / 快速响应        │      │
│  │   人类擅长: 战略判断 / 创意方向 / 风险评估 / 最终决策          │      │
│  │   目标:    不是取代运营，而是让每个运营拥有10倍生产力          │      │
│  │                                                              │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐      │
│  │                                                              │      │
│  │              "店铺安全是生命线"                                │      │
│  │                                                              │      │
│  │   关联=死亡:  多店铺关联导致的批量封号是毁灭性的               │      │
│  │   隔离优先:  宁可牺牲效率，也要保证隔离                       │      │
│  │   安全投入:  风控系统的投入应占总开发资源的30%+               │      │
│  │   持续演练:  每月进行一次安全事故模拟演练                     │      │
│  │                                                              │      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  数字总结:                                                            │
│  ══════════════════════════════════════════════════                   │
│  75项功能 = 35项零风险(47%) + 28项需确认(37%)                         │
│            + 7项高风险(9%) + 5项永远人工(7%)                          │
│                                                                      │
│  近半数功能可以立即零风险部署                                          │
│  超过八成功能在6个月内可以上线                                         │
│  只有不到10%的功能需要谨慎地多级审批                                   │
│  资金操作永远保留给人类                                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

> **一句话总结：OpenClaw的未来是让AI成为每个跨境卖家的"超级运营团队"——它能看懂屏幕上的一切、能执行电脑上的一切操作、能7×24不间断工作——但它永远在人类设定的安全围栏内运行，该快的快、该慢的慢、该停的停、不该碰的绝对不碰。**