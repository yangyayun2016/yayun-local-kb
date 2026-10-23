"""把本地图/视频传成公网 HTTPS 直链（生成接口要外链）。
litterbox 临时图床（免注册）跑通即可；生产换火山 TOS 只换本函数实现，接口不变。
有效期取 24h：seedance 排队可能超 1h，1h 链接会过期→首帧 URL 失效→静默废片。
同一张图（如跨镜复用的 g1 锚点）只上传一次：进程内按 路径+mtime 缓存直链，省得并发重复传。
"""
import requests
import time
from pathlib import Path

LITTERBOX = "https://litterbox.catbox.moe/resources/internals/api.php"
RETRYABLE = (429, 500, 502, 503, 504)
_CACHE = {}   # (abspath, mtime) -> url，避免 8 路并发把同一张锚点图重复上传


def upload(path, max_retries=5, wait=10) -> str:
    path = Path(path)
    try:
        key = (str(path.resolve()), path.stat().st_mtime)
        if key in _CACHE:
            return _CACHE[key]
    except OSError:
        key = None
    last = None
    for i in range(max_retries):
        try:
            with open(path, "rb") as f:
                resp = requests.post(
                    LITTERBOX,
                    data={"reqtype": "fileupload", "time": "24h"},
                    files={"fileToUpload": (path.name, f)},
                    timeout=120,
                )
            if resp.ok:
                url = resp.text.strip()
                if not url.startswith("http"):
                    raise RuntimeError(f"上传失败: {url}")
                if key:
                    _CACHE[key] = url
                return url
            last = requests.HTTPError(f"{resp.status_code}: {resp.text[:200]}")
            if resp.status_code not in RETRYABLE:
                raise last
        except requests.RequestException as e:
            last = e
        print(f"  上传失败，{wait}s 后重试 ({i + 1}/{max_retries}): {last}")
        time.sleep(wait)
    raise RuntimeError(f"上传持续失败超 {max_retries} 次: {path} ({last})")


if __name__ == "__main__":
    import sys
    print(upload(sys.argv[1]))
