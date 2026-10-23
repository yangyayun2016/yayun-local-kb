"""每个生成单元的「机器可读分镜」：首帧文生图 prompt + 图生视频运镜 prompt。

来源二选一：
- 有 `_work/storyboard.json` → SHOT_PROMPTS / OVERLAYS 全从它派生。
  每个 unit 的 frame_prompt 只写「场景+主体+构图」，本文件自动追加全局 style + neg，
  省得 agent 每镜重抄，也强制跨镜风格一致。
- 没有 → 回退内置样例（爆款视频.mp4：格斗青年 × 墙绘活化对打）。

铁律：分镜创意是引擎命根。后期叠字用 OVERLAYS（ffmpeg drawtext），绝不让模型画字。
"""
import json

from pipeline.storyboard import load as _load_sb

_SB = _load_sb()

if _SB:
    _style = _SB.get("style", "")
    _neg = _SB.get("neg", "")

    # ── 护栏 0：爆款点必须先填 ──────────────────────────────────────────────
    # 上一版复刻丢爆点（换装/转身做成了静态白底清单）就是因为没人先回答「为什么火」。
    _hook = _SB.get("爆款点", {})
    _hook_text = json.dumps(_hook, ensure_ascii=False)
    if (not _hook) or ("TODO" in _hook_text):
        raise ValueError(
            "storyboard.json 的『爆款点』没填完（为空或仍含 TODO）。\n"
            "  这是复刻的命根：先看原片回答『这视频为什么火？爆点是什么动作？』，\n"
            "  把 爆款点.一句话 / 核心机制 / 必须复刻的动作 / 千万别做成 填满，再往下生成。")

    # 爆点里出现这些『动作类』关键词 → 全片必须有对应的身体动作，不能整片做成静态。
    # 注意：故意不含「运镜」这种几乎任何视频都会写到的泛词，否则护栏会误伤一堆本该静态的片。
    _MOTION_WORDS = ("换装", "转场", "转身", "转圈", "旋转", "一起转", "甩", "跳",
                     "翻", "反差", "前后", "变身", "切换", "卡点", "踩拍", "起身", "走动", "舞")
    _hook_is_motion = any(w in _hook_text for w in _MOTION_WORDS)
    # 逃生口（tradeoff）：真的就是静态片型（如纯产品平铺、口播大头）→ 顶部写 "confirm_static": true 放行，
    # 既不误杀合法静态片，又逼你『显式确认』而不是默认绕过。
    _confirm_static = bool(_SB.get("confirm_static", False))

    SHOT_PROMPTS = {}
    OVERLAYS = {}
    _motion_units = 0
    for _u in _SB["units"]:
        _gid = _u["gid"]
        _fp = _u.get("frame_prompt", "").strip()
        _pp = _u.get("prompt", "").strip()
        _act = (_u.get("动作") or "").strip()
        _kind = (_u.get("kind") or "").strip()
        # kind 必填：它决定模型分档(Mini/Fast)和分辨率，留着 TODO 会把人物镜误判成无脸镜降到 Mini 崩脸。
        if (not _kind) or ("TODO" in _kind) or (_kind not in ("product", "person", "scene")):
            raise ValueError(
                f"storyboard.json 的 {_gid} 的 kind 没填对（当前：{_kind or '空'}）。"
                f"必须是 product / person / scene 之一——它决定走哪档模型和分辨率。")
        # 护栏：分镜没填完就别往下跑——空 prompt / 空动作 / 残留 "TODO" 都会被当真 prompt 喂 API 烧钱产垃圾。
        # （动作字段也纳入完整性校验：上一版正是因为它没被检查，留着 TODO 也能过闸。）
        if (not _fp or not _pp or not _act
                or "TODO" in _fp or "TODO" in _pp or "TODO" in _act):
            raise ValueError(
                f"storyboard.json 的 {_gid} 分镜没填完（frame_prompt / prompt / 动作 为空或仍含 'TODO'）。"
                f"先让 agent 看 _work/storyboard/{_gid}_a/_b/_c.jpg，写清『动作』再写 frame_prompt 和 prompt，再生成。")
        # 护栏 1：这一镜到底有没有动作——以『动作字段或 prompt 命中动作词』为准（不再用脆弱的子串 hack）。
        if any(w in _act for w in _MOTION_WORDS) or any(w in _pp for w in _MOTION_WORDS):
            _motion_units += 1
        if _style:
            _fp = f"{_fp} Style: {_style}."
        if _neg:
            _fp = f"{_fp} Constraints: {_neg}."
        SHOT_PROMPTS[_gid] = {
            "dur": round(_u["end"] - _u["start"], 3),
            "frame_prompt": _fp,
            "prompt": _pp,
        }
        if _u.get("overlays"):
            OVERLAYS[_gid] = list(_u["overlays"])

    # 护栏 1 总判：爆点是『动作型』，但没有一镜写了动作 → 拦下（除非显式 confirm_static）。
    # 这正是上一版把换装做成静态白底清单、人不跟着转的失败模式，必须挡回去。
    if _hook_is_motion and _motion_units == 0 and not _confirm_static:
        raise ValueError(
            "⚠ 爆款点是『动作型』（含 换装/转身/转场/卡点 等），但没有任何一镜的『动作』或 prompt 写了身体动作。\n"
            "  这就是上一版丢爆点的失败模式（把换装做成了静态白底清单，人不跟着转）。\n"
            "  请把爆点动作写进对应镜头（如『正面起身→原地转一圈→背对镜头，转回正面已换好下一套』），再生成。\n"
            "  Seedance 首帧锁定，不写死动作就不会动。\n"
            "  （如果这条片『真的就是静态展示』，在 storyboard.json 顶部加一行 \"confirm_static\": true 显式放行。）")
else:
    # ====================== 内置样例：爆款视频.mp4 ======================
    IDENTITY = (
        "the same muscular young male street fighter, mid-20s, short mohawk undercut with shaved "
        "sides, arm tattoos, red sleeveless tank top, dark slim jeans, white sneakers, white cloth "
        "hand wraps on both fists, lean athletic build, gritty confident expression, "
        "consistent face, consistent tattoos, same hairstyle across all shots"
    )

    ALLEY = (
        "the same gritty urban back-alley: weathered brick and concrete walls fully covered by a huge "
        "black-and-white charcoal graffiti mural of muscular warriors, a red scooter parked against the "
        "wall, scattered debris and oil drums, overhead natural daylight, cinematic urban grime"
    )

    FRAME_STYLE = (
        "photorealistic cinematic 16:9 video-game-trailer first frame, shallow depth of field, dynamic "
        "handheld realism, subtle film grain, high-contrast slightly desaturated urban color grade, "
        "realistic skin, muscle and fabric detail"
    )

    NEG = (
        "no text, no logo, no watermark, no on-screen letters, no subtitles, no extra people, "
        "no distorted hands, no extra fingers, no warped anatomy, no duplicated limbs"
    )

    SHOT_PROMPTS = {
        "g1": dict(
            dur=8.00,
            frame_prompt=(
                f"Use case: photorealistic-natural. Asset type: first frame for cinematic 16:9 video. "
                f"Scene/backdrop: {ALLEY}. Subject: {IDENTITY}, walking past the parked red scooter "
                f"along the mural wall, mid-stride, body slightly turned toward camera. "
                f"Composition/framing: wide-to-medium tracking shot, full body visible, the giant charcoal "
                f"mural filling the background. Style: {FRAME_STYLE}. Constraints: {NEG}. "
                f"Do not render any title card or letters; title is added in post."
            ),
            prompt=(
                "电影感横屏16:9，建立镜：格斗青年从红色踏板摩托旁走过，沿着整面黑白炭笔涂鸦墙前行。"
                "手持环绕跟拍，镜头从全景缓慢推近到中景，他步伐沉稳、眼神锐利。脏污后巷、自然顶光、电影颗粒感，"
                "人物脸型/纹身/红背心保持一致。画面不出现任何文字、logo 或水印。"
            ),
        ),

        "g2": dict(
            dur=6.00,
            frame_prompt=(
                f"Use case: identity-preserve. Asset type: first frame for cinematic 16:9 video. "
                f"Reference intent: same fighter as g1, same face, tattoos, red tank top. "
                f"Scene/backdrop: {ALLEY}. VFX: one of the black-and-white charcoal mural warriors is "
                f"peeling off the wall and coming alive as a semi-translucent monochrome painted fighter "
                f"stepping toward the hero. Subject: {IDENTITY}, in a boxing guard, fist raised mid-jab "
                f"toward the living mural figure. Composition: medium action shot, both figures in frame. "
                f"Style: {FRAME_STYLE}. Constraints: {NEG}."
            ),
            prompt=(
                "电影感横屏16:9，动作A：墙上黑白炭笔武者①剥离墙面、半透明地活过来扑向主角；"
                "主角摆出拳架，快速出直拳与之对打。手持微晃配合出拳节奏，镜头小幅推拉跟随冲击点，"
                "活化人物是单色炭笔质感、半透明，与真实主角形成黑白vs彩色对比。同一后巷涂鸦墙，人物一致，不出现文字。"
            ),
        ),

        "g3": dict(
            dur=5.80,
            frame_prompt=(
                f"Use case: identity-preserve. Asset type: first frame for cinematic 16:9 video. "
                f"Reference intent: same fighter as g1/g2, same face, tattoos, red tank top. "
                f"Scene/backdrop: {ALLEY}. VFX: a second charcoal mural warrior has come alive; faint "
                f"monochrome motion-trails where the murals move. Subject: {IDENTITY}, caught mid spinning "
                f"capoeira-style kick, body rotating, one leg extended toward the living mural figure. "
                f"Composition: dynamic low-angle action shot, full body. Style: {FRAME_STYLE}. Constraints: {NEG}."
            ),
            prompt=(
                "电影感横屏16:9，动作B：第二个墙绘武者②活化，主角顺势做卡波耶拉式回旋踢/侧身闪避，"
                "身体大幅旋转、白球鞋扫向活化人物。低角度手持快速横移，运动衔接无硬切，墙绘移动处留单色拖影。"
                "同一后巷、同一主角，黑白活化人物vs彩色真人对比，画面无文字无水印。"
            ),
        ),

        "g4": dict(
            dur=5.83,
            frame_prompt=(
                f"Use case: identity-preserve. Asset type: first frame for cinematic 16:9 video. "
                f"Reference intent: same fighter as g1, same face, tattoos, red tank top, white hand wraps. "
                f"Scene/backdrop: {ALLEY}, mural slightly out of focus behind. Subject: {IDENTITY}, hero "
                f"close-up, giving a confident thumbs-up with a slight smirk, in-ear earphones visible. "
                f"Composition: tight close-up to chest-up, shallow depth of field, the hero centered. "
                f"Style: {FRAME_STYLE}. Constraints: {NEG}."
            ),
            prompt=(
                "电影感横屏16:9，英雄特写：主角自信竖起大拇指、嘴角微扬，戴着入耳耳机，背景涂鸦墙虚化。"
                "镜头从中景缓慢推近到胸上特写，浅景深，光打在脸和肌肉上。脸型/纹身/红背心严格一致，"
                "稳定手持质感，画面干净无文字无水印。"
            ),
        ),

        "g5": dict(
            dur=5.17,
            frame_prompt=(
                f"Use case: photorealistic-natural. Asset type: first frame for cinematic 16:9 video. "
                f"Scene/backdrop: {ALLEY}, but EMPTY — no fighter, the quiet back-alley with the charcoal "
                f"mural wall and red scooter, soft natural light, slight haze. Composition: clean static "
                f"wide establishing shot leaving open central space for a large title to be overlaid in post. "
                f"Style: {FRAME_STYLE}. Constraints: {NEG}. Absolutely no text in the image."
            ),
            prompt=(
                "电影感横屏16:9，片尾空镜：无人后巷，黑白涂鸦墙与红色踏板摩托，安静、轻微薄雾，固定机位。"
                "中央留出大片空间用于后期叠片名大字。光线柔和电影感，画面绝不出现任何文字。"
            ),
        ),
    }

    # 后期 ffmpeg 叠字，绝不让模型画字。
    # ⚠ 原片片尾大字是 SEGA 商标，不要复现——换成你自己的虚构片名（改这一行即可）。
    OVERLAYS = {
        "g5": ["STREET CROSSROADS"],
    }
