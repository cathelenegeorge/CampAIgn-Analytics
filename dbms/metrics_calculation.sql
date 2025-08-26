-- database: /Users/cathelenegeorge/Desktop/AB_Testing/sql.db
-- metrics_calculation.sql
-- Aggregated KPIs by group. Run this to see a tabular output in VS Code or sqlite3.

WITH base AS (
    SELECT
        group_name,
        SUM(spend_usd)        AS spend_usd,
        SUM(impressions)      AS impressions,
        SUM(reach)            AS reach,
        SUM(website_clicks)   AS clicks,
        SUM(searches)         AS searches,
        SUM(view_content)     AS view_content,
        SUM(add_to_cart)      AS add_to_cart,
        SUM(purchases)        AS purchases
    FROM campaign_data
    GROUP BY group_name
),
calc AS (
    SELECT
        group_name,
        spend_usd,
        impressions,
        reach,
        clicks,
        searches,
        view_content,
        add_to_cart,
        purchases,
        -- Core rates
        CASE WHEN impressions > 0 THEN ROUND(1.0 * clicks / impressions, 4) ELSE NULL END AS ctr,                -- Click-Through Rate
        CASE WHEN clicks > 0 THEN ROUND(1.0 * purchases / clicks, 4) ELSE NULL END AS conversion_rate,           -- Purchase / Click
        -- Costs
        CASE WHEN clicks > 0 THEN ROUND(spend_usd / clicks, 4) ELSE NULL END AS cpc,                             -- Cost per Click
        CASE WHEN purchases > 0 THEN ROUND(spend_usd / purchases, 4) ELSE NULL END AS cpa,                       -- Cost per Acquisition (Purchase)
        CASE WHEN impressions > 0 THEN ROUND(1000.0 * spend_usd / impressions, 4) ELSE NULL END AS cpm,          -- Cost per 1,000 Impressions
        -- Reach quality
        CASE WHEN impressions > 0 THEN ROUND(1.0 * reach / impressions, 4) ELSE NULL END AS reach_rate,
        -- Funnel step rates
        CASE WHEN clicks > 0 THEN ROUND(1.0 * searches / clicks, 4) ELSE NULL END AS search_rate,                -- Searches / Clicks
        CASE WHEN clicks > 0 THEN ROUND(1.0 * view_content / clicks, 4) ELSE NULL END AS view_content_rate,      -- ViewContent / Clicks
        CASE WHEN clicks > 0 THEN ROUND(1.0 * add_to_cart / clicks, 4) ELSE NULL END AS add_to_cart_rate         -- AddToCart / Clicks
    FROM base
)
SELECT
    group_name                                      AS group_name,   -- avoid reserved keyword 'group'
    spend_usd,
    impressions,
    reach,
    clicks,
    searches,
    view_content,
    add_to_cart,
    purchases,
    ctr,
    conversion_rate,
    cpc,
    cpa,
    cpm,
    reach_rate,
    search_rate,
    view_content_rate,
    add_to_cart_rate
FROM calc
ORDER BY group_name;
