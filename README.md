# SME Trade Openness & Revenue — Research Note
### ExInt II: Research Designs in SME Research | WU Vienna | SS 2026

---

## Research Question

> Inwiefern beeinflusst das allgemeine Niveau der Handelsoffenheit, gemessen am
> KOF Trade Globalisation Index, den Umsatz kleiner börsennotierter Unternehmen
> in Deutschland und Österreich, und moderiert die Firmengröße diesen
> Zusammenhang?

## Theoretical Background

| Theory / Study | Key Claim | Implication for this Study |
|---|---|---|
| Baier & Bergstrand (2007) | FTAs double bilateral trade within 10 years | EU–Mercosur may improve export opportunities for DACH SMEs |
| Timini & Viani (2020) | EU–Mercosur generates significant trade and welfare effects | Effects likely differ by industry and firm size |
| Tröster & Raza (2021) | Benefits of EU–Mercosur are unevenly distributed | Some SMEs may face competitive pressure and adjustment costs |
| Cernat et al. (2014) | SMEs underutilise FTA preferences due to information deficits | Trade agreements may not automatically benefit SMEs |
| Penrose (1959) | Firm-specific resources drive competitive advantage | Larger firms have more capacity to exploit trade openness |
| Lu & Beamish (2001) | SMEs face resource constraints in internationalisation | Firm size moderates the trade openness–revenue relationship |

## Hypotheses

- **H1:** Ein höheres Niveau der Handelsoffenheit, gemessen am KOF Trade
  Globalisation Index, wirkt sich positiv auf den Umsatz kleiner börsennotierter
  Unternehmen in Deutschland und Österreich aus.
- **H2:** Firmengröße moderiert den Zusammenhang positiv — größere KMU
  profitieren stärker von einem höheren Niveau der Handelsoffenheit, da sie
  über mehr Ressourcen verfügen um internationale Märkte zu erschließen.

## Data

| Item | Detail |
|------|--------|
| Source | WRDS / Compustat Global + KOF ETH Zürich |
| Table | comp_global_daily.g_funda |
| Downloaded | 2026-05-28 |
| License | WRDS subscriber agreement |
| Currency | EUR only (curcd = 'EUR') |
| Countries | DEU, AUT |
| Sample | SMEs (≤250 employees OR ≤€43m total assets) |
| Quality filters | at > 0.1, sale > 0, seq > 0 |
| Period | 2000–2023 |
| Unit of analysis | Firm-year |
| Raw rows | 17,382 |
| Clean rows | 8,416 |
| Unique firms | 1,046 |

**Note on DOI variable:** `pifo` (foreign income) is not available in
Compustat Global. Instead, the KOF Trade Globalisation Index (de facto)
is used as the independent variable — a country-level measure of trade
openness with full temporal coverage (2000–2023) for DEU and AUT.

**Note on period:** KOF data is available until 2023. Compustat pull was
aligned accordingly (END_YEAR = 2023).

## Key Variables

| Variable | Field(s) | Formula | Role |
|----------|----------|---------|------|
| Revenue (Sale) | `sale` | `sale` | Dependent (Y) |
| KOF Trade Index | KOF ETH | `kof_trade_defacto` | Independent (X) |
| KOF × Size | — | `kof_trade_defacto × ln_at` | H2 interaction |
| Firm size | `at` | `log(at)` | Moderator + Control |
| Profitability (RoA) | `ib`, `at` | `ib / at` | Control |
| Leverage | `dltt`, `dlc`, `seq` | `(dltt + dlc) / seq` | Control |
| Employees | `emp` | direct field | SME filter + Control |

All continuous variables winsorized at 1st–99th percentiles.

## Main Results

| Model | β(KOF Trade Index) | β(KOF × Size) | Firm FE | Year FE |
|-------|-------------------|---------------|---------|---------|
| (1) Pooled OLS | — | — | No | No |
| (2) TWFE | — | — | Yes | Yes |
| (3) TWFE + H2 | — | — | Yes | Yes |

*Results to be filled in after running 04_regression.py.*

## How to Reproduce

```bash
git clone https://github.com/TL2304/Research-Note
cd Research-Note
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Add your WRDS username to .env
# Place kof_dach_prepared.csv in data/processed/
task all
```

## Project Structure

```
research-note/
├── data/
│   ├── raw/                   ← WRDS pull (not in Git)
│   └── processed/             ← clean panel + KOF data (not in Git)
├── code/
│   ├── 01_pull_data.py        ← WRDS Compustat Global pull
│   ├── 02_clean.py            ← EUR filter, SME filter, quality filters
│   ├── 03_descriptives.py     ← variable construction, summary stats, figures
│   └── 04_regression.py       ← panel FE regressions
├── output/
│   ├── tables/                ← summary_statistics.csv, regression_results.csv
│   └── figures/               ← correlation_matrix.png, main_relationship.png
├── references/
│   └── library.bib            ← Zotero auto-export (Better BibTeX)
├── research_note.md           ← Quarto → PDF
├── Taskfile.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## References

Baier, S. L., & Bergstrand, J. H. (2007). Do free trade agreements actually
increase members' international trade? *Journal of International Economics*,
71(1), 72–95.

Cernat, L., Norman-López, A., & Duch T-Figueras, A. (2014). SMEs are more
important than you think! Challenges and opportunities for EU exporting SMEs.
*DG Trade Chief Economist Notes*, 3.

Gygli, S., Haelg, F., Potrafke, N., & Sturm, J.-E. (2019). The KOF
Globalisation Index — revisited. *Review of International Economics*, 27(3),
543–558.

Lu, J. W., & Beamish, P. W. (2001). The internationalization and performance
of SMEs. *Strategic Management Journal*, 22(6–7), 565–586.

Penrose, E. T. (1959). *The theory of the growth of the firm*. Oxford
University Press.

Timini, J., & Viani, F. (2020). A highway across the Atlantic? Trade and
welfare effects of the EU–Mercosur agreement. *Bank of Spain Working Paper*.

Tröster, B., & Raza, W. (2021). Economic effects of the EU–Mercosur FTA on
developing countries. *ÖFSE Working Paper*.


## Main Results (Session 6 — preliminary)

- **H1 nicht bestätigt:** Der KOF Trade Globalisation Index zeigt nach 
  Einführung von Firm- und Year Fixed Effects keinen signifikanten Effekt 
  auf den Umsatz von KMU in Deutschland und Österreich (β = 0.74, p = 0.423). 
  Die fehlende Signifikanz ist methodisch auf die geringe Within-Variation 
  eines Länderindikators nach Firm Fixed Effects zurückzuführen.

- **H2 nicht bestätigt:** Die Moderationswirkung der Firmengröße auf den 
  Zusammenhang zwischen Handelsoffenheit und Umsatz ist ebenfalls nicht 
  signifikant (β = 0.09, p = 0.548).

- **OLS vs. FE:** Der massive Unterschied zwischen OLS (β = -0.06) und 
  TWFE (β = 0.74) deutet auf substantiellen Omitted Variable Bias im 
  Pooled OLS hin — zeitinvariante Firmenheterogenität korreliert stark 
  mit dem Umsatz und wird erst durch Firm Fixed Effects kontrolliert.