"""把生成好的片段抽『首/中/尾』帧拼成一张图，方便一眼判断：go/no-go、哪一镜崩了。

不依赖任何 API，纯 ffmpeg。go/no-go 时跑 `python -m pipeline.preview g1` 看一眼 g1 是否首帧锁形象+爆点动作生效；
想看全部就 `python -m pipeline.preview`。产物在 _work/preview/<gid>.jpg。
"""
import subprocess
import sys
from pathlib import Path

from pipeline.config import GEN, WORK, SHOTS, ensure_ffmpeg

PREVIEW = WORK / "preview"


def _dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def contact_sheet(gid):
    """对 clip_<gid>.mp4 抽首/中/尾 3 帧，横向拼成一张 _work/preview/<gid>.jpg。"""
    clip = GEN / f"clip_{gid}_fixed.mp4"
    if not clip.exists():
        clip = GEN / f"clip_{gid}.mp4"
    if not clip.exists():
        print(f"  {gid}: 还没生成 clip，跳过")
        return None
    PREVIEW.mkdir(parents=True, exist_ok=True)
    d = _dur(clip)
    times = [max(0.0, 0.05 * d), d / 2, max(0.0, d - 0.1)] if d else [0, 0, 0]
    tiles = []
    for i, t in enumerate(times):
        tile = PREVIEW / f"_{gid}_{i}.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", str(clip),
                        "-frames:v", "1", "-q:v", "3", str(tile)],
                       check=True, capture_output=True)
        tiles.append(tile)
    out = PREVIEW / f"{gid}.jpg"
    subprocess.run(["ffmpeg", "-y", "-i", str(tiles[0]), "-i", str(tiles[1]), "-i", str(tiles[2]),
                    "-filter_complex", "[0][1][2]hstack=inputs=3", str(out)],
                   check=True, capture_output=True)
    for t in tiles:
        t.unlink(missing_ok=True)
    print(f"  {gid}: {out}")
    return out


def main():
    ensure_ffmpeg()
    ids = sys.argv[1:] or [s["gid"] for s in SHOTS]
    print("抽帧预览（首/中/尾，用来判 go/no-go 和哪镜崩了）：")
    made = [contact_sheet(g) for g in ids]
    if any(made):
        print(f"\n看 {PREVIEW}/ 里的图。每张是一镜的『首 中 尾』——人有没有动、脸有没有漂、爆点动作在不在，一眼可见。")


if __name__ == "__main__":
    main()
