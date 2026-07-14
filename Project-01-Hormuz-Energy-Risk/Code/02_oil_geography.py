"""Q2: compare the geography and concentration of the global oil market."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


YEAR = 2024
CODE_DIR = Path(__file__).resolve().parent
DATA_FILE = CODE_DIR / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
FIGURES_DIR = CODE_DIR.parent / "Figures"

PRODUCTION_COLOR = "#2962A3"
CONSUMPTION_COLOR = "#D9852B"
SOURCE_NOTE = "Source: Energy Institute, Statistical Review of World Energy 2025."

REGIONAL_TOTALS = {
    "North America": "Total North America",
    "S. & Cent. America": "Total S. & Cent. America",
    "Europe": "Total Europe",
    "CIS": "Total CIS",
    "Middle East": "Total Middle East",
    "Africa": "Total Africa",
    "Asia Pacific": "Total Asia Pacific",
}


def country_series(data, variable, value_name):
    """Select one country series and remove regional and world totals."""

    selected = data[(data["Year"] == YEAR) & (data["Var"] == variable)][
        ["Country", "Region", "Value"]
    ].copy()
    selected = selected[
        ~selected["Country"].str.startswith(("Total", "Other"), na=False)
    ]
    return selected.rename(columns={"Value": value_name}).sort_values(
        value_name, ascending=False
    )


def one_value(data, country, variable):
    """Return one Energy Institute value for the selected year."""

    values = data[
        (data["Country"] == country)
        & (data["Year"] == YEAR)
        & (data["Var"] == variable)
    ]["Value"]
    if len(values) != 1:
        raise ValueError(f"Expected one {variable} value for {country}, found {len(values)}")
    return float(values.iloc[0])


def save_figure(fig, path):
    """Add the source and save a complete PNG for GitHub."""

    fig.text(0.5, 0.015, SOURCE_NOTE, ha="center", fontsize=9, color="#555555")
    fig.tight_layout(rect=[0.02, 0.06, 0.98, 0.94])
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    data = pd.read_csv(DATA_FILE)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    production = country_series(data, "oilprod_kbd", "Production (kbd)")
    consumption = country_series(data, "oilcons_kbd", "Consumption (kbd)")
    world_production = one_value(data, "Total World", "oilprod_kbd")
    world_consumption = one_value(data, "Total World", "oilcons_kbd")

    # Top-country rankings.
    top_producers = production.head(10).reset_index(drop=True)
    top_consumers = consumption.head(10).reset_index(drop=True)
    top_table = pd.DataFrame(
        {
            "Rank": range(1, 11),
            "Producer": top_producers["Country"],
            "Production (kbd)": top_producers["Production (kbd)"],
            "Consumer": top_consumers["Country"],
            "Consumption (kbd)": top_consumers["Consumption (kbd)"],
        }
    )

    # Use the published regional totals and Total World denominators. Summing
    # only individually named countries would omit the dataset's "Other" rows.
    regional_rows = []
    for region, total_country in REGIONAL_TOTALS.items():
        regional_rows.append(
            {
                "Region": region,
                "Production (kbd)": one_value(data, total_country, "oilprod_kbd"),
                "Consumption (kbd)": one_value(data, total_country, "oilcons_kbd"),
            }
        )
    regional = pd.DataFrame(regional_rows).set_index("Region")
    regional["Production share (%)"] = (
        regional["Production (kbd)"] / world_production * 100
    )
    regional["Consumption share (%)"] = (
        regional["Consumption (kbd)"] / world_consumption * 100
    )
    regional["Gap (percentage points)"] = (
        regional["Production share (%)"] - regional["Consumption share (%)"]
    )
    regional = regional.sort_values("Gap (percentage points)", ascending=False)

    # Top 3/5/10 shares are a simple measure of market concentration.
    concentration_rows = []
    for top_n in [3, 5, 10]:
        concentration_rows.append(
            {
                "Country group": f"Top {top_n}",
                "Production share (%)": production.head(top_n)["Production (kbd)"].sum()
                / world_production
                * 100,
                "Consumption share (%)": consumption.head(top_n)["Consumption (kbd)"].sum()
                / world_consumption
                * 100,
            }
        )
    concentration = pd.DataFrame(concentration_rows)

    print("Top 10 oil producers and consumers (thousand barrels per day):")
    print(top_table.round(0).to_string(index=False))
    print("\nRegional oil production-consumption balance:")
    print(regional[["Production share (%)", "Consumption share (%)", "Gap (percentage points)"]].round(1).to_string())
    print("\nOil-market concentration:")
    print(concentration.round(1).to_string(index=False))

    # Figure 02: Top 10 production and consumption in one two-panel chart.
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.4))
    chart_specs = [
        (axes[0], top_producers, "Production (kbd)", PRODUCTION_COLOR, "Top 10 producers"),
        (axes[1], top_consumers, "Consumption (kbd)", CONSUMPTION_COLOR, "Top 10 consumers"),
    ]
    for ax, table, value_column, color, title in chart_specs:
        plot_data = table.sort_values(value_column)
        plot_data.plot.barh(
            x="Country", y=value_column, ax=ax, color=color, legend=False
        )
        ax.bar_label(
            ax.containers[0],
            labels=[f"{value:,.0f}" for value in plot_data[value_column]],
            padding=3,
            fontsize=8,
        )
        ax.set_title(title)
        ax.set_xlabel("Thousand barrels per day")
        ax.set_ylabel("")
        ax.set_xlim(0, plot_data[value_column].max() * 1.23)
        ax.grid(axis="x", alpha=0.2)
        ax.spines[["top", "right", "left"]].set_visible(False)
    fig.suptitle(f"Largest Oil Producers and Consumers, {YEAR}", fontsize=16, fontweight="bold")
    save_figure(fig, FIGURES_DIR / "02_top_oil_markets_2024.png")

    # Figure 03: regional production and consumption shares.
    region_plot = regional.sort_values("Production share (%)")
    fig, ax = plt.subplots(figsize=(10, 6))
    region_plot[["Production share (%)", "Consumption share (%)"]].plot.barh(
        ax=ax, color=[PRODUCTION_COLOR, CONSUMPTION_COLOR]
    )
    for bars in ax.containers:
        ax.bar_label(bars, fmt="%.1f", padding=2, fontsize=8)
    largest_share = region_plot[["Production share (%)", "Consumption share (%)"]].max().max()
    ax.set_xlim(0, largest_share * 1.16)
    ax.set_title(f"Regional Oil Production and Consumption Shares, {YEAR}", fontweight="bold")
    ax.set_xlabel("Share of world total (%)")
    ax.set_ylabel("")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    save_figure(fig, FIGURES_DIR / "03_regional_oil_balance_2024.png")

    # Figure 04: production and consumption concentration.
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    concentration.set_index("Country group").plot.bar(
        ax=ax,
        color=[PRODUCTION_COLOR, CONSUMPTION_COLOR],
        rot=0,
    )
    for bars in ax.containers:
        ax.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
    largest_share = concentration[["Production share (%)", "Consumption share (%)"]].max().max()
    ax.set_ylim(0, largest_share * 1.18)
    ax.set_title(f"Oil-Market Concentration, {YEAR}", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Share of world total (%)")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, FIGURES_DIR / "04_oil_market_concentration_2024.png")

    print(f"\nThree figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
