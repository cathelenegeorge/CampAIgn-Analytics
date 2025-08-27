
# 🚀 CampAIgn Analytics

> **An end-to-end A/B testing analytics pipeline that cleans campaign data, loads it into SQLite, computes KPIs, generates interactive visualizations, and delivers AI-powered PDF and PPTX reports to identify the winning campaign.**

---

## 📖 Table of Contents
1. [Introduction](#introduction)  
2. [Dataset](#dataset)  
3. [Project Workflow](#project-workflow)  
4. [Folder Structure](#folder-structure)  
5. [SQL Workflow](#sql-workflow)  
6. [Python Pipeline](#python-pipeline)  
7. [Notebooks & Visualizations](#notebooks--visualizations)  
8. [Results & Insights](#results--insights)  
9. [Tech Stack](#tech-stack)  
10. [Setup Instructions](#setup-instructions)  
11. [Future Improvements](#future-improvements)  
12. [License](#license)  

---

## 🔍 Introduction

**CampAIgn Analytics** is an end-to-end  **A/B intelligent testing pipeline** that empowers marketing teams to make data-driven campaign decisions with speed and confidence.

Instead of just comparing raw metrics, this system delivers a fully automated workflow that:

- **Cleans & processes** campaign data with **Python**, ensuring reliability at scale.

- **Computes reproducible KPIs (CTR, CPC, CPA, CPM, Conversion Rate) using SQL & SQLite** for analytical rigor.

- **Generates interactive visualizations** with **Plotly & Jupyter**, enabling stakeholders to explore insights intuitively.

- **Delivers stakeholder-ready reports** in **PDF & PPTX**, enhanced with **AI-generated executive summaries and actionable recommendations**.

⚡ In short, CampAIgn Analytics transforms raw marketing data into clear business outcomes, helping organizations identify the winning campaign and optimize ROI—all in one pipeline.

💡 This project demonstrates qualities like scale—automation, reproducibility, and AI-powered decision intelligence—making it directly relevant to solving large-scale data challenges in industry.

    
## 📂 Dataset

The project is designed around a realistic digital marketing dataset, structured to mirror how enterprises manage campaign analytics pipelines.

- **Raw dataset (`data/raw/campaign_data.csv`)**
  - Captures end-to-end campaign performance metrics:
    - `Campaign Name, Date, Spend [USD], # of Impressions, Reach, # of Website Clicks, # of Searches, # of View Content, # of Add to Cart, # of Purchase`


    <img width="836" height="854" alt="campaign_data" src="https://github.com/user-attachments/assets/20cd3f18-d537-457a-9592-46620b99818a" />
    

- **Processed dataset (`data/processed/cleaned_campaign.csv`)**
  - Automatically generated via loader.py + cleaner.py.
  - Enhancements applied:
    - Standardized headers & enforced datatypes
    - Removal of invalid or incomplete rows
    - Normalized format to ensure reproducibility
  - Acts as the “single source of truth” for all downstream analysis.
  -  - `group` indicates Control (**A**) vs Test (**B**)
  - The group field differentiates Control (A) vs Test (B) cohorts, enabling rigorous A/B testing.
    
    <img width="719" height="727" alt="clean_campaign" src="https://github.com/user-attachments/assets/8e93b498-152f-49d2-a632-5d05dd6948c8" />


✨ This structured data pipeline highlights best practices in data engineering—ensuring clean, validated, and analysis-ready datasets.


---
## 🏗️ Architecture Overview

CampAIgn Analytics follows a modular, production-grade architecture designed for clarity, scalability, and automation.

```

CampAIgn-Analytics/
├─ data/
│  ├─ raw/
│  │  └─ campaign_data.csv
│  └─ processed/
│     └─ cleaned_campaign.csv
│
├─ dbms/                      # SQL workflow
│  ├─ create_table.sql
│  ├─ cleanup_and_reload.sql
│  ├─ sanity_checks.sql
│  ├─ metrics_calculation.sql
│  ├─ ab_summary.sql
│  ├─ daily_trends.sql
│  └─ create_views.sql
│
├─ src/                       # Python package (run: python -m src.pipeline)
│  ├─ __init__.py
│  ├─ pipe.py
│  ├─ data_processing/
│  │  ├─ __init__.py
│  │  ├─ loader.py
│  │  └─ cleaner.py
│  ├─ analysis_engine/
│  │  ├─ __init__.py
│  │  ├─ metrics.py
│  │  ├─ statistic_test.py
│  │  └─ visualization.py
│  └─ reporting/
│     ├─ __init__.py
│     ├─ ai_report.py
│     └─ export.py
│ 
├─ notebook/
│  ├─ chart
│  |  ├─ ts_purchases_by_group.html
│  |  ├─ ts_impressions_by_group.html
│  |  ├─ ts_spend_by_group.html
│  |  ├─ ts_clicks_by_group.html
│  |  ├─ funnel_group_A.html
│  |  ├─ funnel_group_B.html
│  |  ├─ pie_spend_vs_purchases_group_A.html
│  |  └─ pie_spend_vs_purchases_group_B.html
   |─ chart_image
│  |  ├─ ts_purchases_by_group.png
│  |  ├─ ts_impressions_by_group.png
│  |  ├─ ts_spend_by_group.png
│  |  ├─ ts_clicks_by_group.png
│  |  ├─ funnel_group_A.png
│  |  ├─ funnel_group_B.png
│  |  ├─ pie_spend_vs_purchases_group_A.png
│  |  └─ pie_spend_vs_purchases_group_B.png
│  └─ visualisation.ipynb
│
├─ reports/
│  ├─ charts/
│  │  ├─ conversion_rate_by_group.png
│  │  ├─ revenue_distribution.png
│  │  ├─ roi_comparison.png
│  │  ├─ ts_purchases_by_group.png
│  │  ├─ ts_impressions_by_group.png
│  │  ├─ ts_spend_by_group.png
│  │  ├─ ts_clicks_by_group.png
│  │  ├─ funnel_group_A.png
│  │  ├─ funnel_group_B.png
│  │  ├─ pie_spend_vs_purchases_group_A.png
│  │  └─ pie_spend_vs_purchases_group_B.png
│  ├─ final_report.pdf
│  └─ final_report.pptx
│
├─ sql.db                     # SQLite database (often gitignored)
├─ requirements.txt
└─ README.md
```
**🔎 Layer-by-Layer Purpose**
- data/ → Stores raw campaign CSVs and cleaned datasets (single source of truth).
- dbms/ → SQL layer ensures reproducible KPI computation and analytical rigor.
- src/ → Python package for data processing, statistical testing, visualization, and AI   reporting.
- notebook/ → Sandbox for interactive exploration and chart prototyping.
- reports/ → Automatically generated executive-ready deliverables in PDF & PPTX format.
- sql.db → Lightweight database for portability & reproducibility.

💡 This architecture demonstrates a full **data engineering + analytics pipeline**: from raw data ingestion to AI-generated business insights

## 🔄 Project Workflow

CampAIgn Analytics runs as a fully automated pipeline that transforms raw campaign data into executive-ready insights and reports.

**⚡ Step-by-Step Flow**

**1. 📥 Data Ingestion:**  
      - Raw campaign CSVs ingested.  
      - Processed into a clean CSV `(data/processed/cleaned_campaign.csv)` with standardized schema & datatypes.

**2. 🗄️ Database Loading:**  
      - SQLite tables created via `create_table.sql`.  
      - Cleaned data loaded into `sql.db` for reproducibility and fast queries.

**3. ✅ Sanity Checks:**  
      - Validations ensure data integrity:  
        - Row counts match  
        - Nulls handled  
        - Date ranges consistent  
        - Control/Test group distribution verified  

**4. 📊 KPI Calculation:**  
     - Core performance metrics computed directly in SQL:  
         - CTR (Click-Through Rate)  
         - Conversion Rate  
         - CPC (Cost per Click)  
         - CPA (Cost per Acquisition)  
         - CPM (Cost per Mille/1000 Impressions)  

**5. 🔍 Analysis & Summary:**   
    - Statistical testing identifies the winning group (A or B).   
    - Lift analysis quantifies improvement over the control.  

**6. 📈 Visualizations:**  
    - Interactive Plotly dashboards:  
        - Time-series trends  
        - Funnel analysis  
        - Spend vs Purchases breakdown (Pie charts)  

**7. 🤖 AI-Generated Reporting:**   
   - Pipeline produces PDF & PPTX reports with:  
        - Charts embedded  
        - Natural-language executive summaries  
        - Clear business recommendations    

💡 This workflow reflects a production-grade analytics system: data validation, reproducibility, statistical rigor, visualization, and AI-enhanced reporting.

---

## 🗄️ SQL Workflow
- **`create_table.sql`**  
  Creates:  
  - `raw_campaign_data` (staging; mirrors CSV headers for `.import`)  
  - `campaign_data` (normalized; SQL-friendly columns & types)

- **`cleanup_and_reload.sql`**  
  Clears old data, imports `cleaned_campaign.csv` into staging, drops header rows if any, inserts **distinct** rows into `campaign_data`, and prints counts.

- **`sanity_checks.sql`**  
  Validates row counts, date range, nulls, and group distribution.

- **`metrics_calculation.sql`**  
  Group-level KPIs: CTR, Conversion Rate, CPC, CPA, CPM, and funnel step rates.

- **`ab_summary.sql`**  
  Side-by-side comparison of groups with lift metrics and a simple winner decision.

- **`daily_trends.sql`**  
  Time-series KPIs (CTR & Conversion) per group for drift/ramp-up detection.

- **`create_views.sql`**  
  Reusable views:  
  - `vw_group_kpis` (overall KPIs by group)  
  - `vw_daily_kpis` (daily breakdown by group)

---

## 🐍 Python Pipeline
- **`pipe.py`** — Orchestrator that:
  - Runs data cleaning & loading  
  - Executes SQL workflows  
  - Computes KPIs & trends  
  - Generates Plotly charts  
  - Produces AI-written insights  
  - Exports **PDF** and **PPTX** reports to `reports/`

- **`data_processing/`**
  - `loader.py` — Loads raw CSV → SQLite staging table.  
  - `cleaner.py` — Cleans & standardizes dataset → `data/processed/cleaned_campaign.csv`.

- **`analysis_engine/`**
  - `metrics.py` — Python-side KPIs (optional; mirrors SQL).  
  - `statistic_test.py` — Significance testing (e.g., chi-square/t-tests).  
  - `visualization.py` — Plotly charts saved to `reports/charts/`.

- **`reporting/`**
  - `ai_report.py` — Generates narrative insights with AI.  
  - `exporter.py` — Compiles charts + insights → **PDF/PPTX**.

---

## 📓 Notebooks & Visualizations
- **`visualisation.ipynb`** — Interactive Plotly visuals (saved as HTML for sharing).  

**Interactive HTML charts (open in browser):**
- Time Series  
  - [Impressions Over Time](notebook/chart_image/ts_impressions_by_group.png)  
  - [Spend Over Time](notebook/chart_image/ts_spend_by_group.png)  
  - [Purchases Over Time](notebook/chart_image/ts_purchases_by_group.png)  
  - [Website Clicks Over Time](reports/chart_image/ts_clicks_by_group.png)  
- Composition (Spend vs Purchases)  
  - [Group A](notebook/chart_image/pie_spend_vs_purchases_A.png)  
  - [Group B](notebook/chart_image/pie_spend_vs_purchases_B.png)  
- Funnels  
  - [Conversion Funnel — Group A](notebook/chart_image/funnel_group_A.png)  
  - [Conversion Funnel — Group B](notebook/chart_image/funnel_group_B.png)

> GitHub shows notebook outputs as **static previews**. These HTML files keep full **Plotly interactivity** (zoom, hover, toggle series) when opened locally or via a static server.

---

## 📈 Results & Insights
- **Group B** consistently outperformed **Group A**:
  - Higher **Conversion Rate** (≈ +10%)  
  - Lower **Cost per Acquisition (CPA)**  
- Funnel analysis shows **A** drops more between *View Content → Add to Cart*.  
- **Recommendation:** allocate more budget to **B**; optimize mid-funnel for **A**.


## 🛠 Tech Stack
- **Python 3.10+** — pandas, plotly, matplotlib, seaborn  
- **SQLite 3.4+** — SQL-first KPI computation & views  
- **VS Code** — with **SQLite3 Editor** extension for grid outputs  
- **Jupyter Notebooks** — EDA & interactive charts  
- **AI Reporting** — automated insights + **PDF/PPTX** export

---

## ⚙️ Setup Instructions

1. **Clone the repo**   

       git clone https://github.com/cathelenegeorge/CampAIgn-Analytics.gitcd CampAIgn-Analytics

3. **Create a virtual environment**

       -python -m venv venv   
       -source venv/bin/activate   # Mac/Linux     
       -venv\Scripts\activate      # Windows  
       -pip install -r requirements.txt


4. **Create database schema**

       -sqlite3 sql.db ".read dbms/create_table.sql"


5. **Load cleaned dataset**

       -sqlite3 sql.db ".read dbms/cleanup_and_reload.sql"


6. **Run sanity checks**

       -sqlite3 -header -column sql.db ".read dbms/sanity_checks.sql"


7. **Run full pipeline**

        -python -m src.pipeline


Open interactive visuals

Open the PNG files under notebook/chart_image/ see the links above!.

