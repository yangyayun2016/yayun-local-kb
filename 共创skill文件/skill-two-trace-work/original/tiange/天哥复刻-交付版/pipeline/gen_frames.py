"""④ 生首帧（headless/API 回退路线）：按 storyboard 给每个生成单元出首帧 → _work/frames/frame_<gid>.png。

默认路线是宿主 agent（Codex）用内置 images 生首帧到同样路径，那条不跑本文件。
本文件供 headless / 非 Codex 宿主：用 pipeline.gen_image 的 API 链批量出首帧，画幅对齐 config.GEN_SIZE。
先生 g1 主形象，其余镜头把 g1 作参考图喂进去保跨镜一致（identity-preserve）。

用法：python -m pipeline.gen_frames [g1 g3 ...]   (不传 = 全部缺失的)
"""
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from pipeline.config import FRAMES, GEN_SIZE, SHOTS, TOKEN, ROUTE, IMAGE_ENDPOINT
from pipeline.shots import SHOT_PROMPTS
from pipeline.gen_image import gen_image_robust
from pipeline.upload import upload


def main():
    if not TOKEN:
        _hint = ("方舟：在 _work/.secret.env 写 ARK_API_KEY=你的key 且 FK_ROUTE=ark"
                 if ROUTE == "ark" else "APIMart：在 _work/.secret.env 写 APIMART_TOKEN=你的key")
        sys.exit(f"❌ 没读到 API key（路线 {ROUTE}）。{_hint}。没文件就把 _work/.secret.env.example 复制成 _work/.secret.env 再填。")
    if not IMAGE_ENDPOINT:
        sys.exit("❌ 当前路线（ark）没配图像生成端点，这条 API 生图链跑不了。\n"
                 "   首帧请用宿主 agent（Codex/Claude）的内置生图能力，生成到 _work/frames/frame_<gid>.png；\n"
                 "   或临时在 _work/.secret.env 改 FK_ROUTE=apimart 并填 APIMART_TOKEN 来走 APIMart 生图。\n"
                 "   （视频生成仍走 ark / 你的 Mini 包，互不影响。）")
    ids = sys.argv[1:] or [s["gid"] for s in SHOTS]
    targets = [s["gid"] for s in SHOTS if s["gid"] in ids]
    anchor_path = FRAMES / "frame_g1.png"

    # g1 先单独生成当「主形象锚点」，其余镜头参考它保跨镜一致——所以 g1 必须先于并发。
    if "g1" in targets:
        print("=== 生首帧 g1 (主形象锚点) ===")
        gen_image_robust(SHOT_PROMPTS["g1"]["frame_prompt"], anchor_path, size=GEN_SIZE)
        targets = [g for g in targets if g != "g1"]

    anchor_url = upload(anchor_path) if (anchor_path.exists() and targets) else None

    def _work(gid):
        out = FRAMES / f"frame_{gid}.png"
        print(f"=== 生首帧 {gid} ===")
        gen_image_robust(SHOT_PROMPTS[gid]["frame_prompt"], out, size=GEN_SIZE,
                         image_urls=[anchor_url] if anchor_url else None)
        return gid

    # 并发生其余首帧（共用已上传的 g1 锚点直链），墙钟从「N 张之和」降到「最慢 1 张」。
    if targets:
        with ThreadPoolExecutor(max_workers=min(len(targets), 6)) as ex:
            futs = {ex.submit(_work, g): g for g in targets}
            for fut in as_completed(futs):
                g = futs[fut]
                try:
                    fut.result(); print(f"[OK] {g}")
                except Exception as e:
                    print(f"[FAIL] {g}: {e}")
    print(f"\n首帧就绪 → {FRAMES}")


if __name__ == "__main__":
    main()
