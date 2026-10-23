from __future__ import annotations

import copy
import json
import mimetypes
import os
import re
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOT = PROJECT_ROOT / "frontend"


def money(value: float) -> str:
    return f"${value:,.0f}"


SYSTEM_DATA = {
    "meta": {
        "name": "天机OS 广告中心",
        "subtitle": "亚马逊广告健康诊断闭环系统",
        "version": "MVP 1.0",
        "date": "2026-06-26",
        "scope": "广告看板 -> 提交诊断 -> 13步报告 -> 处理清单 -> 执行复盘",
    },
    "navigation": [
        "工作台",
        "销售中心",
        "广告中心",
        "商品中心",
        "选品中心",
        "库存货件",
        "物流中心",
        "采购中心",
        "财务中心",
        "团队管理",
        "Agent中心",
        "数据助手",
        "工具箱",
        "系统设置",
    ],
    "tabs": [
        {"id": "dashboard", "label": "看板"},
        {"id": "diagnosis", "label": "广告诊断"},
        {"id": "tasks", "label": "处理清单"},
        {"id": "report", "label": "健康诊断"},
        {"id": "keywords", "label": "关键词机会"},
        {"id": "asin", "label": "ASIN视图"},
        {"id": "blueprint", "label": "系统版图"},
    ],
    "dashboard": {
        "asOf": "昨日数据 2026-06-10，对比近7天和近30天均值",
        "summary": [
            {"name": "广告花费", "yesterday": "$2,392", "vs7": "+10.4%", "avg7": "$2,168", "vs30": "-21.8%", "avg30": "$3,052", "status": "up"},
            {"name": "TACOS", "yesterday": "12.0%", "vs7": "-2.4%", "avg7": "12.3%", "vs30": "-5.5%", "avg30": "12.7%", "status": "ok"},
            {"name": "ACOS", "yesterday": "31.6%", "vs7": "+2.6%", "avg7": "30.8%", "vs30": "+7.1%", "avg30": "29.5%", "status": "warn"},
            {"name": "广告出单", "yesterday": "46单", "vs7": "+0.9%", "avg7": "46单", "vs30": "-80.5%", "avg30": "236单", "status": "warn"},
            {"name": "预算打满", "yesterday": "0次", "vs7": "-100%", "avg7": "14.7次", "vs30": "-100%", "avg30": "28.5次", "status": "ok"},
        ],
        "stores": [
            {
                "store": "星辰大海(北美)-US",
                "spend": "$13,778",
                "sales": "$47,568",
                "acos": "29.0%",
                "tacos": "11.8%",
                "orders": 292,
                "adShare": "40.8%",
                "impressions": "32.1万",
                "clicks": "6,469",
                "ctr": "2.01%",
                "cpc": "$2.13",
                "cvr": "4.5%",
                "budgetCaps": 0,
                "health": "正常",
            }
        ],
        "alerts": [
            "ACOS 59.2% 高于盈亏平衡ACOS 21.5%，广告亏损约 $70。",
            "自然流量订单掩盖广告亏损，TACOS正常不代表广告健康。",
            "缺少搜索词报告和Campaign层级明细时，系统进入需补充数据状态。",
        ],
    },
    "diagnosis": {
        "defaultAsin": "B0XX-01",
        "store": "星辰大海(北美)-US",
        "site": "US",
        "pipeline": [
            "数据完整性校验",
            "产品基础信息",
            "评分/评论/价格/库存",
            "月度销售广告毛利",
            "盈亏平衡ACOS",
            "Campaign结构",
            "关键词表现",
            "广告位表现",
            "预算打满",
            "竞品BSR",
            "排名下滑根因",
            "立即动作",
            "ABA与外部机会词",
        ],
        "jobs": [
            {
                "id": "JOB-20260625-001",
                "asin": "B0XX-01",
                "title": "B0XX****01 广告健康诊断报告",
                "store": "星辰大海(北美)-US",
                "createdAt": "2026-06-25 16:29",
                "status": "已完成",
                "reportId": "RPT-BOXX-01",
            },
            {
                "id": "JOB-20260626-002",
                "asin": "B0GK****CG",
                "title": "广告亏损被自然流量掩盖",
                "store": "星辰大海(北美)-US",
                "createdAt": "2026-06-26 09:14",
                "status": "需补充数据",
                "reportId": "RPT-B0GK-CG",
            },
        ],
        "missingData": [
            "近14天搜索词报告：花费、点击、订单、CVR、ACOS",
            "Campaign层级报告：预算、出价、广告位、近7/30天花费",
            "广告位报告：搜索首位、详情页、其他搜索位分Campaign表现",
        ],
    },
    "report": {
        "id": "RPT-BOXX-01",
        "title": "B0XX-01 广告分析报告（完整版）",
        "asin": "B0XX-01",
        "store": "星辰大海(北美)-US",
        "generatedAt": "2026-06-25 16:29",
        "sources": "天机OS数据库、领星同步、卖家精灵、SIF MCP、Amazon ABA搜索词绩效",
        "coverage": "月度销售广告数据、Campaign操作日志、关键词层级表现、广告位拆解、关键词需求时机、流量异常诊断",
        "product": [
            ["ASIN", "B0XX-01"],
            ["品牌", "品牌A"],
            ["产品", "多SKU组合产品（约5件套）"],
            ["价格", "$25.99（含5%优惠券）"],
            ["上架时间", "2025年1月14日（满16个月）"],
            ["评分", "4.7 / 65条评论"],
            ["FBA费用", "$6.31"],
            ["Listing质量", "LQS 95/100（含A+内容+视频）"],
        ],
        "baseChecks": [
            {"name": "评分", "value": "4.7", "judge": "优秀"},
            {"name": "评论数", "value": "65条", "judge": "16个月65条，月均4条，偏低"},
            {"name": "Listing质量", "value": "LQS 95", "judge": "无短板"},
            {"name": "价格竞争力", "value": "$25.99", "judge": "涨价后销量仍提升，定价合理"},
            {"name": "库存状态", "value": "未见断货记录", "judge": "5月下滑不是断货导致"},
        ],
        "monthly": [
            ["2025-03", 77, "$1,925", "$265", "20.4%", "-", "$168", "8.7%", "$0.34"],
            ["2025-06", 133, "$3,349", "$535", "22.5%", "9.8%", "$289", "8.6%", "$0.29"],
            ["2025-07", 231, "$5,773", "$387", "20.9%", "6.8%", "$1,150", "19.9%", "$0.25"],
            ["2025-08", 226, "$5,648", "$514", "17.2%", "8.5%", "$872", "15.4%", "$0.24"],
            ["2025-09", 236, "$5,896", "$537", "15.9%", "7.9%", "$696", "11.8%", "$0.26"],
            ["2025-10", 262, "$6,604", "$456", "16.1%", "7.5%", "$1,113", "16.9%", "$0.26"],
            ["2025-11", 131, "$3,344", "$387", "23.2%", "12.8%", "$272", "8.1%", "$0.28"],
            ["2025-12", 137, "$3,425", "$429", "19.3%", "11.4%", "$212", "6.2%", "$0.30"],
            ["2026-01", 136, "$3,399", "$481", "29.8%", "15.2%", "$311", "9.2%", "$0.29"],
            ["2026-02", 153, "$3,951", "$603", "20.8%", "11.0%", "$368", "9.3%", "$0.31"],
            ["2026-03", 253, "$6,575", "$590", "25.0%", "9.8%", "$1,104", "16.8%", "$0.32"],
            ["2026-04", 192, "$4,976", "$510", "26.2%", "11.3%", "$915", "18.4%", "$0.32"],
        ],
        "campaigns": [
            ["海王-B0XX-01", "活跃", "$3", "$60", 11, "21.0%", "2025-03"],
            ["销量词低竞价-B0XX-01", "活跃", "$3", "$85", 16, "20.5%", "2025-02"],
            ["套装asin定位-B0XX-01", "活跃", "$2", "-", "-", "-", "2025-02"],
            ["第二层级-低竞价-B0XX-01", "活跃", "$2", "$74", 8, "35.4%", "2025-11"],
            ["第二层级-常规竞价-B0XX-01", "活跃", "$2", "$46", 7, "25.2%", "2026-01"],
            ["K07-重开--B0XX-01", "活跃", "-", "$2", 0, "-", "2026-01"],
            ["K07-重开-低价竞-B0XX-01", "已停用", "-", "-", "-", "-", "2025-11"],
        ],
        "keywords": [
            {"word": "K01", "volume": 86205, "spend": "$88", "orders": 10, "sales": "$260", "acos": "33.8%", "clicks": 363, "judge": "花费最高但ACOS偏高", "type": "stop"},
            {"word": "K02", "volume": 50999, "spend": "$59", "orders": 7, "sales": "$182", "acos": "32.5%", "clicks": 151, "judge": "ACOS偏高", "type": "stop"},
            {"word": "K03", "volume": 48687, "spend": "$52", "orders": 12, "sales": "$312", "acos": "16.7%", "clicks": 155, "judge": "效率最好", "type": "scale"},
            {"word": "K04", "volume": 20230, "spend": "$23", "orders": 8, "sales": "$208", "acos": "11.1%", "clicks": 77, "judge": "最高效词", "type": "scale"},
            {"word": "K05", "volume": 62146, "spend": "$13", "orders": 1, "sales": "$26", "acos": "49.6%", "clicks": 28, "judge": "亏损，需降价或否定", "type": "reduce"},
            {"word": "K06", "volume": 7386, "spend": "$7", "orders": 0, "sales": "$0", "acos": "-", "clicks": 31, "judge": "纯消耗，无转化", "type": "negative"},
            {"word": "K07", "volume": 201025, "spend": "$6", "orders": 0, "sales": "$0", "acos": "-", "clicks": 15, "judge": "大词未认真投放，需重建", "type": "layout"},
            {"word": "K09", "volume": 20230, "spend": "$6", "orders": 3, "sales": "$78", "acos": "7.3%", "clicks": 28, "judge": "小词高效", "type": "scale"},
            {"word": "K10", "volume": 18927, "spend": "$2", "orders": 1, "sales": "$26", "acos": "8.8%", "clicks": 8, "judge": "小词高效但投入极少", "type": "priority"},
        ],
        "placements": [
            ["海王", "详情页", "$127", 28, "17.1%", "优秀"],
            ["海王", "其他搜索位", "$307", 58, "20.4%", "主力，效率好"],
            ["海王", "搜索首位", "$33", 5, "25.3%", "搜索首位本身没问题"],
            ["销量词低竞价", "详情页", "$138", 32, "16.6%", "全表最高效"],
            ["销量词低竞价", "其他搜索位", "$164", 36, "16.9%", "全表最高效"],
            ["顶首页", "详情页", "$39", 8, "18.9%", "正常"],
            ["顶首页", "搜索首位", "$103", 6, "65.9%", "该Campaign搜索首位严重亏损"],
            ["K07-重开", "详情页", "$94", 8, "45.3%", "全面差"],
            ["K07-重开", "其他搜索位", "$173", 13, "51.2%", "全面差"],
        ],
        "budgetCaps": [
            ["第二层级-常规竞价", 30, "$2", "几乎每天都打满"],
            ["K07-重开", 29, "-", "几乎每天都打满"],
            ["第二层级-低竞价", 28, "$2", "几乎每天都打满"],
            ["海王", 23, "$3", "频繁打满"],
            ["销量词低竞价", 9, "$3", "偶发打满"],
        ],
        "competitors": [
            ["4月中旬", "#700~1,100", "#900~1,200", "#560~630（最强）"],
            ["4月下旬", "#1,000~1,400", "#900~1,300", "#570~970"],
            ["5月1~5日", "#1,700~2,200", "#1,200~1,800", "#926~1,556"],
            ["5月6~10日", "#1,800~3,343", "#1,800~2,853", "#1,351~1,559"],
        ],
        "timeline": [
            ["4月中旬", "$18~30/天", "6~10单/天", "正常"],
            ["4月26-30", "$15~22/天", "5~8单/天", "顶页上午已打满"],
            ["5月1日", "$0", "3单", "顶首页最后一条活动记录"],
            ["5月6日", "$0.50", "4单", "广告几乎停止"],
        ],
        "actions": [
            {"priority": "今日止损", "action": "立即停投K01和K02", "impact": "释放$147/3月浪费花费，避免词不转化继续烧钱。"},
            {"priority": "今日止损", "action": "扩大高效Campaign预算", "impact": "销量词低竞价 $3 -> $10，海王 $3 -> $8，第二层级低竞价 $2 -> $5。"},
            {"priority": "本周处理", "action": "修正顶首页搜索首位倍增", "impact": "不是停掉Campaign，而是将搜索结果顶部出价倍增降至0%。"},
            {"priority": "本周处理", "action": "加大高效词出价", "impact": "K10 -> $0.90~1.10，K04 -> $0.60，K09 -> $0.55。"},
            {"priority": "中期布局", "action": "K07大词重建和自然排名布局", "impact": "旺季峰值在7月，现在是自然排名窗口。"},
        ],
        "aba": [
            ["K07", 74733, "21%", "14%", "3单", "$6", "0转化", "旺季，峰值7月", "自然流量探出单，大词先养排名"],
            ["K01", 23872, "40%", "0%", "0单", "$88", "33.8%", "淡季（36周后）", "词不转化且已进淡季，立即停投"],
            ["K03", 13300, "7%", "22%", "1单", "$52", "16.7%", "旺季上升期", "广告效率好+BA有购买+旺季上行"],
            ["K02", 12976, "32%", "0%", "0单", "$59", "32.5%", "旺季峰值", "产品不匹配，停投"],
            ["K10", 5535, "31%", "80%", "1单", "$2", "8.8%", "旺季", "三维度最高分，最优先加投"],
        ],
        "longTail": [
            ["K14", 161, "极高", "加入精准投放，出价$0.80"],
            ["K15", 157, "极高", "加入精准投放"],
            ["K16", 184, "极高", "加入精准投放，出价$0.70"],
            ["K17", 17, "极高", "长尾词，竞争少，低价可拿量"],
            ["K18", 11, "极高", "同步测试"],
        ],
        "evidence": [f"/assets/evidence/report-step-{i:02d}.png" for i in range(1, 16)],
    },
    "tasks": [
        {
            "id": "TASK-0625-ACOS",
            "title": "ASIN-星辰大海 北美站US-2026-06-25诊断：ACOS提升",
            "asin": "B0XX-01",
            "risk": "ACOS提升",
            "level": "极高",
            "metric": "ACOS 33.0% -> 52.2%，当前7天ACOS均值55.7%",
            "summary": "近期CVR从5%跌至2.5%，广告花费未同步收紧，ACOS远超盈亏平衡ACOS 22.3%，毛利率为负。",
            "action": "补充7/30天广告活动和搜索词报告；复核前先将该ASIN广告活动日预算总额降低约50%，或暂停高ACOS活动。",
            "status": "待处理",
            "owner": "广告手",
            "due": "今日",
            "source": "处理清单 2026-06-25",
        },
        {
            "id": "TASK-0626-LOSS",
            "title": "ASIN-星辰大海 北美站US-2026-06-26诊断：广告亏损被自然流量掩盖",
            "asin": "B0GK****CG",
            "risk": "ACOS提升",
            "level": "高",
            "metric": "ACOS 59.2%，盈亏平衡21.5%，广告亏损约$70",
            "summary": "自然流量订单较多，整体TACOS可能较低，但广告ACOS远超盈亏平衡，掩盖广告亏损事实。",
            "action": "补充近14天搜索词报告与Campaign层级数据，定位低效关键词后降价或否定。",
            "status": "复核中",
            "owner": "运营主管",
            "due": "明日",
            "source": "处理清单 2026-06-26",
        },
    ],
    "rules": [
        {"name": "广告亏损", "logic": "ACOS > 盈亏平衡ACOS", "sample": "59.2% > 21.5%", "level": "高"},
        {"name": "自然流量掩盖亏损", "logic": "TACOS正常且广告ACOS超线", "sample": "整体健康但广告亏损$70", "level": "中"},
        {"name": "预算断流", "logic": "预算打满次数 >= 20天/月", "sample": "第二层级常规竞价30次", "level": "高"},
        {"name": "词不转化", "logic": "高花费 + BA购买占比为0", "sample": "K01/K02", "level": "极高"},
        {"name": "加投机会", "logic": "低ACOS + BA购买占比高 + SIF旺季", "sample": "K10", "level": "机会"},
    ],
    "blueprint": {
        "oneYear": "验证广告诊断闭环：看板、提交、报告、清单、执行、复盘，跑出可成交可续费的MVP。",
        "threeYear": "扩展到跨境电商智能体平台：广告、选品、Listing、库存、财务、客服形成模块化积木。",
        "fiveYear": "形成一站式AI OS生态：模板市场、培训、软件开发供应端、客户成功和行业IP。",
        "modules": [
            "广告诊断",
            "关键词机会",
            "ASIN视图",
            "数据导入",
            "Prompt管理",
            "处理清单",
            "规则引擎",
            "权限审计",
            "案例沉淀",
            "售前Demo生成",
        ],
    },
}


TASKS = copy.deepcopy(SYSTEM_DATA["tasks"])
JOBS = copy.deepcopy(SYSTEM_DATA["diagnosis"]["jobs"])


class TianjiAdsHandler(BaseHTTPRequestHandler):
    server_version = "TianjiAdsOS/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._handle_api_get(parsed.path)
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/diagnosis/jobs":
            self._create_job(self._read_json())
            return
        self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_PATCH(self) -> None:
        parsed = urlparse(self.path)
        match = re.fullmatch(r"/api/tasks/([^/]+)", parsed.path)
        if match:
            self._patch_task(unquote(match.group(1)), self._read_json())
            return
        self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._cors_headers()
        self.end_headers()

    def log_message(self, fmt: str, *args: object) -> None:
        print("%s - %s" % (self.address_string(), fmt % args))

    def _handle_api_get(self, path: str) -> None:
        if path == "/api/health":
            self._json({"status": "ok", "service": "tianji-amazon-ads-system"})
            return
        if path == "/api/system":
            payload = copy.deepcopy(SYSTEM_DATA)
            payload["tasks"] = TASKS
            payload["diagnosis"]["jobs"] = JOBS
            self._json(payload)
            return
        if path == "/api/ad-dashboard/summary":
            self._json(SYSTEM_DATA["dashboard"])
            return
        if path == "/api/diagnosis/jobs":
            self._json({"items": JOBS})
            return
        if path == "/api/diagnosis/reports/main":
            self._json(SYSTEM_DATA["report"])
            return
        if path == "/api/tasks":
            self._json({"items": TASKS})
            return
        if path == "/api/keywords/opportunities":
            self._json({"items": SYSTEM_DATA["report"]["keywords"], "aba": SYSTEM_DATA["report"]["aba"], "longTail": SYSTEM_DATA["report"]["longTail"]})
            return
        if path.startswith("/api/asins/") and path.endswith("/ad-view"):
            self._json({"product": SYSTEM_DATA["report"]["product"], "report": SYSTEM_DATA["report"]})
            return
        self._json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def _create_job(self, payload: dict) -> None:
        asin = str(payload.get("asin") or SYSTEM_DATA["diagnosis"]["defaultAsin"]).strip().upper()
        clean_asin = asin if asin else SYSTEM_DATA["diagnosis"]["defaultAsin"]
        status = "已完成" if clean_asin in {"B0XX-01", "BOXX-01", "B0XXX88888801"} else "需补充数据"
        job = {
            "id": f"JOB-{int(time.time())}",
            "asin": clean_asin,
            "title": f"{clean_asin} 广告健康诊断报告",
            "store": payload.get("store") or SYSTEM_DATA["diagnosis"]["store"],
            "createdAt": time.strftime("%Y-%m-%d %H:%M"),
            "status": status,
            "reportId": "RPT-BOXX-01" if status == "已完成" else f"RPT-{clean_asin}",
        }
        JOBS.insert(0, job)
        self._json({"job": job, "missingData": [] if status == "已完成" else SYSTEM_DATA["diagnosis"]["missingData"]}, HTTPStatus.CREATED)

    def _patch_task(self, task_id: str, payload: dict) -> None:
        for task in TASKS:
            if task["id"] == task_id:
                task["status"] = str(payload.get("status") or task["status"])
                if payload.get("note"):
                    task["note"] = str(payload["note"])
                self._json({"task": task})
                return
        self._json({"error": "Task not found"}, HTTPStatus.NOT_FOUND)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, requested_path: str) -> None:
        safe_path = unquote(requested_path).strip("/")
        target = FRONTEND_ROOT / (safe_path or "index.html")
        if target.is_dir():
            target = target / "index.html"
        try:
            target.resolve().relative_to(FRONTEND_ROOT.resolve())
        except ValueError:
            self._json({"error": "Forbidden"}, HTTPStatus.FORBIDDEN)
            return
        if not target.exists():
            target = FRONTEND_ROOT / "index.html"
        content = target.read_bytes()
        mime_type, _ = mimetypes.guess_type(str(target))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime_type or "application/octet-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PATCH,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def run() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer((host, port), TianjiAdsHandler)
    print(f"天机OS广告中心 running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
