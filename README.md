# SME Trade Openness & Revenue — Research Note
### ExInt II: Research Designs in SME Research | WU Vienna | SS 2026

---

## Research Question

> Does trade openness, measured by the KOF Trade Globalisation Index,
> affect the revenue of listed SMEs in Germany and Austria, and does
> firm size moderate this relationship?

## Theoretical Background

| Theory / Study | Key Claim | Implication for this Study |
|---|---|---|
| Baier & Bergstrand (2007) | FTAs double bilateral trade within 10 years | Higher trade openness may increase revenue opportunities for DACH SMEs |
| Timini & Viani (2020) | EU–Mercosur generates significant trade and welfare effects | Effects likely differ by firm size |
| Tröster & Raza (2021) | Benefits of EU–Mercosur are unevenly distributed | Some SMEs may face competitive pressure |
| Cernat et al. (2014) | SMEs underutilise FTA preferences | Trade openness may not automatically benefit all SMEs |
| Penrose (1959) | Firm-specific resources drive competitive advantage | Larger firms have more capacity to exploit trade openness |
| Lu & Beamish (2001) | SMEs face resource constraints in internationalisation | Firm size moderates the trade openness–revenue relationship |

## Hypotheses

- **H1:** A higher level of trade openness, measured by the KOF Trade
  Globalisation Index, positively affects the revenue of listed SMEs
  in Germany and Austria.
- **H2:** Firm size positively moderates this relationship — larger SMEs
  benefit more from higher trade openness due to greater resources.

## Data

| Item | Detail |
|------|--------|
| Source | WRDS / Compustat Global + KOF ETH Zürich |
| Table | comp_global_daily.g_funda |
| Currency | EUR only (curcd = 'EUR') |
| Countries | DEU, AUT |
| Sample | SMEs (≤250 employees OR ≤€43m total assets) |
| Quality filters | at > 0.1, sale > 0, seq > 0 |
| Period | 2000–2023 |
| Unit of analysis | Firm-year |

## Key Variables

| Variable | Field(s) | Formula | Role |
|----------|----------|---------|------|
| Revenue (Sale) | `sale` | `sale` | Dependent (Y) |
| KOF Trade Index | KOF ETH | `kof_trade_defacto` | Independent (X) |
| KOF × Size | — | `kof_trade_defacto × ln_at` | H2 interaction |
| Firm size | `at` | `log(at)` | Moderator + Control |
| Profitability (RoA) | `ib`, `at` | `ib / at` | Control |
| Leverage | `dltt`, `dlc`, `seq` | `(dltt + dlc) / seq` | Control |
| CAPX intensity | `capx`, `at` | `capx / at` | Control |

## Main Results

- **H1 nicht bestätigt:** Der KOF Trade Index zeigt nach Firm- und Year
  Fixed Effects keinen signifikanten Effekt auf den Umsatz (β = 0.74,
  p = 0.423). Die fehlende Signifikanz ist methodisch auf die geringe
  Within-Variation eines Länderindikators nach Firm Fixed Effects
  zurückzuführen.

- **H2 nicht bestätigt:** Die Moderationswirkung der Firmengröße ist
  ebenfalls nicht signifikant (β = 0.09, p = 0.548).

- **OLS vs. FE:** Massiver Unterschied zwischen OLS (β = -0.06) und
  TWFE (β = 0.74) deutet auf substantiellen Omitted Variable Bias hin.

## How to Reproduce

```bash
git clone https://github.com/TL2304/Research-Note
cd Research-Note
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add WRDS username to .env
task all
```

## Project Structure

```
research-note/
├── data/
│   ├── raw/                   ← WRDS pull (not in Git)
│   └── processed/             ← clean panel + KOF data (not in Git)
├── code/
│   ├── 01_pull_data.py
│   ├── 02_clean.py
│   ├── 03_descriptives.py
│   └── 04_regression.py
├── output/
│   ├── tables/
│   └── figures/
├── references/
│   ├── library.bib
│   └── apa.csl
├── research_note.qmd
├── Taskfile.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```