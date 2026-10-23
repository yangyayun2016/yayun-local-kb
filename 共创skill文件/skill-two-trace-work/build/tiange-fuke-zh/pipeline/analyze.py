"""① 原片逐帧分析：ffmpeg 场景检测拿硬切点 + 总时长/fps，输出分镜骨架 JSON。
这是「锁骨架」的第一步 —— 切点、时长比例就是要 1:1 复刻的东西。
用法：python -m pipeline.analyze [视频路径]   (默认 config.SRC_VIDEO)
输出：_work/skeleton.json  +  控制台打印切点表
"""
import json
import subprocess
import sys
from pathlib import Path

from pipeline.config import SRC_VIDEO, WORK


def probe(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
         "-show_entries", "format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout
    j = json.loads(out)
    s, f = j["streams"][0], j["format"]
    num, den = (s["r_frame_rate"].split("/") + ["1"])[:2]
    return {"width": s["width"], "height": s["height"],
            "fps": round(float(num) / float(den), 3),
            "duration": round(float(f["duration"]), 3)}


def scene_cuts(video, threshold=0.3):
    out = subprocess.run(
        ["ffmpeg", "-i", str(video), "-filter:v",
         f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    cuts = []
    for line in out.splitlines():
        if "pts_time:" in line:
            t = line.split("pts_time:")[1].split()[0]
            try:
                cuts.append(round(float(t), 3))
            except ValueError:
                pass
    return sorted(set(cuts))


def main():
    video = Path(sys.argv[1]) if len(sys.argv) > 1 else SRC_VIDEO
    meta = probe(video)
    cuts = scene_cuts(video)
    bounds = [0.0] + cuts + [meta["duration"]]
    shots = [{"i": i + 1, "start": bounds[i], "end": bounds[i + 1],
              "dur": round(bounds[i + 1] - bounds[i], 3)}
             for i in range(len(bounds) - 1)]
    skeleton = {"video": str(video), **meta, "cuts": cuts, "shots": shots}
    (WORK / "skeleton.json").write_text(
        json.dumps(skeleton, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{video.name}  {meta['width']}x{meta['height']} "
          f"{meta['fps']}fps  {meta['duration']}s  {len(shots)} 个原始镜头")
    for s in shots:
        print(f"  镜{s['i']:>2}  {s['start']:>6.2f} → {s['end']:>6.2f}  ({s['dur']}s)")
    print(f"\n→ 已存骨架 _work/skeleton.json。下一步：跑 `python -m pipeline.auto_storyboard <视频>` "
          f"自动合并生成单元 + 抽关键帧 + 出 storyboard 脚手架（不必手填 config.SHOTS）。")


if __name__ == "__main__":
    main()
