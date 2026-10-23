---
name: tiange_fuke
description: 天哥·复刻术 — 爆款视频复刻引擎。扔一条爆款视频，自动「拆骨架→自动分镜→换血肉生成→拼接→上下屏对比」，输出骨架神似、画面全新的新片 + 上下屏对比片（上复刻/下原片）。触发词：复刻、爆款复刻、天哥复刻、复刻这条视频、把这个视频复刻、上下屏对比。
---

# 天哥·复刻术 · 爆款视频复刻引擎

扔一条爆款视频，全自动复刻成「骨架神似、画面全新」的新片 + 上下屏对比片。
**复刻 = 先抓爆点（为什么火）+ 锁死骨架（切点/时长/运镜/冲击点）+ 替换血肉（主体/环境/配色/文案）。**
> 啥也不懂的新手 → 直接看 `新手必读-大白话.md`，三句话上手。

## 运行位置
本 skill 的流水线代码（`pipeline/`）和引擎手册（`AGENTS.md`）就在本目录 `~/.codex/skills/天哥复刻/`。
执行时 `cd` 到本目录再跑，目标视频用**绝对路径**传给 auto_storyboard（不必移动源片，源片只读）。
若当前项目自带 `AGENTS.md` + `pipeline/`（如「爆款复刻」项目），在那个项目里跑也一样。

## 七步流水线（详见同目录 AGENTS.md）
1. `python -m pipeline.auto_storyboard "<视频绝对路径>"` — 自动拆骨架 + 合并/均匀切生成单元 + 每镜抽『首/中/尾 3 帧』 + 出 `_work/storyboard.json` 脚手架。
   ⭐ **先填『爆款点』**：看原片回答「这视频为什么火」，把顶部 `爆款点` 四项填满（没填满会被护栏拦下）。
2. 对比每镜 `g*_a/_b/_c.jpg` 三帧 → 写清每镜『动作』；补满片型 / identity / scene / 每镜 frame_prompt+prompt / overlays。
   ⚠ 爆点是动作（换装/转身）时，prompt 必须把动作写死——Seedance 首帧锁定，不写就不动。
3. 用你内置 `images` 生每单元首帧 → `_work/frames/frame_<gid>.png`（先 g1 主形象，其余参考它保一致）；无内置生图则 `python -m pipeline.gen_frames`。
4. 🔴 go/no-go：`python -m pipeline.gen_video g1`，确认首帧锁形象+爆点动作生效、主体不崩，OK 再全量。
5. `python -m pipeline.gen_video` — 全量生视频（已并发，已生成的自动跳过；无人脸镜走 Mini、有人脸镜走 Fast 省钱）。
6. `python -m pipeline.assemble` — 裁回真实时长 + 拼接 + 叠角标 + 自动出上下屏对比片 → `_work/final/`。
> 第 5+6 步可一条命令跑完：`python -m pipeline.run`。

## 约束
- 密钥只在 `_work/.secret.env`。默认 480p（要高清改 storyboard.json 的 gen_resolution）。
- **先抓爆点**：换装/转身/转场这类「动作」就是爆点，必须 1:1 复刻，绝不做成静态展示（护栏会拦）。
- **省钱分流**：无人脸镜→Mini（最便宜，但人脸弱）、有人脸镜→Fast、换脸→Pro；按 token 计费，一条约几元~十几元。
- 源片只读，不改不移不删。抽卡崩坏只重跑那个单元，不整片返工。
- 🛑 生成不了或被策略拦的镜，停下来把 tradeoff 抛给用户，不要静默降级。
- 产品文字/片名用 ffmpeg overlay 后期叠，绝不让模型画字。

by 天哥
