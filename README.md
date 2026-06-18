# Bluestock MF Capstone — Mutual Fund Analytics Platform

End-to-end data engineering, ETL pipeline, and interactive Power BI dashboard for mutual fund analytics, built as a capstone project for Bluestock Fintech.

**Repo:** `https://github.com/kutty12122004-ui/bluestock-mf-capstone`

## Overview

Covers 40 real mutual fund schemes, ~89,000 rows across 10 source datasets, anchored to real AMFI India NAV and AUM data. The platform ingests raw CSV data, loads it into a PostgreSQL star-schema database, and surfaces fund performance, risk metrics, and investor behaviour through Jupyter notebooks and a 4-page Power BI dashboard.

## Tech Stack

- Python 3 (Pandas, NumPy, SciPy) — ETL and metric computation
- PostgreSQL — production relational database
- Power BI Desktop — interactive dashboard
- Jupyter / Kaggle Notebooks — EDA and advanced analytics
- Matplotlib, Seaborn, Plotly — charting

## Project Structure

```
bluestock-mf-capstone/
├── data/                       Raw CSV datasets (10 files)
├── sql/
│   └── schema_postgres.sql     Database schema (2 dim + 9 fact tables)
├── scripts/
│   └── etl_to_postgres.py      Loads CSVs into PostgreSQL
├── notebooks/
│   ├── EDA_Analysis.ipynb              Exploratory data analysis
│   └── Advanced_Analytics.ipynb        VaR, Sharpe, cohorts, recommender
├── dashboard/
│   └── bluestock_mf.pbix       Power BI dashboard file
├── reports/
│   ├── Bluestock_MF_Final_Report.docx
│   └── Bluestock_MF_Presentation.pptx
└── README.md
```

## Database Schema

Star schema with 2 dimension tables and 9 fact tables, ~89,000 rows total.

| Table | Type | Rows | Grain |
|---|---|---|---|
| dim_fund | Dimension | 40 | One row per scheme |
| dim_date | Dimension | 1,826 | One row per day, 2022–2026 |
| fact_nav | Fact | 46,000 | Fund × Trading Day |
| fact_transactions | Fact | 32,778 | One row per transaction |
| fact_performance | Fact | 40 | One row per fund |
| fact_portfolio | Fact | 322 | Fund × Stock Holding |
| fact_aum | Fact | 90 | Fund House × Quarter |
| fact_sip_industry | Fact | 48 | One row per month |
| fact_category_inflows | Fact | 144 | Month × Category |
| fact_folio_count | Fact | 21 | One row per quarter |
| fact_benchmark | Fact | 8,050 | Index × Trading Day |

## Setup

### 1. Create the database

In PostgreSQL (via pgAdmin or psql):

```sql
CREATE DATABASE bluestock_mf;
```

Then run `sql/schema_postgres.sql` against that database to create all 11 tables.

### 2. Load the data

Edit `scripts/etl_to_postgres.py` to set your CSV folder path and Postgres password, then:

```bash
pip install pandas sqlalchemy psycopg2-binary
python scripts/etl_to_postgres.py
```

This loads all 10 CSVs into the 11 tables and prints a row-count verification.

### 3. Run the notebooks

Open `notebooks/EDA_Analysis.ipynb` and `notebooks/Advanced_Analytics.ipynb` in Jupyter or Kaggle. Both auto-detect the CSV folder path.

### 4. Open the dashboard

Open `dashboard/bluestock_mf.pbix` in Power BI Desktop and point the data source connection at your local `bluestock_mf` database.

## Dashboard Pages

- **Industry Overview** — AUM by year and fund house, KPI cards
- **Fund Performance** — Risk-vs-Return bubble chart, sortable fund scorecard
- **Investor Analytics** — City, age group, transaction-type breakdowns
- **SIP & Market Trends** — SIP inflow vs Nifty 50, category inflow matrix

## Key Metrics Computed

Sharpe Ratio, Sortino Ratio, Alpha, Beta, Maximum Drawdown, Historical VaR/CVaR (95%), rolling 90-day Sharpe, sector concentration (HHI), and a rule-based fund recommender by risk appetite.

## Limitations

Investor transaction data is synthetically generated. Cohort analysis is limited to 2024–2025 due to the transaction data's date range. Full details in the final report.

## Disclaimer

All data is sourced from publicly available AMFI India, mfapi.in, and NSE/BSE information. This project is for educational purposes only and does not constitute financial advice.
