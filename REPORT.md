# Global Energy and Strait of Hormuz Exposure

## Detailed analytical report

**Reference period:** 2024, with EIA chokepoint history from 2020 through first-half 2025  
**Core tools:** Python, pandas, Matplotlib, unittest  
**Unit conventions:** energy in exajoules (EJ); oil in thousand barrels per day (kbd) or million barrels per day (mb/d), as labelled

## 1. Research question and approach

The Strait of Hormuz is often described as a critical oil chokepoint, but that statement combines several different questions:

1. How important is oil in the global energy system?
2. How far apart are the main locations of oil production and consumption?
3. Which large economies and markets are structurally oil-intensive?
4. What share of their reported crude-import partners are selected Hormuz-related exporters?
5. How large are actual aggregate Hormuz flows relative to global oil trade and supply?

The project answers these questions sequentially. Q1–Q3 establish the global and market context. Q4 constructs transparent screening proxies while preserving missing data and distinguishing exporter origin from shipping route. Q5 then measures the chokepoint's global scale with EIA flow data.

The headline conclusion is deliberately two-sided: **Hormuz is systemically important, but country exposure cannot be measured from exporter origin alone.**

## 2. Results at a glance

| Indicator | Result |
|---|---:|
| Global total energy supply, 2024 | 592.2 EJ |
| Oil share of global energy supply | 33.6% |
| Oil + coal + natural gas share | 86.6% |
| Middle East oil production / consumption shares | 31.3% / 9.8% |
| Asia Pacific oil production / consumption shares | 7.5% / 39.4% |
| Top 10 country share of oil production / consumption | 74.7% / 64.5% |
| Hormuz flow, 2024 | 20.7 mb/d |
| Hormuz share of maritime oil trade / total supply, 2024 | 26.0% / 20.0% |
| Hormuz flow, first-half 2025 | 20.9 mb/d |

## 3. Analytical sequence

### Q1: Global energy overview

Q1 uses the Energy Institute's 2024 `Total World` observations. Each source is divided by total energy supply (`tes_ej`), with one validated observation required for every country-year-variable key.

| Energy source | Energy (EJ) | Share of total supply |
|---|---:|---:|
| Oil | 199.05 | 33.6% |
| Coal | 165.06 | 27.9% |
| Natural gas | 148.60 | 25.1% |
| Renewables | 48.77 | 8.2% |
| Nuclear | 30.74 | 5.2% |
| **Total energy supply** | **592.22** | **100.0%** |

Oil was the largest single category, but the broader structural result is the continued weight of fossil fuels: oil, coal, and natural gas together represented 86.6% of the selected global supply categories. This makes the security of oil transport relevant even as renewables grow.

### Q2: Oil production and consumption geography

Q2 removes aggregate and `Other` rows before creating country rankings and regional totals. This prevents world or regional summary records from being mixed into country-level calculations.

#### Leading countries

| Rank | Oil production | kbd | Oil consumption | kbd |
|---:|---|---:|---|---:|
| 1 | United States | 20,135 | United States | 18,995 |
| 2 | Saudi Arabia | 10,856 | China | 16,374 |
| 3 | Russian Federation | 10,752 | India | 5,621 |
| 4 | Canada | 5,888 | Saudi Arabia | 3,959 |
| 5 | Iran | 5,062 | Russian Federation | 3,846 |

Six countries appeared in both Top 10 lists: the United States, Saudi Arabia, Russian Federation, Canada, China, and Brazil. The incomplete overlap is an early indication that oil must move between structurally different production and consumption centres.

#### Regional balance

| Region | Production share | Consumption share | Production minus consumption share |
|---|---:|---:|---:|
| Middle East | 31.3% | 9.8% | +21.5 pp |
| CIS | 14.0% | 5.0% | +9.0 pp |
| Africa | 7.2% | 2.1% | +5.1 pp |
| North America | 29.2% | 24.2% | +5.0 pp |
| South & Central America | 8.0% | 5.2% | +2.8 pp |
| Europe | 2.8% | 14.3% | −11.5 pp |
| Asia Pacific | 7.5% | 39.4% | −32.0 pp |

The Middle East was the clearest supply centre, while Asia Pacific was the clearest demand centre. Europe was also structurally demand-heavy. This geographic separation provides the economic context for the importance of maritime routes and chokepoints.

Country-level concentration was also higher on the production side:

| Country group | Production share | Consumption share |
|---|---:|---:|
| Top 3 | 43.6% | 42.7% |
| Top 5 | 55.1% | 50.9% |
| Top 10 | 74.7% | 64.5% |

### Q3: Energy structure of selected markets

Q3 compares China, the United States, India, Japan, South Korea, Germany, and the European Union aggregate. `Total EU` is explicitly treated as a regional market benchmark, not as a country.

| Economy / market | Oil | Natural gas | Coal | Nuclear | Renewables | Largest source |
|---|---:|---:|---:|---:|---:|---|
| China | 20.3% | 9.8% | 58.0% | 3.1% | 8.7% | Coal |
| United States | 39.0% | 35.4% | 8.6% | 9.8% | 7.2% | Oil |
| India | 28.1% | 6.5% | 59.2% | 1.5% | 4.6% | Coal |
| Japan | 39.1% | 19.9% | 27.6% | 5.6% | 7.8% | Oil |
| South Korea | 42.2% | 17.4% | 21.7% | 15.7% | 3.0% | Oil |
| Germany | 41.8% | 27.9% | 15.6% | 0.0% | 14.7% | Oil |
| European Union aggregate | 42.0% | 22.4% | 9.1% | 13.6% | 12.9% | Oil |

China and India were coal-led, whereas oil was the largest source for the other selected markets. These energy-mix shares describe structural importance, not short-run disruption sensitivity: inventory cover, refinery configuration, product trade, contracts, and substitution capacity are outside this dataset.

### Q4: Domestic supply-gap and exporter-origin proxies

#### Why proxies are needed

The Energy Institute file supplies production and consumption observations, while UN Comtrade supplies reported crude-import partners. Neither dataset identifies the physical route of each cargo. Q4 therefore keeps the following concepts separate.

#### Proxy 1 — domestic supply gap

```text
Domestic supply-gap proxy (%)
    = max(consumption − production, 0) / consumption × 100
```

This measures the uncovered domestic production-consumption gap. It is **not gross imports or a complete oil balance** because it excludes inventory changes, crude-versus-product differences, exports, refinery gains, and other balance items.

#### Proxy 2 — Hormuz-related exporter origin

```text
Origin-based Hormuz-related share (%)
    = imports reported from selected exporter origins
      / all usable non-World partner imports × 100
```

The trade scope is annual 2024 imports of crude petroleum, HS 2709. The Hormuz-related origin set is Saudi Arabia, Iraq, United Arab Emirates, Kuwait, Qatar, Iran, and Bahrain. It is a geographic screening set, not a cargo-route classification.

Partner net weight is used when available. Primary value is the fallback only when a reporter has no usable partner weights. Separately, the sum of partner rows is compared with each reporter's independent `World` row; all seven reporters reconcile within 1% in the supplied query.

#### Proxy 3 — combined screening indicator

```text
Combined proxy (percentage points)
    = domestic supply-gap proxy × origin-based share / 100
```

The combined value is calculated only when both inputs exist. It is not labelled an exposure score because its interpretation is narrower than economic exposure.

| Reporter | Supply-gap proxy | Hormuz-related exporter-origin share | Combined screening proxy |
|---|---:|---:|---:|
| Japan | Not calculated | 94.5% | Not calculated |
| South Korea | Not calculated | 71.9% | Not calculated |
| India | 86.9% | 45.4% | 39.5 pp |
| China | 74.0% | 36.9% | 27.3 pp |
| European Union aggregate | 96.9% | 13.7% | 13.3 pp |
| United States | 0.0% | 8.1% | 0.0 pp |
| Germany | Not calculated | 7.7% | Not calculated |

Production observations were unavailable for Germany, Japan, and South Korea in the scoped Energy Institute series. The code does not silently replace them with zero, so their supply-gap and combined values remain unavailable.

The United States illustrates another limitation: aggregate production exceeded consumption, which makes its supply-gap proxy zero, while 8.1% of reported crude-import partner totals still came from the selected exporter set. The combined proxy therefore cannot replace a gross-import or route-level exposure measure.

Most importantly, **exporter origin does not prove passage through Hormuz**. Saudi Arabia and the UAE have bypass routes, and exporters may use different ports or logistics. Conversely, a cargo's route cannot be reconstructed from a reporter-partner trade row.

### Q5: Hormuz in the global oil system

Q5 uses EIA *World Oil Transit Chokepoints*, Table 1. Values for 2020–2024 are annual averages; `1H25` is the first-half 2025 average.

| Period | Hormuz flow (mb/d) | World maritime oil trade (mb/d) | World total oil supply (mb/d) | Hormuz / maritime trade | Hormuz / total supply |
|---|---:|---:|---:|---:|---:|
| 2020 | 19.2 | 74.1 | 94.1 | 25.9% | 20.4% |
| 2021 | 19.7 | 75.9 | 95.8 | 26.0% | 20.6% |
| 2022 | 21.9 | 78.6 | 100.6 | 27.9% | 21.8% |
| 2023 | 21.8 | 80.2 | 102.6 | 27.2% | 21.2% |
| 2024 | 20.7 | 79.7 | 103.3 | 26.0% | 20.0% |
| 1H25 | 20.9 | 79.8 | 104.4 | 26.2% | 20.0% |

Hormuz handled approximately one quarter of maritime oil trade throughout the period. Its share peaked in this series at 27.9% in 2022 and stood at 26.0% in 2024. Relative to all oil supply—including oil that was not traded by sea—the 2024 share was 20.0%.

These ratios establish global significance, not the volume that would necessarily be lost under a disruption. Rerouting, spare bypass capacity, inventories, demand response, policy action, and the duration and severity of an event would determine realised effects.

## 4. Data and provenance

### Energy Institute

- Dataset: *Statistical Review of World Energy 2025*, narrow-format CSV (data through 2024)
- Snapshot retrieved: 2026-06-25; exact SHA-256 recorded in `DATA_SOURCES.md`
- Use: global total energy supply and mix; oil production and consumption; selected-market energy structure; Q4 supply-gap inputs
- Main period: 2024

### UN Comtrade

- Flow: imports
- Frequency and year: annual, 2024
- Commodity: HS 2709, crude petroleum oils
- Reporters: USA, China, Germany, European Union, Japan, India, and Rep. of Korea
- Partners: `World` and available individual partner economies
- Snapshot retrieved: 2026-07-02; exact query-file SHA-256 recorded in `DATA_SOURCES.md`
- Use: crude-import origin shares and independent partner-versus-World reconciliation

### U.S. Energy Information Administration

- Source: *World Oil Transit Chokepoints*, Table 1
- Periods: 2020–2024 annual averages and first-half 2025
- Use: Hormuz flows, world maritime oil trade, and world total oil supply

Full download instructions, official links, access dates, and licensing notes are in [`DATA_SOURCES.md`](DATA_SOURCES.md). The IEA workbook used during early exploration is not used by the final analysis.

## 5. Data-quality controls

The code includes explicit controls intended to make analytical failure visible:

- Required-column checks before calculation
- Numeric validation for year and value fields
- Rejection of duplicate country-year-variable keys
- Exclusion of aggregate and `Other` rows from country rankings
- Positive-denominator checks for share calculations
- Complete economy-variable coverage checks in Q3
- Missing Q4 production retained as missing unless an explicit assumption is supplied and flagged
- Preference for Comtrade net weight, with documented value fallback
- Independent partner-total reconciliation against Comtrade `World` rows
- Logical EIA validation that Hormuz flow ≤ maritime trade ≤ total supply
- Figure creation isolated from calculation logic so non-plot tests remain lightweight

The repository contains 20 unit tests for these behaviours, and GitHub Actions runs them on pushes and pull requests.

## 6. Limitations

1. **Snapshot analysis:** most cross-sectional results describe 2024, not a forecast.
2. **Exporter origin is not transit:** UN Comtrade partner data do not identify routes, ports, vessels, or bypass use.
3. **Supply gap is not import dependency:** production minus consumption omits product trade, exports, inventories, refinery effects, and other balance items.
4. **Missing production:** Germany, Japan, and South Korea are intentionally left without Q4 combined proxies.
5. **Reporter coverage:** the seven selected reporters are illustrative major markets, not the full set of global importers.
6. **No disruption model:** the project does not estimate price effects, lost volumes, inventories, substitution, or macroeconomic impact under closure scenarios.
7. **Source conventions:** source revisions, country definitions, and differences between crude oil, petroleum products, and total liquids can affect comparisons.
8. **First-half period:** `1H25` is not a full-year annual average and should be compared with that distinction in mind.

## 7. Reproducibility

Third-party raw data are excluded from version control. After downloading the two required files as described in [`data_raw/README.md`](data_raw/README.md):

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
python run_analysis.py
```

Run selected sections with:

```bash
python run_analysis.py --only q1 q4 q5
```

Run the validation suite with:

```bash
python -m unittest discover -s tests -v
```

## 8. Final interpretation

The analysis shows why Hormuz matters without treating every related statistic as the same kind of exposure. The global flow evidence is strong: around 20–22 mb/d, approximately one quarter of world maritime oil trade, passed through Hormuz across 2020–first-half 2025. The geographic analysis also shows a large structural separation between Middle Eastern supply and Asia-Pacific demand.

At the market level, however, exporter-origin shares are only a first screen. A stronger next-stage model would add cargo routes, port of loading, refinery crude compatibility, strategic and commercial inventories, contract structures, product imports, bypass-pipeline capacity, and disruption duration. Those additions would turn the present descriptive framework into a scenario-based resilience model.

[Back to the project overview](README.md)
