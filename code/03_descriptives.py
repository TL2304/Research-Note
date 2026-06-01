"""
03_descriptives.py
------------------
Summary statistics and exploratory figures.

Input:  data/processed/panel_clean.parquet
        data/processed/kof_dach_prepared.xlsx
Output: output/tables/summary_statistics.csv
        output/figures/correlation_matrix.png
        output/figures/kof_sale_relationship.png
        output/figures/sample_composition.png
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"figure.dpi": 150, "font.family": "sans-serif"})
WU_BLUE = "#002f5f"
WU_RED  = "#c8102e"

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_PATH   = Path("data/processed/panel_clean.parquet")
KOF_PATH    = Path("data/processed/kof_dach_prepared.xlsx")
TABLE_PATH  = Path("output/tables")
FIGURE_PATH = Path("output/figures")
TABLE_PATH.mkdir(parents=True, exist_ok=True)
FIGURE_PATH.mkdir(parents=True, exist_ok=True)

# ── Load Compustat Panel ───────────────────────────────────────────────────────
df = pd.read_parquet(DATA_PATH)
print(f"Loaded {len(df):,} observations | {df['gvkey'].nunique():,} firms")

# ── Load & Merge KOF ──────────────────────────────────────────────────────────
kof = pd.read_excel(KOF_PATH, header=1)
kof = kof[["ISO3", "Year", "KOF Trade (de facto)"]].rename(columns={
    "ISO3":                 "fic",
    "Year":                 "fyear",
    "KOF Trade (de facto)": "kof_trade_defacto",
})
df = df.merge(kof, on=["fic", "fyear"], how="left")
n_matched = df["kof_trade_defacto"].notna().sum()
print(f"KOF merged: {n_matched:,} / {len(df):,} Beobachtungen ({n_matched/len(df)*100:.1f}%)")

# ── Fix ROA & Leverage (Float64 → float64, inf → NaN) ────────────────────────
def clean_col(series):
    arr = series.to_numpy(dtype=float, na_value=np.nan)
    arr[np.isinf(arr)] = np.nan
    return pd.Series(arr, index=series.index)

df["roa"]      = clean_col(df["roa"])
df["leverage"] = clean_col(df["leverage"])

# ── 1. Summary Statistics ─────────────────────────────────────────────────────
VAR_LABELS = {
    "kof_trade_defacto": "KOF Trade Index (de facto)",
    "sale":              "Umsatz (Sale, Mio EUR)",
    "roa":               "ROA",
    "leverage":          "Leverage",
    "log_at":            "Firm size (log assets)",
    "emp":               "Mitarbeiter (Tsd.)",
}

rows = []
for col, label in VAR_LABELS.items():
    arr = np.array([x if x is not None and str(x) != '<NA>' else np.nan for x in df[col].to_list()], dtype=float)
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
print(f"Saved summary_statistics.csv")

# ── 2. Correlation Matrix ─────────────────────────────────────────────────────
corr_vars = list(VAR_LABELS.keys())
corr = df[corr_vars].rename(columns=VAR_LABELS).corr().round(2)

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, annot=True, fmt=".2f",
    cmap="RdYlBu_r", center=0, vmin=-1, vmax=1,
    linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8},
)
ax.set_title("Correlation Matrix — Key Variables", fontsize=13, pad=12, color=WU_BLUE)
fig.tight_layout()
fig.savefig(FIGURE_PATH / "correlation_matrix.png", dpi=150)
plt.close()
print("Saved correlation_matrix.png")

# ── 3. KOF–Sale Relationship (H1 preview) ─────────────────────────────────────
df_plot = df.dropna(subset=["kof_trade_defacto", "sale"]).copy()
df_plot.reset_index(drop=True, inplace=True)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

axes[0].scatter(df_plot["kof_trade_defacto"], df_plot["sale"],
                alpha=0.08, s=8, color=WU_BLUE)
bins = pd.cut(df_plot["kof_trade_defacto"], bins=15)
bin_means = df_plot.groupby(bins, observed=True)[["kof_trade_defacto", "sale"]].mean()
axes[0].plot(bin_means["kof_trade_defacto"], bin_means["sale"],
             color=WU_RED, lw=2.5, label="Bin mean")
axes[0].set_xlabel("KOF Trade Globalisation Index (de facto)")
axes[0].set_ylabel("Umsatz (Sale, Mio EUR)")
axes[0].set_title("KOF Trade Index vs. Umsatz — Raw Relationship", color=WU_BLUE)
axes[0].legend()

kof_full = pd.read_excel(KOF_PATH, header=1)
for country, color, ls in [("AUT", WU_BLUE, "-"), ("DEU", WU_RED, "--")]:
    subset = kof_full[kof_full["ISO3"] == country]
    axes[1].plot(subset["Year"], subset["KOF Trade (de facto)"],
                 lw=2, label=country, color=color, linestyle=ls)

axes[1].axvspan(2008, 2009, alpha=0.08, color="gray", label="Finanzkrise")
axes[1].axvspan(2020, 2020.5, alpha=0.08, color="orange", label="COVID")
axes[1].set_xlabel("Jahr")
axes[1].set_ylabel("KOF Trade Index (de facto)")
axes[1].set_title("KOF Trade Index — DEU vs. AUT (2000–2023)", color=WU_BLUE)
axes[1].legend()

fig.suptitle(
    "KOF Trade Globalisation Index & Umsatz — KMU in DEU & AUT",
    fontsize=13, y=1.02, color=WU_BLUE,
)
fig.tight_layout()
fig.savefig(FIGURE_PATH / "kof_sale_relationship.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved kof_sale_relationship.png")

# ── 4. Sample Composition ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

country_counts = df["loc"].value_counts().head(10)
axes[0].barh(country_counts.index[::-1], country_counts.values[::-1], color=WU_BLUE)
axes[0].set_xlabel("Firm-year observations")
axes[0].set_title("Länder im Sample", color=WU_BLUE)

year_counts = df["fyear"].value_counts().sort_index()
axes[1].bar(year_counts.index, year_counts.values, color=WU_BLUE)
axes[1].set_xlabel("Fiscal Year")
axes[1].set_ylabel("Observations")
axes[1].set_title("Sample Coverage by Year", color=WU_BLUE)

fig.tight_layout()
fig.savefig(FIGURE_PATH / "sample_composition.png", dpi=150)
plt.close()
print("Saved sample_composition.png")

print("\nDescriptives complete. Check output/tables/ and output/figures/")