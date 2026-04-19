import pandas as pd

# ── Load Data ──────────────────────────────────────────
df = pd.read_csv("../data/social_media_revenue.csv")

# ── 1. Basic Info ──────────────────────────────────────
print("="*50)
print("SHAPE (rows, columns):")
print(df.shape)

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nDATA TYPES:")
print(df.dtypes)

# ── 2. First Look ──────────────────────────────────────
print("\n" + "="*50)
print("FIRST 5 ROWS:")
print(df.head())

print("\nLAST 5 ROWS:")
print(df.tail())

# ── 3. Missing Values ──────────────────────────────────
print("\n" + "="*50)
print("MISSING VALUES PER COLUMN:")
print(df.isnull().sum())

# ── 4. Duplicates ──────────────────────────────────────
print("\n" + "="*50)
print(f"DUPLICATE ROWS: {df.duplicated().sum()}")

# ── 5. Basic Statistics ────────────────────────────────
print("\n" + "="*50)
print("BASIC STATISTICS:")
print(df.describe().round(2))

# ── 6. Unique Values ───────────────────────────────────
print("\n" + "="*50)
print(f"PLATFORMS: {df['platform'].unique()}")
print(f"YEARS: {sorted(df['year'].unique())}")
print(f"COVID PERIODS: {df['covid_period'].unique()}")

# ── 7. Revenue Range Per Platform ─────────────────────
print("\n" + "="*50)
print("REVENUE RANGE PER PLATFORM (USD Billion):")
print(df.groupby('platform')['revenue_usd_billion'].agg(['min','max','mean']).round(2))

# ── 8. Any Negative Growth? ───────────────────────────
print("\n" + "="*50)
print("PLATFORMS WITH NEGATIVE GROWTH:")
print(df[df['yoy_revenue_growth_pct'] < 0][['platform','year','yoy_revenue_growth_pct']])

print("\n" + "="*50)
print("EDA COMPLETE - Data looks good to clean!")