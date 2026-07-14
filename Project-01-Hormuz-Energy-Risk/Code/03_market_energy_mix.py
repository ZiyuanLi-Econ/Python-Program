"""Q3: compare energy use and energy mix across selected markets."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


YEAR = 2024
CODE_DIR = Path(__file__).resolve().parent
DATA_FILE = CODE_DIR / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
FIGURES_DIR = CODE_DIR.parent / "Figures"

MARKET_NAMES = {
    "China": "China",
    "US": "United States",
    "India": "India",
    "Japan": "Japan",
    "South Korea": "South Korea",
    "Germany": "Germany",
    "Total EU": "European Union (regional aggregate)",
}
ENERGY_NAMES = {
    "oilcons_ej": "Oil",
    "gascons_ej": "Natural gas",
    "coalcons_ej": "Coal",
    "nuclear_ej": "Nuclear",
    "renewables_ej": "Renewables",
}
COLORS = ["#2F6B9A", "#E38B2C", "#3A9D5D", "#C94C4C", "#8C6BB1"]
SOURCE_NOTE = (
    "Source: Energy Institute, Statistical Review of World Energy 2025. "
    "European Union is a regional aggregate."
)


def prepare_tables(data):
    """Filter the long data, pivot it, and calculate source shares."""

    variables = ["tes_ej"] + list(ENERGY_NAMES)
    selected = data[
        (data["Year"] == YEAR)
        & (data["Country"].isin(MARKET_NAMES))
        & (data["Var"].isin(variables))
    ][["Country", "Var", "Value"]].copy()

    wide = selected.pivot(index="Country", columns="Var", values="Value")
    wide = wide.reindex(MARKET_NAMES).rename(index=MARKET_NAMES)
    totals = wide["tes_ej"].rename("Total energy supply (EJ)")
    amounts = wide[list(ENERGY_NAMES)].rename(columns=ENERGY_NAMES)
    shares = amounts.div(totals, axis=0) * 100
    return totals, amounts, shares


def finish_figure(fig, path):
    """Add a source footnote and save a complete white-background PNG."""

    fig.text(0.5, -0.015, SOURCE_NOTE, ha="center", fontsize=8.5, color="#555555")
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_total_energy(totals):
    plot_data = totals.sort_values()
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    bars = ax.barh(plot_data.index, plot_data, color="#2F6B9A")
    ax.bar_label(bars, labels=[f"{value:.1f} EJ" for value in plot_data], padding=4)
    ax.set_xlim(0, plot_data.max() * 1.18)
    ax.set_title(f"Total Energy Supply in Selected Markets, {YEAR}", fontweight="bold")
    ax.set_xlabel("Exajoules (EJ)")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    finish_figure(fig, FIGURES_DIR / "05_selected_market_total_energy_2024.png")


def plot_energy_amounts(amounts, totals):
    fig, ax = plt.subplots(figsize=(11.5, 6.6), constrained_layout=True)
    amounts.plot.bar(stacked=True, ax=ax, color=COLORS, width=0.72)
    for position, total in enumerate(totals):
        ax.text(position, total + totals.max() * 0.012, f"{total:.1f}", ha="center", fontsize=8)
    ax.set_ylim(0, totals.max() * 1.13)
    ax.set_title(f"Energy Supply by Source and Market, {YEAR}", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Energy supply (EJ)")
    ax.tick_params(axis="x", rotation=22)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    ax.legend(title="Energy source", frameon=False, ncol=5, loc="upper right")
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    finish_figure(fig, FIGURES_DIR / "06_selected_market_energy_amount_2024.png")


def plot_energy_shares(shares):
    fig, ax = plt.subplots(figsize=(11.5, 6.6), constrained_layout=True)
    shares.plot.bar(stacked=True, ax=ax, color=COLORS, width=0.72)
    for bars in ax.containers:
        labels = [f"{value:.1f}%" if value >= 4 else "" for value in bars.datavalues]
        ax.bar_label(bars, labels=labels, label_type="center", fontsize=7.5, color="white")
    ax.set_ylim(0, 105)
    ax.set_title(
        f"Energy Mix in Selected Markets, {YEAR}",
        fontweight="bold",
        pad=55,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Share of total energy supply (%)")
    ax.tick_params(axis="x", rotation=22)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    ax.legend(
        title="Energy source",
        frameon=False,
        ncol=5,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.04),
    )
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    finish_figure(fig, FIGURES_DIR / "07_selected_market_energy_mix_2024.png")


def main():
    data = pd.read_csv(DATA_FILE)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    totals, amounts, shares = prepare_tables(data)

    summary = pd.DataFrame({
        "Total energy (EJ)": totals,
        "Largest source": shares.idxmax(axis=1),
        "Largest source share (%)": shares.max(axis=1),
        "Oil share (%)": shares["Oil"],
    })
    print(f"Energy supply by source in {YEAR} (EJ):")
    print(amounts.round(1).to_string())
    print(f"\nEnergy mix in {YEAR} (%):")
    print(shares.round(1).to_string())
    print("\nMarket summary:")
    print(summary.round(1).to_string())
    print("\nNote: European Union is a regional aggregate, not a country.")

    plot_total_energy(totals)
    plot_energy_amounts(amounts, totals)
    plot_energy_shares(shares)
    print(f"\nThree figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
