"""一次性确认 Mini 档能用（火山方舟 Doubao-Seedance-2.0-mini，资源包或按量付费）。

只发一个最小任务：480p / 4s / 纯文字 / 无人脸，花费极小（几百~几千 token）。
跑通 = Mini 的 model id 正确、ARK 视频链路通；跑挂会把 ARK 的原始报错打出来，方便对症。
用法（先在 _work/.secret.env 填好两条 key（APIMART_TOKEN + ARK_API_KEY））：
    python -m pipeline.verify_mini
"""
import sys
import time

from pipeline.config import ROUTES
from pipeline import gen_video

ARK = ROUTES["ark"]


def main():
    if not ARK["token"]:
        sys.exit("没读到 ARK_API_KEY。在 _work/.secret.env 写一行 ARK_API_KEY=你的key。")

    mini = ARK["models"]["mini"]
    print(f"[verify] 试 Mini：model={mini}  480p 9:16 4s 纯文字（最小花费）")
    print(f"[verify] 端点={ARK['gen_endpoint']}")
    try:
        tid = gen_video.submit(
            "一只橘猫在白色窗台上慵懒地伸懒腰，午后阳光，浅景深特写，无文字。",
            duration=4, route="ark", size="9:16", resolution="480p", model=mini)
    except Exception as e:
        msg = str(e)
        print(f"\n❌ 提交失败：{msg[:400]}")
        if "model" in msg.lower() or "not found" in msg.lower() or "InvalidParameter" in msg:
            print("→ 八成是 Mini 的 model id 不对。去火山方舟控制台看 Seedance 2.0 mini 的确切 Model ID，"
                  "把它写进 _work/.secret.env：FK_MODEL_MINI=正确id（不用改代码）。")
        sys.exit(1)

    # 轮询读完整响应（要拿 usage / 状态）
    start, wait = time.time(), 6
    while time.time() - start < 480:
        data = gen_video._req("GET", f"{ARK['task_endpoint']}/{tid}", ARK["token"]).json()
        st = data.get("status")
        print(f"[{int(time.time()-start):>4}s] status={st}")
        if st in ("succeeded", "success", "completed"):
            usage = data.get("usage") or {}
            print(f"\n✅ Mini 可用！model id 正确：{mini}")
            print(f"   本次 token：{usage.get('total_tokens', '未知')}（你的包共 1400 万 token）")
            print("   下一步：直接复刻即可。无人脸镜会自动走 Mini（省钱），人脸镜走 Fast。")
            print("   想整片都用 Mini（最省，但人脸弱）：在 _work/.secret.env 写 FK_MODEL_TIER=mini。")
            return
        if st in ("failed", "error", "cancelled", "expired"):
            sys.exit(f"\n❌ 任务失败：{data}")
        time.sleep(wait); wait = min(wait * 2, 30)
    sys.exit("\n轮询超时（队列可能很忙）。稍后重跑 python -m pipeline.verify_mini。")


if __name__ == "__main__":
    main()
