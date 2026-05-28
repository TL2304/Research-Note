# SME Trade Openness & Revenue — Research Note
**Author:** Tobias Lahner | WU Vienna · ExInt II · SS 2026

## Research Question
Inwiefert beeinflusst das allgemeine Niveau der Handelsoffenheit, gemessen am 
KOF Trade Globalisation Index, den Umsatz kleiner börsennotierter Unternehmen 
in Deutschland und Österreich, und welche Schlussfolgerungen lassen sich daraus 
für das EU-Mercosur-Abkommen ableiten?

## Hypotheses
**H1:** Ein höheres Niveau der Handelsoffenheit, gemessen am KOF Trade 
Globalisation Index, wirkt sich positiv auf den Umsatz kleiner börsennotierter 
Unternehmen in Deutschland und Österreich aus.

## Theoretical Background
| Theory / Study | Key Claim | Implication for my Study |
|---|---|---|
| Baier & Bergstrand (2007) | FTAs double bilateral trade within 10 years | EU–Mercosur may improve export opportunities for DACH SMEs |
| Timini & Viani (2020) | EU–Mercosur generates significant trade and welfare effects | Effects likely differ by industry and firm size |
| Tröster & Raza (2021) | Benefits of EU–Mercosur are unevenly distributed | Some SMEs may face competitive pressure and adjustment costs |
| Cernat et al. (2014) | SMEs underutilise FTA preferences due to information deficits | Trade agreements may not automatically benefit SMEs |
| Maton / Oxford Economics (2024) | EU–Mercosur is more strategic than macroeconomic | Market access and positioning may matter more than aggregate growth |

## Variables

### Dependent Variable (Y)
| Construct | Data Item(s) | Formula | Note |
|-----------|-------------|---------|------|
| Revenue | SALE | SALE | Net sales in EUR millions |

### Independent Variable (X)
| Construct | Data Item(s) | Formula | Note |
|-----------|-------------|---------|------|
| Trade Openness | KOF Index | external | Downloaded from kof.ethz.ch |

### Control Variables
| Construct | Data Item(s) | Formula | Note |
|-----------|-------------|---------|------|
| Firm Size | AT | log(AT) | Log-transform reduces skewness |
| Profitability | IB, AT | IB / AT | Return on Assets |
| Leverage | DLTT, DLC, SEQ | (DLTT + DLC) / SEQ | Total debt / equity |
| Employees | EMP | direct field | In thousands; emp < 0.25 = SME |

## Data
| Item | Detail |
|------|--------|
| Source | WRDS / Compustat Global |
| Table | comp_global_daily.g_funda |
| Downloaded | 2026-05-28 |
| License | WRDS subscriber agreement |
| Countries | DEU, AUT |
| Fiscal years | 2000–2024 |
| Raw rows | 17,382 |
| Clean rows | 8,609 |
| Unique firms | 1,049 |