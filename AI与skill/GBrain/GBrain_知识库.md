# GBrain 知识库

> **仓库地址：** [github.com/garrytan/gbrain](https://github.com/garrytan/gbrain)
> **作者：** Garry Tan（Y Combinator 总裁兼 CEO）
> **许可证：** MIT
> **语言：** TypeScript (98.2%)
> **Stars：** 11.1k+ ｜ **Forks：** 1.3k+

---

## 一、项目概述

GBrain 是一个为 AI Agent 设计的 **自组织知识大脑**。它解决的核心问题是：AI 大模型虽然聪明，但没有持久记忆。GBrain 让 AI Agent 拥有一个不断自我增长的知识图谱，能够摄入会议纪要、邮件、推文、语音通话和原创想法，在后台自动丰富每一个人物和公司的信息，修复引用并整合记忆。

**生产规模实绩：** 17,888 个页面、4,383 个人物、723 家公司、21 个定时任务自主运行，12 天内建成。

**核心理念：** "薄框架，胖技能"（Thin Harness, Fat Skills）——智能不在运行时，而在技能文件中。技能文件是编码了完整工作流的 Markdown 文档，Agent 读取并执行。

---

## 二、核心架构

### 2.1 三层架构

```
┌──────────────────┐    ┌───────────────┐    ┌──────────────────┐
│   Brain Repo     │    │    GBrain     │    │    AI Agent      │
│   (git)          │    │  (检索层)      │    │  (读/写)         │
│                  │    │               │    │                  │
│  Markdown 文件   │───>│  Postgres +   │<──>│  29 个技能       │
│  = 真理源        │    │  pgvector     │    │  定义如何使用大脑 │
│                  │<───│  混合搜索      │    │                  │
│  人类可随时      │    │  (向量+关键词  │    │  RESOLVER.md     │
│  阅读和编辑      │    │   +RRF)       │    │  路由意图到技能   │
└──────────────────┘    └───────────────┘    └──────────────────┘
```

- **Brain Repo（Git）：** 记录系统，每个 Markdown 文件即一个知识页面
- **GBrain（检索层）：** Postgres + pgvector，提供混合搜索
- **AI Agent：** 通过 29 个技能定义如何读写大脑

### 2.2 引擎架构

```
CLI / MCP Server
       |
  BrainEngine 接口（可插拔）
       |
  +----+----+
  |         |
PGLite   PostgresEngine
(默认)    (Supabase)
```

- **PGLite：** 嵌入式 Postgres，零配置，2 秒就绪
- **PostgresEngine：** Supabase 托管，适合 1000+ 文件或多设备场景
- 支持 `gbrain migrate --to supabase|pglite` 双向迁移

---

## 三、知识模型

每个页面遵循 **编译真理 + 时间线** 模式：

```markdown
---
type: concept
title: Do Things That Don't Scale
tags: [startups, growth, pg-essay]
---

Paul Graham 关于创业公司应早期做不可规模化事情的论点。
核心洞察：不可规模化的努力教会你用户真正想要什么。

---

- 2013-07-01: 发布于 paulgraham.com
- 2024-11-15: 在 W25 批次启动演讲中引用
```

- **分割线以上：** 编译真理（当前最佳理解，新证据时可重写）
- **分割线以下：** 时间线（仅追加的证据记录，永不编辑）

---

## 四、知识图谱（自动连线）

每次写入页面时，GBrain 自动从内容中提取实体引用并创建类型化链接，**零 LLM 调用**：

- `attended` — 会议页面 + 人物引用
- `works_at` — "CEO of X" 模式
- `invested_in` — "投资了" 模式
- `advises` — "顾问" 模式
- `founded` — "创办" 模式

**性能基准（BrainBench v1，240 页语料库）：**

| 指标 | 数值 |
|------|------|
| Precision@5 | 49.1% |
| Recall@5 | 97.9% |
| 相比禁用图谱 | +31.4 点 P@5 |

图谱能回答向量搜索无法触及的问题，如"谁在 Acme AI 工作？""Bob 投资了什么？"

---

## 五、搜索管线

混合搜索：向量 + 关键词 + RRF 融合 + 多查询扩展 + 4 层去重。

```
查询 → 意图分类器（实体/时间/事件/通用）
     → 多查询扩展（Claude Haiku）
     → 向量搜索 (HNSW cosine) + 关键词搜索 (tsvector)
     → RRF 融合: score = sum(1/(60+rank))
     → 余弦重排 + 编译真理提升 + 反向链接提升
     → 4 层去重 + 编译真理保证
     → 结果
```

---

## 六、29 个技能全览

### 6.1 始终在线

| 技能 | 功能 |
|------|------|
| **signal-detector** | 每条消息触发，并行运行廉价模型捕获原创思维和实体提及 |
| **brain-ops** | 先查大脑再调外部 API，读-丰富-写循环 |

### 6.2 内容摄入

| 技能 | 功能 |
|------|------|
| **ingest** | 薄路由器，检测输入类型并委派 |
| **idea-ingest** | 链接/文章/推文变脑页，含分析和交叉链接 |
| **media-ingest** | 视频/音频/PDF/截图/GitHub 仓库，转录+实体提取 |
| **meeting-ingestion** | 转录变脑页，每个参会者被丰富 |

### 6.3 大脑操作

| 技能 | 功能 |
|------|------|
| **enrich** | 分层丰富（Tier 1/2/3），人物/公司页面更新 |
| **query** | 3 层搜索+综合+引用，不会幻觉 |
| **maintain** | 周期健康检查：过时页面、孤儿、死链、引用审计 |
| **citation-fixer** | 扫描和修复格式不符的引用 |
| **repo-architecture** | 新文件存放位置决策协议 |
| **publish** | 分享页面为密码保护的 HTML |
| **data-research** | YAML 参数化结构数据研究 |

### 6.4 运营类

| 技能 | 功能 |
|------|------|
| **daily-task-manager** | P0-P3 优先级任务生命周期管理 |
| **daily-task-prep** | 晨间准备：日历预览+脑内上下文+任务回顾 |
| **cron-scheduler** | 调度错峰、时区感知静默时段 |
| **reports** | 带关键词路由的时间戳报告 |
| **cross-modal-review** | 第二模型质量门 + 拒绝路由 |
| **webhook-transforms** | 外部事件转脑页 |
| **testing** | 验证每个技能的 SKILL.md 合规性 |
| **skill-creator** | 创建新技能，MECE 检查 |
| **skillify** | "skillify it!" 元技能，10 步循环 |
| **skillpack-check** | Agent 可读的健康报告 |
| **smoke-test** | 8 项重启后健康检查+自动修复 |
| **minion-orchestrator** | 后台工作：Shell 作业和 LLM 子代理 |

### 6.5 身份与设置

| 技能 | 功能 |
|------|------|
| **soul-audit** | 6 阶段面试生成 SOUL.md / USER.md / ACCESS_POLICY.md |
| **setup** | 自动配置 PGLite 或 Supabase |
| **migrate** | 从 Obsidian/Notion/Logseq/Roam 等迁移 |
| **briefing** | 含会议上下文的每日简报 |

### 6.6 跨切约定（`skills/conventions/`）

- **quality.md** — 引用、反链、知名度门槛
- **brain-first.md** — 5 步查找先于任何外部 API
- **model-routing.md** — 哪个模型用于哪个任务
- **test-before-bulk.md** — 批量操作前先测 3-5 项
- **cross-modal.yaml** — 审查配对和拒绝路由链

---

## 七、Minions：持久化作业队列

内置于大脑的 Postgres 原生持久作业队列。核心路由规则：

> **确定性任务**（相同输入 → 相同步骤 → 相同输出）→ **Minions**（$0 token 开销）
> **判断性任务**（需要评估或决策）→ **子代理**（Sub-agents）

**生产对比数据（19 定时任务负载下）：**

| | Minions | sessions_spawn |
|---|---------|----------------|
| 耗时 | 753ms | >10,000ms（超时）|
| Token 成本 | $0.00 | ~$0.03/次 |
| 成功率 | 100% | 0% |
| 内存/作业 | ~2 MB | ~80 MB |

---

## 八、持久子代理：`gbrain agent`（v0.15）

子代理运行在崩溃后可恢复。每个 Anthropic 调用提交到 `subagent_messages`，每个工具调用提交到 `subagent_tool_executions`。支持 Fan-out 跨多分片并行。

```bash
gbrain agent run "summarize my last 10 journal pages"
gbrain agent run "analyze every page" \
  --fanout-manifest manifests/pages.json \
  --subagent-def analyzer
gbrain agent logs 1247 --follow --since 5m
```

---

## 九、数据集成

### 内置集成配方

| 配方 | 功能 |
|------|------|
| Public Tunnel | ngrok 固定 URL，用于 MCP + 语音 |
| Credential Gateway | Gmail + Calendar 访问 |
| Voice-to-Brain | 电话通话转脑页（Twilio + OpenAI Realtime） |
| Email-to-Brain | Gmail 转实体页面 |
| X-to-Brain | Twitter 时间线 + 提及 + 删除 |
| Calendar-to-Brain | Google Calendar 转每日页面 |
| Meeting Sync | Circleback 转录转脑页 |

### 语音功能

打电话给一个号码，AI 接听，拉取来电者的完整上下文，通话结束后自动生成含转录和实体检测的脑页。

---

## 十、安装方式

### 10.1 通过 AI Agent 安装（推荐）

支持平台：OpenClaw、Hermes Agent

```
Retrieve and follow the instructions at:
https://raw.githubusercontent.com/garrytan/gbrain/master/INSTALL_FOR_AGENTS.md
```

Agent 自动克隆仓库、安装、设置大脑、加载 29 个技能。约 30 分钟完成。

### 10.2 独立 CLI 安装

```bash
git clone https://github.com/garrytan/gbrain.git && cd gbrain && bun install && bun link
gbrain init                     # 本地大脑，2 秒就绪
gbrain import ~/notes/          # 索引你的 Markdown
gbrain query "what themes show up across my notes?"
```

> ⚠️ **不要使用** `bun install -g` 或 `npm install -g gbrain`。npm 注册表上有同名包抢注。

### 10.3 MCP Server 模式

```json
{
  "mcpServers": {
    "gbrain": { "command": "gbrain", "args": ["serve"] }
  }
}
```

支持 Claude Code、Cursor、Windsurf 等。

---

## 十一、常用命令速查

### 设置

| 命令 | 说明 |
|------|------|
| `gbrain init` | 创建大脑（默认 PGLite） |
| `gbrain migrate --to supabase` | 迁移到 Supabase |
| `gbrain upgrade` | 自我更新 |

### 页面操作

| 命令 | 说明 |
|------|------|
| `gbrain get <slug>` | 读取页面（模糊匹配） |
| `gbrain put <slug>` | 写入/更新（自动版本化） |
| `gbrain delete <slug>` | 删除页面 |
| `gbrain list [--type T]` | 列出页面 |

### 搜索

| 命令 | 说明 |
|------|------|
| `gbrain search <query>` | 关键词搜索 |
| `gbrain query <question>` | 混合搜索（向量+关键词+RRF） |

### 导入/导出

| 命令 | 说明 |
|------|------|
| `gbrain import <dir>` | 导入 Markdown（幂等） |
| `gbrain sync` | Git 到大脑增量同步 |
| `gbrain export` | 导出为 Markdown |

### 图谱

| 命令 | 说明 |
|------|------|
| `gbrain extract links --source db` | 批量回填链接 |
| `gbrain graph-query <slug>` | 类型化遍历 |
| `gbrain check-backlinks check` | 反链检查 |

### 作业（Minions）

| 命令 | 说明 |
|------|------|
| `gbrain jobs submit <name>` | 提交后台作业 |
| `gbrain jobs list` | 列出作业 |
| `gbrain jobs stats` | 健康仪表板 |
| `gbrain jobs smoke` | 一键健康检查 |
| `gbrain jobs supervisor` | 启动自动重启 worker |

### 技能管理（v0.19）

| 命令 | 说明 |
|------|------|
| `gbrain skillify scaffold <name>` | 创建 5 个桩文件 |
| `gbrain skillify check [path]` | 10 项审计 |
| `gbrain skillpack install <name>` | 安装技能+依赖 |
| `gbrain check-resolvable` | Resolver 全树审计 |
| `gbrain routing-eval --llm` | 路由准确性评估 |

### 管理

| 命令 | 说明 |
|------|------|
| `gbrain doctor` | 健康检查 |
| `gbrain stats` | 大脑统计 |
| `gbrain serve` | 启动 MCP 服务器 |
| `gbrain integrations` | 集成仪表板 |
| `gbrain dream` | 一次维护周期（定时任务友好） |

---

## 十二、Skillify 工作流

当 Agent 遇到新故障时：修复一次 → 说 "skillify it!" → 永久修复。

```bash
# 1. 搭建桩文件
gbrain skillify scaffold webhook-verify \
  --description "verify ngrok webhooks"

# 2. 编写真实逻辑和测试
$EDITOR skills/webhook-verify/scripts/webhook-verify.mjs

# 3. 运行 10 项审计
gbrain skillify check skills/webhook-verify/scripts/webhook-verify.mjs

# 4. 验证全树
gbrain check-resolvable
```

---

## 十三、与 GStack 的关系

- **GStack** = 编码技能（发布、审查、QA、调查）— 70,000+ Stars
- **GBrain** = 非编码技能（大脑操作、信号检测、摄入、丰富、定时任务）
- **`hosts/gbrain.ts`** = 桥接文件，让 GStack 的编码技能在编码前先查大脑

---

## 十四、关键文档索引

| 文档 | 路径 | 用途 |
|------|------|------|
| RESOLVER.md | `skills/RESOLVER.md` | 技能调度入口 |
| AGENTS.md | `AGENTS.md` | 非 Claude Agent 操作协议 |
| CLAUDE.md | `CLAUDE.md` | Claude Code 专用指南 |
| GBRAIN_SKILLPACK.md | `docs/GBRAIN_SKILLPACK.md` | 参考架构全书 |
| GBRAIN_V0.md | `docs/GBRAIN_V0.md` | 完整产品规格 |
| GBRAIN_RECOMMENDED_SCHEMA.md | `docs/GBRAIN_RECOMMENDED_SCHEMA.md` | Brain Repo 目录结构 |
| THIN_HARNESS_FAT_SKILLS.md | `docs/ethos/THIN_HARNESS_FAT_SKILLS.md` | 架构哲学 |
| ENGINES.md | `docs/ENGINES.md` | 可插拔引擎接口 |
| CHANGELOG.md | `CHANGELOG.md` | 版本历史 |
| llms.txt | `llms.txt` | LLM 文档地图 |
| llms-full.txt | `llms-full.txt` | 文档地图+核心内容内联 |

---

## 十五、项目生态

| 项目 | 说明 |
|------|------|
| [gbrain](https://github.com/garrytan/gbrain) | 知识大脑核心 |
| [gbrain-evals](https://github.com/garrytan/gbrain-evals) | BrainBench 评估套件 |
| [gstack](https://github.com/garrytan/gstack) | Claude Code 编码技能（97.8k Stars） |
| [alphaclaw](https://github.com/chrysb/alphaclaw) | OpenClaw 部署工具 |

---

*知识库创建于 2026-05-17，基于 garrytan/gbrain 仓库公开内容整理。*
