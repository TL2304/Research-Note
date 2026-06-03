"""
03_descriptives.py
------------------
Variable construction, winsorizing, summary statistics and figures.

Input:  data/processed/panel_clean.parquet
        data/processed/kof_dach_prepared.xlsx
Output: data/processed/panel_with_vars.parquet
        output/tables/summary_statistics.csv
        output/figures/correlation_matrix.png
        output/figures/dv_distribution.png
        output/figures/main_relationship.png

Research design
---------------
Y:   Sale (Umsatz)     = sale
X:   KOF Trade Index   = kof_trade_defacto  (from KOF ETH Zürich)
Mod: Firm size         = log(at)  → ln_at
Int: kof_x_size        = kof_trade_defacto * ln_at  (H2)
Controls:
     roa               = ib / at
     leverage          = (dltt + dlc) / seq
     capx_intensity    = capx / at
     cash_ratio        = che / at

Usage
-----
    python code/03_descriptives.py
"""

import os, math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ── Project root ──────────────────────────────────────────────────────────────
# Hard-coded to avoid slow Box-Sync folder scan
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
print(f"Project root: {PROJECT_ROOT}")

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150, "font.family": "sans-serif"})
WU_BLUE = "#002f5f"
WU_RED  = "#c8102e"

# ── Paths ─────────────────────────────────────────────────────────────────────
IN_PATH   = Path("data/processed/panel_clean.parquet")
KOF_PATH  = Path("data/processed/kof_dach_prepared.xlsx")
OUT_PANEL = Path("data/processed/panel_with_vars.parquet")
TABLE_PATH = Path("output/tables")
FIG_PATH   = Path("output/figures")
TABLE_PATH.mkdir(parents=True, exist_ok=True)
FIG_PATH.mkdir(parents=True, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
print("\nLoading clean panel...")
df = pd.read_parquet(IN_PATH)
print(f"  Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

# ── Load & Merge KOF ──────────────────────────────────────────────────────────
print("\nMerging KOF Trade Index...")
kof = pd.read_excel(KOF_PATH, header=1)
kof = kof[["ISO3", "Year", "KOF Trade (de facto)"]].rename(columns={
    "ISO3":                 "fic",
    "Year":                 "fyear",
    "KOF Trade (de facto)": "kof_trade_defacto",
})
df = df.merge(kof, on=["fic", "fyear"], how="left")
n_matched = df["kof_trade_defacto"].notna().sum()
print(f"  KOF matched: {n_matched:,} / {len(df):,} ({n_matched/len(df)*100:.1f}%)")

# ── Data quality filters ──────────────────────────────────────────────────────
print("\nApplying data quality filters...")
n = len(df)
df = df[(df["at"] > 0.1) & (df["sale"] > 0) & (df["seq"] > 0)].copy()
print(f"  After at>0.1, sale>0, seq>0: {len(df):,} (removed {n-len(df):,})")

n = len(df)
df = df[df["at"] >= 1].copy()
print(f"  After at>=1 (remove micro-firms): {len(df):,} (removed {n-len(df):,})")

# ── SME filter ────────────────────────────────────────────────────────────────
n = len(df)
sme_mask = (df["emp"] < 0.25) | (df["at"] <= 43)
df = df[sme_mask].copy()
print(f"  After SME filter: {len(df):,} (removed {n-len(df):,})")

# ── Variable construction ─────────────────────────────────────────────────────
print("\nConstructing variables...")

# Dependent variable
df["sale"] = df["sale"]  # already in Mio EUR

# Independent variable
# kof_trade_defacto already merged above

# Moderator + control: firm size
df["ln_at"] = df["at"].apply(lambda x: math.log(x) if x > 0 else np.nan)

# H2 interaction
df["kof_x_size"] = df["kof_trade_defacto"] * df["ln_at"]

# Controls
at = df["at"].to_numpy(dtype=float, na_value=np.nan)
ib = df["ib"].to_numpy(dtype=float, na_value=np.nan)
dltt = df["dltt"].to_numpy(dtype=float, na_value=np.nan)
dlc  = df["dlc"].to_numpy(dtype=float, na_value=np.nan)
seq  = df["seq"].to_numpy(dtype=float, na_value=np.nan)

roa      = ib / at
leverage = (dltt + dlc) / seq
roa[np.isinf(roa)]           = np.nan
leverage[np.isinf(leverage)] = np.nan

df["roa"]            = roa
df["leverage"]       = leverage
df["capx_intensity"] = df["capx"].fillna(0) / df["at"]
df["cash_ratio"]     = df["che"].fillna(0)  / df["at"]

# ── Drop missing core variables ───────────────────────────────────────────────
CORE_VARS = ["sale", "kof_trade_defacto", "ln_at", "leverage"]
n = len(df)
df = df.dropna(subset=CORE_VARS).copy()
print(f"  Dropped {n-len(df):,} rows with missing core vars")
print(f"  Working sample: {len(df):,} firm-years | {df['gvkey'].nunique():,} firms")

# ── Winsorize at 1%-99% ───────────────────────────────────────────────────────
def winsorize(series, lower=0.01, upper=0.99):
    lo = series.quantile(lower)
    hi = series.quantile(upper)
    return series.clip(lo, hi)

print("\nWinsorizing at 1%-99%...")
for col in ["sale", "roa", "leverage", "capx_intensity", "cash_ratio"]:
    df[col] = winsorize(df[col])
    print(f"  {col:<20} [{df[col].min():>10.4f}, {df[col].max():>10.4f}]")

# Recompute interaction after winsorizing
df["kof_x_size"] = df["kof_trade_defacto"] * df["ln_at"]

# ── Minimum 3 observations per firm ──────────────────────────────────────────
obs   = df.groupby("gvkey")["fyear"].count()
valid = obs[obs >= 3].index
n = len(df)
df = df[df["gvkey"].isin(valid)].copy()
print(f"\nMin 3 obs: {n:,} -> {len(df):,} | {df['gvkey'].nunique():,} firms")

# ── Summary statistics ────────────────────────────────────────────────────────
VAR_LABELS = {
    "sale":              "Revenue / Sale (Mio EUR)",
    "kof_trade_defacto": "KOF Trade Index (de facto)",
    "ln_at":             "Firm Size (log assets)",
    "roa":               "RoA (ib/at)",
    "leverage":          "Leverage ((dltt+dlc)/seq)",
    "capx_intensity":    "CAPX Intensity (capx/at)",
    "cash_ratio":        "Cash Ratio (che/at)",
}

rows = []
for col, label in VAR_LABELS.items():
    arr = np.array(
        [x if x is not None and str(x) != "<NA>" else np.nan
         for x in df[col].to_list()], dtype=float
    )
    arr = arr[~np.isnan(arr) & ~np.isinf(arr)]
    rows.append({
        "Variable": label,
        "count": len(arr),
        "mean":  round(float(np.mean(arr)), 3),
        "std":   round(float(np.std(arr, ddof=1)), 3),
        "min":   round(float(np.min(arr)), 3),
        "25%":   round(float(np.percentile(arr, 25)), 3),
        "50%":   round(float(np.percentile(arr, 50)), 3),
        "75%":   round(float(np.percentile(arr, 75)), 3),
        "max":   round(float(np.max(arr)), 3),
    })
summary = pd.DataFrame(rows).set_index("Variable")
print("\n=== Summary Statistics ===")
print(summary.to_string())
summary.to_csv(TABLE_PATH / "summary_statistics.csv")
print(f"\nSaved summary_statistics.csv")

# ── Correlation matrix ────────────────────────────────────────────────────────
corr = df[list(VAR_LABELS.keys())].rename(columns=VAR_LABELS).corr().round(2)
fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f",
            cmap="RdYlBu_r", center=0, vmin=-1, vmax=1,
            linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
ax.set_title("Correlation Matrix — Research Variables",
             fontsize=13, color=WU_BLUE)
fig.tight_layout()
fig.savefig(FIG_PATH / "correlation_matrix.png", dpi=150)
plt.close()
print("Saved correlation_matrix.png")

# ── DV distribution + median Sale by year ─────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].hist(df["sale"], bins=60, color=WU_BLUE, alpha=0.8, edgecolor="white")
axes[0].axvline(df["sale"].mean(),   color=WU_RED,   lw=2,
                label=f"Mean   = {df['sale'].mean():.1f}")
axes[0].axvline(df["sale"].median(), color="orange", lw=2, ls="--",
                label=f"Median = {df['sale'].median():.1f}")
axes[0].set_xlabel("Umsatz / Sale (Mio EUR)")
axes[0].set_title("Distribution of Sale (Y)", color=WU_BLUE)
axes[0].legend()

yearly = df.groupby("fyear")["sale"].median()
axes[1].bar(yearly.index, yearly.values, color=WU_BLUE, alpha=0.8)
axes[1].set_xlabel("Fiscal Year")
axes[1].set_ylabel("Median Sale (Mio EUR)")
axes[1].set_title("Median Sale by Year", color=WU_BLUE)
fig.tight_layout()
fig.savefig(FIG_PATH / "dv_distribution.png", dpi=150)
plt.close()
print("Saved dv_distribution.png")

# ── Main relationship: KOF Trade Index vs Sale ────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
df_plot = df.dropna(subset=["kof_trade_defacto", "sale"]).reset_index(drop=True)

# Links: Scatter + Bin-Means
axes[0].scatter(df_plot["kof_trade_defacto"], df_plot["sale"],
                alpha=0.08, s=8, color=WU_BLUE)
bins = pd.cut(df_plot["kof_trade_defacto"], bins=15)
bm   = df_plot.groupby(bins, observed=True)[["kof_trade_defacto", "sale"]].mean()
axes[0].plot(bm["kof_trade_defacto"], bm["sale"],
             color=WU_RED, lw=2.5, label="Bin mean")
axes[0].set_xlabel("KOF Trade Globalisation Index (de facto)")
axes[0].set_ylabel("Umsatz / Sale (Mio EUR)")
axes[0].set_title("KOF Trade Index vs. Sale\n(H1 preview)", color=WU_BLUE)
axes[0].legend()

# Rechts: Median Sale by Firm Size — DEU vs AUT (H2 preview)
df_plot["size_bin"] = pd.cut(df_plot["ln_at"], bins=10)
palette2 = {"AUT": WU_BLUE, "DEU": WU_RED}
for country, group in df_plot.groupby("fic", observed=True):
    g  = group.reset_index(drop=True)
    bm = g.groupby("size_bin", observed=True)[["ln_at", "sale"]].median()
    axes[1].plot(bm["ln_at"], bm["sale"], lw=2,
                 label=country, color=palette2.get(country, "gray"),
                 marker="o", markersize=5)
axes[1].set_xlabel("Firm Size (log assets)")
axes[1].set_ylabel("Median Sale (Mio EUR)")
axes[1].set_title("Median Sale by Firm Size:\nDEU vs AUT (H2 preview)", color=WU_BLUE)
axes[1].legend()

fig.suptitle("Main Relationship: KOF Trade Index → Sale",
             fontsize=13, color=WU_BLUE, y=1.02)
fig.tight_layout()
fig.savefig(FIG_PATH / "main_relationship.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved main_relationship.png")

# ── Save panel with variables ─────────────────────────────────────────────────
df.to_parquet(OUT_PANEL, index=False)
print(f"\nSaved panel_with_vars.parquet: {df.shape[0]:,} rows x {df.shape[1]} columns")
print("Next step: python code/04_regression.py")