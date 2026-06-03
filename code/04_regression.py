"""
04_regression.py
----------------
Panel fixed-effects regressions testing H1 and H2.

Input:  data/processed/panel_with_vars.parquet
Output: output/tables/regression_results.csv

Research design
---------------
Y:   Sale (Umsatz)   = sale
X:   KOF Trade Index = kof_trade_defacto
Mod: Firm size       = log(at) → ln_at
Int: kof_x_size      = kof_trade_defacto * ln_at

Hypotheses
----------
H1: β(kof_trade_defacto) > 0 and significant
    Ein höheres Niveau der Handelsoffenheit wirkt sich positiv auf den
    Umsatz kleiner börsennotierter Unternehmen in DE und AT aus.

H2: β(kof_x_size) > 0
    Firmengröße moderiert den Zusammenhang positiv — größere KMU
    profitieren stärker von Handelsoffenheit.

Models
------
(1) Pooled OLS     — baseline, ignores panel structure
(2) TWFE           — two-way FE (firm + year), main specification
(3) TWFE + H2      — adds kof_x_size interaction term

Usage
-----
    python code/04_regression.py
"""

import os, sys, warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from linearmodels.panel import PanelOLS, RandomEffects

warnings.filterwarnings("ignore")

# ── Project root ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
print(f"Project root: {PROJECT_ROOT}")

# ── Paths ─────────────────────────────────────────────────────────────────────
IN_PATH    = Path("data/processed/panel_with_vars.parquet")
TABLE_PATH = Path("output/tables")
TABLE_PATH.mkdir(parents=True, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
print("\nLoading panel with variables...")
df = pd.read_parquet(IN_PATH)
print(f"  Shape: {df.shape[0]:,} rows | {df['gvkey'].nunique():,} firms | "
      f"years {df['fyear'].min()}-{df['fyear'].max()}")

# ── Variables ─────────────────────────────────────────────────────────────────
DV       = "sale"
X_MAIN   = "kof_trade_defacto"
INTERACT = "kof_x_size"        # kof_trade_defacto * ln_at
CONTROLS = ["ln_at", "roa", "leverage", "capx_intensity", "cash_ratio"]

# Build interaction if not already present
if "kof_x_size" not in df.columns:
    df["kof_x_size"] = df["kof_trade_defacto"] * df["ln_at"]

# ── Regression sample ─────────────────────────────────────────────────────────
reg_vars = [DV, X_MAIN, INTERACT] + CONTROLS
df_reg   = df.dropna(subset=reg_vars).copy()
df_panel = df_reg.set_index(["gvkey", "fyear"])
print(f"\nRegression sample: {len(df_reg):,} obs | "
      f"{df_reg['gvkey'].nunique():,} firms")

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_se(res, var):
    """Handles statsmodels (bse) and linearmodels (std_errors)."""
    if hasattr(res, "std_errors"):
        return res.std_errors[var]   # linearmodels
    return res.bse[var]              # statsmodels

def stars(p):
    if p < 0.01: return "***"
    if p < 0.05: return "**"
    if p < 0.10: return "*"
    return ""

# ── Model 1: Pooled OLS ───────────────────────────────────────────────────────
print("\n── Model 1: Pooled OLS ──────────────────────────────")
f1   = f"{DV} ~ {X_MAIN} + {' + '.join(CONTROLS)}"
res1 = smf.ols(f1, data=df_reg).fit(cov_type="HC3")
print(f"  N={int(res1.nobs):,} | R²={res1.rsquared:.3f} | "
      f"{X_MAIN}: {res1.params[X_MAIN]:.4f}{stars(res1.pvalues[X_MAIN])}")

# ── Model 2: TWFE (main) ──────────────────────────────────────────────────────
print("── Model 2: Two-Way Fixed Effects ───────────────────")
f2   = (f"{DV} ~ {X_MAIN} + {' + '.join(CONTROLS)} "
        f"+ EntityEffects + TimeEffects")
res2 = PanelOLS.from_formula(f2, data=df_panel).fit(
    cov_type="clustered", cluster_entity=True)
print(f"  N={int(res2.nobs):,} | R²(within)={res2.rsquared:.3f} | "
      f"{X_MAIN}: {res2.params[X_MAIN]:.4f}{stars(res2.pvalues[X_MAIN])}")

# ── Model 3: TWFE + H2 interaction ───────────────────────────────────────────
print("── Model 3: TWFE + H2 Interaction ───────────────────")
f3   = (f"{DV} ~ {X_MAIN} + {INTERACT} + {' + '.join(CONTROLS)} "
        f"+ EntityEffects + TimeEffects")
res3 = PanelOLS.from_formula(f3, data=df_panel).fit(
    cov_type="clustered", cluster_entity=True)
b_int = res3.params.get(INTERACT, np.nan)
p_int = res3.pvalues.get(INTERACT, 1)
print(f"  N={int(res3.nobs):,} | R²(within)={res3.rsquared:.3f} | "
      f"{INTERACT}: {b_int:.4f}{stars(p_int)}")

# ── Random Effects + Hausman comparison ───────────────────────────────────────
print("── Random Effects (Hausman comparison) ──────────────")
f_re   = f"{DV} ~ {X_MAIN} + {' + '.join(CONTROLS)}"
res_re = RandomEffects.from_formula(f_re, data=df_panel).fit()
diff   = abs(res2.params[X_MAIN] - res_re.params[X_MAIN])
print(f"  FE: {res2.params[X_MAIN]:.4f} | "
      f"RE: {res_re.params[X_MAIN]:.4f} | diff: {diff:.4f}")
print(f"  {'Prefer FE (non-trivial difference)' if diff > 0.005 else 'Small difference — FE still recommended in IB research'}")

# ── Results table ─────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("Regression Results")
print("="*65)

all_vars = [X_MAIN, INTERACT] + CONTROLS
models   = [res1, res2, res3]
labels   = ["(1) OLS", "(2) TWFE", "(3) TWFE+H2"]

rows = []
for var in all_vars:
    row = {"Variable": var}
    for label, res in zip(labels, models):
        if var in res.params.index:
            b  = res.params[var]
            se = get_se(res, var)
            p  = res.pvalues[var]
            row[label]         = f"{b:.4f}{stars(p)}"
            row[f"{label}_se"] = f"({se:.4f})"
        else:
            row[label]         = ""
            row[f"{label}_se"] = ""
    rows.append(row)

stats_rows = [
    {"Variable": "Firm FE",
     "(1) OLS": "No",  "(2) TWFE": "Yes", "(3) TWFE+H2": "Yes"},
    {"Variable": "Year FE",
     "(1) OLS": "No",  "(2) TWFE": "Yes", "(3) TWFE+H2": "Yes"},
    {"Variable": "Clustered SE",
     "(1) OLS": "No",  "(2) TWFE": "Yes", "(3) TWFE+H2": "Yes"},
    {"Variable": "N",
     "(1) OLS":     f"{int(res1.nobs):,}",
     "(2) TWFE":    f"{int(res2.nobs):,}",
     "(3) TWFE+H2": f"{int(res3.nobs):,}"},
    {"Variable": "R²",
     "(1) OLS":     f"{res1.rsquared:.3f}",
     "(2) TWFE":    f"{res2.rsquared:.3f}",
     "(3) TWFE+H2": f"{res3.rsquared:.3f}"},
]
rows.extend(stats_rows)

results_df = pd.DataFrame(rows).set_index("Variable")
print(results_df[labels].to_string())
print("\n* p<0.10  ** p<0.05  *** p<0.01")
print("SEs in parentheses. Models (2)-(3): clustered at firm level.")

results_df.to_csv(TABLE_PATH / "regression_results.csv")
print(f"\nSaved regression_results.csv")

# ── H1 Diagnostic ─────────────────────────────────────────────────────────────
print("\n── H1 Diagnostic ────────────────────────────────────")
b_x = res2.params[X_MAIN]
p_x = res2.pvalues[X_MAIN]
print(f"  β(kof_trade_defacto) = {b_x:.4f}{stars(p_x)} (p={p_x:.3f})")
if p_x < 0.10:
    if b_x > 0:
        print("  H1 SUPPORTED: positiver Effekt wie vorhergesagt")
        print("  Höhere Handelsoffenheit geht mit höherem Umsatz bei KMU einher")
    else:
        print("  H1 NOT SUPPORTED: Effekt ist negativ (unerwartete Richtung)")
        print("  Check: Winsorisierung, Sample-Selektion, Variablenkonstruktion")
else:
    print(f"  H1 NOT SUPPORTED: nicht signifikant (p={p_x:.3f})")
    print("  Mögliche Ursache: KOF ist ein Länderindikator — wenig Within-Variation nach Firm FE")

# ── H2 Diagnostic ─────────────────────────────────────────────────────────────
print("\n── H2 Diagnostic ────────────────────────────────────")
print(f"  β(kof_x_size) = {b_int:.4f}{stars(p_int)} (p={p_int:.3f})")
if p_int < 0.10:
    if b_int > 0:
        print("  H2 SUPPORTED: größere KMU profitieren stärker von Handelsoffenheit")
        print("  Konsistent mit Resource-based View (Penrose 1959)")
    else:
        print("  H2 NOT SUPPORTED in erwarteter Richtung: negative Moderation")
        print("  Kleinere KMU profitieren möglicherweise stärker am Rand")
else:
    print(f"  H2 NOT SUPPORTED: Interaktion nicht signifikant (p={p_int:.3f})")

# ── OLS vs TWFE ───────────────────────────────────────────────────────────────
print("\n── OLS vs TWFE comparison ───────────────────────────")
ols_b    = res1.params[X_MAIN]
fe_b     = res2.params[X_MAIN]
pct_diff = abs((ols_b - fe_b) / ols_b) * 100 if ols_b != 0 else 0
print(f"  OLS β = {ols_b:.4f} | FE β = {fe_b:.4f} | difference = {pct_diff:.1f}%")
print(f"  R² OLS = {res1.rsquared:.3f} | R² within FE = {res2.rsquared:.3f}")
if pct_diff > 20:
    print("  Große Differenz → substantieller Omitted Variable Bias in OLS")
    print("  Firm FE absorbiert zeitinvariante Heterogenität")

print(f"\nDone. Results in output/tables/regression_results.csv")