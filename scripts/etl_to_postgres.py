"""
=============================================================
 BLUESTOCK FINTECH — Mutual Fund Analytics Platform
 etl_to_postgres.py  |  Loads CSVs directly into local PostgreSQL
=============================================================

PREREQUISITES:
  1. PostgreSQL installed & running on this machine
  2. Database 'bluestock_mf' created in pgAdmin:
       CREATE DATABASE bluestock_mf;
  3. schema_postgres.sql already run inside that database
     (creates all 11 empty tables)
  4. pip install pandas sqlalchemy psycopg2-binary

EDIT BELOW:
  - PG_PASSWORD  → your actual Postgres password
  - DATA_DIR     → folder where your 10 CSV files are saved

RUN:
  python etl_to_postgres.py
=============================================================
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

# ─────────────────────────────────────────────
#  CONFIG — EDIT THESE
# ─────────────────────────────────────────────
DATA_DIR    = r"C:\Users\ELCOT\Downloads\last project"        # CSV folder
PG_USER     = "postgres"
PG_PASSWORD = "password"                                       # Postgres password
PG_HOST     = "localhost"
PG_PORT     = "5432"
PG_DATABASE = "bluestock_mf"


def get_engine():
    url = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    return create_engine(url)


# ─────────────────────────────────────────────
#  STEP 1: dim_fund
# ─────────────────────────────────────────────
def load_dim_fund(engine):
    print("\n[1/11] Loading dim_fund...")
    df = pd.read_csv(f"{DATA_DIR}/01_fund_master.csv")
    df["launch_date"] = pd.to_datetime(df["launch_date"]).dt.strftime("%Y-%m-%d")
    df.to_sql("dim_fund", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → dim_fund")


# ─────────────────────────────────────────────
#  STEP 2: dim_date (auto-generated, no CSV needed)
# ─────────────────────────────────────────────
def load_dim_date(engine):
    print("\n[2/11] Generating dim_date...")
    dates = pd.date_range(start="2022-01-01", end="2026-12-31", freq="D")

    def fy_year(dt):
        return f"FY{dt.year + 1}" if dt.month >= 4 else f"FY{dt.year}"

    records = []
    for dt in dates:
        records.append({
            "date_value"  : dt.strftime("%Y-%m-%d"),
            "year"        : dt.year,
            "quarter"     : dt.quarter,
            "month"       : dt.month,
            "month_name"  : dt.strftime("%B"),
            "week_of_year": int(dt.strftime("%W")),
            "day_of_week" : dt.dayofweek,
            "day_name"    : dt.strftime("%A"),
            "is_weekday"  : 1 if dt.dayofweek < 5 else 0,
            "fy_year"     : fy_year(dt),
        })
    df = pd.DataFrame(records)
    df.to_sql("dim_date", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → dim_date")


# ─────────────────────────────────────────────
#  STEP 3: fact_nav  (with computed daily_return_pct)
# ─────────────────────────────────────────────
def load_fact_nav(engine):
    print("\n[3/11] Loading fact_nav...")
    df = pd.read_csv(f"{DATA_DIR}/02_nav_history.csv")
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
    df = df.rename(columns={"date": "date_value"})
    df.to_sql("fact_nav", engine, if_exists="append", index=False,
               method="multi", chunksize=5000)
    print(f"      ✅ {len(df)} rows → fact_nav")


# ─────────────────────────────────────────────
#  STEP 4: fact_aum
# ─────────────────────────────────────────────
def load_fact_aum(engine):
    print("\n[4/11] Loading fact_aum...")
    df = pd.read_csv(f"{DATA_DIR}/03_aum_by_fund_house.csv")
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.rename(columns={"date": "quarter_end_date"})
    df.to_sql("fact_aum", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → fact_aum")


# ─────────────────────────────────────────────
#  STEP 5: fact_sip_industry
# ─────────────────────────────────────────────
def load_fact_sip_industry(engine):
    print("\n[5/11] Loading fact_sip_industry...")
    df = pd.read_csv(f"{DATA_DIR}/04_monthly_sip_inflows.csv")
    df.to_sql("fact_sip_industry", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → fact_sip_industry")


# ─────────────────────────────────────────────
#  STEP 6: fact_category_inflows
# ─────────────────────────────────────────────
def load_fact_category_inflows(engine):
    print("\n[6/11] Loading fact_category_inflows...")
    df = pd.read_csv(f"{DATA_DIR}/05_category_inflows.csv")
    df.to_sql("fact_category_inflows", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → fact_category_inflows")


# ─────────────────────────────────────────────
#  STEP 7: fact_folio_count
# ─────────────────────────────────────────────
def load_fact_folio_count(engine):
    print("\n[7/11] Loading fact_folio_count...")
    df = pd.read_csv(f"{DATA_DIR}/06_industry_folio_count.csv")
    df.to_sql("fact_folio_count", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → fact_folio_count")


# ─────────────────────────────────────────────
#  STEP 8: fact_performance
# ─────────────────────────────────────────────
def load_fact_performance(engine):
    print("\n[8/11] Loading fact_performance...")
    df = pd.read_csv(f"{DATA_DIR}/07_scheme_performance.csv")
    df = df.drop(columns=["scheme_name", "fund_house", "category", "plan"], errors="ignore")
    df["as_of_date"] = "2025-12-31"
    df.to_sql("fact_performance", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → fact_performance")


# ─────────────────────────────────────────────
#  STEP 9: fact_transactions
# ─────────────────────────────────────────────
def load_fact_transactions(engine):
    print("\n[9/11] Loading fact_transactions...")
    df = pd.read_csv(f"{DATA_DIR}/08_investor_transactions.csv")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.strftime("%Y-%m-%d")
    df.to_sql("fact_transactions", engine, if_exists="append", index=False,
               method="multi", chunksize=5000)
    print(f"      ✅ {len(df)} rows → fact_transactions")


# ─────────────────────────────────────────────
#  STEP 10: fact_portfolio
# ─────────────────────────────────────────────
def load_fact_portfolio(engine):
    print("\n[10/11] Loading fact_portfolio...")
    df = pd.read_csv(f"{DATA_DIR}/09_portfolio_holdings.csv")
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"]).dt.strftime("%Y-%m-%d")
    df.to_sql("fact_portfolio", engine, if_exists="append", index=False)
    print(f"      ✅ {len(df)} rows → fact_portfolio")


# ─────────────────────────────────────────────
#  STEP 11: fact_benchmark
# ─────────────────────────────────────────────
def load_fact_benchmark(engine):
    print("\n[11/11] Loading fact_benchmark...")
    df = pd.read_csv(f"{DATA_DIR}/10_benchmark_indices.csv")
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df.rename(columns={"date": "date_value"})
    df.to_sql("fact_benchmark", engine, if_exists="append", index=False,
               method="multi", chunksize=5000)
    print(f"      ✅ {len(df)} rows → fact_benchmark")


# ─────────────────────────────────────────────
#  VERIFY
# ─────────────────────────────────────────────
def verify_load(engine):
    print("\n" + "="*50)
    print("  LOAD VERIFICATION — Row Counts (PostgreSQL)")
    print("="*50)
    tables = [
        "dim_fund", "dim_date", "fact_nav", "fact_aum",
        "fact_sip_industry", "fact_category_inflows", "fact_folio_count",
        "fact_performance", "fact_transactions", "fact_portfolio", "fact_benchmark"
    ]
    with engine.connect() as conn:
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  ✅ {table:<25} {count:>7} rows")
    print("="*50)
    print("\n  🎉 All data loaded into PostgreSQL successfully!\n")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("="*50)
    print("  BLUESTOCK MF — CSV → PostgreSQL ETL")
    print("="*50)

    engine = get_engine()

    load_dim_fund(engine)
    load_dim_date(engine)
    load_fact_nav(engine)
    load_fact_aum(engine)
    load_fact_sip_industry(engine)
    load_fact_category_inflows(engine)
    load_fact_folio_count(engine)
    load_fact_performance(engine)
    load_fact_transactions(engine)
    load_fact_portfolio(engine)
    load_fact_benchmark(engine)

    verify_load(engine)
