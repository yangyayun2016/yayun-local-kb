# 复刻流水线

## 方法论

复刻 = 爆点 + 骨架 + 血肉。

- 爆点：视频为什么火，必须先写清。常见是换装、转身、转场、反差、产品冲击点、宠物动作。
- 骨架：切点、时长比例、运镜、视觉冲击点和转场节奏。
- 血肉：主体、产品、人物、环境、配色、文案和卖点全部替换。

## 七步流水线

1. 自动拆骨架：

```bash
python -m pipeline.auto_storyboard "<视频绝对路径>"
```

产物：

- `_work/storyboard.json`
- `_work/storyboard/g*_a.jpg`
- `_work/storyboard/g*_b.jpg`
- `_work/storyboard/g*_c.jpg`

2. 填爆款点。

先看整段原片和每镜首/中/尾三帧，补齐 storyboard 顶部“爆款点”四项：一句话、核心机制、必须复刻的动作、千万别做成什么。

3. 填每镜分镜。

每个 unit 必须写：

- 动作：是否转身、换装、推拉、甩动、遮挡、宠物动作。
- 片型：product / person / scene。
- frame_prompt：首帧英文提示词。
- prompt：视频动作和运镜提示词。
- overlays：后期叠字，不让模型画字。

4. 生成首帧。

有内置生图能力时，按每镜 `frame_prompt` 生成 `_work/frames/frame_<gid>.png`。无内置生图能力时跑：

```bash
python -m pipeline.gen_frames
```

5. 单镜 go/no-go。

```bash
python -m pipeline.gen_video g1
python -m pipeline.preview g1
```

确认形象稳定、爆点动作生效、主体不崩，再继续。

6. 全量生成。

```bash
python -m pipeline.gen_video
```

已生成片段会自动跳过。单镜崩坏时只重跑对应 gid。

7. 拼接和上下屏对比。

```bash
python -m pipeline.assemble
```

或一键跑后半程：

```bash
python -m pipeline.run
```

输出在 `_work/final/`。

## 换装/转场打法

换装类爆点不能做成静态展示。优先用两种方式：

- 单镜内转换：写清正面起身、原地转身、服装在转身中变化、回到正面已换好。
- 拼接转场：上一镜转到背对镜头，下一镜从背对镜头的新造型起，切点藏在背对或快速转身处。

无论哪种，人必须跟着转；如果 prompt 只写服装展示，必须重写。

## 失败处理

- ffmpeg 缺失：让用户先安装。
- key 缺失：提示补 `_work/.secret.env`，不要询问或展示密钥。
- 爆款点未填：停下补爆点。
- storyboard JSON 坏：先修 JSON。
- 被策略拦截：给出改提示词、降相似度、换镜头或换片的选择。
- 人脸崩坏：换 seed 或只重跑该镜，必要时切 Fast/Pro。
