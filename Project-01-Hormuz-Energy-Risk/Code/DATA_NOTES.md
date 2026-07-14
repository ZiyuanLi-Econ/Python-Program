# Data notes

The downloaded source files are not stored in this repository. Create a local
`Code/data_raw/` folder and place the two CSV files below inside it before
running the analysis.

## 1. Energy Institute

- File: `Statistical Review of World Energy Narrow format.csv`
- Source: [Statistical Review data downloads](https://www.energyinst.org/statistical-review/resources-and-data-downloads)
- Snapshot used: 2025 edition, containing data through 2024
- Used by: scripts 01-04

The analysis deliberately keeps the 2024 snapshot used for this project. Newer
editions may revise both the historical series and the total-energy methodology.

## 2. UN Comtrade

- File: `TradeData.csv`
- Source: [UN Comtrade](https://comtradeplus.un.org/TradeFlow)
- Query: 2024 annual imports, HS 2709 (crude petroleum)
- Reporters: United States, China, Germany, European Union, Japan, India, and South Korea
- Partners: World plus all available individual partner economies
- Used by: script 04

UN Comtrade can revise observations as reporters submit updates. The results in
this repository therefore describe the downloaded snapshot rather than a live
query.

## 3. U.S. EIA

Script 05 contains the small 2020-first-half 2025 series from
[EIA World Oil Transit Chokepoints, Table 1](https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/).
No separate download is needed. Values are in million barrels per day.

## Public-repository boundary

The Energy Institute and UN Comtrade CSV files remain subject to their
publishers' terms. Download them from the official sources and do not commit the
local `data_raw` folder.
