"""分镜事实源（storyboard.json）的唯一读取口。

「扔视频→出片」的全自动闭环里，agent 看原片关键帧后只填这一份 _work/storyboard.json，
config.py / shots.py 全部从它派生 —— agent 不再手改 python，填错也只是数据错、不会崩语法。

storyboard.json 结构（auto_storyboard.py 先生成脚手架，agent 把 prompt 字段补满）：
{
  "src_video": "示例.mp4",
  "片型": "product" | "person",
  "gen_size": "16:9" | "9:16",          # 横屏片必须 16:9，否则 seedance 默认 9:16 裁脸
  "gen_resolution": "720p",
  "out": {"w": 1080, "h": 1920, "fps": 30},
  "final_name": "示例_复刻.mp4",
  "compare_name": "示例_上下屏对比.mp4",
  "identity": "全片复用的主体描述（同一产品 / 同一人物，锁死跨镜一致）",
  "scene":    "全片复用的场景描述",
  "style":    "首帧风格（photorealistic cinematic …）",
  "neg":      "no text, no logo, no watermark, …",
  "units": [
    {"gid":"g1","start":0.0,"end":2.1,"kind":"product",
     "frame_prompt":"…首帧文生图 prompt…","prompt":"…图生视频运镜 prompt…","overlays":["卖点角标"]},
    ...
  ]
}
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SB_PATH = ROOT / "_work" / "storyboard.json"


def validate(sb):
    """对 storyboard.json 做结构体检，用大白话中文报错——普通人手改 JSON 写歪一个值，
    要么深埋成 ffmpeg 天书、要么抛英文 traceback，这里提前拦住给人话。脚手架(含 TODO)不在此校验范围。"""
    if not isinstance(sb, dict):
        raise ValueError("storyboard.json 顶层应该是一个 {...} 对象。")
    units = sb.get("units")
    if not isinstance(units, list) or not units:
        raise ValueError("storyboard.json 里没有镜头（units 为空）。先跑 auto_storyboard 重新生成脚手架。")
    out = sb.get("out", {})
    for k in ("w", "h", "fps"):
        if k not in out:
            raise ValueError(f"storyboard.json 的 out 缺少 {k}（画幅/帧率）。别手删 out 里的字段。")
    seen = set()
    for i, u in enumerate(units, 1):
        gid = u.get("gid", f"第{i}个")
        if u.get("gid") in seen:
            raise ValueError(f"有两个镜头都叫 {gid}，gid 不能重复。")
        seen.add(u.get("gid"))
        s, e = u.get("start"), u.get("end")
        if not isinstance(s, (int, float)) or not isinstance(e, (int, float)):
            raise ValueError(f"镜头 {gid} 的 start/end 必须是数字（秒）。检查是不是写成了文字或留了 TODO。")
        if s < 0 or e <= s:
            raise ValueError(f"镜头 {gid} 的时间不对：开始 {s}s、结束 {e}s（结束必须比开始大）。")
    return sb


def load():
    """有 storyboard.json 就返回 dict，没有返回 None（→ config/shots 回退内置样例）。"""
    if not SB_PATH.exists():
        return None
    raw = SB_PATH.read_text(encoding="utf-8")
    try:
        sb = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"storyboard.json 格式坏了（第 {e.lineno} 行附近）：很可能少了逗号、引号没成对，或多了个逗号。\n"
            f"  原始报错：{e.msg}。用 VSCode 之类打开会高亮出错的位置。") from None
    return validate(sb)


def require():
    sb = load()
    if sb is None:
        raise FileNotFoundError(
            f"缺 {SB_PATH}。先跑 `python -m pipeline.auto_storyboard <视频>` 生成脚手架，"
            f"再让 agent 看关键帧把 prompt 字段补满。")
    return sb
