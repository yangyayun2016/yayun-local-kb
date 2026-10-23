"""爆款复刻流水线包。

所有 `python -m pipeline.x` 都会先导入本包 —— 在这里统一把 stdout/stderr 切到 UTF-8，
一处覆盖全部入口，避免 Windows 默认 GBK 控制台遇到中文/emoji 抛 UnicodeEncodeError 中断流水线。
"""
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass
