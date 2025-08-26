-- database: ../sql.db
-- daily_trends.sql
-- Daily KPI trends by group (for plotting or inspection).

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
FROM daily
ORDER BY date, group_name;
