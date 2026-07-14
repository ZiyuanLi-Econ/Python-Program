"""Q1: calculate the global energy mix in 2024."""

from pathlib import Path

import pandas as pd


YEAR = 2024
DATA_FILE = (
    Path(__file__).resolve().parent
    / "data_raw"
    / "Statistical Review of World Energy Narrow format.csv"
)

ENERGY_NAMES = {
    "oilcons_ej": "Oil",
    "coalcons_ej": "Coal",
    "gascons_ej": "Natural gas",
    "nuclear_ej": "Nuclear",
    "renewables_ej": "Renewables",
}


def main():
    data = pd.read_csv(DATA_FILE)

    # Select the world total for the five main energy sources.
    world = data[(data["Country"] == "Total World") & (data["Year"] == YEAR)]
    total_energy = world.loc[world["Var"] == "tes_ej", "Value"].iloc[0]

    energy_mix = world[world["Var"].isin(ENERGY_NAMES)][["Var", "Value"]].copy()
    energy_mix["Energy source"] = energy_mix["Var"].map(ENERGY_NAMES)
    energy_mix["Share (%)"] = energy_mix["Value"] / total_energy * 100
    energy_mix = energy_mix[["Energy source", "Value", "Share (%)"]]
    energy_mix = energy_mix.sort_values("Share (%)", ascending=False)

    print(f"Global total energy supply in {YEAR}: {total_energy:.1f} EJ")
    print("\nGlobal energy mix:")
    print(energy_mix.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
