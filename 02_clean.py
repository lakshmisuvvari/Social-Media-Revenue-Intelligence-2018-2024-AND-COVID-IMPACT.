import pandas as pd
import os

# ── Load raw data ──────────────────────────────────────────────────
df = pd.read_csv("../data/social_media_revenue.csv")

print("=" * 50)
print("CLEANING STARTED")
print(f"Raw shape: {df.shape}")

# ── 1. Standardise column names ────────────────────────────────────
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
print(f"\nColumns: {df.columns.tolist()}")

# ── 2. Check & fix data types ─────────────────────────────────────
df["year"] = df["year"].astype(int)
df["revenue_usd_billion"]         = pd.to_numeric(df["revenue_usd_billion"],         errors="coerce")
df["ad_revenue_usd_billion"]      = pd.to_numeric(df["ad_revenue_usd_billion"],      errors="coerce")
df["other_revenue_usd_billion"]   = pd.to_numeric(df["other_revenue_usd_billion"],   errors="coerce")
df["monthly_active_users_million"]= pd.to_numeric(df["monthly_active_users_million"],errors="coerce")
df["yoy_revenue_growth_pct"]      = pd.to_numeric(df["yoy_revenue_growth_pct"],      errors="coerce")
print(f"\nAfter type fix nulls: {df.isnull().sum().sum()}")

# ── 3. Fill nulls with platform median ────────────────────────────
num_cols = ["revenue_usd_billion", "ad_revenue_usd_billion",
            "other_revenue_usd_billion", "monthly_active_users_million",
            "yoy_revenue_growth_pct"]

for col in num_cols:
    nulls = df[col].isnull().sum()
    if nulls > 0:
        df[col] = df.groupby("platform")[col].transform(
            lambda x: x.fillna(x.median())
        )
        print(f"  Filled {nulls} nulls in {col}")

# ── 4. Feature engineering ────────────────────────────────────────

# COVID flag (overwrite/confirm from raw data)
df["covid_flag"] = df["year"].apply(
    lambda y: "Pre-COVID" if y <= 2019
    else "COVID"     if y == 2020
    else "Recovery"  if y <= 2022
    else "Post-COVID"
)

# Negative growth flag
df["growth_flag"] = df["yoy_revenue_growth_pct"].apply(
    lambda x: "Decline"  if pd.notna(x) and x < 0
    else      "Growth"   if pd.notna(x) and x > 0
    else      "Baseline"
)

# Revenue in millions (useful for Power BI visuals)
df["revenue_usd_million"] = (df["revenue_usd_billion"] * 1000).round(1)

# Ad revenue share %
df["ad_revenue_share_pct"] = (
    df["ad_revenue_usd_billion"] / df["revenue_usd_billion"] * 100
).round(1)

# ── 5. Validation ─────────────────────────────────────────────────
print("\n" + "=" * 50)
print("VALIDATION")
print(f"Shape after clean     : {df.shape}")
print(f"Nulls remaining       : {df.isnull().sum().sum()}")
print(f"Platforms             : {sorted(df['platform'].unique())}")
print(f"Years                 : {sorted(df['year'].unique())}")
print(f"Decline rows          : {len(df[df['growth_flag'] == 'Decline'])}")
print(f"COVID period counts   :\n{df['covid_flag'].value_counts()}")

# ── 6. Preview ────────────────────────────────────────────────────
print("\nSample clean rows (Twitter):")
print(df[df["platform"] == "Twitter"].to_string(index=False))

# ── 7. Export ─────────────────────────────────────────────────────
os.makedirs("../output", exist_ok=True)
df.to_csv("../output/clean_social_media.csv", index=False)

print("\n" + "=" * 50)
print("CLEANING COMPLETE")
print("Saved → output/clean_social_media.csv")
print("Next  → run 03_load_to_sql.py")
