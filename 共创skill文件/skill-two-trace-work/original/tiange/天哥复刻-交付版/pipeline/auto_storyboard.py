"""①+②+③ 自动拆解：扔一条爆款视频，自动拆骨架 + 合并生成单元 + 抽关键帧 + 出分镜脚手架。

这是「扔视频→出片」全自动闭环的入口。脚本做掉所有确定性的活：
  - ffmpeg 场景检测拿硬切点 / 时长 / fps / 画幅
  - 把碎切按时长合并成 4–7 个生成单元（GU）—— 省钱且对齐 seedance 出片粒度
  - 每个 GU 抽 1 张中点关键帧 → _work/storyboard/<gid>.jpg（给 agent 看）
  - 写出脚手架 _work/storyboard.json（时长/画幅/GU 已填好，prompt 字段留空）

剩下唯一需要「看」的活——判断片型、写每镜 prompt——交给宿主 agent 的视觉能力：
agent 看 _work/storyboard/*.jpg，把 storyboard.json 的 identity/scene/style/neg + 各 unit 的
frame_prompt/prompt 补满。补满即可直接 gen_frames → gen_video → assemble，无需人工。

用法：python -m pipeline.auto_storyboard [视频路径]   (默认 config.SRC_VIDEO 或拖进目录的视频)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")   # Windows GBK 控制台兜底，避免非 ASCII 崩
except Exception:
    pass

from pipeline.analyze import probe, scene_cuts
from pipeline.storyboard import SB_PATH

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "_work"
SB_DIR = WORK / "storyboard"

# 生成单元(GU)合并参数。可用环境变量覆盖：
#   越少越省钱越快，但换装类视频「一套衣服 = 一个 GU」，砍太狠会丢掉换装次数。
#   换装/快切爆款想多留几套：FK_MAX_GU=10 python -m pipeline.auto_storyboard <视频>
MIN_GU = float(os.environ.get("FK_MIN_GU", "1.2"))    # 单个生成单元最短秒数（短于此并入邻居）
MAX_GU = int(os.environ.get("FK_MAX_GU", "7"))         # 生成单元数量上限
MIN_GU_COUNT = int(os.environ.get("FK_MIN_GU_COUNT", "4"))


# 软切兜底时每个单元目标秒数。默认 3.5 而非 2.6：API 最短按 4s 计费，单元太短(如2.6s)生成 4s 再裁掉
# 近 40% 是白烧的钱+墙钟。3.5 更贴近 4s 下限、少浪费。但换装类「一套衣服=一个单元」想多留几套，
# 把它调小：FK_TARGET_GU_SEC=2.2 python -m pipeline.auto_storyboard <视频>（配合 FK_MAX_GU 调大）。
TARGET_GU_SEC = float(os.environ.get("FK_TARGET_GU_SEC", "3.5"))


def _uniform_shots(duration, seconds_each=TARGET_GU_SEC):
    """按时间均匀切片（软切兜底）。"""
    n = max(MIN_GU_COUNT, min(MAX_GU, round(duration / seconds_each)))
    step = duration / n
    return [{"start": round(i * step, 3), "end": round((i + 1) * step, 3)} for i in range(n)]


def _raw_shots(video):
    meta = probe(video)
    cuts = scene_cuts(video)
    dur = meta["duration"]
    # 软切兜底：换装/转场类爆款常用「转身/旋转」做无缝转场，没有硬切点，
    # ffmpeg 场景检测会几乎找不到切点 → 整片塌成 1 个单元，看不出多次换装。
    # 这时按时间均匀切，给 agent 多个窗口去看（每镜 3 帧），由 agent 看帧定真正的换装点。
    soft = len(cuts) < MIN_GU_COUNT - 1 and dur > MIN_GU_COUNT * MIN_GU
    if soft:
        shots = _uniform_shots(dur)
        return meta, shots, True
    bounds = [0.0] + cuts + [dur]
    shots = [{"start": round(bounds[i], 3), "end": round(bounds[i + 1], 3)}
             for i in range(len(bounds) - 1)]
    return meta, shots, False


def _merge(shots):
    """把碎切合并成 4–7 个生成单元：反复把最短的片段并进较短的邻居，直到达标。"""
    s = [dict(x) for x in shots]
    while len(s) > MAX_GU or (len(s) > MIN_GU_COUNT and
                              min(x["end"] - x["start"] for x in s) < MIN_GU):
        # 找最短片段
        i = min(range(len(s)), key=lambda k: s[k]["end"] - s[k]["start"])
        # 并进较短的那个邻居
        if i == 0:
            j = 1
        elif i == len(s) - 1:
            j = len(s) - 2
        else:
            left = s[i - 1]["end"] - s[i - 1]["start"]
            right = s[i + 1]["end"] - s[i + 1]["start"]
            j = i - 1 if left <= right else i + 1
        lo, hi = min(i, j), max(i, j)
        s[lo] = {"start": s[lo]["start"], "end": s[hi]["end"]}
        del s[hi]
    return s


def _grab_frame(video, t, out_path):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(video),
         "-frames:v", "1", "-q:v", "3", str(out_path)],
        check=True, capture_output=True)
    return out_path


def _grab_triptych(video, start, end, gid):
    """每个生成单元抽「首/中/尾」3 帧 —— 这样 agent 才能『看见运动』。
    只看中点 1 帧会把转身/换装/转场误判成静态站姿（这是上一版复刻丢爆点的根因）。
    """
    dur = end - start
    pad = min(0.15, dur * 0.1)          # 躲开硬切的黑场/糊帧
    times = {
        "a": start + pad,               # 首：动作起手
        "b": (start + end) / 2,         # 中：动作过程
        "c": end - pad,                 # 尾：动作落点（转身后/换装后）
    }
    paths = []
    for tag, t in times.items():
        p = SB_DIR / f"{gid}_{tag}.jpg"
        _grab_frame(video, max(0.0, t), p)
        paths.append(f"_work/storyboard/{gid}_{tag}.jpg")
    return paths


def main():
    from pipeline.config import ensure_ffmpeg
    ensure_ffmpeg()   # 没装 ffmpeg/ffprobe 就先给人话+安装指引（普通人最大隐藏门槛）
    if len(sys.argv) > 1:
        video = Path(sys.argv[1])
    else:
        from pipeline.config import SRC_VIDEO
        video = SRC_VIDEO
    if not video.exists():
        sys.exit(f"找不到视频：{video}")

    meta, raw, soft = _raw_shots(video)
    units = raw if soft else _merge(raw)   # 软切兜底已是均匀片，不再合并
    SB_DIR.mkdir(parents=True, exist_ok=True)

    portrait = meta["height"] >= meta["width"]
    gen_size = "9:16" if portrait else "16:9"
    # fps 不抄源片、clamp 到 ≤30：把 24fps 素材假升 60fps 只增体积不增流畅，还暗示了素材没有的丝滑。
    fps = min(int(round(meta["fps"])), 30)
    # 默认 480p（快+省）：竖屏 480x854 / 横屏 854x480。要高清就把 gen_resolution 改 720p、out 改 1080/1280。
    out = ({"w": 480, "h": 854, "fps": fps} if portrait
           else {"w": 854, "h": 480, "fps": fps})

    sb_units = []
    for k, u in enumerate(units, 1):
        gid = f"g{k}"
        # 抽首/中/尾 3 帧：让 agent 看见这一镜里『发生了什么动作』（转身/换装/甩头…）
        frames = _grab_triptych(video, u["start"], u["end"], gid)
        sb_units.append({
            "gid": gid, "start": u["start"], "end": u["end"],
            "ref_frames": frames,                       # [首, 中, 尾] —— 对比这 3 张判断有没有运动
            "ref_frame": frames[1],                     # 兼容旧字段（中点帧）
            "kind": "TODO(product|person|scene)",
            "动作": "TODO: 对比首/中/尾3帧，一句话写清这一镜主体在做什么（如『正面起身→原地转一圈→背对镜头』）。静态就写『静态』。",
            "frame_prompt": "TODO: 看 ref_frames 写这一镜的首帧文生图 prompt（场景+主体+构图，英文）",
            "prompt": "TODO: 图生视频运镜 prompt（中文）。把上面『动作』写成明确的身体动作指令，别只写运镜——Seedance 首帧锁定，不写死动作就不会动。",
            "overlays": [],
        })

    stem = video.stem
    scaffold = {
        "src_video": video.name,
        # ⭐ 第 0 步（最重要）：先回答「这视频为什么火」。爆点不抓住，骨架对了也白搭。
        "爆款点": {
            "一句话": "TODO: 用大白话说——这视频为什么让人想看第二遍？那个『爽点/钩子』是什么？",
            "核心机制": ["TODO: 如 换装 / 转场 / 人和衣服一起转 / 前后反差 / 节奏卡点"],
            "必须复刻的动作": "TODO: 把爆点拆成画面上看得见的动作（如『人物正面起身，原地转360度，转一圈衣服已换成下一套』）。这是要 1:1 锁死的，不是血肉。",
            "千万别做成": "TODO: 写下最容易踩的『丢爆点』的做法（如『做成静态白底清单 / 逐套站定展示 → 爆点全没了』）。",
        },
        "片型": "TODO(product|person)",
        "gen_size": gen_size,
        "gen_resolution": "480p",   # 草稿档：快+省。要发布改 720p（人物/小商品糊脸时尤其）。
        "ai_label": False,          # 合规开关：真人样貌/换脸成片在国内平台发布建议设 true（叠『AI生成』标识）
        "confirm_static": False,    # 这条片『真的就是静态展示』(纯产品平铺/口播大头)时设 true，放行动作护栏
        "out": out,
        "final_name": f"{stem}_复刻.mp4",
        "compare_name": f"{stem}_上下屏对比.mp4",
        # 人物片务必写成『虚构人物、不影射任何真实存在的人』，规避肖像风险（见下方 neg 的 no resemblance）。
        "identity": "TODO: 全片复用的主体描述（同一产品/同一人物，锁死跨镜一致）。人物片加：a fictional person, no resemblance to any specific real person.",
        "scene": "TODO: 全片复用的场景描述",
        "style": "photorealistic cinematic first frame, shallow depth of field, subtle film grain, realistic detail",
        "neg": "no text, no logo, no watermark, no subtitles, no extra fingers, no warped anatomy, no resemblance to any real public figure or celebrity",
        "units": sb_units,
    }
    SB_PATH.write_text(json.dumps(scaffold, ensure_ascii=False, indent=2), encoding="utf-8")

    seg_note = ("按时间均匀切（⚠ 原片几乎没有硬切点，大概率是『转身/旋转』式无缝转场——"
                "这往往就是爆点。请看每镜 3 帧确认真正的换装/转场时刻，必要时手动调 start/end）"
                if soft else f"原始 {len(raw)} 切 → 合并")
    if not soft and len(raw) > 12:
        print(f"⚠ 这是『高密度快剪/卡点』片（原片 {len(raw)} 刀）。当前合并成 {len(units)} 个单元会抹平密集节奏。"
              f"想更贴原片节奏：FK_MAX_GU={min(len(raw), 12)} 重跑；或接受节奏只能像个大概（卡点类本就难 1:1）。")
    print(f"\n{video.name}  {meta['width']}x{meta['height']} {meta['fps']}fps "
          f"{meta['duration']}s  {seg_note} {len(units)} 个生成单元 ({gen_size})")
    for u in sb_units:
        s, e = u["start"], u["end"]
        print(f"  {u['gid']}  {s:>6.2f} → {e:>6.2f}  ({round(e - s, 2)}s)   帧 {u['ref_frame']}")
    print(f"""
脚手架已生成：{SB_PATH}
关键帧已抽好：{SB_DIR}/g*_a/_b/_c.jpg（每镜 首/中/尾 3 张，用来看运动）

接下来（agent 自动做，无需人工）：
  ⭐ 0. 【先做这步！】把整段原片或每镜的 a/b/c 三帧连起来看，回答「这视频为什么火」，
        把 storyboard.json 顶部的『爆款点』填满。爆点是换装/转场/转身/反差这类『动作』时，
        它属于必须 1:1 复刻的骨架，绝不能简化成静态展示。这一步丢了，下面全白做。
  1. 对比每镜 a/b/c 三帧，先把每个 unit 的『动作』字段写清（有没有转身/换装/甩动）。
  2. 判断片型（product / person）；把 identity / scene / style / neg 补成「锁死一致性」的全局描述。
  3. 给每个 unit 写 frame_prompt（首帧·英文）和 prompt（运镜+动作·中文）；
     ⚠ prompt 里必须把『动作』写成明确指令（Seedance 首帧锁定，不写死就不动），
     爆点动作尤其要写满；片尾若要片名填 overlays（绝不让模型画字）。
  4. 全部 TODO 填完 → python -m pipeline.gen_frames（或用 Codex 内置 images 生首帧）
     → 先 go/no-go 跑 g1 → python -m pipeline.gen_video → python -m pipeline.assemble。
     （或一条命令跑完后三步：python -m pipeline.run）
""")


if __name__ == "__main__":
    main()
