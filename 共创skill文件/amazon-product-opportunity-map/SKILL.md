---
name: amazon-product-opportunity-map
description: |
  Generate Amazon product opportunity maps from a seed product, keyword, ASIN, or existing product line. Use when the user wants Amazon product selection, product expansion, category deepening, adjacent product discovery, complementary product discovery, SellerSprite/market-data interpretation, or a shortlist of testable Amazon product opportunities from one validated product.
---

# Amazon Product Opportunity Map

## Purpose

Turn one validated product or keyword into a structured Amazon product opportunity map. Treat AI as a judgment amplifier: expand many directions, filter them into a few credible candidate opportunities, then identify one or more products worth validating or testing.

Use the mental model:

`single product = target user x use scenario x demand x solution`

`category opportunity = keep 1-2 variables stable, then expand adjacent users, scenarios, demands, or solutions`

## Workflow

1. Clarify the seed and constraints.
   - Identify the seed product, keyword, ASIN, or current listing.
   - Ask for marketplace, target category, price band, supply-chain strengths, margin target, compliance limits, and company stage when missing and materially needed.
   - If the user only provides a product keyword, proceed with assumptions and mark data gaps clearly.

2. Decompose the seed product.
   - Define the current user, scenario, demand, solution, usage flow, and buying motivation.
   - Ask: What does the buyer want to complete? Why now? Where is it used? What happens before and after use? What failure or anxiety is the buyer trying to avoid?

3. Expand from single product to opportunity map.
   - Generate subdivision tracks by changing the display object, target user, use scenario, function, form, material/process, package, protection, or storage method.
   - Generate complementary tracks by following the buyer's full workflow: installation, connection, replacement, consumables, accessories, maintenance, storage, gifting, and adjacent scene needs.
   - Classify every direction as either `subdivision`, `complementary`, or `bundle/system opportunity`.

4. Validate demand and competition.
   - Use available marketplace data tools, SellerSprite exports, keyword tools, Amazon search observations, or user-provided data.
   - Evaluate search volume, purchase volume, purchase rate, trend, seasonality, product count, SPR or similar competition proxy, average price, supply-demand ratio, review distribution, rating gaps, and low-review sales cases.
   - Never judge by search volume alone. High demand can mean high competition; low search volume can still be useful when the scenario is precise and conversion intent is strong.

5. Validate user pain and product differentiation.
   - Mine reviews, Q&A, listing copy, image claims, and competitor complaints.
   - Convert pain points into specific product hypotheses: feature, material, size, kit, installation method, packaging, content, use guide, or visual-expression improvement.

6. Validate business fit.
   - Check supply-chain fit, gross margin, FBA/logistics cost, MOQ, iteration speed, patent/compliance risk, category restrictions, brand fit, and operational asset reuse.
   - Prefer opportunities that reuse existing supply chain, operations, visual assets, content knowledge, or customer understanding.

7. Shortlist and recommend next action.
   - Reduce broad directions into 5 candidate opportunities.
   - Rank them with a transparent score and explain why each survives or fails.
   - Recommend 1-2 products for deeper validation or small-batch testing, with the next validation steps.

## Reference Loading

- Read `references/evaluation-framework.md` when scoring, classifying, or comparing opportunities.
- Read `references/output-template.md` when the user asks for a formal report, table, roadmap, or final deliverable.

## Output Rules

Deliver structured, decision-ready output:

1. Start with the seed-product decomposition.
2. Show the opportunity map with subdivision and complementary tracks.
3. Provide evidence and data caveats for each candidate.
4. Give a ranked shortlist, not just a long brainstorm.
5. End with specific validation actions.

When data is unavailable, label the field as `unknown` and state what data should be collected next. Do not invent metrics, sales, review counts, patent status, or compliance conclusions.

## Example

Input: `Use photo frame as the seed product and find Amazon expansion opportunities.`

Expected approach:

- Decompose `photo frame` into users, scenarios, display needs, and solutions.
- Expand subdivision tracks such as diploma frame, certificate frame, shadow box frame, kids art frame, puzzle frame, and poster frame.
- Expand complementary tracks such as picture hanging strips, wall anchors, picture wire, photo corners, and glossy photo paper.
- Distinguish product variation from category opportunity.
- Use market data and business fit to shortlist candidates instead of treating every generated idea as actionable.

## Guardrails

- Do not present AI-generated directions as final product decisions.
- Do not recommend restricted, unsafe, counterfeit, patented, or compliance-sensitive products without explicit risk checks.
- Do not use one metric as a pass/fail rule.
- Do not ignore supply chain, margin, logistics, compliance, or company stage.
- Do not overfit to the seed product's surface form; always reason from user, scenario, demand, and solution.
