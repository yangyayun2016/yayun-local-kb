---
name: "ppt-deck-builder"
description: "Create polished non-AI-looking PPT decks with narrative, visual style, and PPTX export workflow."
user-invocable: true
---

# PPT Deck Builder

Use when the user asks to create, redesign, polish, or export a PowerPoint/PPTX deck, especially when they care about business storytelling, visual taste, non-generic design, or presentation-ready output.

## Core Principle

Do not start with generic title-and-bullet slides. Build a deck like a director:

- one audience
- one decision or outcome
- one storyline
- one visual system
- one clear takeaway per slide

Avoid AI-looking filler: vague buzzwords, evenly weighted bullet blocks, decorative gradients without meaning, random icons, stock-looking diagrams, and pages that say everything but decide nothing.

## First Pass: Clarify or Infer

If the user provides enough context, proceed without asking. If critical context is missing, ask at most two questions.

Useful inputs:

- audience: boss, team, client, investor, operator, seller
- purpose: explain, persuade, report, train, sell, decide
- format: 16:9 PPTX by default
- length: default 8-12 slides unless requested
- language: Chinese by default for Jimmy
- tone: consulting, SaaS/product, executive brief, workshop, investor, operating manual
- source materials: notes, documents, screenshots, reports, CSV/XLSX, diagrams, links

## Deck Workflow

1. Define the deck promise.
   - Write the one-sentence answer the deck must prove.
   - Example: “知识库不是资料仓库，而是 Amazon Ads Director 持续优化的证据与经验引擎。”

2. Build the storyline.
   - Prefer: context → problem → evidence → diagnosis → decision → action → expected result.
   - For strategy decks: current state → tension → insight → model → roadmap → ask.
   - For reporting decks: headline → KPI movement → drivers → risks → actions → next checkpoint.

3. Create a slide map before making slides.
   - Each slide gets: page title, takeaway, visual type, key content, speaker note.
   - Use action titles, not labels.
   - Bad: “广告优化流程”
   - Good: “Director 用知识库把一次性优化变成可复利的判断系统”

4. Choose a visual direction.
   - Recommend 2-3 directions when not specified.
   - Examples:
     - Executive SaaS: white canvas, blue/green accents, cards, dashboards, thin lines.
     - Consulting brief: white/black, strong hierarchy, big numbers, minimal decoration.
     - Premium dark: dark navy, cyan/green highlights, glass cards, system architecture feel.
     - Operator playbook: clean grids, checklists, status labels, workflow arrows.

5. Design pages with constraints.
   - One message per slide.
   - Max 3-5 content blocks.
   - Use whitespace deliberately.
   - Prefer diagrams, tables, timelines, scorecards, and before/after layouts over bullet lists.
   - Replace generic icons with labels, metrics, or meaningful shapes.
   - Every chart/diagram must support the slide takeaway.

6. Produce artifacts in stages.
   - Stage A: outline + slide map.
   - Stage B: visual style board or 1-2 sample slides.
   - Stage C: full deck draft.
   - Stage D: export PPTX and optionally PNG/PDF previews.

## Page Type Library

Use these instead of default bullet pages:

- Executive summary: 3 cards: conclusion, evidence, decision.
- Problem framing: current state vs desired state with gap.
- Diagnostic chain: metric symptom → root cause → implication → action.
- Operating loop: input → knowledge base → director → action → feedback.
- Architecture map: layers, responsibilities, data flow, decision flow.
- Prioritization matrix: impact vs effort, risk vs upside.
- KPI scorecard: metric, current, target, movement, interpretation.
- Action table: owner, action, evidence, expected impact, review date.
- Roadmap: now / next / later or week 1 / month 1 / quarter 1.
- Decision slide: recommendation, alternatives rejected, ask.

## Writing Style

Use specific business language.

Prefer:

- “把 Auto 里的有效词转入 Exact 承接”
- “压缩无单高花费探索层预算”
- “知识库记录动作结果，避免重复试错”
- “Director 基于证据输出下一轮动作”

Avoid:

- “赋能增长”
- “提升效率” without a mechanism
- “打造闭环生态”
- “智能化升级” unless tied to concrete workflow

## Visual Anti-AI Checklist

Before exporting, check:

- Does each slide have a sharp action title?
- Would a busy executive understand the point in 5 seconds?
- Is there any vague filler language?
- Are there more than 5 bullets on a slide?
- Are all icons necessary and consistent?
- Are colors used as meaning, not decoration?
- Are diagrams aligned and readable?
- Is there a consistent grid, margin, font scale, and accent color?
- Does the deck feel like a human made tradeoffs?

## PPTX Generation

When asked to generate an actual PPTX:

1. Inspect the workspace for existing deck assets/templates if relevant.
2. Prefer deterministic generation with local code.
3. Use a workspace-local dependency such as `pptxgenjs` only when needed; do not install globally.
4. Save outputs in the workspace with clear names.
5. Export or render at least one preview when possible.
6. Verify the file exists and report the path as `MEDIA:<path>`.

Recommended output files:

- `<topic>_deck.pptx`
- `<topic>_outline.md`
- `<topic>_preview.png` or `<topic>_preview.pdf` when available

## When Source Data Is Business/Ads Data

If the deck is about Amazon Ads, ASIN Center, LT traffic layers, advertising diagnostics, or search-term actions, combine this skill with the Amazon Ads optimization workflow:

- Treat uploaded reports as source of truth.
- Use ASIN/L2/L3/lifecycle/inventory/rating/margin as context gates.
- Map advertising evidence into LT layers before making claims.
- Separate diagnosis, architecture action, and execution checklist.

## Default Deliverable Shape

Unless the user asks otherwise, reply with:

1. deck objective
2. recommended style direction
3. slide map
4. what files were generated or what confirmation is needed

For actual deck creation, continue until a PPTX or named blocker exists.
