"""Q2: compare the geography of oil production and consumption."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


YEAR = 2024
CODE_DIR = Path(__file__).resolve().parent
DATA_FILE = CODE_DIR / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
FIGURE_FILE = CODE_DIR.parent / "Figures" / "01_regional_oil_balance.png"


def main():
    data = pd.read_csv(DATA_FILE)

    # Remove regional and world totals before ranking countries.
    oil = data[
        (data["Year"] == YEAR)
        & (data["Var"].isin(["oilprod_kbd", "oilcons_kbd"]))
    ].copy()
    oil = oil[~oil["Country"].str.startswith(("Total", "Other"), na=False)]

    production = oil[oil["Var"] == "oilprod_kbd"]
    consumption = oil[oil["Var"] == "oilcons_kbd"]

    top_producers = production.nlargest(10, "Value")[["Country", "Value"]]
    top_consumers = consumption.nlargest(10, "Value")[["Country", "Value"]]

    # Compare each region's share of world production and consumption.
    regional_production = production.groupby("Region")["Value"].sum()
    regional_consumption = consumption.groupby("Region")["Value"].sum()
    regional = pd.concat(
        [regional_production, regional_consumption],
        axis=1,
        keys=["Production", "Consumption"],
    ).fillna(0)
    regional["Production share (%)"] = regional["Production"] / regional["Production"].sum() * 100
    regional["Consumption share (%)"] = regional["Consumption"] / regional["Consumption"].sum() * 100
    regional["Gap (percentage points)"] = (
        regional["Production share (%)"] - regional["Consumption share (%)"]
    )
    regional = regional.sort_values("Production share (%)")

    print("Top 10 oil producers (thousand barrels per day):")
    print(top_producers.round(0).to_string(index=False))
    print("\nTop 10 oil consumers (thousand barrels per day):")
    print(top_consumers.round(0).to_string(index=False))
    print("\nRegional oil balance:")
    print(
        regional[
            ["Production share (%)", "Consumption share (%)", "Gap (percentage points)"]
        ].round(1).to_string()
    )

    # One chart is enough to show the main geographic mismatch.
    FIGURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    regional[["Production share (%)", "Consumption share (%)"]].plot(
        kind="barh",
        figsize=(9, 5),
        color=["#2962a3", "#d9852b"],
    )
    plt.title(f"Regional Oil Production and Consumption Shares, {YEAR}")
    plt.xlabel("Share of world total (%)")
    plt.ylabel("")
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIGURE_FILE, dpi=200)
    plt.close()
    print(f"\nFigure saved to: {FIGURE_FILE}")


if __name__ == "__main__":
    main()
