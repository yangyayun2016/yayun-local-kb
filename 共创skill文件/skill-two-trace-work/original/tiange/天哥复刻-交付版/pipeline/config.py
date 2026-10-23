"""爆款复刻流水线 · 配置中心。

两种来源，自动二选一：
- 有 `_work/storyboard.json`（扔新视频跑 auto_storyboard 生成）→ 所有片子参数从它派生。
- 没有 → 回退到内置样例（爆款视频.mp4，电影感格斗预告片，横屏 16:9），保证开箱即跑。

换新爆款时你什么都不用手改：`auto_storyboard` 生成脚手架 → agent 看帧补 prompt → 直接出片。
首帧图：Codex 内置 images 生成（默认）/ 或 `pipeline.gen_frames` 走 API 生图（headless 回退）。
"""
import os
import shutil
import sys
from pathlib import Path

from pipeline.storyboard import load as _load_sb

# === 项目路径 ===
ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "_work"
FRAMES = WORK / "frames"
GEN = WORK / "gen"
FINAL = WORK / "final"
for d in (WORK, FRAMES, GEN, FINAL):
    d.mkdir(parents=True, exist_ok=True)

_SB = _load_sb()

# token：优先环境变量，回退本地密钥文件 _work/.secret.env（含密钥，已 .gitignore，勿外传）
_SECRET = WORK / ".secret.env"


def _read_token(env_key):
    v = os.environ.get(env_key, "")
    if not v and _SECRET.exists():
        txt = _SECRET.read_text(encoding="utf-8").strip()
        for line in txt.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):   # 跳空行/注释
                continue
            if line.startswith("export "):          # 容忍 export 前缀
                line = line[len("export "):].strip()
            if line.startswith(env_key + "="):
                v = line.split("=", 1)[1].strip().strip('"').strip("'")
                break                               # 首个匹配即用，别被后面覆盖
        if not v and "=" not in txt and not txt.startswith("#"):
            v = txt                                  # 整个文件就一个裸 token 的情况
    return v


def _cfg(key, default=""):
    """配置项：先环境变量，再 _work/.secret.env，最后默认。普通人只改 .secret.env 一个文件就行。"""
    return os.environ.get(key, "") or _read_token(key) or default


def ensure_ffmpeg():
    """入口处调用：没装 ffmpeg/ffprobe 就给一句人话+安装指引，别让普通人撞 FileNotFoundError 天书。"""
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        sys.exit(
            f"❌ 没找到 {' / '.join(missing)}（拆视频/拼视频必须装它）。\n"
            f"   Windows 最简单：在 PowerShell 跑  winget install Gyan.FFmpeg  装好后『重开终端』再跑本工具。\n"
            f"   （或到 ffmpeg.org 下载、解压、把 bin 目录加进 PATH。）\n"
            f"   Mac：brew install ffmpeg   Linux：sudo apt install ffmpeg")


# ============================================================================
# 两条后端同时在线，按镜头分流：
#   有人脸（人物镜）→ APIMart（脸更稳）；无人脸（产品/场景/清单）→ 火山方舟 ARK 的 Mini 资源包（最便宜）。
# 两条路同时用各自的 key，互不影响。请求/响应格式不同，gen_video 已按 route 分支。
# ============================================================================
# 火山方舟(ARK)的一个 key 同时能调 Fast / Mini / Pro。模型 id 命名规律：都是 -260128 版（以官方文档为准）。
# Mini：用「Doubao-Seedance-2.0-mini」资源包或按量付费最省。若实测 id 不符 → _work/.secret.env 写 FK_MODEL_MINI=正确id。
ROUTES = {
    "apimart": {
        "token": _read_token("APIMART_TOKEN"),
        "gen_endpoint": "https://api.apimart.ai/v1/videos/generations",
        "task_endpoint": "https://api.apimart.ai/v1/tasks",   # 轮询 GET {task_endpoint}/{id}
        "models": {"fast": _cfg("FK_APIMART_MODEL", "doubao-seedance-2.0-fast"),
                   "mini": "doubao-seedance-2.0-mini", "pro": "doubao-seedance-2.0"},
        "verified": {"fast": True, "mini": False, "pro": False},
        "image_endpoint": "https://api.apimart.ai/v1/images/generations",
        "image_model": "z-image-turbo",   # 秒出、支持中文
    },
    "ark": {
        "token": _read_token("ARK_API_KEY"),
        "gen_endpoint": "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
        "task_endpoint": "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks",
        "models": {"mini": _cfg("FK_MODEL_MINI", "doubao-seedance-2-0-mini-260128"),
                   "fast": _cfg("FK_ARK_FAST", "doubao-seedance-2-0-fast-260128"),
                   "pro": "doubao-seedance-2-0-260128"},
        "verified": {"mini": False, "fast": True, "pro": True},   # Mini id 首次用 verify_mini 确认
        "image_endpoint": "",   # 方舟未配图像端点；首帧用宿主内置生图或临时切 APIMart
        "image_model": "",
    },
}

# 分流规则：
#   无脸镜（product/scene）→ ARK Mini 资源包（最省）。
#   有脸镜（person）→ 走 FACE_ROUTE：默认 'apimart'(脸更稳)；可设 'ark' 改用火山 Fast(同一个 key)。
#   FK_ROUTE 显式设了 → 整片强制走那条（覆盖分流）。
FACE_ROUTE = _cfg("FK_FACE_ROUTE", "apimart").lower().strip()  # 有脸镜走哪条：apimart | ark
FORCED_ROUTE = _cfg("FK_ROUTE", "").lower().strip()            # 设了就整片强制一条


def plan_for(kind, route=None, tier=None, model=None):
    """这一镜的 (route, tier, model_id)。优先级：单元显式 route/tier/model > FK_ROUTE 强制 > 按脸分流。"""
    faceless = kind in ("product", "scene")
    if route in ROUTES:
        r = route
    elif FORCED_ROUTE in ROUTES:
        r = FORCED_ROUTE
    else:
        r = "ark" if faceless else (FACE_ROUTE if FACE_ROUTE in ROUTES else "apimart")
    t = tier or ("mini" if faceless else "fast")
    models = ROUTES[r]["models"]
    mid = model or models.get(t) or models.get("fast") or next(iter(models.values()))
    return r, t, mid


# 兼容旧调用名
def route_for(kind, route=None):
    return plan_for(kind, route=route)[0]


def model_for(kind, route=None, model=None, tier=None):
    return plan_for(kind, route=route, tier=tier, model=model)[2]


def resolution_for(kind: str) -> str:
    """按镜头分辨率分档：人物镜默认 720p（480p 糊脸）、产品/场景/清单 480p（省钱）。
    想整片强制一档省钱草稿：FK_RESOLUTION=480p（覆盖全部）。
    """
    forced = _cfg("FK_RESOLUTION", "").strip()
    if forced:
        return forced
    return "720p" if kind == "person" else "480p"


# 向后兼容的全局默认（verify_mini 等显式指定 route；这里给个兜底默认路线）。
DEFAULT_ROUTE = FORCED_ROUTE if FORCED_ROUTE in ROUTES else "apimart"
ROUTE = DEFAULT_ROUTE
TOKEN=[已移除]token"]
GEN_ENDPOINT = ROUTES[DEFAULT_ROUTE]["gen_endpoint"]
TASK_ENDPOINT = ROUTES[DEFAULT_ROUTE]["task_endpoint"]
MODEL = ROUTES[DEFAULT_ROUTE]["models"]["fast"]
IMAGE_ENDPOINT = ROUTES[DEFAULT_ROUTE]["image_endpoint"]
IMAGE_MODEL = ROUTES[DEFAULT_ROUTE]["image_model"]

# ============================================================================
# 片子参数：storyboard.json 优先，回退内置样例
# ============================================================================
if _SB:
    SRC_VIDEO = ROOT / _SB["src_video"]
    GEN_SIZE = _SB.get("gen_size", "9:16")
    GEN_RESOLUTION = _SB.get("gen_resolution", "480p")   # 全局兜底；实际每镜按 kind 分档（resolution_for）
    _out = _SB.get("out", {"w": 480, "h": 854, "fps": 30})
    OUT_W, OUT_H, OUT_FPS = _out["w"], _out["h"], _out["fps"]
    FINAL_NAME = _SB.get("final_name", "复刻.mp4")
    COMPARE_NAME = _SB.get("compare_name", "上下屏对比.mp4")
    # 每镜带上 route/tier/model/resolution：无脸→ARK Mini+480p，有脸→FACE_ROUTE 的 Fast+720p；
    # 单元可显式写 "route":"ark|apimart"、"tier":"mini|fast|pro" 或 "model":"完整id" 覆盖。
    def _shot(u):
        k = u.get("kind", "person")
        r, t, m = plan_for(k, route=u.get("route"), tier=u.get("tier"), model=u.get("model"))
        return {"gid": u["gid"], "start": u["start"], "end": u["end"], "kind": k,
                "route": r, "tier": t, "model": m,
                "resolution": u.get("resolution") or resolution_for(k)}
    SHOTS = [_shot(u) for u in _SB["units"]]
else:
    # ---- 内置样例：爆款视频.mp4（电影感格斗游戏概念预告片 · 横屏 16:9）----
    SRC_VIDEO = ROOT / "爆款视频.mp4"
    GEN_SIZE = "16:9"          # 横屏必须 16:9，否则 seedance 默认 9:16 裁脸/变形
    GEN_RESOLUTION = "480p"    # 默认 480p（快+省）；要 720p 高清在 storyboard.json 改 gen_resolution
    OUT_W, OUT_H, OUT_FPS = 854, 480, 30
    FINAL_NAME = "爆款视频_复刻.mp4"
    COMPARE_NAME = "爆款视频_上下屏对比.mp4"
    # 源：1280x720/30fps/30.8s；硬切 19.80/25.63 → 切成 5 个生成单元
    SHOTS = [
        {"gid": "g1", "start": 0.00,  "end": 8.00,  "kind": "person"},
        {"gid": "g2", "start": 8.00,  "end": 14.00, "kind": "person"},
        {"gid": "g3", "start": 14.00, "end": 19.80, "kind": "person"},
        {"gid": "g4", "start": 19.80, "end": 25.63, "kind": "person"},
        {"gid": "g5", "start": 25.63, "end": 30.80, "kind": "scene"},
    ]
