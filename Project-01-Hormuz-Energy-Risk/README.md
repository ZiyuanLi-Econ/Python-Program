# Strait of Hormuz: A Python Analysis of Oil-Market Exposure

*Python data project | pandas, matplotlib | 2024 cross-sectional data; EIA flows through 1H25*

## 1. Project question & headline finding

**Project question.** How important is the Strait of Hormuz to the global oil system, and which of seven sampled importing markets show the highest structural-exposure indicators?

> **Headline finding:** Oil still supplied 33.6% of global energy in 2024, while the main production and consumption centres were geographically separated. That separation helps explain why maritime routes are structurally important: Hormuz carried 20.7 million barrels per day (mb/d), equal to 26.0% of global maritime oil trade and 20.0% of total oil supply. Exposure is uneven across the seven sampled importers; Japan and South Korea had the highest selected Hormuz-region exporter-origin shares at 94.5% and 71.9%. The project establishes this chain of structural exposure; it does not estimate disruption probability or price impact.

The code produces 15 figures. Six key outputs are shown below; the complete set is available in the [figure gallery](Figures/README.md).

## 2. Data and analytical path

| Dataset | Use in the project | Observation period |
|---|---|---|
| [Energy Institute, Statistical Review of World Energy](https://www.energyinst.org/statistical-review/resources-and-data-downloads) | Global energy mix, oil production and consumption, selected-market energy structure | 2024 |
| [UN Comtrade, HS 2709](https://comtradeplus.un.org/TradeFlow) | Crude-import exporter origins for seven reporting markets; net weight where available, otherwise trade value | 2024 |
| [U.S. EIA, World Oil Transit Chokepoints](https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/) | Route flows and global oil-flow totals used to calculate Hormuz shares | 2020-2024 and 1H25 |

```mermaid
flowchart LR
    A["Oil's role in global energy"] --> B["Producer-consumer mismatch"]
    B --> C["Regional need for trade"]
    C --> D["Major maritime routes"]
    D --> E["Hormuz scale and persistence"]
    E --> F["Uneven importer exposure"]
```

The evidence is read sequentially. Oil must first be large enough to matter; production and consumption must then be sufficiently separated to require trade; major routes must carry sufficiently large flows to matter; and only after the scale of Hormuz is established does the analysis compare market-level exposure indicators. In the code, three public datasets are cleaned and aggregated with pandas, checked, and converted into 15 matplotlib outputs. Domestic supply gaps, exporter-origin concentration and measured physical flows remain separate concepts.

## 3. Evidence

Each step below answers the question left open by the previous one. The purpose is not to collect six unrelated charts, but to move from the global energy system to the specific countries for which Hormuz-related exposure may matter most.

### 3.1 Start with oil's role in the global energy system

![Global energy mix in 2024](Figures/01_global_energy_mix_2024.png)

Global energy supply totalled 592.2 exajoules in 2024. Oil was the largest source at 33.6%, ahead of coal at 27.9% and natural gas at 25.1%; the three fossil sources together accounted for 86.6%. The point is not that every oil disruption must create a large economic shock. It is that oil remains large enough for a material transport constraint to potentially affect delivered energy costs, trade balances and inflation-sensitive sectors.

This establishes why oil matters, but not where the system is vulnerable. The next question is whether the barrels are produced in the same places where they are consumed.

### 3.2 The major producers and consumers are not fully aligned

![Largest oil producers and consumers in 2024](Figures/02_top_oil_markets_2024.png)

The United States was unusual in appearing at the top of both lists, producing about 20.1 mb/d and consuming 19.0 mb/d. Beyond the United States, the rankings diverged. Saudi Arabia and Russia each produced about 10.8 mb/d, while China consumed 16.4 mb/d but produced only 4.3 mb/d. Five of the ten largest producers were Middle Eastern economies: Saudi Arabia, Iran, Iraq, the United Arab Emirates and Kuwait. On the demand side, India consumed 5.6 mb/d, and Japan and South Korea consumed 3.2 and 2.9 mb/d respectively, without appearing among the ten largest producers.

Country rankings therefore reveal a first mismatch between supply centres and demand centres. They do not by themselves show the direction or scale of interregional trade, so the analysis next aggregates production and consumption by region.

### 3.3 Regional share gaps point to a structural need for trade

![Regional oil production and consumption shares in 2024](Figures/03_regional_oil_balance_2024.png)

The Middle East produced 31.1% of world oil but consumed 9.8%, a positive production-consumption share gap of 21.3 percentage points. Asia Pacific showed the reverse pattern: 7.5% of production and 37.9% of consumption, a negative gap of 30.4 points. Europe also consumed a much larger share than it produced, at 13.9% versus 3.1%.

These share gaps are not observed bilateral trade flows, but their opposing direction is consistent with a structural need to move oil from producing regions toward Asian and European demand centres. Once large volumes must cross regions, the location and throughput of maritime routes become part of the supply system rather than a secondary logistics detail.

### 3.4 Large oil volumes pass through a small number of major routes

![Oil flows through major global maritime routes in 2024](Figures/13_global_oil_chokepoints_2024.png)

The EIA route comparison places the Strait of Malacca first at 22.5 mb/d in 2024 and Hormuz second at 20.7 mb/d. The next route in the comparison, the Cape of Good Hope, carried 9.3 mb/d. This makes Hormuz a systemically large transport corridor: disruption risk is relevant not simply because the strait is narrow, but because a large absolute volume is concentrated there.

The 2024 comparison establishes scale, but a single year could still be exceptional. A historical share calculation is therefore needed to determine whether the importance of Hormuz is persistent.

### 3.5 Hormuz is a persistent part of the global oil system

![Strait of Hormuz share of global oil flows from 2020 through first-half 2025](Figures/15_hormuz_global_share_2020_1H25.png)

Hormuz flow remained between 19.2 and 21.9 mb/d from 2020 through 1H25. Across the same period, its share stayed within 25.9%-27.9% of world maritime oil trade and 20.0%-21.8% of total oil supply. The 2024 readings of 20.7 mb/d, 26.0% and 20.0% were therefore close to the middle of the displayed ranges rather than an exceptional peak.

The consistently high range shows that Hormuz was not important only in one unusual year. Yet a route can be globally important without every importing market being equally exposed. The final step therefore turns from system-wide physical flow to market-level domestic supply and crude-import origin indicators.

### 3.6 Market exposure is uneven and must be measured in separate dimensions

UN Comtrade provides the reported origin of crude imports for seven sampled reporters. The chart compares two nested definitions: a selected Middle East group of eight exporters and a narrower selected Hormuz-region group that excludes Oman. These shares describe exporter origin, not the vessel's physical route.

![Selected Middle East and Hormuz-region exporter-origin shares in 2024](Figures/10_middle_east_vs_hormuz_origin_share_2024.png)

| Reporter | Selected Middle East origin share | Selected Hormuz-region origin share | Domestic supply-gap proxy |
|---|---:|---:|---:|
| Japan | 95.1% | 94.5% | N/A |
| South Korea | 72.5% | 71.9% | N/A |
| India | 45.8% | 45.4% | 86.9% |
| China | 44.3% | 36.9% | 74.0% |
| European Union | 13.7% | 13.7% | 96.9% |
| United States | 8.1% | 8.1% | 0.0% |
| Germany | 7.7% | 7.7% | N/A |

Japan and South Korea had the highest selected-exporter origin concentration in the sample. India and China combined material Hormuz-region origin shares with domestic supply-gap proxies of 86.9% and 74.0%. The European Union illustrates why the measures must remain separate: its domestic supply-gap proxy was high at 96.9%, but only 13.7% of reported crude-import origins came from the selected Hormuz-region group. The United States had both a zero domestic supply-gap proxy and a relatively low origin share of 8.1%.

China also shows why the exporter definition matters. Its share falls from 44.3% under the broader Middle East group to 36.9% under the narrower group because Oman is excluded. For Japan, South Korea and India, the difference is less than one percentage point.

The conclusion is therefore conditional but clear. Hormuz is structurally important to the global oil system; Japan and South Korea show the greatest selected-exporter origin concentration; India and China combine domestic production shortfalls with material regional origin shares; and the European Union, United States and Germany show lower concentration in this particular origin screen. None of these statistics alone proves physical transit through Hormuz, and the project deliberately does not combine them into a single dependency score.

The domestic supply-gap proxy is calculated as the positive difference between reported oil consumption and production, divided by consumption. `N/A` means the required production observation was unavailable; it is not treated as zero and is not a claim of self-sufficiency or gross import dependence.

Taken together, the evidence moves from global scale to geographic imbalance, from imbalance to route concentration, and from route concentration to unequal importer exposure. The financial question is therefore how a disruption could transmit, not whether every market would be affected in the same way.

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
- Regional production and consumption shares use different world totals; their percentage-point gap is a structural indicator, not observed net exports.
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
