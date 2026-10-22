"""
权重加载器 —— 供 pqs_scorer.py / scs_scorer.py 读取回归校准后的权重
================================================
若同目录存在 calibrated_weights.json（由 calibrate_weights.py 生成），
则对应模块会自动使用校准后的权重；文件不存在或某个key缺失时，
自动回退到模块内写死的默认值 —— 不会因为没跑过校准就报错或行为改变。

注意：CDQ的顶层权重（30/25/5/15/5/20/0-20）是Amazon官方公开的精确值，
不适合用回归校准覆盖，因此 cdq_scorer.py 不接入本加载器。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CALIBRATED_WEIGHTS_PATH = Path(__file__).parent / "calibrated_weights.json"


def _load_all() -> dict:
    if CALIBRATED_WEIGHTS_PATH.exists():
        try:
            with open(CALIBRATED_WEIGHTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


_CALIBRATED = _load_all()


def load_group(key: str, default: Any) -> Any:
    """
    按点分路径（如 'pqs.sub_weights.listing_quality'）读取校准权重。
    找不到对应节点、或校准文件不存在时，原样返回 default，不做任何修改。
    """
    node: Any = _CALIBRATED
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return default
    return node


def is_calibrated(key: str) -> bool:
    """判断某个权重组是否已被校准覆盖（用于报告中标注数据来源）。"""
    node: Any = _CALIBRATED
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return False
    return True
