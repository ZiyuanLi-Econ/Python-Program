"""Q3: compare the energy mix of selected economies and markets."""

from pathlib import Path

import pandas as pd


YEAR = 2024
DATA_FILE = (
    Path(__file__).resolve().parent
    / "data_raw"
    / "Statistical Review of World Energy Narrow format.csv"
)

MARKETS = ["China", "US", "India", "Japan", "South Korea", "Germany", "Total EU"]
ENERGY_NAMES = {
    "oilcons_ej": "Oil",
    "gascons_ej": "Natural gas",
    "coalcons_ej": "Coal",
    "nuclear_ej": "Nuclear",
    "renewables_ej": "Renewables",
}


def main():
    data = pd.read_csv(DATA_FILE)
    variables = ["tes_ej"] + list(ENERGY_NAMES)

    selected = data[
        (data["Year"] == YEAR)
        & (data["Country"].isin(MARKETS))
        & (data["Var"].isin(variables))
    ]

    # Put one market on each row, then divide each source by total energy supply.
    amounts = selected.pivot(index="Country", columns="Var", values="Value")
    amounts = amounts.reindex(MARKETS)
    shares = amounts[list(ENERGY_NAMES)].div(amounts["tes_ej"], axis=0) * 100
    shares = shares.rename(columns=ENERGY_NAMES)

    summary = pd.DataFrame(index=shares.index)
    summary["Largest energy source"] = shares.idxmax(axis=1)
    summary["Largest source share (%)"] = shares.max(axis=1)
    summary["Oil share (%)"] = shares["Oil"]

    print(f"Energy mix by market in {YEAR} (%):")
    print(shares.round(1).to_string())
    print("\nMain comparison:")
    print(summary.round(1).to_string())
    print("\nNote: Total EU is a regional market aggregate, not a country.")


if __name__ == "__main__":
    main()
