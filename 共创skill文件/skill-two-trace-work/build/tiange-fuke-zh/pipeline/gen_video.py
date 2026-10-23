"""④ 逐生成单元出视频：首帧锁形象(first_frame) + 运镜写进 prompt → seedance 图生视频。
沿用已验证的 提交→轮询→下载 + 退避重试逻辑（队列拥堵 429/503 是常态，重试是底座不是可选）。
首帧来自 _work/frames/frame_<gid>.png（Codex 内置 images 生成），本地图先上传拿公网直链。
用法：python -m pipeline.gen_video g1 g3 g5   (不传 = 全部)
"""
import base64
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path

from pipeline.config import (ROUTES, route_for, MODEL, FRAMES, GEN, SHOTS,
                             GEN_SIZE, GEN_RESOLUTION, DEFAULT_ROUTE)
from pipeline.upload import upload

RETRYABLE = (429, 500, 502, 503, 504)


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _img_ref(x):
    """图片喂给接口的形式：已是 http(s) 直链就原样用；否则当本地路径转成 base64 data URL。
    ARK 支持 data URL，所以走 ARK 时本地首帧/参考图无需上传图床（少一个外部依赖、少一处失败点）。"""
    s = str(x)
    if s.startswith("http://") or s.startswith("https://"):
        return s
    p = Path(s)
    ext = p.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}.get(ext, ext or "png")
    return f"data:image/{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def _req(method, url, token, max_retries=20, wait=12, **kw):
    """退避重试是底座：队列 429/503 是常态。指数退避（12s 起，封顶 60s），比固定 30s 更快从短暂拥堵恢复。"""
    cur = wait
    for i in range(max_retries):
        try:
            r = requests.request(method, url, headers=_headers(token), timeout=60, **kw)
        except requests.RequestException as e:
            print(f"  网络异常，{cur}s 后重试 ({i+1}/{max_retries}): {e}")
            time.sleep(cur); cur = min(int(cur * 1.5), 60); continue
        if r.ok:
            return r
        if r.status_code in RETRYABLE:
            print(f"  {r.status_code} 服务忙，{cur}s 后重试 ({i+1}/{max_retries})")
            time.sleep(cur); cur = min(int(cur * 1.5), 60); continue
        raise RuntimeError(f"{method} {r.status_code}: {r.text[:300]}")
    raise RuntimeError(f"{method} 持续失败超 {max_retries} 次: {url}")


def submit(prompt, duration, route, first_frame=None, refs=None,
           size=GEN_SIZE, resolution=GEN_RESOLUTION, seed=42, model=None):
    """两条后端请求体不同，按 route 分支（route = 'ark' | 'apimart'）：
    - ARK（火山方舟）：content 数组 + ratio + 本地图 base64；响应 id。
    - APIMart：prompt + size + image_with_roles（图需先传成直链）；响应 data[].task_id。
    first_frame/refs：ARK 传本地路径(自动 base64)；APIMart 传已上传的 https 直链。"""
    cfg = ROUTES[route]
    token, endpoint = cfg["token"], cfg["gen_endpoint"]
    dur = max(4, int(round(duration)))   # API 最小 4s，拼接阶段再裁回真实时长
    model = model or cfg["models"]["fast"]
    refs = refs or []
    if route == "ark":
        content = [{"type": "text", "text": prompt}]
        if first_frame:
            content.append({"type": "image_url", "image_url": {"url": _img_ref(first_frame)},
                            "role": "first_frame"})
        for r_ in refs:
            content.append({"type": "image_url", "image_url": {"url": _img_ref(r_)},
                            "role": "reference_image"})
        body = {"model": model, "content": content, "resolution": resolution,
                "ratio": size, "duration": dur, "watermark": False}
        r = _req("POST", endpoint, token, json=body)
        task_id = r.json()["id"]
    else:
        roles = []
        if first_frame:
            roles.append({"url": first_frame, "role": "first_frame"})
        for u in refs:
            roles.append({"url": u, "role": "reference_image"})
        body = {"model": model, "prompt": prompt, "duration": dur, "size": size,
                "resolution": resolution, "seed": seed, "generate_audio": False}
        if roles:
            body["image_with_roles"] = roles
        r = _req("POST", endpoint, token, json=body)
        d = r.json().get("data")
        task_id = (d[0] if isinstance(d, list) else d)["task_id"]
    print(f"  submitted task_id={task_id} (route={route}, model={model})")
    return task_id


def poll(task_id, out_path, route, interval=5, max_wait=480):
    cfg = ROUTES[route]
    token, task_endpoint = cfg["token"], cfg["task_endpoint"]
    waited = 0
    while waited < max_wait:
        resp = _req("GET", f"{task_endpoint}/{task_id}", token).json()
        d = resp if route == "ark" else resp.get("data", {})   # ARK 状态在顶层，APIMart 在 data 里
        st = d.get("status")
        print(f"  [{waited}s] status={st} progress={d.get('progress')}")
        if st in ("completed", "succeeded", "success"):
            url = _extract_url(d)
            Path(out_path).write_bytes(requests.get(url, timeout=300).content)
            print(f"  saved -> {out_path}")
            return out_path
        if st in ("failed", "error", "cancelled", "expired"):
            raise RuntimeError(f"任务终止: {d}")
        time.sleep(interval); waited += interval
    raise TimeoutError(f"轮询超时 {task_id}")


def _extract_url(d):
    # ARK：content.video_url
    cv = d.get("content") if isinstance(d, dict) else None
    if isinstance(cv, dict) and isinstance(cv.get("video_url"), str):
        return cv["video_url"]
    # APIMart：result.videos[0].url
    try:
        u = d["result"]["videos"][0]["url"]
        return u[0] if isinstance(u, list) else u
    except (KeyError, IndexError, TypeError):
        pass
    for path in (("result", "video_url"), ("video_url",), ("url",)):
        cur = d
        for k in path:
            cur = cur.get(k) if isinstance(cur, dict) else None
        if isinstance(cur, str):
            return cur
    raise RuntimeError(f"找不到视频URL: {d}")


def generate(gid, prompt, duration, route, first_frame=None, ref_imgs=None, attempts=3,
             seed=42, model=None, resolution=None):
    """卡死(超时)自动换 seed 重提，最多 attempts 次。route='ark'|'apimart'。first_frame/ref_imgs 为本地路径。"""
    model = model or ROUTES[route]["models"]["fast"]
    resolution = resolution or GEN_RESOLUTION
    # ARK 支持本地图 base64，无需图床；APIMart 要 https 直链 → 先上传。
    if route == "ark":
        ff = str(first_frame) if first_frame else None
        refs = [str(p) for p in (ref_imgs or [])]
    else:
        ff = upload(first_frame) if first_frame else None
        refs = [upload(p) for p in (ref_imgs or [])]
    out = GEN / f"clip_{gid}.mp4"
    meta_path = GEN / f"clip_{gid}.json"
    last = None
    for a in range(attempts):
        actual_seed = seed + a * 7
        try:
            tid = submit(prompt, duration, route, first_frame=ff, refs=refs,
                         seed=actual_seed, model=model, resolution=resolution)
            result = poll(tid, out, route)
            meta = {
                "gid": gid,
                "route": route,
                "model": model,
                "task_id": tid,
                "seed": actual_seed,
                "attempt": a + 1,
                "max_attempts": attempts,
                "target_duration": duration,
                "api_duration": max(4, int(round(duration))),
                "resolution": resolution,
                "size": GEN_SIZE,
                "first_frame": str(first_frame) if first_frame else None,
                "reference_images": [str(p) for p in (ref_imgs or [])],
                "output": str(result),
                "prompt": prompt,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            (GEN / f"clip_{gid}.err.json").unlink(missing_ok=True)   # 之前若失败过，成功后清掉错误记录
            return result
        except TimeoutError as e:
            last = e
            print(f"  [WARN] 卡死/超时，换 seed 重提 ({a+1}/{attempts})")
    raise RuntimeError(f"{out} 多次重提仍卡死（队列可能严重拥堵）: {last}")


if __name__ == "__main__":
    import os
    import sys
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from pipeline.shots import SHOT_PROMPTS   # 每镜 prompt 表（分镜创意）

    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    force = "--force" in sys.argv[1:]          # --force 强制重生已存在的片段
    ids = args or [s["gid"] for s in SHOTS]
    targets = [s for s in SHOTS if s["gid"] in ids]

    # 预检：这次实际用到的每条路线都要有 key（有脸→apimart，无脸→ark Mini 包）。缺哪条报哪条，别撞英文 401。
    _key_hint = {"ark": "ARK_API_KEY=[已移除] 资源包）",
                 "apimart": "APIMART_TOKEN=[已移除]}
    _used_routes = sorted({s["route"] for s in targets})
    _missing = [r for r in _used_routes if not ROUTES[r]["token"]]
    if _missing:
        lines = "\n".join(f"     {r}: 在 _work/.secret.env 写  {_key_hint[r]}" for r in _missing)
        sys.exit(f"❌ 这次要用到的路线缺 key：{', '.join(_missing)}\n{lines}\n"
                 f"   没文件就把 _work/.secret.env.example 复制成 _work/.secret.env 再填。\n"
                 f"   （只想先跑一条路线：在 .secret.env 写 FK_ROUTE=ark 或 apimart 强制整片走一条。）")

    # 提速：跳过已生成的片段。go/no-go 先跑 g1 通过后，全量这步会自动复用它，不再重生一遍。
    if not force:
        skipped = [s["gid"] for s in targets if (GEN / f"clip_{s['gid']}.mp4").exists()]
        if skipped:
            print(f"跳过已生成（--force 可强制重生）：{', '.join(skipped)}")
            targets = [s for s in targets if s["gid"] not in skipped]
    if not targets:
        print("没有需要生成的片段（都已存在）。要重生请加 --force。")
        sys.exit(0)

    anchor = FRAMES / "frame_g1.png"   # g1 主形象：其余镜把它作 reference_image 喂进去，锁跨镜人物/产品一致

    # 用到未实测确认的 (路线,档位)（如 ark Mini id 还没确认）→ 运行时 WARN 一次。
    _seen_warn = set()
    for s in targets:
        key = (s["route"], s.get("tier", "fast"))
        if key in _seen_warn:
            continue
        _seen_warn.add(key)
        if not ROUTES[s["route"]]["verified"].get(s.get("tier", "fast"), True):
            print(f"  ⚠ 用到未实测确认的 {s['route']}/{s.get('tier')}（model={s['model']}）。"
                  f"建议先跑 python -m pipeline.verify_mini 确认；id 不符就在 .secret.env 写 FK_MODEL_MINI=正确id。")
    # 分流概览：让人看清哪几镜走 ark(Mini包/Fast)、哪几镜走 apimart。
    _by = {}
    for s in targets:
        _by.setdefault((s["route"], s["model"]), []).append(s["gid"])
    print("路线分流：" + " | ".join(f"{r}({m}): {','.join(g)}" for (r, m), g in _by.items()))

    def _work(s):
        sp = SHOT_PROMPTS[s["gid"]]
        ff = FRAMES / f"frame_{s['gid']}.png"
        route = s["route"]
        m = s.get("model") or ROUTES[route]["models"]["fast"]
        res = s.get("resolution") or GEN_RESOLUTION
        # 非 g1 镜头：除自己的首帧外，再把 g1 作参考图，保证脸/产品跨镜不漂（这步原来漏接了，是人脸漂移的根因）。
        refs = [anchor] if (s["gid"] != "g1" and anchor.exists()) else None
        print(f"=== 提交 {s['gid']}  dur={sp['dur']}s  {res}  route={route}  首帧={'有' if ff.exists() else '无'}"
              f"  参考g1={'有' if refs else '无'}  model={m} ===")
        return s["gid"], generate(s["gid"], sp["prompt"], sp["dur"], route,
                                  first_frame=ff if ff.exists() else None, ref_imgs=refs,
                                  model=m, resolution=res)

    # 并发：一次性全提交、并发轮询。seedance 异步接口，墙钟从「N 条之和」降到「最慢 1 条」。
    # go/no-go 单 gid 时自然只 1 个 worker。退避重试逻辑不变，仍是底座。
    # 并发数可调（FK_WORKERS，默认 8）；号池小就调小避免整片 429。
    workers = min(len(targets), int(os.environ.get("FK_WORKERS", "8"))) or 1
    ok = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_work, s): s["gid"] for s in targets}
        for fut in as_completed(futs):
            gid = futs[fut]
            try:
                _, out = fut.result()
                print(f"[OK] {gid} -> {out}")
                ok += 1
            except Exception as e:
                # 失败原因落盘：重跑时报缺失能一并打印上次为什么挂（别让人重跑还看不到原因）。
                try:
                    (GEN / f"clip_{gid}.err.json").write_text(
                        json.dumps({"gid": gid, "error": str(e)[:500],
                                    "at": datetime.now(timezone.utc).isoformat()},
                                   ensure_ascii=False, indent=2), encoding="utf-8")
                except Exception:
                    pass
                print(f"[FAIL] {gid}: {e}")
    print(f"\n并发完成 {ok}/{len(targets)} 条 (workers={workers})")
