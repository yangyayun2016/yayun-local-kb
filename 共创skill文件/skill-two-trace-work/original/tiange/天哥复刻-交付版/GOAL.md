# /goal · 目标式入口

> 用「给一句目标」的方式干活：你不写步骤，只写**目标**。
> Codex 进本目录会自动读 `AGENTS.md`（引擎手册）+ `tiange_fuke.md`（天哥复刻 skill），把目标全自动展开跑完。
> 装成斜杠命令（一次性）：`cp GOAL.md ~/.codex/prompts/goal.md`，以后任意目录敲 `/goal`。

---

## 怎么写（就一句）
```
/goal 复刻 <视频文件>，跑完输出上下屏对比，上是我的复刻、下是原片
```

## 复制即用
把爆款视频拖进本目录，改文件名即可：
```
/goal 复刻 爆款视频.mp4，跑完输出上下屏对比，上是我的复刻、下是原片
```

## Codex 收到后自动做（对照 AGENTS.md 六步）
1. `python -m pipeline.auto_storyboard <视频>` —— 自动拆骨架 + 合并生成单元 + 抽关键帧 + 出 storyboard 脚手架。
2. 看关键帧把 `storyboard.json` 的分镜 TODO 补满（片型 / 全局一致性 / 每镜 prompt / 角标）。
3. 内置 `images` 生每单元首帧（先 g1 主形象，其余参考它保一致）。
4. **先 go/no-go** 跑 g1 验证锁形象，OK 再 `python -m pipeline.gen_video` 全量。
5. `python -m pipeline.assemble` —— 裁切+拼接+叠角标 + **自动出上下屏对比片** → `_work/final/`。
6. 回报：成片路径、每单元 seed/抽卡次数、本条真实 API 成本。

> skill 定义见 `tiange_fuke.md`（天哥·复刻术）。`/goal` 与 `/tiange_fuke` 都能进，效果一样。
