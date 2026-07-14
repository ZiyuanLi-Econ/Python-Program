"""Q5: place Strait of Hormuz flows in the global oil system."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CODE_DIR = Path(__file__).resolve().parent
FIGURES_DIR = CODE_DIR.parent / "Figures"
PERIODS = ["2020", "2021", "2022", "2023", "2024", "1H25"]
SOURCE_NOTE = (
    "Source: U.S. EIA, World Oil Transit Chokepoints, Table 1. "
    "2020-2024 annual averages; 1H25 first-half average."
)


def build_chokepoint_table():
    """Enter the EIA Table 1 data in million barrels per day."""

    return pd.DataFrame(
        {
            "Location": [
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


def build_hormuz_share_table(chokepoints):
    indexed = chokepoints.set_index("Location")
    table = pd.DataFrame(
        {
            "Period": PERIODS,
            "Hormuz flow (mb/d)": indexed.loc["Strait of Hormuz", PERIODS].values,
            "World maritime trade (mb/d)": indexed.loc[
                "World maritime oil trade", PERIODS
            ].values,
            "World total supply (mb/d)": indexed.loc[
                "World total oil supply", PERIODS
            ].values,
        }
    )
    table["Share of maritime trade (%)"] = (
        table["Hormuz flow (mb/d)"] / table["World maritime trade (mb/d)"] * 100
    )
    table["Share of total supply (%)"] = (
        table["Hormuz flow (mb/d)"] / table["World total supply (mb/d)"] * 100
    )
    return table


def save_chart(fig, filename):
    fig.text(0.5, 0.02, SOURCE_NOTE, ha="center", fontsize=8.5, color="#555555")
    fig.tight_layout(rect=[0.02, 0.07, 0.98, 0.95])
    fig.savefig(FIGURES_DIR / filename, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_2024_chokepoints(chokepoints):
    physical_routes = chokepoints.iloc[:8].sort_values("2024")
    colors = ["#C65D3A" if name == "Strait of Hormuz" else "#5B7FA3" for name in physical_routes["Location"]]

    fig, ax = plt.subplots(figsize=(10.5, 6.1))
    bars = ax.barh(physical_routes["Location"], physical_routes["2024"], color=colors)
    ax.bar_label(bars, labels=[f"{value:.1f}" for value in physical_routes["2024"]], padding=4)
    ax.set_title("Oil flows through major maritime routes, 2024")
    ax.set_xlabel("Million barrels per day")
    ax.set_ylabel("")
    ax.set_xlim(0, 26)
    ax.grid(axis="x", alpha=0.2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    save_chart(fig, "11_global_oil_chokepoints_2024.png")


def plot_hormuz_flow(share_table):
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.plot(
        share_table["Period"],
        share_table["Hormuz flow (mb/d)"],
        marker="o",
        linewidth=2.5,
        color="#C65D3A",
    )
    for period, value in zip(share_table["Period"], share_table["Hormuz flow (mb/d)"]):
        ax.annotate(f"{value:.1f}", (period, value), xytext=(0, 8), textcoords="offset points", ha="center")
    ax.set_title("Oil flow through the Strait of Hormuz")
    ax.set_xlabel("")
    ax.set_ylabel("Million barrels per day")
    ax.set_ylim(18, 23)
    ax.grid(axis="y", alpha=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    save_chart(fig, "12_hormuz_flow_2020_1H25.png")


def plot_global_shares(share_table):
    fig, ax = plt.subplots(figsize=(9.8, 5.4))
    series = [
        ("Share of maritime trade (%)", "World maritime oil trade", "#2962A3"),
        ("Share of total supply (%)", "World total oil supply", "#C65D3A"),
    ]
    for column, label, color in series:
        ax.plot(
            share_table["Period"],
            share_table[column],
            marker="o",
            linewidth=2.4,
            label=label,
            color=color,
        )
        for period, value in zip(share_table["Period"], share_table[column]):
            offset = 8 if "maritime" in column else -14
            ax.annotate(
                f"{value:.1f}%",
                (period, value),
                xytext=(0, offset),
                textcoords="offset points",
                ha="center",
                fontsize=8.5,
            )

    ax.annotate(
        "Share of maritime trade",
        (share_table.index[-1], share_table["Share of maritime trade (%)"].iloc[-1]),
        xytext=(12, 9),
        textcoords="offset points",
        fontsize=8.5,
        color="#2962A3",
    )
    ax.annotate(
        "Share of total supply",
        (share_table.index[-1], share_table["Share of total supply (%)"].iloc[-1]),
        xytext=(12, -11),
        textcoords="offset points",
        fontsize=8.5,
        color="#C65D3A",
    )
    ax.set_title("Strait of Hormuz share of global oil flows")
    ax.set_xlabel("")
    ax.set_ylabel("Share (%)")
    ax.set_ylim(17, 30)
    ax.grid(axis="y", alpha=0.2)
    ax.set_xlim(-0.1, len(share_table) - 0.3)
    ax.spines[["top", "right"]].set_visible(False)
    save_chart(fig, "13_hormuz_global_share_2020_1H25.png")


def main():
    chokepoints = build_chokepoint_table()
    share_table = build_hormuz_share_table(chokepoints)

    print("EIA World Oil Transit Chokepoints, Table 1 (million barrels per day):")
    print(chokepoints.to_string(index=False))
    print("\nStrait of Hormuz shares of global oil flows:")
    print(share_table.round(1).to_string(index=False))

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_2024_chokepoints(chokepoints)
    plot_hormuz_flow(share_table)
    plot_global_shares(share_table)


if __name__ == "__main__":
    main()
