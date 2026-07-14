# Data sources

Source pages were last checked on **2026-07-13**. File retrieval dates and
snapshot hashes are recorded separately so later source revisions remain
distinguishable from the data used for the published results.

The repository does not redistribute the third-party source files. Download them from their publishers and place them in `data_raw/` using the filenames listed below. The `.gitignore` intentionally excludes everything in that directory except its README.

## Energy Institute — Statistical Review of World Energy

- **File used:** `Statistical Review of World Energy Narrow format.csv`
- **Edition:** Statistical Review of World Energy 2025 (data through 2024)
- **Publisher:** Energy Institute
- **Official source:** [Statistical Review resources and data downloads](https://www.energyinst.org/statistical-review/resources-and-data-downloads)
- **Format:** narrow-format CSV
- **File retrieved:** 2026-06-25
- **SHA-256:** `1A4C40400712600FB25C1BDD7D57F0B410857FC4205A6D74DD6E6349EDD044E4`
- **Use in this project:** 2024 energy consumption, production, and energy-mix observations used in Q1–Q4.

The publisher may replace the current download with a later edition or revise
historical observations. The hash above identifies the exact 2025-edition
snapshot used to produce this repository's reported values. The dataset remains
the property of its publisher and is subject to the terms shown on the Energy
Institute download page. Obtain your own copy from the official source; do not
assume that this repository's code license applies to the data.

## UN Comtrade — crude-oil imports

- **File used:** `TradeData.csv`
- **Publisher:** United Nations Statistics Division, UN Comtrade
- **Official query portal:** [UN Comtrade Trade Data](https://comtradeplus.un.org/TradeFlow)
- **Reference year:** 2024
- **Trade flow:** Imports
- **Commodity classification:** HS
- **Commodity code:** 2709 — petroleum oils and oils obtained from bituminous minerals, crude
- **Reporters (7, as labelled in the download):** USA, China, Germany, European Union, Japan, India, and Rep. of Korea
- **Partners:** World and available individual partner economies
- **Frequency:** Annual
- **File retrieved:** 2026-07-02
- **Rows in snapshot:** 279
- **SHA-256:** `1515520AD73AC2CE13456855348CED1964F2BC98A9F89BA608635E6C14643A4D`
- **Use in this project:** reporter totals, supplier shares, and the origin-based Hormuz exposure proxy in Q4.

UN Comtrade data use and redistribution are governed by the [UN Comtrade license agreement](https://comtradeplus.un.org/LicenseAgreement). Download the query result directly from UN Comtrade and review its current terms before reusing or publishing derived data.

## U.S. EIA — World Oil Transit Chokepoints

- **Publisher:** U.S. Energy Information Administration (EIA)
- **Official source:** [World Oil Transit Chokepoints](https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/)
- **Table used:** Table 1
- **Periods used:** 2020–2024 annual averages and first-half 2025
- **Unit:** million barrels per day
- **Use in this project:** Strait of Hormuz flow and share calculations in Q5.

The small set of values used by Q5 is recorded in the analysis code with source metadata rather than copied from a separately distributed source file. Cite EIA when reusing the resulting analysis.

## IEA workbook not used

`WorldEnergyBalancesHighlights2025.xlsx` was reviewed during early exploration but is **not used by the final analysis and is not uploaded to this repository**. It is IEA third-party material and may carry restrictions that differ from the source code license. Anyone wishing to use it should obtain it independently from the [IEA World Energy Balances Highlights page](https://www.iea.org/data-and-statistics/data-product/world-energy-balances-highlights) and follow the applicable IEA terms.

## Licensing note

Any license later selected for this repository will cover only the original source code and documentation unless it explicitly says otherwise. It will not grant rights to Energy Institute, UN Comtrade, EIA, or IEA materials. Users are responsible for complying with each publisher's current terms, attribution requirements, and redistribution restrictions.
