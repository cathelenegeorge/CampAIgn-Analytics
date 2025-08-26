-- create_table.sql
-- SQLite schema for raw staging (matches CSV headers exactly) and a clean normalized table.
-- Run this once to create both tables.

PRAGMA foreign_keys = ON;

-- 1) Drop existing tables if they exist (safe for re-runs)
DROP TABLE IF EXISTS raw_campaign_data;
DROP TABLE IF EXISTS campaign_data;

-- 2) Create RAW table that mirrors the CSV headers exactly (including spaces/#).
--    This lets us import the CSV with .import without worrying about column order.
CREATE TABLE raw_campaign_data (
    "Campaign Name"        TEXT,
    "Date"                 TEXT,
    "Spend [USD]"          REAL,
    "# of Impressions"     INTEGER,
    "Reach"                INTEGER,
    "# of Website Clicks"  INTEGER,
    "# of Searches"        INTEGER,
    "# of View Content"    INTEGER,
    "# of Add to Cart"     INTEGER,
    "# of Purchase"        INTEGER,
    "group"                TEXT
);

-- 3) Create a CLEAN, normalized table with SQL-friendly column names and types.
CREATE TABLE campaign_data (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name       TEXT NOT NULL,
    date                DATE NOT NULL,
    spend_usd           REAL NOT NULL,
    impressions         INTEGER NOT NULL,
    reach               INTEGER NOT NULL,
    website_clicks      INTEGER NOT NULL,
    searches            INTEGER NOT NULL,
    view_content        INTEGER NOT NULL,
    add_to_cart         INTEGER NOT NULL,
    purchases           INTEGER NOT NULL,
    group_name          TEXT NOT NULL
);

-- 4) After loading into raw_campaign_data (see load_data.sql), populate campaign_data via:
-- INSERT INTO campaign_data (...columns...)
-- SELECT ... FROM raw_campaign_data;
-- (That statement lives in load_data.sql so you can re-run it after each import.)
