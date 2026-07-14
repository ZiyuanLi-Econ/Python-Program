# Project 1 — Strait of Hormuz Energy-Market Risk

## Energy Market Risk Research Note

The Strait of Hormuz is a major oil-market chokepoint linking Middle Eastern supply with demand centres in Asia and Europe. This project uses Python to examine that relationship from the global energy mix through to country import exposure.

## 2024 snapshot

| Hormuz oil flow | Share of maritime oil trade | Share of total oil supply | Asia-Pacific oil balance gap |
|---:|---:|---:|---:|
| **20.7 mb/d** | **26.0%** | **20.0%** | **−32.0 pp** |

*The first three indicators use EIA data. The regional balance gap is the region's share of global oil production minus its share of global oil consumption.*

## Key findings

1. **Supply and demand are geographically separated.** The Middle East produced 31.3% of the world's oil but consumed 9.8%, while Asia Pacific produced 7.5% and consumed 39.4%.
2. **Several Asian markets rely heavily on Hormuz-related suppliers.** These exporters represented 94.5% of Japan's, 71.9% of South Korea's, 45.4% of India's, and 36.9% of China's reported crude-import origins in the selected data.
3. **Hormuz has remained systemically important.** Its oil flow equalled roughly one quarter of global maritime oil trade in every year from 2020 to first-half 2025.

## Evidence

### 1. Regional oil imbalance

![Regional oil production and consumption shares](Figures/01_regional_oil_balance.png)

The Middle East is the largest surplus region, whereas Asia Pacific has the largest production-consumption gap. This imbalance creates a structural need for long-distance oil trade.

### 2. Import-origin exposure

![Crude imports from Hormuz-related exporters](Figures/02_import_origin_exposure.png)

Japan and South Korea have the highest shares in the selected sample. This is an **export-origin indicator**, not proof that every cargo physically passed through the strait.

### 3. Global chokepoint share

![Hormuz share of global oil flows](Figures/03_hormuz_global_share.png)

Hormuz carried 20.7 million barrels per day in 2024, or 26.0% of maritime oil trade and 20.0% of total oil supply.

## Market interpretation

A disruption would first affect the availability and transport cost of Middle Eastern crude, with the strongest direct pressure likely falling on import-dependent Asian refiners. The broader financial effect could include higher oil prices, wider shipping and insurance costs, and increased volatility in energy-sensitive assets. The figures identify structural sensitivity; they are not a forecast of the size or duration of a price shock.

## Limitations

1. Most results are a 2024 snapshot rather than a forecast.
2. Export country does not reveal a cargo's actual route or use of bypass pipelines.
3. Regional production-consumption gaps do not measure a country's full import dependency.
4. The analysis does not model inventories, substitution, policy responses, disruption length, or price effects.

## Reproduce

```bash
python -m pip install -r Code/requirements.txt
# Add the two downloaded CSV files to Code/data_raw/ as described in Code/DATA_NOTES.md
python Code/run_all.py
```

## Sources

- [Energy Institute — Statistical Review of World Energy](https://www.energyinst.org/statistical-review/resources-and-data-downloads)
- [UN Comtrade — international trade data](https://comtradeplus.un.org/TradeFlow)
- [U.S. EIA — World Oil Transit Chokepoints](https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/)

Data scope and download notes are in [`Code/DATA_NOTES.md`](Code/DATA_NOTES.md). Third-party raw data are not included in this repository.
