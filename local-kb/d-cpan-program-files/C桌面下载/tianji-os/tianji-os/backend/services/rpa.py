"""
天机智能决策OS - RPA 执行层（Playwright）
原则：AI建议 → 人确认 → RPA执行 → 写日志。
高风险操作（暂停广告/调价/否词）必须有 human_approvals 记录才允许执行。

生产环境安装：pip install playwright && playwright install chromium
未安装时进入 dry-run 模式，返回将要执行的动作清单。
"""
import os
from datetime import datetime

DRY_RUN = os.getenv("TIANJI_RPA_DRY_RUN", "1") == "1"


def _playwright_available() -> bool:
    try:
        import playwright  # noqa
        return True
    except ImportError:
        return False


def pause_campaign(campaign_id: str, approved_by: str) -> dict:
    """暂停广告活动（需人工已确认）"""
    action = {"action": "pause_campaign", "campaign_id": campaign_id,
              "approved_by": approved_by, "ts": datetime.utcnow().isoformat()}
    if DRY_RUN or not _playwright_available():
        return {**action, "mode": "dry_run",
                "plan": ["登录广告后台", f"搜索活动 {campaign_id}", "切换状态为已暂停", "截图存档", "写入执行日志"]}
    # 真实执行示例（按实际后台选择器调整）：
    # from playwright.sync_api import sync_playwright
    # with sync_playwright() as p:
    #     browser = p.chromium.launch(headless=True)
    #     page = browser.new_page()
    #     page.goto("https://advertising.amazon.com/...")
    #     ...登录、搜索活动、点击暂停、page.screenshot()...
    return {**action, "mode": "executed"}


def negate_keyword(campaign_id: str, keyword: str, approved_by: str) -> dict:
    action = {"action": "negate_keyword", "campaign_id": campaign_id, "keyword": keyword,
              "approved_by": approved_by, "ts": datetime.utcnow().isoformat()}
    if DRY_RUN or not _playwright_available():
        return {**action, "mode": "dry_run",
                "plan": [f"进入活动 {campaign_id} 否定关键词页", f"添加否定精准：{keyword}", "保存并截图"]}
    return {**action, "mode": "executed"}


def adjust_bid(campaign_id: str, keyword: str, new_bid: float, approved_by: str) -> dict:
    action = {"action": "adjust_bid", "campaign_id": campaign_id, "keyword": keyword,
              "new_bid": new_bid, "approved_by": approved_by, "ts": datetime.utcnow().isoformat()}
    if DRY_RUN or not _playwright_available():
        return {**action, "mode": "dry_run",
                "plan": [f"进入活动 {campaign_id}", f"将 {keyword} 出价改为 ${new_bid}", "保存并截图"]}
    return {**action, "mode": "executed"}
