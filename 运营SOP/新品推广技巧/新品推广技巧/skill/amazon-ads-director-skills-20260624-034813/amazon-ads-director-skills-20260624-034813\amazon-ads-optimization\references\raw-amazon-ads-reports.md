# Raw Amazon Ads Reports Mode

Use this reference when the user uploads raw Amazon Ads reports instead of ASIN Center JSON. The most common minimum pair is:

- Search Term Report / 搜索词报告
- Advertised Product Report, Product Targeting Report, or the user's "投放商品报告"

## Source Boundaries

Raw reports can support campaign, ad group, targeting, search-term, ASIN/SKU, bid, budget, and negative-keyword recommendations. They cannot prove inventory, rating, lifecycle, margin, category rank, L2/L3 diagnosis, or listing/product-root-cause issues unless those fields are separately provided.

Never fabricate missing context. Put missing fields in the final "无法判断/需补充数据" section.

When the user asks about advertising architecture, traffic hierarchy, LT, missing traffic, redundant traffic, empty-shell groups, or budget transfer, also read `lt-ad-architecture.md` and make LT traffic layers the first diagnostic frame.

## Report Aliases

Search Term Report aliases:

- `Customer Search Term`, `Search Term`, `搜索词`, `客户搜索词`
- `Targeting`, `Keyword`, `关键词`, `投放`, `定向`
- `Match Type`, `匹配类型`
- `Campaign`, `Campaign Name`, `广告活动`
- `Ad Group`, `Ad Group Name`, `广告组`
- Optional: `Advertised ASIN`, `ASIN`, `SKU`

Advertised Product Report / 投放商品报告 aliases:

- `Advertised ASIN`, `ASIN`, `广告商品`, `投放商品`
- `SKU`, `Advertised SKU`
- `Campaign`, `Campaign Name`, `广告活动`
- `Ad Group`, `Ad Group Name`, `广告组`
- `Impressions`, `Clicks`, `Spend`, `Sales`, `Orders`, `Units`
- `CTR`, `CPC`, `CVR`, `ACOS`, `ROAS`

If the user's "投放商品报告" is actually a Product Targeting or Targeting report, use target/product columns such as `Targeting`, `Target ASIN`, `Product`, or `Expression`. State that this is target-level evidence, not advertised-ASIN performance.

## Required Normalization

Normalize but preserve the original uploaded values:

| Canonical field | Common aliases |
|---|---|
| `campaign` | Campaign, Campaign Name, 广告活动 |
| `ad_group` | Ad Group, Ad Group Name, 广告组 |
| `search_term` | Customer Search Term, Search Term, 搜索词, 客户搜索词 |
| `targeting` | Targeting, Keyword, 关键词, 投放, 定向 |
| `match_type` | Match Type, 匹配类型 |
| `advertised_asin` | Advertised ASIN, ASIN, 广告商品, 投放商品 |
| `sku` | SKU, Advertised SKU |
| `impressions` | Impressions, 展示量 |
| `clicks` | Clicks, 点击量 |
| `spend` | Spend, Cost, 花费 |
| `sales` | Sales, 7 Day Total Sales, 销售额 |
| `orders` | Orders, 7 Day Total Orders, 订单 |
| `units` | Units, 7 Day Total Units, 件数 |

Use whichever columns exist. Do not rename missing fields into existence.

## Metrics

Compute derived metrics only when numerator and denominator exist:

- `CTR = clicks / impressions`
- `CPC = spend / clicks`
- `CVR = orders / clicks`
- `ACOS = spend / sales`
- `ROAS = sales / spend`
- `CPA = spend / orders`

If `targetACOS`, `targetCPA`, margin, or product lifecycle is not provided, mark thresholds as provisional and ask for the target before high-impact budget scaling.

## Join Logic

1. Normalize date range, account/portfolio if present, campaign, ad group, advertised ASIN, and SKU.
2. Aggregate Search Term Report by campaign + ad group + targeting + search term + match type. Include advertised ASIN/SKU only if present.
3. Aggregate Advertised Product Report by campaign + ad group + advertised ASIN/SKU.
4. Join on campaign + ad group + advertised ASIN/SKU when available in both reports.
5. If Search Term Report lacks ASIN/SKU, join only to campaign + ad group and label ASIN attribution as indirect.
6. If campaign or ad group names do not match, do not force a join. Report the unmatched rows.

## Default Action Heuristics

Defaults are review heuristics, not universal rules. Prefer user-provided targets when available.

Negative candidate:

- orders = 0 and clicks >= 10; or
- orders = 0 and spend >= max(5 USD, provisional target CPA); or
- clearly irrelevant term with clicks/spend.

Exact-harvest candidate:

- customer search term has orders and acceptable ACOS/ROAS; and
- the term is not already launched as exact match in the uploaded targeting/keyword evidence.

Bid down / pause candidate:

- orders > 0 but ACOS is above target or ROAS is below target; or
- spend is high, CVR is weak, and the term/product is not strategically protected.

Bid up / protect candidate:

- orders > 0, ACOS is at or below target, and there is meaningful click/order volume; or
- branded/core term that is efficient and should not lose coverage.

Monitor candidate:

- low data volume, missing target threshold, missing sales/orders, or mixed evidence.

## Keyword Library Classification

Treat search terms as durable keyword-library candidates, not one-off rows.

Allowed term types:

- brand
- competitor
- ASIN
- core
- long-tail
- attribute
- scenario
- Spanish
- irrelevant
- category
- unclassified

Use this decision ladder:

`user-confirmed rule > ASIN-specific relationship > deterministic rule > AI suggestion > human confirmation`

Candidate terms should usually have one of these signals:

- action is negative, exact-harvest, protect, or bid-up;
- risk is high;
- orders > 0;
- spend >= 5 USD, orders = 0, and clicks >= 5;
- clicks or spend exist and the term is not only a plain category/unclassified term.

Always keep global `termType` separate from ASIN-specific `relationshipType`. A term can be a good global keyword and still be waste for one ASIN.

## Output Contract

Use Chinese output by default.

`数据完整性`

- report names
- date range
- row counts
- required/missing columns
- join keys used
- unmatched or indirectly attributed rows

`账户/ASIN/活动概览`

- totals and top spenders by account/campaign/ad group/ASIN where possible
- spend, sales, orders, ACOS, ROAS, clicks, CTR, CPC, CVR

`LT广告架构归因表`

Include: LT layer, architecture purpose, current carrying campaign/ad group, spend, ACOS/ROAS, layer state, attribution conclusion, and governance action. Use this table to show what traffic is missing, redundant, mixed, empty-shell, transferable, or healthy before listing detailed row-level actions.

`搜索词动作表`

Include: action, search term, campaign, ad group, targeting/keyword, match type, LT layer, spend, clicks, sales, orders, ACOS/ROAS, term type, evidence, confidence, and whether human confirmation is required.

`投放商品/定向动作表`

Include: action, advertised ASIN/SKU or target/product, campaign, ad group, LT layer, spend, sales, orders, ACOS/ROAS, evidence, and confidence.

`否定与转精准清单`

Keep negative candidates and exact-harvest candidates in separate tables.

`竞价/预算建议`

Recommend bid down, bid up/protect, pause, budget shift, or monitor only with explicit metric evidence.

`无法判断/需补充数据`

List missing inventory, rating, lifecycle, margin, category rank, L2/L3, listing conversion, and target ACOS/CPA when absent.

## Guardrails

- Produce recommendations only; do not execute Amazon Ads changes.
- Never auto-confirm AI keyword classifications.
- Never invent categories, targets, campaign names, thresholds, or missing metrics.
- Do not merge unmatched reports by fuzzy guessing.
- High-impact actions such as negatives, pauses, and budget increases require human confirmation.
