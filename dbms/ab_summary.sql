-- database: ../sql.db
-- ab_summary.sql
-- Compare groups (e.g., 'control' vs 'test') and declare a simple winner by conversion rate.
-- Assumes 'group_name' has exactly 2 values representing the variants to compare.

WITH agg AS (
  SELECT
    group_name,
    SUM(spend_usd)      AS spend_usd,
    SUM(impressions)    AS impressions,
    SUM(website_clicks) AS clicks,
    SUM(purchases)      AS purchases
  FROM campaign_data
  GROUP BY group_name
),
kpi AS (
  SELECT
    group_name,
    spend_usd,
    impressions,
    clicks,
    purchases,
    CASE WHEN impressions > 0 THEN 1.0 * clicks / impressions END  AS ctr,
    CASE WHEN clicks > 0 THEN 1.0 * purchases / clicks END         AS conversion_rate,
    CASE WHEN clicks > 0 THEN spend_usd / clicks END               AS cpc,
    CASE WHEN purchases > 0 THEN spend_usd / purchases END         AS cpa,
    CASE WHEN impressions > 0 THEN 1000.0 * spend_usd / impressions END AS cpm
  FROM agg
),
pair AS (
  SELECT
    (SELECT group_name FROM kpi ORDER BY group_name LIMIT 1)                        AS group_a,
    (SELECT group_name FROM kpi ORDER BY group_name DESC LIMIT 1)                   AS group_b
),
pivot AS (
  SELECT
    p.group_a,
    p.group_b,
    ka.spend_usd AS spend_a, kb.spend_usd AS spend_b,
    ka.impressions AS imp_a, kb.impressions AS imp_b,
    ka.clicks AS clicks_a, kb.clicks AS clicks_b,
    ka.purchases AS purchases_a, kb.purchases AS purchases_b,
    ka.ctr AS ctr_a, kb.ctr AS ctr_b,
    ka.conversion_rate AS conv_a, kb.conversion_rate AS conv_b,
    ka.cpc AS cpc_a, kb.cpc AS cpc_b,
    ka.cpa AS cpa_a, kb.cpa AS cpa_b,
    ka.cpm AS cpm_a, kb.cpm AS cpm_b
  FROM pair p
  JOIN kpi ka ON ka.group_name = p.group_a
  JOIN kpi kb ON kb.group_name = p.group_b
),
lift AS (
  SELECT
    group_a, group_b,
    conv_a, conv_b,
    CASE WHEN conv_b IS NOT NULL AND conv_b <> 0 THEN (conv_a - conv_b) / conv_b END AS conv_lift_a_vs_b,
    ctr_a, ctr_b,
    CASE WHEN ctr_b IS NOT NULL AND ctr_b <> 0 THEN (ctr_a - ctr_b) / ctr_b END       AS ctr_lift_a_vs_b,
    cpa_a, cpa_b,
    cpc_a, cpc_b,
    cpm_a, cpm_b
  FROM pivot
),
winner AS (
  SELECT
    CASE
      WHEN conv_a IS NOT NULL AND conv_b IS NOT NULL
           AND conv_a > conv_b AND (cpa_a IS NULL OR cpa_b IS NULL OR cpa_a <= cpa_b)
        THEN group_a
      WHEN conv_a IS NOT NULL AND conv_b IS NOT NULL
           AND conv_b > conv_a AND (cpa_a IS NULL OR cpa_b IS NULL OR cpa_b <= cpa_a)
        THEN group_b
      ELSE 'tie/needs more data'
    END AS winner_group
  FROM lift
)
SELECT
  l.*,
  w.winner_group
FROM lift l
CROSS JOIN winner w;
