"""Q5: compare Strait of Hormuz flows with global oil flows."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CODE_DIR = Path(__file__).resolve().parent
FIGURE_FILE = CODE_DIR.parent / "Figures" / "03_hormuz_global_share.png"


def main():
    # U.S. EIA Table 1, million barrels per day.
    data = pd.DataFrame(
        {
            "Period": ["2020", "2021", "2022", "2023", "2024", "1H25"],
            "Hormuz": [19.2, 19.7, 21.9, 21.8, 20.7, 20.9],
            "World maritime trade": [74.1, 75.9, 78.6, 80.2, 79.7, 79.8],
            "World total supply": [94.1, 95.8, 100.6, 102.6, 103.3, 104.4],
        }
    )

    data["Maritime trade share (%)"] = (
        data["Hormuz"] / data["World maritime trade"] * 100
    )
    data["Total supply share (%)"] = (
        data["Hormuz"] / data["World total supply"] * 100
    )

    print("Strait of Hormuz in global oil flows")
    print(data.round(1).to_string(index=False))

    FIGURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.plot(
        x="Period",
        y=["Maritime trade share (%)", "Total supply share (%)"],
        marker="o",
        figsize=(9, 5),
        color=["#173F5F", "#C65D3A"],
    )
    plt.title("Strait of Hormuz Share of Global Oil Flows")
    plt.ylabel("Share (%)")
    plt.xlabel("")
    plt.ylim(17, 30)
    plt.grid(axis="y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(FIGURE_FILE, dpi=200)
    plt.close()


if __name__ == "__main__":
    main()
