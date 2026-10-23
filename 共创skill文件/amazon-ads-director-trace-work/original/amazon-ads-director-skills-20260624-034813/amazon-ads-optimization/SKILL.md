---
name: amazon-ads-optimization
description: Use when optimizing Amazon Ads from ASIN Center reports, raw Amazon Ads Search Term or Advertised Product reports, LT traffic-layer architecture, HAR files, ASIN JSON, ACOS/CVR/traffic/margin/inventory diagnostics, or campaign/ad group/targeting/search-term action plans.
user-invocable: true
---

# Amazon Ads Optimization

Use this skill for Amazon Ads optimization work, especially when the user uploads ASIN Center data, HAR files, ASIN report JSON, raw Amazon Ads Search Term / Advertised Product reports, or asks for campaign/keyword/search-term actions.

## Core Rule

Treat the uploaded report files as the source of truth. Do not invent metrics, thresholds, campaign names, ASIN attributes, or actions. If a field is missing, say what is missing and what capture/export is needed.

For advertising architecture, use LT traffic layers as the primary coordinate system. Do not only judge whether each ad group is healthy. First place traffic into LT layers, then explain what traffic is missing, redundant, mixed, empty-shell, transferable, or correctly performing.

## Input Priority

1. Raw Amazon Ads report pair: Search Term Report plus Advertised Product Report, Product Targeting Report, or the user's "投放商品报告". If no ASIN Center report is present, enter **Raw Amazon Ads Reports Mode**.
2. A single uploaded ASIN report file, preferably JSON, but text/Markdown is acceptable if it contains the report sections.
3. ASIN Center detail JSON. If it came from the web app, it may appear as `/json/{username}/{ASIN}.json`.
4. HAR with content that includes an ASIN detail JSON response.
5. ASIN Center page text or screenshots.
6. One raw Amazon Ads table or CSV file. Use Raw Amazon Ads Reports Mode, but mark joins and product-level conclusions as limited.

If only an ASIN Center ASIN list is available, ask the user to search one ASIN and export another HAR after the full report loads.

## Mode Selection

- Use **Raw Amazon Ads Reports Mode** when the user uploads Search Term Report plus Advertised Product Report / Product Targeting Report / 投放商品报告, even if no ASIN Center JSON exists.
- Use **ASIN Center Workflow** when the input contains `header`, `part1_review`, `part2_diagnosis`, or `part5_operations`.
- If both sources exist, prefer ASIN Center for lifecycle, inventory, rating, margin, L2/L3, and operation IDs; use raw reports to audit and enrich campaign/search-term evidence.

## Raw Amazon Ads Reports Mode

Read `references/raw-amazon-ads-reports.md` before producing recommendations from raw reports.
Read `references/lt-ad-architecture.md` before producing advertising architecture or LT-layer conclusions.

### Default local closed-loop pipeline

When a raw Amazon Ads report pair is available (Search Term Report + Advertised Product Report / 投放商品报告), prefer the local Amazon Ads Director pipeline over ad-hoc chat analysis unless the user explicitly asks otherwise or the files cannot be saved to normal workspace paths:

```powershell
cd C:\Users\BD\.openclaw\workspace
node amazon_ads_ops/ads_ops.js run `
  --search <search_term_report.xlsx> `
  --advertised <advertised_product_report.xlsx> `
  --out ads_ops_output/<run_name> `
  --db amazon_ads_ops/amazon_ads_ops.db `
  --asinKnowledgeDb "D:\ASIN知识库-All Listing信息\asin_knowledge.db"
```

This canonical flow is:

```text
广告报表 → 标准化 → LT 层归因 → 知识库 keyword_library 富化
→ products 产品 Gate / ASIN 定向判断 → 动作台账
→ 回写 search_term_classified → 高价值词晋升 keyword_library
→ 写 asin_keyword_evidence
```

Report the run metrics: `runId`, `outputDir`, `keywordAssetsTouched`, `actionCandidates`, `knowledgeEnriched`, `knowledgeWrittenBack`, `knowledgePromoted`, `productKnowledgeMatched`, and data-quality warnings.

1. Identify uploaded report names, date ranges, marketplace/account scope, and currency.
2. Normalize column aliases for campaign, ad group, search term, targeting/keyword, match type, advertised ASIN/SKU, impressions, clicks, spend, sales, orders, units, CTR, CPC, CVR, ACOS, and ROAS.
3. Compute missing derived metrics only from available numeric fields:
   - CTR = clicks / impressions
   - CPC = spend / clicks
   - CVR = orders / clicks
   - ACOS = spend / sales
   - ROAS = sales / spend
4. Join reports conservatively:
   - Prefer campaign + ad group + advertised ASIN/SKU when both reports contain ASIN/SKU.
   - Fall back to campaign + ad group when the Search Term Report lacks advertised ASIN/SKU.
   - If the user's "投放商品报告" is actually a targeting/product-targeting report, use targeting/product fields and say the product-level join is not the same as advertised-ASIN performance.
5. Map campaigns/ad groups/targeting/search terms into LT traffic layers before judging architecture:
   - brand defense, core exact harvest, phrase/category expansion, broad exploration, competitor conquest, product/ASIN targeting, auto discovery, and empty-shell/edge traffic.
   - If a group mixes layers, mark the conflict and propose split/cleanup rather than calling it simply healthy or unhealthy.
6. Classify search terms as reusable keyword-library candidates only when they are valuable, risky, or actionable. Use the decision ladder: confirmed user rule > ASIN-specific relationship > deterministic rule > AI suggestion > human confirmation.
7. Produce recommendations only. Do not claim Amazon Ads changes were executed.

Raw reports cannot infer inventory, rating, lifecycle, margin, category rank, L2/L3 diagnosis, or listing/product issues unless the user provides those fields separately. Put these items in a "missing context" section instead of guessing.

## ASIN Center Workflow

1. Identify the ASIN and report source.
2. Read `header` first:
   - `asin`, `productName`, `销售账号`, `负责人`
   - `L2`, `L3`, `库存模式`, `可销月`, `评分`, `生命周期`, `生成时间`
3. Summarize `part1_review.dataComparison`:
   - visitors, conversion rate, ACOS, ad clicks, ad conversion, orders, sales, margin, refund rate, category rank, sellable months.
4. Use `part2_diagnosis` as the authoritative diagnosis chain:
   - `l2Process`, `l2TypeReference`, `l3Details`, `rating`, `decisionFields`.
   - Do not recalculate L2/L3 unless the user explicitly asks for an audit.
5. Use `part4_adArchitecture` to explain advertising structure:
   - budget layer allocation, strategy match, traffic distribution, core match efficiency, negative word control, empty-rate waste, coverage, and risk warnings.
   - When architecture is discussed, convert campaign/ad-tree evidence into the LT advertising architecture attribution table from `references/lt-ad-architecture.md`.
6. Use `part5_operations` for executable action output:
   - `currentRisks`, `inventoryImpact`, `asinLevelOperations`, `priceCheck`, `moduleCoverage`, `reviewCheck`, `newActivities`, `operationStats`, `adTree`.
7. Add later-section notes:
   - `part6_decisionAttribution`, `part7_expectedResults`, `part8_memo`, `part9_productOptimization`, `part10_multiAsinPriority`.

## Output Shape

Respond in Chinese by default. Keep the answer operational.

For ASIN Center Workflow:

1. **诊断结论**: ASIN, L2/L3, lifecycle, inventory, rating, one-line issue.
2. **核心证据**: 3-6 metrics that drove the conclusion.
3. **根因链路**: traffic/conversion/ACOS/margin/inventory/architecture causal chain.
4. **广告架构动作**: budget layer shifts, SP/SB/SD coverage, match-type strategy.
5. **执行清单**: campaign/ad group/targeting/search-term actions from `part5_operations` and `adTree`.
6. **风险与监控**: risks, expected results, next review date, metrics to watch.

For Raw Amazon Ads Reports Mode:

1. **数据完整性**: report names, date range, row counts, missing required columns, join quality.
2. **账户/ASIN/活动概览**: spend, sales, orders, ACOS, ROAS, clicks, CTR, CPC, CVR by account, campaign, ad group, and ASIN/SKU where possible.
3. **LT广告架构归因表**: LT layer, architecture role, current groups, spend, ACOS/ROAS, layer state, architecture conclusion, action.
4. **搜索词动作表**: customer search term, campaign, ad group, targeting/keyword, match type, LT layer, metrics, term type, action, evidence, confidence, human-confirmation flag.
5. **投放商品/定向动作表**: ASIN/SKU or target/product, campaign, ad group, LT layer, current efficiency, action, evidence.
6. **否定与转精准清单**: separate negative candidates from exact-harvest candidates; never mix them into one ambiguous list.
7. **竞价/预算建议**: bid down, bid up/protect, pause, budget shift, or monitor with explicit metric evidence.
8. **无法判断/需补充数据**: margin, inventory, rating, lifecycle, rank, L2/L3, listing conversion, and any missing raw columns.

When the user asks for a skill-like output, prefer a reusable template over one-off advice.

## Action Semantics

- Module A: offsite traffic and brand content.
- Module B: advertising traffic actions.
- Module C: conversion, price, coupon, promotion, and quantity discount checks.
- Module D: review and rating actions.
- `B7-6`: negative keyword / traffic cleanup.
- `B5-1`: exact match targeting / match tightening.
- `D16-1`: review/Vine related action.

For L2 `E流量质量差`, prioritize:

- reduce waste in over-allocated exploration layers;
- add or enforce negative keywords where irrelevant or zero-order traffic is spending;
- move budget toward conversion layers and proven exact/phrase targets;
- separate strong search terms from broad/auto exploration;
- keep margin and inventory gates before increasing spend.

## Risk Gates

- If margin is below 25%, say budget should tighten unless the user states a growth exception.
- If inventory is constrained, suppress expansion and prioritize price/profit protection.
- If rating is low or review count is insufficient, include review/product risk before scaling ads.
- If ACOS is high while CVR is low, do not recommend broad budget increases.
- If report sections disagree, show the conflict and prefer concrete operation tables over narrative summaries.

## References

For ASIN Center schema and the captured B0DMV84TDX example, read:

- `references/asin-center-schema.md`
- `references/b0dmv84tdx-example.md`

For raw Amazon Ads Search Term Report and 投放商品报告 workflows, read:

- `references/raw-amazon-ads-reports.md`

For LT traffic-layer advertising architecture workflows, read:

- `references/lt-ad-architecture.md`
