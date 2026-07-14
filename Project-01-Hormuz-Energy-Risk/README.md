# Strait of Hormuz: A Python Analysis of Oil-Market Exposure

*Python data project | pandas, matplotlib | 2024 cross-sectional data; EIA flows through 1H25*

## 1. Project question & headline finding

**Project question.** How important is the Strait of Hormuz to the global oil system, and which of seven sampled importing markets show the highest structural-exposure indicators?

> **Headline finding:** Hormuz is a large and persistent oil chokepoint. It carried 20.7 million barrels per day (mb/d) in 2024, equal to 26.0% of global maritime oil trade and 20.0% of total oil supply. Japan and South Korea also show the highest selected-exporter origin shares among the sampled importers. These results establish structural exposure, not the probability or price impact of a disruption.

The code produces 15 figures. Six key outputs are shown below; the complete set is available in the [figure gallery](Figures/README.md).

## 2. Data and analytical path

| Dataset | Use in the project | Observation period |
|---|---|---|
| [Energy Institute, Statistical Review of World Energy](https://www.energyinst.org/statistical-review/resources-and-data-downloads) | Global energy mix, oil production and consumption, selected-market energy structure | 2024 |
| [UN Comtrade, HS 2709](https://comtradeplus.un.org/TradeFlow) | Crude-import exporter origins for seven reporting markets; net weight where available, otherwise trade value | 2024 |
| [U.S. EIA, World Oil Transit Chokepoints](https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/) | Route flows and global oil-flow totals used to calculate Hormuz shares | 2020-2024 and 1H25 |

```mermaid
flowchart LR
    A["Three public datasets"] --> B["pandas cleaning and aggregation"]
    B --> C["Validation checks"]
    C --> D["matplotlib charts"]
    D --> E["15 outputs"]
    E --> F["6 key figures in README"]
    E --> G["Full figure gallery"]
```

The analysis moves from global oil relevance to geographic imbalance, importer concentration and direct chokepoint evidence. The data workflow keeps trade-origin proxies separate from measured physical flows.

## 3. Evidence

### 3.1 Oil remains macro-relevant

![Global energy mix in 2024](Figures/01_global_energy_mix_2024.png)

**Finding.** Oil was the largest source of global energy supply in 2024 at 33.6%. This scale makes oil-flow disruptions potentially macro-relevant, although the project does not estimate their inflation or price effects.

### 3.2 Supply and demand are geographically separated

![Regional oil production and consumption shares in 2024](Figures/03_regional_oil_balance_2024.png)

**Finding.** The Middle East's production share exceeded its consumption share by 21.3 percentage points, while Asia Pacific's production share lagged its consumption share by 30.4 points. These opposite share gaps are consistent with a structural need for interregional oil trade.

### 3.3 Importer sensitivity differs across markets

![Energy mix of selected markets in 2024](Figures/07_selected_market_energy_mix_2024.png)

**Finding.** Oil represented 39.0%-42.2% of energy supply in Japan, South Korea, Germany, the European Union aggregate and the United States. China and India had lower oil shares; because this chart presents percentages, it should not be read as a ranking of absolute oil demand.

### 3.4 Exporter-origin concentration is highest in selected Asian markets

![Selected Middle East and Hormuz-region exporter-origin shares in 2024](Figures/10_middle_east_vs_hormuz_origin_share_2024.png)

**Finding.** Among the seven sampled reporters, Japan and South Korea had the highest selected-exporter origin shares under both definitions. China was more sensitive to the definition: 44.3% for the selected Middle East group versus 36.9% for the narrower Hormuz-region group, which excludes Oman.

### 3.5 Hormuz is one of the world's largest oil routes

![Oil flows through major global maritime routes in 2024](Figures/13_global_oil_chokepoints_2024.png)

**Finding.** Hormuz carried 20.7 mb/d in 2024, close to Malacca at 22.5 mb/d and well above the other individual routes in the EIA comparison.

### 3.6 The exposure is persistent

![Strait of Hormuz share of global oil flows from 2020 through first-half 2025](Figures/15_hormuz_global_share_2020_1H25.png)

**Finding.** Hormuz consistently handled roughly one quarter of maritime oil trade and about one fifth of total oil supply from 2020 through 1H25. Its importance is not the result of a single exceptional year.

## 4. Financial relevance

| Exposure | First observable effect | Financial relevance |
|---|---|---|
| Higher or repriced transit, freight and insurance costs | Higher delivered crude cost | Refiner and airline margins; inflation pressure |
| Material flow decline | Prompt prices, time spreads and inventory draws | Importer FX/current accounts and producer-user earnings dispersion |
| Inventory, spare-capacity and bypass response | Net volume loss and duration | Determines whether repricing is temporary or persistent |

This is a transmission map, not an oil-price target or a security recommendation.

## 5. Limitations & reproduction

### Limitations

- The cross-market analysis is a 2024 snapshot, not a live risk monitor.
- UN Comtrade reports exporter origin, not the vessel's physical route through Hormuz.
- HS 2709 covers crude oil, while the EIA chokepoint series uses a broader oil-flow definition.
- The selected Hormuz-region group is a seven-exporter screening definition; the broader Middle East group also includes Oman.
- The European Union is a regional aggregate, not an additional country.
- The auxiliary domestic supply-gap figure is not observed gross import dependence.
- EIA throughput is not an estimate of barrels lost in a disruption; `1H25` is a half-year average.
- The project does not estimate disruption probability, oil-price elasticity, company earnings or valuation.

### Scripts

| Script | Analysis | Figures |
|---|---|---|
| [`01_global_energy.py`](Code/01_global_energy.py) | Global energy mix | 01 |
| [`02_oil_geography.py`](Code/02_oil_geography.py) | Oil-market rankings, regional balance and concentration | 02-04 |
| [`03_market_energy_mix.py`](Code/03_market_energy_mix.py) | Selected-market energy supply and mix | 05-07 |
| [`04_import_exposure.py`](Code/04_import_exposure.py) | Exporter-origin and supply-gap screens | 08-12 |
| [`05_hormuz_chokepoint.py`](Code/05_hormuz_chokepoint.py) | Direct EIA chokepoint flows | 13-15 |

### Run the project

The Energy Institute and UN Comtrade source files are not redistributed. Download the two CSV files described in [`Code/DATA_NOTES.md`](Code/DATA_NOTES.md) and place them in `Code/data_raw/`.

```bash
python -m pip install -r Code/requirements.txt
python Code/run_all.py
```

`run_all.py` executes the five scripts and regenerates all 15 current PNG outputs. The workflow was last validated with Python 3.14.3, pandas 3.0.1 and matplotlib 3.10.8.

- [Source-file names, query scope and snapshot hashes](Code/DATA_NOTES.md)
- [Complete 15-figure gallery](Figures/README.md)
