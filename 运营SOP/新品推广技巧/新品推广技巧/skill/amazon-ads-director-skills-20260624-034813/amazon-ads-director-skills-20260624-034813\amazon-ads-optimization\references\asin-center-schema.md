# ASIN Center Schema

ASIN Center is a static JSON-backed dashboard. The observed app title is `ASIN Center`.

## Data URLs

- Login/users: `/json/user.json`
- Normal user ASIN list: `/json/{username}/asin-list.json`
- Admin ASIN list: `/json/_all/asin-list.json`
- Normal user ASIN detail: `/json/{username}/{ASIN}.json`
- Admin ASIN detail: `/json/_all/{ASIN}.json`

Observed user folder: `罗志明`.

Observed ASIN list:

- `B0DMV84TDX`
- `B0G1XQS7KG`
- `B0FWK4MQC3`

## Top-Level Report Sections

- `header`: ASIN metadata and headline diagnosis.
- `part1_review`: data comparison, cross validation, strategy review.
- `part2_diagnosis`: L2/L3 diagnosis process and decision fields.
- `part3_changes`: change explanation.
- `part4_adArchitecture`: advertising architecture recommendation and attribution.
- `part5_operations`: concrete operation plan and campaign tree.
- `part6_decisionAttribution`: decision attribution.
- `part7_expectedResults`: expected results and monitoring plan.
- `part8_memo`: derived memo.
- `part9_productOptimization`: product optimization suggestions.
- `part10_multiAsinPriority`: multi-ASIN priority notes.

## Important Field Groups

`header`:

- `asin`, `productName`, `销售账号`, `负责人`, `L2`, `L3`, `库存模式`, `可销月`, `评分`, `生命周期`, `生成时间`

`part1_review`:

- `dataComparison`, `crossValidation`, `strategyReview`

`part2_diagnosis`:

- `l2Process`, `l2TypeReference`, `l3Details`, `rating`, `decisionFields`

`part4_adArchitecture`:

- `budgetAllocation`, `strategyMatch`, `strippingWords`, `architectureAttribution`
- `m1TrafficDistribution`, `m2CoreMatchEfficiency`, `m3NegativeWordControl`, `m4EmptyRate`
- `architectureSummary`, `coverageCheck`, `riskWarnings`

`part5_operations`:

- `currentRisks`, `inventoryImpact`, `asinLevelOperations`, `priceCheck`, `moduleCoverage`
- `reviewCheck`, `newActivities`, `operationStats`, `adTree`, `dataLegend`

## HAR Capture Requirement

To capture useful data, the HAR must include the ASIN detail request, for example:

`/json/罗志明/B0DMV84TDX.json`

If the HAR only includes `asin-list.json`, ask the user to search an ASIN in ASIN Center, wait for the report to load, then export HAR with content again.
