---
name: tiange-fuke-zh
description: |
  中文爆款短视频复刻 skill，用于把用户提供的爆款视频拆解成爆点、分镜骨架、关键动作、运镜节奏和可替换素材，再通过本 skill 自带 pipeline 与 Seedance/APIMart/火山方舟生成画面全新的复刻片和上下屏对比片。Use when 用户说复刻、爆款复刻、天哥复刻、复刻这条视频、拆分镜、生成上下屏对比、产品视频复刻、换装/转场/宠物/Vlog/单主体画面驱动视频复刻；不适合口播对口型、高密度卡点快剪、多人复杂剧情或未经授权真人换脸。
---

# 天哥复刻

## 核心目标

把一条爆款视频复刻成“骨架神似、画面全新”的新片，并输出上下屏对比片。复刻逻辑是：先抓爆点，再锁骨架，最后替换血肉。

## TRACE 执行原则

- Trust: 源片只读；API key 只放 `_work/.secret.env`；真人样貌、换脸、商标、字幕、音乐和平台发布必须遵守授权与 AI 标识要求。
- Reliability: 先拆片和抽关键帧，再填爆款点与动作分镜；先跑 g1 go/no-go，确认形象和爆点动作生效后再批量生成。
- Adaptability: 只接画面驱动、单主体、可通过分镜和动作复刻的视频；遇到口播、复杂多人剧情、高密度卡点时先说明 tradeoff。
- Convention: 运行入口和详细规则按需读取 `references/`；可执行流水线在 `pipeline/`，样片在 `assets/sample-videos/`。
- Effectiveness: 输出必须包含复刻片路径、上下屏对比片路径、失败镜头/重跑建议、成本估算和需要用户确认的取舍。

## 使用流程

1. 确认用户提供了视频文件路径和复刻目标：产品、人物、宠物、换装、转场或 Vlog。
2. 如用户第一次使用，先读 `references/setup-and-api.md`，确认 ffmpeg、Python 依赖、APIMart/火山方舟 key 和 Mini 验证。
3. 读 `references/engine-workflow.md`，按七步流水线执行。
4. 先运行：

```bash
python -m pipeline.auto_storyboard "<视频绝对路径>"
```

5. 查看 `_work/storyboard/` 中每镜首/中/尾三帧，先填写 `_work/storyboard.json` 顶部“爆款点”字段，再补每镜动作、frame_prompt、prompt、overlays。
6. 用宿主内置生图或 `python -m pipeline.gen_frames` 生成首帧。
7. 先跑单镜检查：

```bash
python -m pipeline.gen_video g1
python -m pipeline.preview g1
```

8. 确认通过后再跑全量：

```bash
python -m pipeline.run
```

成片和上下屏对比片输出到 `_work/final/`。

## 必读参考

- 新用户、安装和 API：`references/setup-and-api.md`
- 七步流水线、爆点和分镜规则：`references/engine-workflow.md`
- 适用边界、合规和发布红线：`references/guardrails-and-fit.md`

## 关键防线

- 不要跳过“爆款点”。换装、转身、转场、前后反差这类动作必须写进每镜 prompt。
- 不要让模型生成文字；产品卖点、标题、角标用 storyboard 的 overlays 后期叠。
- 不要静默降级。生成失败、被策略拦截、主体崩坏或爆点动作做不出来时，暂停并给用户选择：换提示词、降低相似度、简化动作、换片或重跑单镜。
- 不要直接复用原片人脸、商标、字幕、音乐。复刻是再创作，不是搬运或逐帧克隆。
- 真人/换脸仅限本人或已授权素材；发布到需要 AI 标识的平台时启用 `ai_label` 或 `FK_AI_LABEL=1`。

## 默认回复结构

```text
复刻进度：
爆点判断：
分镜/动作处理：
go/no-go 结果：
输出文件：
成本估算：
风险与需确认：
```
