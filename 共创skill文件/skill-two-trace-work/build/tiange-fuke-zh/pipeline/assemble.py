"""⑥ 精确拼接：每个生成单元裁回原片目标时长 → 统一 1080x1920/30fps → 按切点 concat。
生成时 clamp 到 ≥4s 的片段，这里用 -t 裁回真实时长（如 0.93s），骨架节奏才 1:1。
某 gid 若有 _fixed 版（后期叠真实产品图/角标）优先用。
用法：python -m pipeline.assemble
"""
import os
import subprocess
from pathlib import Path

from pipeline.config import (GEN, FINAL, FRAMES, SHOTS, OUT_W, OUT_H, OUT_FPS,
                             FINAL_NAME, SRC_VIDEO, COMPARE_NAME)
from pipeline.shots import OVERLAYS
from pipeline.storyboard import load as _load_sb, SB_PATH

_SB_AI_LABEL = bool((_load_sb() or {}).get("ai_label", False))
try:
    SB_MTIME = SB_PATH.stat().st_mtime
except OSError:
    SB_MTIME = 0.0


def _ffmpeg_path(path):
    return Path(path).as_posix().replace(":", "\\:")


def _font_file():
    # 中文可渲染字体优先（Mac / Windows / Linux）
    cjk = [
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/msyh.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
    ]
    for p in cjk:
        if p.exists():
            return p
    # 没有任何中文字体——中文角标会渲染成豆腐块，显式告警（不静默降级）
    fallback = Path("C:/Windows/Fonts/arial.ttf")
    print("[WARN] 未找到中文字体，叠中文角标会变方块。请装思源/微软雅黑（Linux: fonts-noto-cjk）。")
    return fallback


def _px(v, dim):
    """叠字坐标支持两种写法：整数=像素；0~1 的小数=相对画布比例（改分辨率不用重调坐标）。"""
    if isinstance(v, float) and 0 < v <= 1:
        return int(round(v * dim))
    return int(v)


def _vf_for(gid):
    vf = [
        f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase",
        f"crop={OUT_W}:{OUT_H}",
        f"fps={OUT_FPS}",
    ]
    overlays = OVERLAYS.get(gid, [])
    if overlays:
        font = _ffmpeg_path(_font_file())
        for i, entry in enumerate(overlays):
            if isinstance(entry, dict) and entry.get("type") == "box":
                vf.append(
                    "drawbox="
                    f"x={_px(entry.get('x', 70), OUT_W)}:"
                    f"y={_px(entry.get('y', 138 + i * 96), OUT_H)}:"
                    f"w={_px(entry.get('w', 320), OUT_W)}:"
                    f"h={_px(entry.get('h', 120), OUT_H)}:"
                    f"color={entry.get('color', 'black@0.58')}:"
                    f"t={entry.get('t', 'fill')}"
                )
                continue

            if isinstance(entry, dict):
                label = entry.get("text", "")
                x = _px(entry.get("x", 70), OUT_W)
                y = _px(entry.get("y", 138 + i * 96), OUT_H)
                fontsize = _px(entry.get("fontsize", 58), OUT_H)
                fontcolor = entry.get("fontcolor", "white")
                line_spacing = entry.get("line_spacing", 10)
                box = entry.get("box", False)
                boxcolor = entry.get("boxcolor", "black@0.58")
                boxborderw = entry.get("boxborderw", 18)
            else:
                label = entry
                x = 70
                y = 138 + i * 96
                fontsize = 66 if gid == "g1" else 58
                fontcolor = "white"
                line_spacing = 10
                box = True
                boxcolor = "0xff4da6@0.84" if gid == "g1" else "black@0.58"
                boxborderw = 24

            textfile = GEN / f"overlay_{gid}_{i}.txt"
            textfile.write_text(label, encoding="utf-8")
            parts = [
                "drawtext=",
                f"fontfile='{font}':",
                f"textfile='{_ffmpeg_path(textfile)}':",
                f"fontcolor={fontcolor}:",
                f"fontsize={fontsize}:",
                f"line_spacing={line_spacing}:",
                f"x={x}:",
                f"y={y}",
            ]
            if box:
                parts.extend([
                    ":box=1",
                    f":boxcolor={boxcolor}",
                    f":boxborderw={boxborderw}",
                ])
            vf.append("".join(parts))
    return ",".join(vf)


def _norm_one(gid, dur):
    fixed = GEN / f"clip_{gid}_fixed.mp4"
    src = fixed if fixed.exists() else GEN / f"clip_{gid}.mp4"
    if not src.exists():
        raise FileNotFoundError(f"缺片段 {gid}: {src}")
    out = GEN / f"norm_{gid}.mp4"
    # 跳过重编码：norm 已存在且比『源片段』和『storyboard.json(叠字/时长来源)』都新 → 直接复用。
    try:
        newest_in = max(src.stat().st_mtime, SB_MTIME)
        if out.exists() and out.stat().st_mtime >= newest_in:
            print(f"norm {gid}: 已是最新，跳过")
            return out
    except OSError:
        pass
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-t", str(dur), "-vf",
         _vf_for(gid),
         "-c:v", "libx264", "-preset", "fast", "-an", str(out)],
        check=True, capture_output=True)
    print(f"norm {gid}: 裁到 {dur}s")
    return out


def _ai_label_vf():
    """合规：AI 生成内容标识。国内平台发布『真人样貌/换脸』成片，按《AI生成合成内容标识办法》须显著标识。
    开关：环境变量 FK_AI_LABEL=1 或 storyboard.json 顶部 "ai_label": true。默认关（不破坏调性），但文档强提示真人片要开。
    """
    on = os.environ.get("FK_AI_LABEL", "").strip() in ("1", "true", "yes") or bool(_SB_AI_LABEL)
    if not on:
        return None
    font = _ffmpeg_path(_font_file())
    textfile = GEN / "ai_label.txt"
    textfile.write_text("AI生成", encoding="utf-8")
    fs = max(20, OUT_W // 24)
    return (f"drawtext=fontfile='{font}':textfile='{_ffmpeg_path(textfile)}':"
            f"fontcolor=white:fontsize={fs}:box=1:boxcolor=black@0.5:boxborderw=10:"
            f"x=w-tw-20:y=h-th-20")


def assemble():
    norm = [_norm_one(s["gid"], round(s["end"] - s["start"], 3)) for s in SHOTS]
    concat = GEN / "concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in norm), encoding="utf-8")
    out = FINAL / FINAL_NAME
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat)]
    label = _ai_label_vf()
    if label:
        cmd += ["-vf", label]
        print("  已叠『AI生成』标识（FK_AI_LABEL / ai_label 开启）")
    cmd += ["-c:v", "libx264", "-preset", "medium", "-pix_fmt", "yuv420p", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"\nfinal -> {out}")
    return out


def _label_filter(idx, text, font):
    """把某一路视频缩放铺满 OUT_W×OUT_H（不裁、补黑边）并左上角叠标签。"""
    textfile = GEN / f"cmp_label_{idx}.txt"
    textfile.write_text(text, encoding="utf-8")
    return (
        f"[{idx}:v]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=decrease,"
        f"pad={OUT_W}:{OUT_H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={OUT_FPS},"
        f"drawtext=fontfile='{font}':textfile='{_ffmpeg_path(textfile)}':"
        f"x=28:y=22:fontsize=44:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=12"
    )


def make_compare(replica_path, src_path=SRC_VIDEO, out_name=COMPARE_NAME, keep_audio=None):
    """对比片：复刻 vs 原片。
    竖屏(9:16)用左右并排(hstack)——否则上下堆成又高又窄的两条带，手机上看不清脸和衣服；
    横屏(16:9)仍用上下堆叠(vstack)。
    默认保留原片音轨（自审用）；公开发布带原片画面+音轨有搬运风险 → FK_COMPARE_NOAUDIO=1 出无声版。
    """
    if not Path(src_path).exists():
        raise FileNotFoundError(f"缺原片: {src_path}")
    if keep_audio is None:
        keep_audio = os.environ.get("FK_COMPARE_NOAUDIO", "").strip() not in ("1", "true", "yes")
    font = _ffmpeg_path(_font_file())
    out = FINAL / out_name
    portrait = OUT_H >= OUT_W
    stack = "hstack" if portrait else "vstack"
    fc = (
        f"{_label_filter(0, '我的复刻', font)}[t];"
        f"{_label_filter(1, '原片', font)}[b];"
        f"[t][b]{stack}=inputs=2[v]"
    )
    cmd = ["ffmpeg", "-y", "-i", str(replica_path), "-i", str(src_path),
           "-filter_complex", fc, "-map", "[v]"]
    if keep_audio:
        cmd += ["-map", "1:a", "-c:a", "aac"]
    cmd += ["-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-pix_fmt", "yuv420p", str(out)]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"compare({stack} 复刻+原片{'，带原片音轨' if keep_audio else '，无声'}) -> {out}")
    return out


if __name__ == "__main__":
    from pipeline.config import ensure_ffmpeg
    ensure_ffmpeg()
    replica = assemble()
    make_compare(replica)
