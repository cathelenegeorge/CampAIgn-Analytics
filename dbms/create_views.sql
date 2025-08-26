-- database: ../sql.db
-- create_views.sql
-- Create reusable views for quick exploration.

DROP VIEW IF EXISTS vw_group_kpis;
CREATE VIEW vw_group_kpis AS
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
)
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
  CASE WHEN impressions > 0 THEN ROUND(1.0 * clicks / impressions, 4) END AS ctr,
  CASE WHEN clicks > 0 THEN ROUND(1.0 * purchases / clicks, 4) END        AS conversion_rate,
  CASE WHEN clicks > 0 THEN ROUND(spend_usd / clicks, 4) END              AS cpc,
  CASE WHEN purchases > 0 THEN ROUND(spend_usd / purchases, 4) END        AS cpa,
  CASE WHEN impressions > 0 THEN ROUND(1000.0 * spend_usd / impressions, 4) END AS cpm
FROM base;

DROP VIEW IF EXISTS vw_daily_kpis;
CREATE VIEW vw_daily_kpis AS
WITH daily AS (
  SELECT
    date,
    group_name,
    SUM(spend_usd)      AS spend_usd,
    SUM(impressions)    AS impressions,
    SUM(website_clicks) AS clicks,
    SUM(purchases)      AS purchases
  FROM campaign_data
  GROUP BY date, group_name
)
SELECT
  date,
  group_name,
  impressions,
  clicks,
  purchases,
  CASE WHEN impressions > 0 THEN ROUND(1.0 * clicks / impressions, 4) END AS ctr,
  CASE WHEN clicks > 0 THEN ROUND(1.0 * purchases / clicks, 4) END        AS conversion_rate
FROM daily;
