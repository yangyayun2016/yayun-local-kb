# LT Advertising Architecture

Use this reference when the user wants advertising architecture, traffic hierarchy, LT logic, campaign/ad-group health, or "缺什么流量 / 哪里多余 / 哪里是空壳 / 预算怎么转移" conclusions.

## Core Principle

Advertising architecture answers: what traffic should exist, what is missing, what is redundant, and where budget can move.

LT answers: which traffic layer each campaign/ad group/search term belongs to, whether that layer matches the intended architecture, and how it is performing.

Do not output only a flat ad-group health table. First map traffic into LT layers, then judge layer coverage, performance, conflicts, and actions.

## Operating Chain

Use this chain for every architecture answer:

```text
raw reports / ASIN Center ad tree
-> normalize campaign, ad group, targeting, search term, ASIN/SKU, metrics
-> map each row to an LT traffic layer
-> aggregate performance by LT layer
-> compare current layers with expected architecture
-> identify missing, redundant, mixed, empty-shell, transferable, and healthy layers
-> produce actions: supplement, split, clean, transfer budget, protect, pause, monitor
```

## LT Layers

Use these default LT layers unless the user's account has a custom taxonomy:

| LT layer | Architecture purpose | Typical signals |
|---|---|---|
| 品牌防守层 | Protect brand/high-certainty traffic | own brand terms, branded campaign names, brand phrase/exact |
| 核心Exact收割层 | Harvest proven high-conversion core terms | exact match, orders > 0, efficient ACOS/ROAS |
| 品类Phrase扩展层 | Expand related category traffic with controlled query shape | phrase match, category/core modifiers |
| Broad探索层 | Discover new traffic and future exact candidates | broad match, broad campaign/ad-group names |
| 竞品抢夺层 | Win competitor brand or competing ASIN traffic | competitor terms, competitor ASINs, conquest naming |
| ASIN/商品定向层 | Product detail page and ASIN targeting | target ASIN/product targeting/expression |
| Auto探索层 | Low-friction query discovery | auto, close match, loose match, substitutes, complements |
| 空壳/边缘层 | Low-value shells or tiny residual traffic | low spend, no clear role, no meaningful conversion evidence |

If one campaign/ad group mixes multiple layers, mark it as 混层. A mixed layer is an architecture issue even when ACOS looks acceptable.

## Layer Judgments

Use these architecture states:

- `符合架构`: layer role is clear and performance supports keeping it.
- `缺失`: expected layer has no clear campaign/ad group/targeting coverage.
- `承接不足`: layer exists but cannot carry enough traffic, exact harvest, or conversion.
- `多余`: traffic layer exists but duplicates another layer or burns budget outside strategy.
- `混层`: brand/core/category/competitor/auto traffic are mixed in one group.
- `空壳`: campaign/ad group exists but contributes little useful traffic or evidence.
- `可转移`: budget/traffic should move from weak or empty layer to a stronger or missing layer.
- `需观察`: data volume is too low for high-impact action.

## LT Architecture Attribution Table

When architecture is requested, prefer this summary table before detailed actions:

```text
LT层级 | 架构目的 | 当前承接组 | 花费 | ACOS/ROAS | 层级状态 | 归因结论 | 治理动作
```

Column rules:

- `LT层级`: one of the LT layers above.
- `架构目的`: what this layer should do in the traffic system.
- `当前承接组`: campaign/ad group/targeting rows that currently carry this layer.
- `花费` and `ACOS/ROAS`: aggregate by layer where possible.
- `层级状态`: one of the layer judgments.
- `归因结论`: explain missing/redundant/mixed/empty/healthy in one sentence.
- `治理动作`: supplement, split, clean, transfer budget, protect, pause, or monitor.

## Decision Rules

Architecture view should answer these questions in order:

1. Is each required LT layer present?
2. Which layers are missing or under-carried?
3. Which layers have redundant traffic or unnecessary spend?
4. Which campaigns/ad groups are empty shells that can release budget?
5. Which groups mix layers and need split or cleanup?
6. Which layers match architecture and are performing well?
7. What budget or traffic should be transferred, and why?

Do not make the user infer these from many ad-group rows. The output should make the next action obvious.

## Action Mapping

- `补层`: create or strengthen a missing LT layer, such as Broad探索 or 核心Exact收割.
- `拆层`: split mixed groups, such as brand + category or phrase + exact harvest.
- `清层`: remove irrelevant search terms, brand leakage, or wrong-layer terms.
- `转移预算`: move spend from empty/redundant/weak layers to healthy or missing layers.
- `保护`: keep or bid up efficient core/brand layers.
- `暂停`: pause high-spend no-order or strategically wrong traffic.
- `观察`: keep low-data or uncertain rows without high-impact changes.

## Example Pattern

```text
LT层级 | 架构目的 | 当前承接组 | 花费 | ACOS | 层级状态 | 归因结论 | 治理动作
核心Exact收割层 | 承接已验证高转化词 | AR800-series | $53 | 6.0% | 符合架构 | 核心流量表现健康 | 保护/提BID
品牌防守层 | 防守本品牌流量 | AR800-auxbeam | $29 | 无销售 | 多余 | 品牌Phrase引非本品流量 | 暂停/清词
品类Phrase扩展层 | 受控拓展品类词 | ALL-1x | $39 | 25.9% | 混层 | 品类层混入品牌词 | 清品牌词，保留品类探索
核心Exact收割层 | 承接Phrase中已验证词 | 缺失 | - | - | 缺失 | 已有词表现但没有独立Exact承接 | 从Phrase转Exact
Auto探索层 | 发现边缘新词 | auto等3组 | $4 | - | 空壳 | 低消耗低证据 | 保留观察或合并
```

## Guardrails

- Do not call an ad group healthy without saying which LT layer it belongs to.
- Do not confuse good ACOS with good architecture; mixed-layer traffic can still need splitting.
- Do not treat all low-spend groups as useless; mark low-data rows as `需观察` unless role is clearly redundant.
- Do not infer listing, price, review, inventory, or margin root causes from LT architecture alone.
- High-impact actions such as pause, negative, budget transfer, or bid increase require human confirmation.
