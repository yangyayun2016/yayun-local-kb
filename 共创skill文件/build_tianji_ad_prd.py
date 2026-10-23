from pathlib import Path
import csv
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


sys.stdout.reconfigure(encoding="utf-8")


def find_source_dir():
    desktop = Path.home() / "Desktop"
    for p in desktop.iterdir():
        if p.is_dir() and "OS" in p.name and any(p.glob("*.docx")):
            return p
    raise RuntimeError("Cannot locate Tianji OS source folder on Desktop.")


BASE = find_source_dir()
OUT_DOCX = BASE / "天机OS广告诊断闭环MVP_PRD_开发需求表.docx"
OUT_MD = BASE / "天机OS广告诊断闭环MVP_PRD_开发需求表.md"
OUT_CSV = BASE / "天机OS广告诊断闭环MVP_模块开发清单.csv"


prd = {
    "title": "天机OS广告诊断闭环MVP PRD开发需求表",
    "subtitle": "第一年验证闭环版本：广告看板 -> 提交诊断 -> 诊断报告 -> 处理清单 -> 任务执行 -> 复盘沉淀",
    "meta": [
        ["文档版本", "V1.0"],
        ["生成日期", "2026-06-26"],
        ["产品定位", "跨境电商卖家的广告、自然流量、利润联动诊断系统"],
        ["开发周期建议", "8-12周完成MVP；后续按迭代扩展"],
        ["核心约束", "第一年不做大而全平台，只验证可成交、可交付、可复用、可续费的闭环"],
        ["资料依据", "系统开发需求表、广告诊断子模块需求表、广告诊断提示、提交广告健康诊断流程、处理清单、界面截图"],
    ],
}


scope_in = [
    "广告中心首页与广告看板",
    "提交广告健康诊断",
    "诊断任务队列和状态流转",
    "ASIN广告健康诊断报告",
    "处理清单与动作采纳",
    "关键词机会分析",
    "ASIN视图下钻",
    "数据导入与字段映射",
    "广告诊断规则引擎",
    "AI报告生成与Prompt版本管理",
    "基础权限、日志、通知、阈值配置",
]

scope_out = [
    "商品中心、选品中心、采购中心、物流中心、财务中心、库存中心、客服中心的完整业务系统",
    "自动执行广告调价、自动暂停Campaign、自动改预算等高风险动作",
    "完整ERP替代能力",
    "多平台Amazon/TikTok/Walmart/Shopify全量适配",
    "第三方开发者市场、模板市场、大学生培训生态",
    "企业级私有化部署和复杂计费系统",
]

roles = [
    ["老板/经营负责人", "查看广告、流量、利润异常，判断是否投入资源和调整方向。"],
    ["运营主管", "查看ASIN健康度、诊断报告、处理清单，安排执行动作。"],
    ["广告手", "查看Campaign、关键词、广告位、预算打满和建议动作。"],
    ["数据/财务", "维护成本、利润、销售额、毛利率、退款等数据口径。"],
    ["售前/客户成功", "提交诊断、解释报告、生成案例、推动续费和下阶段模块。"],
    ["系统管理员", "配置店铺、权限、数据源、阈值、通知、Prompt版本。"],
]

modules = [
    {
        "id": "M0",
        "name": "平台壳与导航",
        "priority": "P0",
        "goal": "提供广告诊断闭环所需的基础入口、菜单、账号、店铺上下文和统一视觉框架。",
        "pages": "左侧菜单、顶部用户区、广告中心页签、帮助入口。",
        "requirements": [
            "左侧菜单包含工作台、销售中心、广告中心、商品中心、选品中心、库存货件、物流中心、采购中心、财务中心、团队管理、Agent中心、数据助手、工具箱、系统设置。",
            "MVP阶段只有广告中心相关页可进入；其他菜单显示为二期占位，不进入开发深度。",
            "广告中心二级页签包含看板、广告诊断、处理清单、健康诊断、关键词机会、ASIN视图。",
            "顶部显示当前用户、角色、退出、帮助入口。",
        ],
        "acceptance": [
            "用户登录后默认进入广告中心看板。",
            "点击广告中心页签可切换页面且保留店铺和日期筛选上下文。",
            "未开放模块不能出现空白页或报错，应显示二期规划提示。",
        ],
    },
    {
        "id": "M1",
        "name": "广告中心看板",
        "priority": "P0",
        "goal": "让老板和运营快速看到昨日广告健康、7天均值、30天均值、趋势和店铺明细。",
        "pages": "广告中心-看板。",
        "requirements": [
            "支持快捷日期：近3天、近7天、近30天、自定义日期。",
            "展示每日广告诊断单：广告花费、TACOS、ACOS、广告出单、预算打满次数。",
            "每项指标展示昨日值、vs 7天均值、7天均值、vs 30天均值、30天均值、趋势状态。",
            "店铺列表展示店铺、广告花费、广告销售额、ACOS、TACOS、广告出单、广告占比、曝光量、点击量、CTR、CPC、CVR、打满次数、健康状态。",
            "支持从店铺行下钻至ASIN视图或健康诊断。",
        ],
        "acceptance": [
            "没有数据时显示缺失原因和上传数据入口。",
            "所有指标均能追溯到对应数据源和计算公式。",
            "ACOS、TACOS、预算打满、CVR异常需要出现颜色和状态提示。",
        ],
    },
    {
        "id": "M2",
        "name": "提交广告健康诊断",
        "priority": "P0",
        "goal": "用户输入ASIN后，系统自动创建诊断任务，执行13步分析并生成报告。",
        "pages": "广告中心-广告诊断。",
        "requirements": [
            "输入字段：店铺、站点、ASIN、诊断日期、诊断周期、竞品ASIN、是否使用ABA、是否使用SIF、备注。",
            "按钮：提交分析、查看竞品、查看历史报告。",
            "提交后生成Diagnosis Job，状态包括待校验、数据校验中、分析中、报告生成中、已完成、失败、需补充数据。",
            "任务完成后在下方列表显示报告卡片：ASIN、店铺站点、生成时间、状态、查看报告、查看Prompt、重新诊断。",
            "缺少关键数据时，系统不能硬生成结论，应进入需补充数据状态，并列出缺失数据。",
        ],
        "acceptance": [
            "输入合法ASIN后能创建任务并返回任务ID。",
            "缺少广告活动或搜索词报告时，报告中必须提示无法定位低效投放，需要补充近7/14/30天数据。",
            "同一ASIN同一天重复提交需要提醒用户是否覆盖或生成新版本。",
        ],
    },
    {
        "id": "M3",
        "name": "13步广告诊断报告",
        "priority": "P0",
        "goal": "把广告、自然流量、利润、竞品、关键词机会和操作建议整合为可读、可复核、可执行的完整报告。",
        "pages": "报告弹窗/报告详情页。",
        "requirements": [
            "报告头部展示ASIN、店铺、站点、生成时间、数据来源、覆盖范围、脱敏说明。",
            "报告结构固定为13步：产品基础信息、基础面判断、月度销售广告毛利、盈亏平衡ACOS、Campaign结构、关键词表现、广告位表现、预算打满、竞品BSR、排名下滑根因、立即动作、BA搜索词绩效、外部机会词。",
            "所有结论必须引用指标、周期、阈值和来源，避免纯主观判断。",
            "报告支持完整版本、摘要版本、导出Word/PDF、复制Prompt。",
            "报告内动作建议可一键生成处理清单任务。",
        ],
        "acceptance": [
            "报告能复现样例中的关键章节和表格结构。",
            "每个异常结论至少包含原因、证据、影响、建议动作。",
            "AI生成内容必须保留规则引擎计算出的事实，不得篡改数值。",
        ],
    },
    {
        "id": "M4",
        "name": "处理清单与动作采纳",
        "priority": "P0",
        "goal": "把诊断结论转成可追踪的运营动作，支持采纳、忽略、复核和闭环复盘。",
        "pages": "广告中心-处理清单。",
        "requirements": [
            "清单字段：任务标题、ASIN、店铺站点、诊断日期、风险类型、风险等级、核心指标、建议动作、历史参考、状态、负责人、截止日期、补充说明。",
            "风险等级包括极高、高、中、低；状态包括待处理、部分采纳、全部采纳、忽略、复核中、已完成、已恢复。",
            "支持动作：全部采纳、部分采纳、忽略、查看完整Prompt、生成执行任务、添加备注。",
            "部分采纳和忽略必须填写原因。",
            "支持从清单跳转到完整报告、ASIN视图和相关数据源。",
        ],
        "acceptance": [
            "样例中的ACOS提升、广告亏损被自然流量掩盖可生成清单。",
            "极高风险默认强提醒，且可配置通知到飞书/钉钉/企业微信。",
            "任务状态变更有操作日志，可追溯操作者和时间。",
        ],
    },
    {
        "id": "M5",
        "name": "健康诊断规则引擎",
        "priority": "P0",
        "goal": "先由规则引擎计算事实和异常，再由AI生成解释和建议，保证报告稳定可复核。",
        "pages": "后台规则配置、诊断执行服务。",
        "requirements": [
            "计算ACOS、TACOS、CTR、CVR、CPC、CPA、广告订单占比、广告花费占比、广告前毛利率、广告后毛利率、盈亏平衡ACOS。",
            "识别异常：ACOS高于盈亏平衡、CVR下滑、广告花费未收紧、预算频繁打满、关键词高花费低转化、广告位亏损、Campaign全面亏损、自然流量掩盖广告亏损。",
            "支持阈值配置：ACOS超阈值、CVR下降比例、预算打满次数、无转化点击数、广告亏损金额、风险等级。",
            "规则输出标准JSON，供报告引擎和处理清单使用。",
        ],
        "acceptance": [
            "当ACOS 59.2%且盈亏平衡ACOS 21.5%时，系统能识别广告亏损高风险。",
            "当广告整体TACOS低但广告ACOS高于盈亏平衡时，系统能识别自然流量掩盖广告亏损。",
            "规则版本变更可追溯，不影响旧报告复算。",
        ],
    },
    {
        "id": "M6",
        "name": "关键词机会分析",
        "priority": "P0",
        "goal": "识别应停投、应加投、应测试、应布局自然排名的关键词机会。",
        "pages": "广告中心-关键词机会。",
        "requirements": [
            "展示搜索词、月搜索量、点击占比、购买占比、购买量、广告花费、广告ACOS、自然排名、广告排名、SIF时机、综合判断。",
            "机会类型包括：立即停投、降价/否词、加大预算、精准投放、长尾测试、自然排名布局、观察。",
            "支持三重验证：广告效率、BA购买占比、SIF季节时机。",
            "支持批量生成动作建议，但MVP不自动执行广告调整。",
        ],
        "acceptance": [
            "K01/K02类高花费且BA购买为0的词应标记为立即停投。",
            "K10类低花费、高购买占比、低ACOS的词应标记为最优先加投。",
            "支持导出关键词机会表。",
        ],
    },
    {
        "id": "M7",
        "name": "ASIN视图下钻",
        "priority": "P1",
        "goal": "围绕单个ASIN展示产品、广告、利润、关键词、竞品和日志的完整诊断上下文。",
        "pages": "广告中心-ASIN视图。",
        "requirements": [
            "展示产品基础信息：ASIN、品牌、产品、价格、上架时间、评分、评论数、FBA费用、Listing质量。",
            "展示月度销售、广告、毛利趋势表和图。",
            "展示Campaign结构、关键词表现、广告位表现、预算打满、竞品BSR、时间线。",
            "展示运营日志、广告日志、历史处理清单和报告版本。",
        ],
        "acceptance": [
            "从看板、报告、处理清单均可跳转到同一ASIN视图。",
            "ASIN视图能显示报告生成时所依赖的数据快照版本。",
            "缺少竞品数据时不影响广告诊断主流程。",
        ],
    },
    {
        "id": "M8",
        "name": "数据导入与连接器",
        "priority": "P0",
        "goal": "第一阶段先支持Excel/CSV上传和半自动映射，为后续API接入留接口。",
        "pages": "数据助手/广告中心上传入口。",
        "requirements": [
            "支持数据源：lx_ad_asin_daily、lx_profit_asin_daily、Campaign报告、搜索词报告、广告位报告、ABA搜索词绩效、SIF关键词时机、竞品BSR、产品基础信息。",
            "上传后做字段映射、格式校验、缺失值检测、重复数据检测。",
            "支持字段别名：ACoS/ACOS、TACOS、广告花费/Spend、点击/Clicks、订单/Orders、销售额/Sales。",
            "每次上传生成Data Import Batch，记录来源、文件名、上传人、时间、覆盖范围和校验结果。",
        ],
        "acceptance": [
            "字段缺失时给出明确缺失项和对应模块影响。",
            "数据上传后可被诊断任务选择使用。",
            "同一日期同一店铺同一ASIN重复导入需提示覆盖、跳过或生成新版本。",
        ],
    },
    {
        "id": "M9",
        "name": "AI报告生成与Prompt管理",
        "priority": "P0",
        "goal": "把结构化数据和规则结论转换成专业、可解释、可复核的中文诊断报告。",
        "pages": "报告生成服务、Prompt版本后台。",
        "requirements": [
            "Prompt输入必须是结构化JSON，包括产品信息、指标、异常、证据、候选动作。",
            "Prompt输出固定章节，不允许随意增删核心章节。",
            "报告需要生成摘要、完整报告、处理清单摘要和可复制Prompt。",
            "保留Prompt版本、模型版本、输入数据快照、输出报告版本。",
            "AI不得直接调用广告执行API；所有高风险动作只生成建议。",
        ],
        "acceptance": [
            "同一输入在同一Prompt版本下生成结构稳定的报告。",
            "报告中数值与规则引擎输出一致。",
            "用户可查看完整Prompt和生成依据。",
        ],
    },
    {
        "id": "M10",
        "name": "权限、通知与审计",
        "priority": "P1",
        "goal": "保证广告诊断、数据、报告和任务在企业团队内可控、可追溯。",
        "pages": "系统设置、团队管理、通知设置。",
        "requirements": [
            "角色：管理员、老板、运营主管、广告手、数据/财务、只读访客。",
            "权限控制到店铺、ASIN、报告、数据导入、处理清单、规则配置。",
            "通知渠道预留邮箱、飞书、钉钉、企业微信。",
            "审计内容：登录、上传、诊断提交、报告查看、状态变更、规则变更、导出。",
        ],
        "acceptance": [
            "广告手不能修改系统阈值和删除数据。",
            "所有处理清单状态变化均有审计记录。",
            "高风险任务可以通知指定负责人。",
        ],
    },
]

formula_rows = [
    ["ACOS", "广告花费 / 广告销售额", "广告销售额为0时显示'-'并进入无转化消耗判断"],
    ["TACOS", "广告花费 / 总销售额", "用于判断广告对整体销售的压力"],
    ["CTR", "点击量 / 曝光量", "评估广告素材和坑位吸引力"],
    ["CVR", "广告订单 / 点击量", "评估流量转化质量"],
    ["CPC", "广告花费 / 点击量", "评估点击成本"],
    ["CPA", "广告花费 / 广告订单", "评估单个广告订单获取成本"],
    ["广告后毛利率", "gross_profit / 总销售额", "gross_profit已扣除广告费时使用"],
    ["盈亏平衡ACOS", "(gross_profit + 广告费) / 总销售额", "广告前毛利率，用于判断广告是否赚钱"],
    ["广告亏损额", "max(0, 广告花费 - 广告销售额 * 盈亏平衡ACOS)", "用于风险金额展示"],
    ["预算打满次数", "周期内预算消耗达到日预算上限的天数", "用于识别预算不足导致断流"],
]

data_sources = [
    ["产品基础信息", "ASIN、品牌、产品、价格、上架时间、评分、评论数、FBA费用、Listing质量", "产品资料、卖家后台、第三方工具"],
    ["ASIN日广告数据", "日期、ASIN、花费、销售额、订单、曝光、点击、ACOS、TACOS、CPC、CTR、CVR", "lx_ad_asin_daily或上传表"],
    ["ASIN利润数据", "日期、ASIN、gross_profit、成本、佣金、FBA费、仓储费、广告费、毛利率", "lx_profit_asin_daily或利润表"],
    ["Campaign报告", "Campaign、状态、日预算、花费、订单、ACOS、上线时间、广告类型", "Amazon Ads/领星导出"],
    ["搜索词报告", "搜索词、关键词、匹配方式、花费、点击、订单、销售额、ACOS、CVR", "Amazon Ads搜索词报告"],
    ["广告位报告", "Campaign、广告位、花费、订单、ACOS、点击、CVR", "Placement报告"],
    ["ABA搜索词绩效", "搜索词、月搜索量、点击占比、购买占比、购买量", "Amazon BA Query Performance"],
    ["SIF关键词时机", "关键词、季节趋势、峰值月份、当前时机", "SIF MCP/手工导入"],
    ["竞品BSR", "竞品ASIN、时间段、BSR范围、变化幅度", "卖家精灵/Keepa/SIF/手工导入"],
    ["运营日志", "日期、事件、责任人、动作、备注", "系统内录入或项目跟进表"],
]

api_rows = [
    ["POST", "/api/diagnosis/jobs", "创建广告健康诊断任务"],
    ["GET", "/api/diagnosis/jobs/{id}", "查询诊断任务状态"],
    ["GET", "/api/diagnosis/reports/{id}", "获取诊断报告详情"],
    ["POST", "/api/diagnosis/reports/{id}/tasks", "从报告生成处理清单"],
    ["GET", "/api/ad-dashboard/summary", "获取广告看板KPI"],
    ["GET", "/api/ad-dashboard/stores", "获取店铺广告明细"],
    ["GET", "/api/asins/{asin}/ad-view", "获取ASIN视图数据"],
    ["GET", "/api/keywords/opportunities", "获取关键词机会列表"],
    ["POST", "/api/data-imports", "上传并校验数据文件"],
    ["GET", "/api/data-imports/{id}/validation", "获取导入校验结果"],
    ["GET", "/api/tasks", "获取处理清单"],
    ["PATCH", "/api/tasks/{id}", "更新处理清单状态"],
    ["GET", "/api/rules", "获取诊断规则配置"],
    ["PATCH", "/api/rules/{id}", "更新诊断规则阈值"],
]

roadmap = [
    ["第1-2周", "基础壳、广告中心导航、数据模型、上传校验、看板静态版", "跑通页面和数据结构"],
    ["第3-4周", "看板动态数据、提交诊断、任务状态、规则引擎第一版", "可提交ASIN并完成基础诊断"],
    ["第5-6周", "13步报告、处理清单、关键词机会、Prompt版本管理", "可生成样例级完整报告"],
    ["第7-8周", "ASIN视图、通知、权限、审计、导出", "形成端到端MVP"],
    ["第9-12周", "标杆客户数据适配、规则调优、报告质量优化、上线验收", "可进入真实客户试点"],
]

dev_items = []
for m in modules:
    dev_items.append({
        "模块ID": m["id"],
        "模块名称": m["name"],
        "优先级": m["priority"],
        "开发事项": m["goal"],
        "主要页面/服务": m["pages"],
        "核心需求": "；".join(m["requirements"]),
        "验收标准": "；".join(m["acceptance"]),
        "建议阶段": "MVP 8周" if m["priority"] == "P0" else "MVP增强/第9-12周",
    })


def md_table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(x).replace("\n", "<br>") for x in row) + " |")
    return "\n".join(lines)


def build_markdown():
    lines = []
    lines.append(f"# {prd['title']}")
    lines.append("")
    lines.append(prd["subtitle"])
    lines.append("")
    lines.append("## 1. 文档信息")
    lines.append(md_table(["字段", "内容"], prd["meta"]))
    lines.append("")
    lines.append("## 2. MVP边界")
    lines.append("### 2.1 MVP包含")
    lines.extend([f"- {x}" for x in scope_in])
    lines.append("")
    lines.append("### 2.2 第一年暂不做")
    lines.extend([f"- {x}" for x in scope_out])
    lines.append("")
    lines.append("## 3. 用户角色")
    lines.append(md_table(["角色", "核心使用目标"], roles))
    lines.append("")
    lines.append("## 4. 端到端闭环流程")
    lines.append("1. 用户进入广告中心看板，选择店铺和日期。")
    lines.append("2. 用户输入ASIN提交广告健康诊断。")
    lines.append("3. 系统校验数据完整性，缺失数据则提示补充。")
    lines.append("4. 规则引擎计算广告、流量、利润、关键词、竞品异常。")
    lines.append("5. AI报告引擎按固定13步生成诊断报告。")
    lines.append("6. 用户查看报告，并将建议动作转为处理清单。")
    lines.append("7. 负责人采纳、部分采纳或忽略动作，并填写备注。")
    lines.append("8. 系统跟踪状态、记录审计日志，并形成复盘案例。")
    lines.append("")
    lines.append("## 5. 模块级PRD")
    for m in modules:
        lines.append(f"### {m['id']} {m['name']} ({m['priority']})")
        lines.append(f"**目标：** {m['goal']}")
        lines.append(f"**页面/服务：** {m['pages']}")
        lines.append("**核心需求：**")
        lines.extend([f"- {x}" for x in m["requirements"]])
        lines.append("**验收标准：**")
        lines.extend([f"- {x}" for x in m["acceptance"]])
        lines.append("")
    lines.append("## 6. 13步诊断报告结构")
    steps = [
        "产品基础信息",
        "基础面判断：评分、评论、价格、库存、Listing质量",
        "月度销售、广告、毛利综合表现",
        "盈亏平衡ACOS和广告亏损判断",
        "Campaign结构概览",
        "关键词层级表现",
        "广告位表现",
        "预算打满和断流情况",
        "竞品BSR横向对比",
        "排名下滑根因诊断和时间线",
        "可立即执行的动作",
        "ABA搜索词绩效报告分析",
        "外部视角机会词和中期布局",
    ]
    lines.extend([f"{i}. {x}" for i, x in enumerate(steps, 1)])
    lines.append("")
    lines.append("## 7. 核心指标公式")
    lines.append(md_table(["指标", "公式", "说明"], formula_rows))
    lines.append("")
    lines.append("## 8. 数据源与字段")
    lines.append(md_table(["数据源", "核心字段", "来源"], data_sources))
    lines.append("")
    lines.append("## 9. API接口建议")
    lines.append(md_table(["方法", "路径", "用途"], api_rows))
    lines.append("")
    lines.append("## 10. 迭代排期")
    lines.append(md_table(["周期", "开发内容", "验收目标"], roadmap))
    lines.append("")
    lines.append("## 11. 关键验收口径")
    acceptance = [
        "能用Excel/CSV数据完成至少1个ASIN的完整诊断。",
        "报告能覆盖样例中的月度毛利、Campaign、关键词、广告位、预算打满、竞品BSR、根因链路、动作建议。",
        "处理清单能从报告一键生成，并支持状态流转和备注。",
        "AI报告中的数值必须与规则引擎事实一致。",
        "MVP不自动执行广告调整，只输出人工确认后的动作建议。",
        "所有数据导入、报告生成、任务状态变化均有日志。",
    ]
    lines.extend([f"- {x}" for x in acceptance])
    lines.append("")
    lines.append("## 12. 技术实现建议")
    lines.append("- 前端：React/Vue均可，重点是表格、筛选、报告弹窗、任务流和导出体验。")
    lines.append("- 后端：建议按诊断任务、报告、数据导入、规则、任务清单拆服务边界。")
    lines.append("- 数据库：先按结构化业务表建模，避免只存Prompt文本。")
    lines.append("- AI：规则引擎先算事实，LLM只做解释、总结、建议生成和报告排版。")
    lines.append("- 安全：MVP即纳入权限、日志、数据版本和导出控制。")
    return "\n".join(lines)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_text(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    run.bold = bold
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(8.5)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        set_cell_text(hdr[i], h, bold=True)
        set_cell_shading(hdr[i], "E8EEF5")
        if widths:
            hdr[i].width = Inches(widths[i])
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            set_cell_text(cells[i], val)
            if widths:
                cells[i].width = Inches(widths[i])
    doc.add_paragraph("")
    return table


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.add_run(item)


def style_document(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.2

    for name, size, color in [
        ("Heading 1", 16, "2E74B5"),
        ("Heading 2", 13, "2E74B5"),
        ("Heading 3", 11.5, "1F4D78"),
    ]:
        st = styles[name]
        st.font.name = "Microsoft YaHei"
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        st.font.size = Pt(size)
        st.font.color.rgb = RGBColor.from_string(color)
        st.font.bold = True
        st.paragraph_format.space_before = Pt(10)
        st.paragraph_format.space_after = Pt(5)


def add_title(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(prd["title"])
    run.bold = True
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor.from_string("0B2545")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(prd["subtitle"])
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor.from_string("555555")
    doc.add_paragraph("")


def build_docx():
    doc = Document()
    style_document(doc)
    add_title(doc)

    doc.add_heading("1. 文档信息", level=1)
    add_table(doc, ["字段", "内容"], prd["meta"], widths=[1.4, 5.7])

    doc.add_heading("2. 第一年度MVP边界", level=1)
    doc.add_heading("2.1 MVP包含", level=2)
    add_bullets(doc, scope_in)
    doc.add_heading("2.2 第一年暂不做", level=2)
    add_bullets(doc, scope_out)

    doc.add_heading("3. 用户角色", level=1)
    add_table(doc, ["角色", "核心使用目标"], roles, widths=[1.7, 5.4])

    doc.add_heading("4. 端到端闭环流程", level=1)
    add_numbered(doc, [
        "用户进入广告中心看板，选择店铺和日期。",
        "用户输入ASIN提交广告健康诊断。",
        "系统校验数据完整性，缺失数据则提示补充。",
        "规则引擎计算广告、流量、利润、关键词、竞品异常。",
        "AI报告引擎按固定13步生成诊断报告。",
        "用户查看报告，并将建议动作转为处理清单。",
        "负责人采纳、部分采纳或忽略动作，并填写备注。",
        "系统跟踪状态、记录审计日志，并形成复盘案例。",
    ])

    doc.add_heading("5. 模块级PRD", level=1)
    for m in modules:
        doc.add_heading(f"{m['id']} {m['name']} ({m['priority']})", level=2)
        doc.add_paragraph(f"目标：{m['goal']}")
        doc.add_paragraph(f"页面/服务：{m['pages']}")
        doc.add_heading("核心需求", level=3)
        add_bullets(doc, m["requirements"])
        doc.add_heading("验收标准", level=3)
        add_bullets(doc, m["acceptance"])

    doc.add_heading("6. 13步诊断报告结构", level=1)
    add_numbered(doc, [
        "产品基础信息。",
        "基础面判断：评分、评论、价格、库存、Listing质量。",
        "月度销售、广告、毛利综合表现。",
        "盈亏平衡ACOS和广告亏损判断。",
        "Campaign结构概览。",
        "关键词层级表现。",
        "广告位表现。",
        "预算打满和断流情况。",
        "竞品BSR横向对比。",
        "排名下滑根因诊断和时间线。",
        "可立即执行的动作。",
        "ABA搜索词绩效报告分析。",
        "外部视角机会词和中期布局。",
    ])

    doc.add_heading("7. 核心指标公式", level=1)
    add_table(doc, ["指标", "公式", "说明"], formula_rows, widths=[1.4, 2.4, 3.3])

    doc.add_heading("8. 数据源与字段", level=1)
    add_table(doc, ["数据源", "核心字段", "来源"], data_sources, widths=[1.4, 4.2, 1.5])

    doc.add_heading("9. API接口建议", level=1)
    add_table(doc, ["方法", "路径", "用途"], api_rows, widths=[0.8, 3.0, 3.3])

    doc.add_heading("10. 迭代排期", level=1)
    add_table(doc, ["周期", "开发内容", "验收目标"], roadmap, widths=[1.0, 3.5, 2.6])

    doc.add_heading("11. 关键验收口径", level=1)
    add_bullets(doc, [
        "能用Excel/CSV数据完成至少1个ASIN的完整诊断。",
        "报告能覆盖样例中的月度毛利、Campaign、关键词、广告位、预算打满、竞品BSR、根因链路、动作建议。",
        "处理清单能从报告一键生成，并支持状态流转和备注。",
        "AI报告中的数值必须与规则引擎事实一致。",
        "MVP不自动执行广告调整，只输出人工确认后的动作建议。",
        "所有数据导入、报告生成、任务状态变化均有日志。",
    ])

    doc.add_heading("12. 技术实现建议", level=1)
    add_bullets(doc, [
        "前端：React/Vue均可，重点是表格、筛选、报告弹窗、任务流和导出体验。",
        "后端：建议按诊断任务、报告、数据导入、规则、任务清单拆服务边界。",
        "数据库：先按结构化业务表建模，避免只存Prompt文本。",
        "AI：规则引擎先算事实，LLM只做解释、总结、建议生成和报告排版。",
        "安全：MVP即纳入权限、日志、数据版本和导出控制。",
    ])

    doc.add_heading("13. 源文件验证结论", level=1)
    add_bullets(doc, [
        "主系统需求表覆盖了完整跨境电商OS，但第一年不应全部开发，应收敛到广告中心闭环。",
        "广告诊断子模块需求表已经明确广告中心页签、搜索词报告字段、ASIN日常数据、利润数据、广告与自然流量关系、止损和增益逻辑。",
        "提交广告健康诊断文本和截图提供了报告结构、弹窗样式、表格形态和处理动作。",
        "处理清单文本验证了高风险任务、人工复核、数据缺失提示、采纳/忽略/查看Prompt等动作必须进入MVP。",
        "截图验证了广告中心导航、看板KPI、报告弹窗、报告章节、风险高亮、可执行动作和关键词机会表的页面形态。",
    ])

    doc.save(OUT_DOCX)


def build_csv():
    with OUT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(dev_items[0].keys()))
        writer.writeheader()
        writer.writerows(dev_items)


def main():
    OUT_MD.write_text(build_markdown(), encoding="utf-8")
    build_csv()
    build_docx()
    print("DOCX", OUT_DOCX)
    print("MD", OUT_MD)
    print("CSV", OUT_CSV)


if __name__ == "__main__":
    main()
