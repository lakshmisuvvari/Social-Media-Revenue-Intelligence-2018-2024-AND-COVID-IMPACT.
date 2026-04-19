"""
03_load_to_sql.py
=================
Loads clean_social_media.csv into a SQLite database and runs
5 analyst queries, printing results and saving them to output/.

Usage:
    python 03_load_to_sql.py
"""

import sqlite3
import pandas as pd
import os

# ── Paths ──────────────────────────────────────────────────────────
CLEAN_CSV  = "../output/clean_social_media.csv"
DB_PATH    = "../output/social_media.db"
OUTPUT_DIR = "../output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 1. Load CSV ────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Loading clean CSV")
print("=" * 60)

df = pd.read_csv(CLEAN_CSV)
print(f"  Rows loaded : {len(df)}")
print(f"  Columns     : {list(df.columns)}")

# ── 2. Write to SQLite ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 2 — Writing to SQLite")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)
df.to_sql("revenue", conn, if_exists="replace", index=False)
print(f"  Database : {DB_PATH}")
print(f"  Table    : revenue  ({len(df)} rows inserted)")

# ── Helper ─────────────────────────────────────────────────────────
def run_query(title, sql, save_as=None):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")
    result = pd.read_sql_query(sql, conn)
    print(result.to_string(index=False))
    if save_as:
        path = os.path.join(OUTPUT_DIR, save_as)
        result.to_csv(path, index=False)
        print(f"  → Saved: {save_as}")
    return result

# ── 3. Analyst Queries ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("STEP 3 — Running 5 Analyst Queries")
print("=" * 60)

# Q1 — Total revenue per platform
run_query(
    "Q1 · Total Revenue per Platform (2018-2024, $B)",
    """
    SELECT
        platform,
        ROUND(SUM(revenue_usd_billion), 1)       AS total_revenue_b,
        ROUND(MIN(revenue_usd_billion), 1)       AS min_revenue_b,
        ROUND(MAX(revenue_usd_billion), 1)       AS max_revenue_b,
        ROUND(AVG(yoy_revenue_growth_pct), 1)    AS avg_yoy_growth_pct
    FROM revenue
    GROUP BY platform
    ORDER BY total_revenue_b DESC
    """,
    save_as="q1_total_revenue_by_platform.csv"
)

# Q2 — COVID impact: avg revenue by era
run_query(
    "Q2 · Average Annual Revenue by Era ($B)",
    """
    SELECT
        platform,
        ROUND(AVG(CASE WHEN covid_flag = 'Pre-COVID'  THEN revenue_usd_billion END), 2) AS avg_pre_covid,
        ROUND(AVG(CASE WHEN covid_flag = 'COVID'      THEN revenue_usd_billion END), 2) AS avg_covid,
        ROUND(AVG(CASE WHEN covid_flag = 'Recovery'   THEN revenue_usd_billion END), 2) AS avg_recovery,
        ROUND(AVG(CASE WHEN covid_flag = 'Post-COVID' THEN revenue_usd_billion END), 2) AS avg_post_covid
    FROM revenue
    GROUP BY platform
    ORDER BY avg_covid DESC
    """,
    save_as="q2_revenue_by_era.csv"
)

# Q3 — Top 10 single-year growth spurts
run_query(
    "Q3 · Top 10 Single-Year Growth Spurts",
    """
    SELECT
        platform,
        year,
        ROUND(revenue_usd_billion, 1)   AS revenue_b,
        yoy_revenue_growth_pct          AS yoy_pct,
        covid_flag
    FROM revenue
    WHERE growth_flag = 'Growth'
    ORDER BY yoy_revenue_growth_pct DESC
    LIMIT 10
    """,
    save_as="q3_top_growth_spurts.csv"
)

# Q4 — Decline years
run_query(
    "Q4 · All Decline Years (Negative Growth)",
    """
    SELECT
        platform,
        year,
        ROUND(revenue_usd_billion, 1)   AS revenue_b,
        yoy_revenue_growth_pct          AS yoy_pct,
        covid_flag
    FROM revenue
    WHERE growth_flag = 'Decline'
    ORDER BY yoy_revenue_growth_pct ASC
    """,
    save_as="q4_decline_years.csv"
)

# Q5 — Industry totals by year
run_query(
    "Q5 · Industry-Wide Revenue Totals by Year ($B)",
    """
    SELECT
        year,
        covid_flag,
        ROUND(SUM(revenue_usd_billion), 1)          AS total_industry_b,
        ROUND(SUM(ad_revenue_usd_billion), 1)       AS total_ad_revenue_b,
        ROUND(AVG(monthly_active_users_million), 0) AS avg_mau_million,
        ROUND(AVG(yoy_revenue_growth_pct), 1)       AS avg_growth_pct
    FROM revenue
    GROUP BY year
    ORDER BY year
    """,
    save_as="q5_industry_totals_by_year.csv"
)

# ── 4. Close & Summary ─────────────────────────────────────────────
conn.close()

print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)
print(f"  Database : output/social_media.db")
print(f"  Query CSVs saved:")
for f in sorted(os.listdir(OUTPUT_DIR)):
    if f.startswith("q") and f.endswith(".csv"):
        print(f"    - {f}")
print()
print("Next -> run 04_export_excel.py")
