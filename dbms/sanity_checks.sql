-- database: ../sql.db
-- sanity_checks.sql
-- Quick data quality checks to run after loading.

-- How many rows?
SELECT COUNT(*) AS row_count FROM campaign_data;

-- Date range?
SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM campaign_data;

-- Any NULLs in critical fields?
SELECT
  SUM(CASE WHEN campaign_name IS NULL THEN 1 ELSE 0 END) AS null_campaign_name,
  SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END)          AS null_date,
  SUM(CASE WHEN spend_usd IS NULL THEN 1 ELSE 0 END)     AS null_spend_usd,
  SUM(CASE WHEN impressions IS NULL THEN 1 ELSE 0 END)   AS null_impressions,
  SUM(CASE WHEN reach IS NULL THEN 1 ELSE 0 END)         AS null_reach,
  SUM(CASE WHEN website_clicks IS NULL THEN 1 ELSE 0 END)AS null_clicks,
  SUM(CASE WHEN purchases IS NULL THEN 1 ELSE 0 END)     AS null_purchases,
  SUM(CASE WHEN group_name IS NULL THEN 1 ELSE 0 END)    AS null_group_name
FROM campaign_data;

-- Distinct groups present
SELECT group_name, COUNT(*) AS rows_in_group
FROM campaign_data
GROUP BY group_name
ORDER BY rows_in_group DESC;
