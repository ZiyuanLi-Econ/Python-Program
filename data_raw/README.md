# Local source data

This directory is intentionally empty in Git. Download the required third-party files from the official publishers described in [`../DATA_SOURCES.md`](../DATA_SOURCES.md), then save them here with these exact names:

```text
data_raw/
├── Statistical Review of World Energy Narrow format.csv
└── TradeData.csv
```

The Energy Institute CSV supplies the energy observations used in Q1–Q4. The
published results use the **2025 edition snapshot (data through 2024)**; if a
later edition is now offered, historical revisions may produce different
results. `TradeData.csv` must be the 2024 UN Comtrade annual import query for HS
2709 and the seven reporters documented in `DATA_SOURCES.md`. Compare both
downloaded files with the hashes in `DATA_SOURCES.md` when exact reproduction is
required.

Do not add `WorldEnergyBalancesHighlights2025.xlsx`: the final project does not use that workbook. Do not commit any downloaded source data; `.gitignore` excludes it because the files are third-party material with their own terms.
