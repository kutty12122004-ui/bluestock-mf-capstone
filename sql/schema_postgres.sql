-- ============================================================
--  BLUESTOCK FINTECH — Mutual Fund Analytics Platform
--  schema_postgres.sql  |  PostgreSQL version
--  Run this in pgAdmin Query Tool, connected to bluestock_mf database
-- ============================================================

DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_portfolio;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS fact_sip_industry;
DROP TABLE IF EXISTS fact_category_inflows;
DROP TABLE IF EXISTS fact_folio_count;
DROP TABLE IF EXISTS fact_benchmark;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;


-- ============================================================
--  DIMENSION TABLE 1: dim_fund
-- ============================================================
CREATE TABLE dim_fund (
    amfi_code           INTEGER     PRIMARY KEY,
    fund_house          TEXT        NOT NULL,
    scheme_name         TEXT        NOT NULL,
    category            TEXT        NOT NULL,
    sub_category        TEXT        NOT NULL,
    plan                TEXT        NOT NULL,
    launch_date         DATE        NOT NULL,
    benchmark            TEXT        NOT NULL,
    expense_ratio_pct   REAL        NOT NULL,
    exit_load_pct       REAL        NOT NULL,
    min_sip_amount      INTEGER     NOT NULL,
    min_lumpsum_amount  INTEGER     NOT NULL,
    fund_manager        TEXT        NOT NULL,
    risk_category       TEXT        NOT NULL,
    sebi_category_code  TEXT        NOT NULL
);


-- ============================================================
--  DIMENSION TABLE 2: dim_date
-- ============================================================
CREATE TABLE dim_date (
    date_value      DATE        PRIMARY KEY,
    year            INTEGER     NOT NULL,
    quarter         INTEGER     NOT NULL,
    month           INTEGER     NOT NULL,
    month_name      TEXT        NOT NULL,
    week_of_year    INTEGER     NOT NULL,
    day_of_week     INTEGER     NOT NULL,
    day_name        TEXT        NOT NULL,
    is_weekday      INTEGER     NOT NULL,
    fy_year         TEXT        NOT NULL
);


-- ============================================================
--  FACT TABLE 1: fact_nav
-- ============================================================
CREATE TABLE fact_nav (
    nav_id              SERIAL      PRIMARY KEY,
    amfi_code           INTEGER     NOT NULL REFERENCES dim_fund(amfi_code),
    date_value          DATE        NOT NULL REFERENCES dim_date(date_value),
    nav                 REAL        NOT NULL CHECK (nav > 0),
    daily_return_pct    REAL,
    UNIQUE (amfi_code, date_value)
);
CREATE INDEX idx_fact_nav_code  ON fact_nav(amfi_code);
CREATE INDEX idx_fact_nav_date  ON fact_nav(date_value);


-- ============================================================
--  FACT TABLE 2: fact_transactions
-- ============================================================
CREATE TABLE fact_transactions (
    tx_id               SERIAL      PRIMARY KEY,
    investor_id         TEXT        NOT NULL,
    transaction_date    DATE        NOT NULL REFERENCES dim_date(date_value),
    amfi_code           INTEGER     NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_type    TEXT        NOT NULL CHECK (transaction_type IN ('SIP','Lumpsum','Redemption')),
    amount_inr          INTEGER     NOT NULL CHECK (amount_inr > 0),
    state               TEXT        NOT NULL,
    city                TEXT        NOT NULL,
    city_tier           TEXT        NOT NULL CHECK (city_tier IN ('T30','B30')),
    age_group           TEXT        NOT NULL,
    gender              TEXT        NOT NULL CHECK (gender IN ('Male','Female')),
    annual_income_lakh  REAL        NOT NULL,
    payment_mode        TEXT        NOT NULL,
    kyc_status          TEXT        NOT NULL CHECK (kyc_status IN ('Verified','Pending'))
);
CREATE INDEX idx_fact_tx_investor  ON fact_transactions(investor_id);
CREATE INDEX idx_fact_tx_code      ON fact_transactions(amfi_code);
CREATE INDEX idx_fact_tx_date      ON fact_transactions(transaction_date);
CREATE INDEX idx_fact_tx_state     ON fact_transactions(state);


-- ============================================================
--  FACT TABLE 3: fact_performance
-- ============================================================
CREATE TABLE fact_performance (
    perf_id             SERIAL      PRIMARY KEY,
    amfi_code           INTEGER     NOT NULL REFERENCES dim_fund(amfi_code),
    as_of_date          DATE        NOT NULL,
    return_1yr_pct      REAL        NOT NULL,
    return_3yr_pct      REAL        NOT NULL,
    return_5yr_pct      REAL        NOT NULL,
    benchmark_3yr_pct   REAL        NOT NULL,
    alpha               REAL        NOT NULL,
    beta                REAL        NOT NULL,
    sharpe_ratio        REAL        NOT NULL,
    sortino_ratio       REAL        NOT NULL,
    std_dev_ann_pct     REAL        NOT NULL,
    max_drawdown_pct    REAL        NOT NULL,
    aum_crore           INTEGER     NOT NULL,
    expense_ratio_pct   REAL        NOT NULL,
    morningstar_rating  INTEGER     NOT NULL CHECK (morningstar_rating BETWEEN 1 AND 5),
    risk_grade          TEXT        NOT NULL,
    UNIQUE (amfi_code, as_of_date)
);


-- ============================================================
--  FACT TABLE 4: fact_portfolio
-- ============================================================
CREATE TABLE fact_portfolio (
    holding_id          SERIAL      PRIMARY KEY,
    amfi_code           INTEGER     NOT NULL REFERENCES dim_fund(amfi_code),
    stock_symbol        TEXT        NOT NULL,
    stock_name          TEXT        NOT NULL,
    sector              TEXT        NOT NULL,
    weight_pct          REAL        NOT NULL CHECK (weight_pct > 0),
    market_value_cr     REAL        NOT NULL,
    current_price_inr   REAL        NOT NULL,
    portfolio_date      DATE        NOT NULL
);
CREATE INDEX idx_fact_portfolio_code    ON fact_portfolio(amfi_code);
CREATE INDEX idx_fact_portfolio_sector  ON fact_portfolio(sector);


-- ============================================================
--  FACT TABLE 5: fact_aum
-- ============================================================
CREATE TABLE fact_aum (
    aum_id              SERIAL      PRIMARY KEY,
    quarter_end_date    DATE        NOT NULL,
    fund_house          TEXT        NOT NULL,
    aum_lakh_crore      REAL        NOT NULL,
    aum_crore           INTEGER     NOT NULL,
    num_schemes         INTEGER     NOT NULL,
    UNIQUE (quarter_end_date, fund_house)
);
CREATE INDEX idx_fact_aum_house  ON fact_aum(fund_house);


-- ============================================================
--  FACT TABLE 6: fact_sip_industry
-- ============================================================
CREATE TABLE fact_sip_industry (
    sip_id                      SERIAL      PRIMARY KEY,
    month                       TEXT        NOT NULL UNIQUE,
    sip_inflow_crore            INTEGER     NOT NULL,
    active_sip_accounts_crore   REAL        NOT NULL,
    new_sip_accounts_lakh       REAL        NOT NULL,
    sip_aum_lakh_crore          REAL        NOT NULL,
    yoy_growth_pct              REAL
);


-- ============================================================
--  FACT TABLE 7: fact_category_inflows
-- ============================================================
CREATE TABLE fact_category_inflows (
    inflow_id           SERIAL      PRIMARY KEY,
    month               TEXT        NOT NULL,
    category            TEXT        NOT NULL,
    net_inflow_crore    REAL        NOT NULL,
    UNIQUE (month, category)
);
CREATE INDEX idx_fact_cat_month     ON fact_category_inflows(month);
CREATE INDEX idx_fact_cat_category  ON fact_category_inflows(category);


-- ============================================================
--  FACT TABLE 8: fact_folio_count
-- ============================================================
CREATE TABLE fact_folio_count (
    folio_id                SERIAL      PRIMARY KEY,
    month                   TEXT        NOT NULL UNIQUE,
    total_folios_crore      REAL        NOT NULL,
    equity_folios_crore     REAL        NOT NULL,
    debt_folios_crore       REAL        NOT NULL,
    hybrid_folios_crore     REAL        NOT NULL,
    others_folios_crore     REAL        NOT NULL
);


-- ============================================================
--  FACT TABLE 9: fact_benchmark
-- ============================================================
CREATE TABLE fact_benchmark (
    benchmark_id    SERIAL      PRIMARY KEY,
    date_value      DATE        NOT NULL REFERENCES dim_date(date_value),
    index_name      TEXT        NOT NULL,
    close_value     REAL        NOT NULL CHECK (close_value > 0),
    UNIQUE (date_value, index_name)
);
CREATE INDEX idx_fact_bm_date   ON fact_benchmark(date_value);
CREATE INDEX idx_fact_bm_index  ON fact_benchmark(index_name);

-- ============================================================
--  END OF SCHEMA
-- ============================================================
