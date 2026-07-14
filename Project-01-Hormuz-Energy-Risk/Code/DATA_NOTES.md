# Data notes

The downloaded data are not stored in this repository. Create a local `Code/data_raw/` folder and add the following two files before running the project.

## 1. Energy Institute

- File: `Statistical Review of World Energy Narrow format.csv`
- Source: [Statistical Review of World Energy — data downloads](https://www.energyinst.org/statistical-review/resources-and-data-downloads)
- Edition used: 2025 edition, containing data through 2024
- Used by: scripts 01–03

## 2. UN Comtrade

- File: `TradeData.csv`
- Source: [UN Comtrade](https://comtradeplus.un.org/TradeFlow)
- Query: 2024 annual imports, HS 2709 (crude petroleum)
- Reporters: United States, China, Germany, European Union, Japan, India, and South Korea
- Partners: World and available individual partner economies
- Used by: script 04

## 3. U.S. EIA

Script 05 contains the small 2020–first-half 2025 series from [EIA World Oil Transit Chokepoints, Table 1](https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/). No separate download is needed.

The two CSV files remain subject to their publishers' terms. Obtain them from the official sources and do not commit the local `data_raw` folder.
