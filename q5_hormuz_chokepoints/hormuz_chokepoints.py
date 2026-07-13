"""Q5: Strait of Hormuz flows in the global oil system.

Source: U.S. Energy Information Administration (EIA),
"World Oil Transit Chokepoints", Table 1.
URL: https://www.eia.gov/international/content/analysis/special_topics/World_Oil_Transit_Chokepoints/
Unit: million barrels per day (mb/d).
Periods: 2020-2024 are annual averages; 1H25 is the first-half 2025 average.

Run ``python hormuz_chokepoints.py`` to print and save the calculations. If
matplotlib is installed, a time-series chart is also saved. Use ``--no-plots``
to skip it.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
TABLES_DIR = SCRIPT_DIR / "tables"
FIGURES_DIR = SCRIPT_DIR / "figures"

SOURCE_TITLE = "EIA World Oil Transit Chokepoints"
SOURCE_TABLE = "Table 1"
SOURCE_ACCESSED = "2026-07-13"
SOURCE_URL = (
    "https://www.eia.gov/international/content/analysis/special_topics/"
    "World_Oil_Transit_Chokepoints/"
)
UNIT = "million barrels per day (mb/d)"
PERIOD_NOTE = (
    "2020-2024 are annual averages; 1H25 is the first-half 2025 average."
)
PERIODS = ["2020", "2021", "2022", "2023", "2024", "1H25"]


def build_eia_chokepoint_table() -> pd.DataFrame:
    """Return the EIA Table 1 values used in this analysis."""

    return pd.DataFrame(
        {
            "location": [
                "Strait of Malacca",
                "Strait of Hormuz",
                "Suez Canal and SUMED Pipeline",
                "Bab el-Mandeb",
                "Danish Straits",
                "Turkish Straits (Dardanelles)",
                "Panama Canal",
                "Cape of Good Hope",
                "World maritime oil trade",
                "World total oil supply",
            ],
            "2020": [22.8, 19.2, 5.4, 5.7, 3.1, 3.2, 1.7, 7.9, 74.1, 94.1],
            "2021": [22.1, 19.7, 5.2, 6.0, 3.1, 3.3, 1.8, 7.2, 75.9, 95.8],
            "2022": [23.0, 21.9, 7.3, 8.0, 4.2, 3.2, 2.2, 6.1, 78.6, 100.6],
            "2023": [24.0, 21.8, 8.8, 9.3, 5.0, 3.5, 2.2, 6.2, 80.2, 102.6],
            "2024": [22.5, 20.7, 4.8, 4.1, 4.9, 3.6, 2.0, 9.3, 79.7, 103.3],
            "1H25": [23.2, 20.9, 4.9, 4.2, 4.9, 3.7, 2.3, 9.1, 79.8, 104.4],
        }
    )


def validate_eia_table(table: pd.DataFrame) -> None:
    """Validate required locations, periods, and basic magnitude relationships."""

    required_columns = {"location", *PERIODS}
    missing_columns = required_columns.difference(table.columns)
    if missing_columns:
        raise ValueError(f"EIA table is missing columns: {sorted(missing_columns)}")

    required_locations = {
        "Strait of Hormuz",
        "World maritime oil trade",
        "World total oil supply",
    }
    locations = set(table["location"])
    missing_locations = required_locations.difference(locations)
    if missing_locations:
        raise ValueError(
            f"EIA table is missing locations: {sorted(missing_locations)}"
        )
    duplicated_locations = table.loc[
        table["location"].duplicated(keep=False), "location"
    ].unique()
    if len(duplicated_locations) > 0:
        raise ValueError(
            "EIA table contains duplicate locations: "
            f"{sorted(duplicated_locations.tolist())}"
        )

    numeric = table.set_index("location")[PERIODS].apply(
        pd.to_numeric, errors="coerce"
    )
    if numeric.isna().any().any() or (numeric < 0).any().any():
        raise ValueError("EIA flow values must be non-negative numbers.")

    hormuz = numeric.loc["Strait of Hormuz"]
    maritime = numeric.loc["World maritime oil trade"]
    total_supply = numeric.loc["World total oil supply"]
    if (maritime <= 0).any() or (total_supply <= 0).any():
        raise ValueError(
            "World maritime trade and world total supply must be greater than zero."
        )
    if not ((hormuz <= maritime) & (maritime <= total_supply)).all():
        raise ValueError(
            "Expected Strait of Hormuz <= maritime trade <= total supply."
        )


def calculate_hormuz_global_shares(table: pd.DataFrame) -> pd.DataFrame:
    """Calculate Hormuz flows as shares of maritime trade and total supply."""

    validate_eia_table(table)
    indexed = table.set_index("location")[PERIODS].T
    result = pd.DataFrame(
        {
            "period": PERIODS,
            "hormuz_flow_mbd": indexed["Strait of Hormuz"].to_numpy(),
            "world_maritime_oil_trade_mbd": indexed[
                "World maritime oil trade"
            ].to_numpy(),
            "world_total_oil_supply_mbd": indexed[
                "World total oil supply"
            ].to_numpy(),
        }
    )
    result["hormuz_share_of_world_maritime_trade_pct"] = (
        result["hormuz_flow_mbd"]
        / result["world_maritime_oil_trade_mbd"]
        * 100
    ).round(1)
    result["hormuz_share_of_world_total_supply_pct"] = (
        result["hormuz_flow_mbd"]
        / result["world_total_oil_supply_mbd"]
        * 100
    ).round(1)
    result["unit"] = UNIT
    result["period_definition"] = PERIOD_NOTE
    result["source_title"] = SOURCE_TITLE
    result["source_table"] = SOURCE_TABLE
    result["source_url"] = SOURCE_URL
    result["source_accessed"] = SOURCE_ACCESSED
    return result


def table_to_long_format(table: pd.DataFrame) -> pd.DataFrame:
    """Convert the full EIA source table to a self-documenting long CSV."""

    validate_eia_table(table)
    long_table = table.melt(
        id_vars="location",
        value_vars=PERIODS,
        var_name="period",
        value_name="flow_mbd",
    )
    long_table["period"] = pd.Categorical(
        long_table["period"], categories=PERIODS, ordered=True
    )
    long_table = long_table.sort_values(["location", "period"]).reset_index(
        drop=True
    )
    long_table["period"] = long_table["period"].astype(str)
    long_table["unit"] = UNIT
    long_table["period_definition"] = PERIOD_NOTE
    long_table["source_title"] = SOURCE_TITLE
    long_table["source_table"] = SOURCE_TABLE
    long_table["source_url"] = SOURCE_URL
    long_table["source_accessed"] = SOURCE_ACCESSED
    return long_table


def save_tables(
    source_table: pd.DataFrame, share_table: pd.DataFrame
) -> list[Path]:
    """Save the complete EIA inputs and the derived Hormuz shares."""

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        TABLES_DIR / "q5_eia_chokepoint_flows_2020_1h2025.csv": table_to_long_format(
            source_table
        ),
        TABLES_DIR / "q5_hormuz_global_shares_2020_1h2025.csv": share_table,
    }
    for path, table in outputs.items():
        table.to_csv(path, index=False)
    return list(outputs)


def save_time_series_figure(share_table: pd.DataFrame) -> Path:
    """Save the two global-share series, importing matplotlib only on demand."""

    import matplotlib.pyplot as plt

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / "q5_hormuz_share_of_global_oil_flows_2020_1h2025.png"

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(
        share_table["period"],
        share_table["hormuz_share_of_world_maritime_trade_pct"],
        marker="o",
        linewidth=2,
        label="Share of world maritime oil trade",
    )
    ax.plot(
        share_table["period"],
        share_table["hormuz_share_of_world_total_supply_pct"],
        marker="o",
        linewidth=2,
        label="Share of world total oil supply",
    )
    ax.set_title("Strait of Hormuz Share of Global Oil Flows")
    ax.set_xlabel("Period")
    ax.set_ylabel("Share (%)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    ax.text(
        0,
        -0.20,
        "Source: EIA World Oil Transit Chokepoints, Table 1. "
        "2020-2024 annual averages; 1H25 first-half average.",
        transform=ax.transAxes,
        fontsize=8,
    )
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    return path


def main(make_plots: bool = True) -> None:
    """Calculate, print, and save the Q5 results."""

    source_table = build_eia_chokepoint_table()
    share_table = calculate_hormuz_global_shares(source_table)
    table_paths = save_tables(source_table, share_table)

    print(f"Source: {SOURCE_TITLE}, {SOURCE_TABLE}")
    print(f"URL: {SOURCE_URL}")
    print(f"Source accessed: {SOURCE_ACCESSED}")
    print(f"Unit: {UNIT}")
    print(f"Periods: {PERIOD_NOTE}")
    print("\nStrait of Hormuz shares of global oil flows:")
    print(
        share_table[
            [
                "period",
                "hormuz_flow_mbd",
                "world_maritime_oil_trade_mbd",
                "world_total_oil_supply_mbd",
                "hormuz_share_of_world_maritime_trade_pct",
                "hormuz_share_of_world_total_supply_pct",
            ]
        ].to_string(index=False)
    )
    print(f"\nSaved {len(table_paths)} tables to {TABLES_DIR}")

    if make_plots:
        try:
            figure_path = save_time_series_figure(share_table)
        except ModuleNotFoundError as error:
            if error.name and error.name.startswith("matplotlib"):
                print("matplotlib is not installed; tables were saved and plot skipped.")
            else:
                raise
        else:
            print(f"Saved figure to {figure_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="save data tables without importing matplotlib",
    )
    arguments = parser.parse_args()
    main(make_plots=not arguments.no_plots)
