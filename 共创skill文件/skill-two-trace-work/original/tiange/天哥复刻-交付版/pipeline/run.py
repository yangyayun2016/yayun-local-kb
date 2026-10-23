"""一键跑完后半程：生视频 → 拼接 → 出上下屏对比片。

给「啥也不会」的人用：分镜（storyboard.json）填好、首帧生好之后，
不用记三条命令，敲一条就行：

    python -m pipeline.run

它会按顺序做：
  1）（可选）首帧缺了就用 API 补：headless 没有内置生图时自动跑 gen_frames。
  2）全量生视频 gen_video（已并发；已生成的自动跳过，不重复烧钱）。
  3）拼接 + 裁回真实时长 + 叠角标 + 自动出上下屏对比片 assemble。

先确认：storyboard.json 的『爆款点』和每镜 prompt 都填完了（没填会被护栏拦下）。
go/no-go 想单独先验 g1：先 `python -m pipeline.gen_video g1` 看一眼再 `python -m pipeline.run`。
"""
import subprocess
import sys
from pathlib import Path

from pipeline.config import FRAMES, GEN, SHOTS, ensure_ffmpeg


def _run(cmd):
    print(f"\n>>> {' '.join(cmd)}")
    r = subprocess.run([sys.executable, "-m"] + cmd)
    if r.returncode != 0:
        sys.exit(f"[STOP] 这步失败了：{' '.join(cmd)}（返回码 {r.returncode}）。先看上面的报错。")


def _preflight():
    """先体检，把『没填完/格式坏了』当人话讲清楚，而不是跑到一半糊一脸 traceback。"""
    ensure_ffmpeg()
    try:
        import pipeline.shots  # noqa: F401  —— 触发爆款点/分镜/动作 等护栏与结构校验
    except ValueError as e:
        sys.exit(f"[STOP] storyboard 还没准备好，先补完再跑：\n{e}")


def main():
    _preflight()

    # 1) 首帧检查：按镜头粒度查缺失，只补缺的（有内置生图的宿主应已自己生好）
    missing_frames = [s["gid"] for s in SHOTS if not (FRAMES / f"frame_{s['gid']}.png").exists()]
    if missing_frames:
        print(f"这些镜头还没有首帧：{', '.join(missing_frames)}。试着用 API 生图链补全……")
        _run(["pipeline.gen_frames"] + missing_frames)
        still = [g for g in missing_frames if not (FRAMES / f"frame_{g}.png").exists()]
        if still:
            print(f"⚠ 仍缺首帧：{', '.join(still)} —— 这些镜会退化成纯文生视频，跨镜人物/产品可能不一致。")

    # 2) 全量生视频（已存在的自动跳过）
    _run(["pipeline.gen_video"])

    # 全部片段就绪才拼接
    missing = [s["gid"] for s in SHOTS if not (GEN / f"clip_{s['gid']}.mp4").exists()]
    if missing:
        sys.exit(f"[STOP] 还缺这些片段没生成：{', '.join(missing)}。"
                 f"单独重跑：python -m pipeline.gen_video {' '.join(missing)}")

    # 3) 拼接 + 上下屏对比
    _run(["pipeline.assemble"])
    print("\n✅ 全部完成。成片和上下屏对比片在 _work/final/。")
    _print_cost_estimate()


def _print_cost_estimate():
    """粗算这条片花了多少钱（按各镜 model+分辨率估，仅供心里有数，实际以平台账单为准）。"""
    import json
    # 每 4s 片段的粗略单价（元），按路线×分辨率。⚠ 估算值，充值后以实测账单校准。
    price = {("ark", "480p"): 0.6, ("ark", "720p"): 1.0,        # ark Mini 资源包，最便宜
             ("apimart", "480p"): 1.5, ("apimart", "720p"): 2.5}  # apimart（有脸镜）
    total, n = 0.0, 0
    for s in SHOTS:
        meta = GEN / f"clip_{s['gid']}.json"
        if not meta.exists():
            continue
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            continue
        route = m.get("route") or s.get("route", "apimart")
        res = "720p" if "720" in str(m.get("resolution", "")) else "480p"
        total += price.get((route, res), 2.0)
        n += 1
    if n:
        print(f"💰 本条约 {n} 个生成镜，粗估 ≈ ¥{total:.1f}（估算，实际以平台账单为准）。")


if __name__ == "__main__":
    main()
