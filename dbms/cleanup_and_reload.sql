-- cleanup_and_reload.sql
-- Run this with:
--   sqlite3 sql.db ".read sql/cleanup_and_reload.sql"
-- IMPORTANT: Edit the .import path below to your actual CSV path before running.

.echo on
.mode csv
.headers on

-- 1) Start clean
DELETE FROM raw_campaign_data;
DELETE FROM campaign_data;

-- 2) Import CSV (EDIT THIS PATH)
.import /Users/cathelenegeorge/Desktop/AB_Testing/data/processed/cleaned_campaign.csv raw_campaign_data

-- 3) Drop any header rows that slipped into RAW
DELETE FROM raw_campaign_data
WHERE TRIM(COALESCE("Date", '')) = 'Date'
   OR TRIM(COALESCE("group", '')) = 'group';

-- 4) Insert DISTINCT clean rows
INSERT INTO campaign_data (
    campaign_name, date, spend_usd, impressions, reach,
    website_clicks, searches, view_content, add_to_cart, purchases, group_name
)
SELECT DISTINCT
    "Campaign Name",
    TRIM("Date"),
    CAST("Spend [USD]" AS REAL),
    CAST("# of Impressions" AS INT),
    CAST("Reach" AS INT),
    CAST("# of Website Clicks" AS INT),
    CAST("# of Searches" AS INT),
    CAST("# of View Content" AS INT),
    CAST("# of Add to Cart" AS INT),
    CAST("# of Purchase" AS INT),
    "group"
FROM raw_campaign_data
WHERE TRIM(COALESCE("Date", '')) <> '';

-- 5) Verify counts
SELECT
  (SELECT COUNT(*) FROM raw_campaign_data)   AS raw_rows,
  (SELECT COUNT(*) FROM campaign_data)       AS clean_rows;
