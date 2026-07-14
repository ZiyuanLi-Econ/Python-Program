"""Q4: calculate crude-import shares by exporter origin."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CODE_DIR = Path(__file__).resolve().parent
TRADE_FILE = CODE_DIR / "data_raw" / "TradeData.csv"
FIGURE_FILE = CODE_DIR.parent / "Figures" / "02_import_origin_exposure.png"

REPORTERS = [
    "USA",
    "China",
    "Germany",
    "European Union",
    "Japan",
    "India",
    "Rep. of Korea",
]

HORMUZ_EXPORTERS = [
    "Saudi Arabia",
    "Iraq",
    "United Arab Emirates",
    "Kuwait",
    "Qatar",
    "Iran",
    "Bahrain",
]


def main():
    # index_col=False keeps the downloaded CSV columns aligned.
    trade = pd.read_csv(
        TRADE_FILE, encoding="latin1", index_col=False, low_memory=False
    )
    trade["refYear"] = pd.to_numeric(trade["refYear"], errors="coerce")
    trade["cmdCode"] = trade["cmdCode"].astype(str).str.replace(".0", "", regex=False)
    trade["netWgt"] = pd.to_numeric(trade["netWgt"], errors="coerce")

    crude = trade[
        (trade["refYear"] == 2024)
        & (trade["flowDesc"] == "Import")
        & (trade["cmdCode"] == "2709")
        & (trade["reporterDesc"].isin(REPORTERS))
        & (trade["partnerDesc"] != "World")
    ]

    by_origin = crude.groupby(["reporterDesc", "partnerDesc"])["netWgt"].sum()
    total_imports = by_origin.groupby("reporterDesc").sum()
    selected_imports = by_origin[
        by_origin.index.get_level_values("partnerDesc").isin(HORMUZ_EXPORTERS)
    ].groupby("reporterDesc").sum()

    shares = (selected_imports / total_imports * 100).reindex(REPORTERS).sort_values()
    print("Crude-import share from selected Hormuz-region exporters, 2024")
    print(shares.round(1).to_string())
    print("\nOrigin is a proxy; it does not show the cargo's actual route.")

    FIGURE_FILE.parent.mkdir(parents=True, exist_ok=True)
    shares.plot(kind="barh", figsize=(9, 5), color="#C65D3A")
    plt.title("Crude Imports from Hormuz-Region Exporters, 2024")
    plt.xlabel("Share of reported crude imports by net weight (%)")
    plt.ylabel("")
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.savefig(FIGURE_FILE, dpi=200)
    plt.close()


if __name__ == "__main__":
    main()
