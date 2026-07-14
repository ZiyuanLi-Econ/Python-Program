"""Q1: calculate and visualise the global energy mix in 2024."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


YEAR = 2024
CODE_DIR = Path(__file__).resolve().parent
DATA_FILE = CODE_DIR / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
FIGURE_FILE = CODE_DIR.parent / "Figures" / "01_global_energy_mix_2024.png"

ENERGY_NAMES = {
    "oilcons_ej": "Oil",
    "coalcons_ej": "Coal",
    "gascons_ej": "Natural gas",
    "nuclear_ej": "Nuclear",
    "renewables_ej": "Renewables",
}

ENERGY_COLORS = {
    "Oil": "#C65D3A",
    "Coal": "#555555",
    "Natural gas": "#2962A3",
    "Nuclear": "#8064A2",
    "Renewables": "#3A8F5B",
}


def main():
    data = pd.read_csv(DATA_FILE)

    # Select the world total and calculate each source's share of energy supply.
    world = data[(data["Country"] == "Total World") & (data["Year"] == YEAR)]
    total_energy = world.loc[world["Var"] == "tes_ej", "Value"].iloc[0]

    energy_mix = world[world["Var"].isin(ENERGY_NAMES)][["Var", "Value"]].copy()
    energy_mix["Energy source"] = energy_mix["Var"].map(ENERGY_NAMES)
    energy_mix["Energy supply (EJ)"] = energy_mix["Value"]
    energy_mix["Share (%)"] = energy_mix["Value"] / total_energy * 100
    energy_mix = energy_mix[["Energy source", "Energy supply (EJ)", "Share (%)"]]
    energy_mix = energy_mix.sort_values("Share (%)", ascending=False).reset_index(drop=True)

    fossil_share = energy_mix.loc[
        energy_mix["Energy source"].isin(["Oil", "Coal", "Natural gas"]),
        "Share (%)",
    ].sum()

    print(f"Global total energy supply in {YEAR}: {total_energy:.1f} EJ")
    print(f"Fossil-fuel share: {fossil_share:.1f}%")
    print("\nGlobal energy mix:")
    print(energy_mix.round(1).to_string(index=False))

    # A bar chart is precise, while the donut gives a quick view of composition.
    FIGURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    colors = [ENERGY_COLORS[name] for name in energy_mix["Energy source"]]
    bar_data = energy_mix.sort_values("Share (%)")
    bar_colors = [ENERGY_COLORS[name] for name in bar_data["Energy source"]]

    fig, (ax_bar, ax_donut) = plt.subplots(
        1,
        2,
        figsize=(12, 5.8),
        gridspec_kw={"width_ratios": [1.15, 1]},
    )

    bars = ax_bar.barh(
        bar_data["Energy source"], bar_data["Share (%)"], color=bar_colors
    )
    ax_bar.bar_label(
        bars,
        labels=[f"{value:.1f}%" for value in bar_data["Share (%)"]],
        padding=4,
        fontsize=10,
    )
    ax_bar.set_title("Share by energy source")
    ax_bar.set_xlabel("Share of total energy supply (%)")
    ax_bar.set_ylabel("")
    ax_bar.set_xlim(0, energy_mix["Share (%)"].max() * 1.22)
    ax_bar.grid(axis="x", alpha=0.2)
    ax_bar.spines[["top", "right", "left"]].set_visible(False)

    ax_donut.pie(
        energy_mix["Share (%)"],
        labels=energy_mix["Energy source"],
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
        pctdistance=0.78,
        wedgeprops={"width": 0.42, "edgecolor": "white"},
    )
    ax_donut.set_title("Composition of global supply")

    fig.suptitle(f"Global Energy Mix, {YEAR}", fontsize=16, fontweight="bold")
    fig.text(
        0.5,
        0.015,
        "Source: Energy Institute, Statistical Review of World Energy 2025.",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=[0.02, 0.06, 0.98, 0.92])
    fig.savefig(FIGURE_FILE, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\nFigure saved to: {FIGURE_FILE}")


if __name__ == "__main__":
    main()
