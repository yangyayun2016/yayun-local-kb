"""首帧文生图（API 路线）：提交 → 轮询 → 下载，多模型 fallback。

默认路线是「宿主 agent（Codex）用内置 images 生首帧」——那条不用本文件。
本文件是 headless / 非 Codex 宿主的回退：用 APIMart 图像接口出首帧，与视频共用 /v1/tasks/{id}。
图片 URL 在 data.result.images[0].url[0]（url 可能是数组）。
"""
import time
import requests
from pathlib import Path

from pipeline.config import TOKEN, IMAGE_ENDPOINT, TASK_ENDPOINT, IMAGE_MODEL

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
RETRYABLE = (429, 500, 502, 503, 504)

# 拥堵时按序 fallback，谁先出用谁
FALLBACK_MODELS = [
    "z-image-turbo", "seedream-5-0-lite", "qwen-image-2.0",
    "gemini-2.5-flash-image-preview", "flux-2-flex",
]


def _submit(prompt, model, size, resolution, n, image_urls):
    body = {"model": model, "prompt": prompt, "size": size, "resolution": resolution, "n": n}
    if image_urls:
        body["image_urls"] = image_urls
    for i in range(8):
        r = requests.post(IMAGE_ENDPOINT, headers=HEADERS, json=body, timeout=60)
        if r.ok:
            d = r.json().get("data")
            return (d[0] if isinstance(d, list) else d)["task_id"]
        if r.status_code in RETRYABLE:
            print(f"    submit {r.status_code} 忙，10s 重试 ({i+1}/8)")
            time.sleep(10); continue
        raise RuntimeError(f"submit {r.status_code}: {r.text[:200]}")
    raise RuntimeError("submit 持续失败")


def _poll(task_id, max_wait, interval=4):
    waited = 0
    while waited < max_wait:
        r = requests.get(f"{TASK_ENDPOINT}/{task_id}", headers=HEADERS, timeout=60)
        if r.ok:
            d = r.json().get("data", {})
            st = d.get("status")
            if st in ("completed", "succeeded", "success"):
                u = d["result"]["images"][0]["url"]
                return u[0] if isinstance(u, list) else u
            if st in ("failed", "error", "cancelled", "expired"):
                raise RuntimeError(f"task {st}: {str(d)[:200]}")
        time.sleep(interval); waited += interval
    raise TimeoutError(f"timeout {task_id} after {max_wait}s")


def _download(url, out_path):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(requests.get(url, timeout=120).content)
    return out_path


def gen_image_robust(prompt, out_path, models=None, size="16:9", resolution="2k",
                     per_model_wait=90, n=1, image_urls=None, race=3):
    """多模型 fallback。先把前 race 个模型『并发』提交+轮询，谁先出用谁（headless 前置等待从串行 90s×N 砍到一批的最慢一个）。
    一批全失败再试下一批。返回 (path, model)。"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    models = models or FALLBACK_MODELS
    last = None
    for batch_start in range(0, len(models), race):
        batch = models[batch_start:batch_start + race]

        def _try(m):
            tid = _submit(prompt, m, size, resolution, n, image_urls)
            return m, _poll(tid, per_model_wait)

        print(f"  --- 并发试 {batch} ---")
        with ThreadPoolExecutor(max_workers=len(batch)) as ex:
            futs = {ex.submit(_try, m): m for m in batch}
            for fut in as_completed(futs):
                try:
                    m, url = fut.result()
                    _download(url, out_path)
                    print(f"  OK [{m}] -> {out_path}")
                    return out_path, m
                except Exception as e:
                    last = e
                    print(f"  {futs[fut]} 不行: {e}")
    raise RuntimeError(f"所有图像模型都失败: {last}")


if __name__ == "__main__":
    import sys
    gen_image_robust(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "_work/test_img.png")
