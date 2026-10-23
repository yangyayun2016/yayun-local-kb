"""
天机智能决策OS - MCP 客户端
对接：卖家精灵MCP / SIF MCP / Sorftime（Streamable HTTP 协议）

配置环境变量后即可调用真实工具：
  TIANJI_MCP_SELLERSPRITE_URL / TIANJI_MCP_SELLERSPRITE_TOKEN
  TIANJI_MCP_SIF_URL          / TIANJI_MCP_SIF_TOKEN
  TIANJI_MCP_SORFTIME_URL     / TIANJI_MCP_SORFTIME_TOKEN
未配置时返回演示数据，保证系统可跑通。
"""
import os
import json
import itertools
import httpx

_id = itertools.count(1)

SERVERS = {
    "sellersprite": {
        "url": os.getenv("TIANJI_MCP_SELLERSPRITE_URL", "https://mcp.sellersprite.com/mcp"),
        "token": os.getenv("TIANJI_MCP_SELLERSPRITE_TOKEN", ""),
    },
    "sif": {
        "url": os.getenv("TIANJI_MCP_SIF_URL", "https://mcp.sif.com/mcp"),
        "token": os.getenv("TIANJI_MCP_SIF_TOKEN", ""),
    },
    "sorftime": {
        "url": os.getenv("TIANJI_MCP_SORFTIME_URL", "https://mcp.sorftime.com"),
        "token": os.getenv("TIANJI_MCP_SORFTIME_TOKEN", ""),
    },
}


class MCPClient:
    """极简 MCP Streamable HTTP 客户端：initialize → tools/list → tools/call"""

    def __init__(self, server: str):
        cfg = SERVERS[server]
        self.url = cfg["url"]
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if cfg["token"]:
            self.headers["Authorization"] = f"Bearer {cfg['token']}"
        self.session_id = None

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        payload = {"jsonrpc": "2.0", "id": next(_id), "method": method}
        if params is not None:
            payload["params"] = params
        headers = dict(self.headers)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        with httpx.Client(timeout=60) as c:
            r = c.post(self.url, json=payload, headers=headers)
            r.raise_for_status()
            if sid := r.headers.get("Mcp-Session-Id"):
                self.session_id = sid
            text = r.text
            # 兼容 SSE 响应
            if text.startswith("event:") or "\ndata:" in text or text.startswith("data:"):
                for line in text.splitlines():
                    if line.startswith("data:"):
                        return json.loads(line[5:].strip())
            return r.json()

    def initialize(self):
        return self._rpc("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "tianji-os", "version": "1.0.0"},
        })

    def list_tools(self) -> list:
        res = self._rpc("tools/list", {})
        return res.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> dict:
        res = self._rpc("tools/call", {"name": name, "arguments": arguments})
        return res.get("result", res)


# ------- 业务封装（带降级演示数据） -------

def keyword_research(keyword: str, marketplace: str = "US") -> dict:
    """关键词市场分析：优先卖家精灵 keyword_research，失败时返回演示数据"""
    try:
        c = MCPClient("sellersprite")
        c.initialize()
        return c.call_tool("keyword_research", {"keyword": keyword, "marketplace": marketplace})
    except Exception as e:
        return {"_demo": True, "_error": str(e), "keyword": keyword,
                "search_volume": 48200, "purchase_rate": 4.2, "cpc": 1.18,
                "top3_click_share": 38.5, "conclusion": "需求稳定、竞争中等，可进入观察池"}


def asin_traffic_keywords(asin: str) -> dict:
    """ASIN 反查关键词：优先 SIF / 卖家精灵 traffic_keyword"""
    try:
        c = MCPClient("sellersprite")
        c.initialize()
        return c.call_tool("traffic_keyword", {"asin": asin, "marketplace": "US"})
    except Exception as e:
        return {"_demo": True, "_error": str(e), "asin": asin,
                "keywords": [{"kw": "led strip lights", "rank": 6, "share": 18.2},
                             {"kw": "smart led lights", "rank": 14, "share": 9.1}]}


def competitor_snapshot(asin: str) -> dict:
    """竞品快照：价格 / Review / BSR / Coupon"""
    try:
        c = MCPClient("sellersprite")
        c.initialize()
        return c.call_tool("asin_detail_with_coupon_trend", {"asin": asin, "marketplace": "US"})
    except Exception as e:
        return {"_demo": True, "_error": str(e), "asin": asin, "price": 22.99,
                "review_count": 1286, "review_7d_delta": 86, "bsr": 1240,
                "coupon": "20%", "judgement": "疑似进入放量阶段"}
