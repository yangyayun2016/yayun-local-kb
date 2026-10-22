---
name: "asin-knowledge-agent"
description: "ASIN knowledge base agent: query structured SQLite data for Amazon Ads optimization"
user-invocable: true
---

# ASIN Knowledge Base Agent

Use this skill when asking about ASIN data, search term analysis, or ad optimization decisions.

## Data Source

- **SQLite DB:** `D:\ASIN知识库-All Listing信息\asin_knowledge.db`
- **Table products:** ASIN-level data (BSR, brand, rating, ownership)
- **Table keyword_library:** Seed + classified keywords with attribute types and weights
- **Table search_term_classified:** Search terms from Amazon Ads, classified and enriched
- **Ingestion:** `node C:\Users\BD\.openclaw\workspace\ingest_to_sqlite.js`

## Products Table Schema

(asin PK, url, title, top_highlights, product_description, rating, ratings_count, reviews_count, status, error, raw_item_details, raw_featured_reviews, first_seen_at, last_updated_at, csv_source, bsr, bsr_category, bsr_subcategory_rank, bsr_subcategory_name, brand, item_model, dimensions, review_count_parsed, ownership)

## Ownership Rules

- **Brand-based:** `AngeRose` → 'self'. All other brands → 'competitor'
- **ASIN-based:** `B0DJ3W7CMQ`, `B0DW8RFFJW` → 'self'
- Defined in `ingest_to_sqlite.js` under `OWN_BRANDS` and `OWN_ASINS`

## Keyword Classification System

Based on reference framework with attribute types and weight hierarchy. The explicit rule docs/config live at:

- `C:\Users\BD\.openclaw\workspace\knowledge_rules\asin_keyword_attribute_matching_rules.md`
- `C:\Users\BD\.openclaw\workspace\knowledge_rules\keyword_attribute_rules.v1.json`
- Runtime engine: `C:\Users\BD\.openclaw\workspace\knowledge_rules\keyword_attribute_engine.js`

`ingest_to_sqlite.js` now loads the JSON rules, extracts ASIN-page keyword candidates into `keyword_library`, and classifies unclassified `search_term_classified` rows after ingestion.

### Attribute Types (by weight)

- 产品核心词 (1.0): Core product terms from title/listing
- 品牌(自有) (0.95): Own brand names
- 品牌(竞品) (0.95): Competitor brand names
- 类目 (0.8): Category terms
- 功能 (0.8): Product functions/features
- 规格参数 (0.75): Specs (color, size, capacity)
- 使用场景 (0.7): Usage scenarios
- 适配对象 (0.6): Compatible users
- 卖点/差异化 (0.55): Selling points
- ASIN (0.7): ASIN code matches
- 风险/限制 (-1): Negative/conflict terms

### Status Levels

- **启用**: Verified, use for matching
- **候选**: Needs review, can match but low priority
- **观察**: Exploratory, match with caution
- **风险**: Risk/conflict terms

### Matching Priority

1. ASIN detection (regex)
2. Risk/conflict term detection
3. Brand exact match
4. Full term exact match
5. Normalized phrase match
6. Substring match (with length bonus)
7. Word-level match (discounted, fallback only)

## Standard Queries

### Top search terms by spend

SELECT search_term, attribute_type, impressions, clicks, spend, sales, orders, ROUND(acos*100,1) as acos_pct FROM search_term_classified WHERE attribute_type IS NOT NULL ORDER BY spend DESC LIMIT 20;

### Search terms by attribute type

SELECT attribute_type, COUNT(*) as cnt, ROUND(AVG(acos)*100,1) as avg_acos, SUM(orders) as total_orders, ROUND(SUM(spend),2) as total_spend FROM search_term_classified WHERE attribute_type IS NOT NULL GROUP BY attribute_type ORDER BY cnt DESC;

### Brand search terms (self)

SELECT search_term, impressions, clicks, spend, orders FROM search_term_classified WHERE attribute_type = '品牌(自有)' ORDER BY impressions DESC;

### Unclassified terms needing review

SELECT search_term, COUNT(*) as cnt, SUM(impressions) as total_imp, SUM(spend) as total_spend FROM search_term_classified WHERE attribute_type IS NULL GROUP BY search_term ORDER BY total_spend DESC;

### Own ASINs performance

SELECT asin, title, bsr, rating, brand, ownership FROM products WHERE ownership = 'self' AND status = 'ok' ORDER BY bsr;

### ASIN-level search term summary

SELECT advertised_asin, COUNT(*) as term_count, SUM(spend) as total_spend, SUM(orders) as total_orders FROM search_term_classified WHERE advertised_asin IS NOT NULL GROUP BY advertised_asin ORDER BY total_spend DESC;
