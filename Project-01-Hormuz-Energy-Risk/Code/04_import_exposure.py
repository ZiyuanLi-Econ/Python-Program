"""Q4: compare oil supply gaps with crude-import exporter origins in 2024."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


YEAR = 2024
CODE_DIR = Path(__file__).resolve().parent
ENERGY_FILE = CODE_DIR / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
TRADE_FILE = CODE_DIR / "data_raw" / "TradeData.csv"
FIGURES_DIR = CODE_DIR.parent / "Figures"

ENERGY_COUNTRIES = {
    "US": "USA",
    "China": "China",
    "Germany": "Germany",
    "Total EU": "European Union",
    "Japan": "Japan",
    "India": "India",
    "South Korea": "Rep. of Korea",
}
REPORTERS = list(ENERGY_COUNTRIES.values())
DISPLAY_NAMES = {"USA": "United States", "Rep. of Korea": "South Korea"}

HORMUZ_EXPORTERS = [
    "Saudi Arabia", "Iraq", "United Arab Emirates", "Kuwait",
    "Qatar", "Iran", "Bahrain",
]
MIDDLE_EAST_EXPORTERS = HORMUZ_EXPORTERS + ["Oman"]
ORIGIN_GROUPS = {
    "Saudi Arabia": ["Saudi Arabia"],
    "Iraq": ["Iraq"],
    "UAE": ["United Arab Emirates"],
    "Kuwait": ["Kuwait"],
    "Other Hormuz-region": ["Qatar", "Iran", "Bahrain"],
    "Oman": ["Oman"],
}
COLORS = [
    "#A6532D", "#D77A3D", "#E7A34B", "#F2C66D",
    "#7B6E5D", "#4E8A67", "#C9CDD2",
]

TRADE_SOURCE_NOTE = "Source: UN Comtrade, HS 2709 crude imports, 2024."
ENERGY_SOURCE_NOTE = "Source: Energy Institute, Statistical Review of World Energy 2025."


def save_chart(fig, filename, note, source_note, bottom=0.10, right=0.98):
    fig.text(0.5, 0.025, source_note, ha="center", fontsize=8.5, color="#555555")
    fig.text(0.5, 0.007, note, ha="center", fontsize=8.5, color="#555555")
    fig.tight_layout(rect=[0.02, bottom, right, 0.95])
    fig.savefig(FIGURES_DIR / filename, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ============================================================
# A. Exporter-origin shares
# ============================================================

trade = pd.read_csv(TRADE_FILE, encoding="latin1", index_col=False, low_memory=False)
trade["refYear"] = pd.to_numeric(trade["refYear"], errors="coerce")
trade["cmdCode"] = trade["cmdCode"].astype(str).str.replace(r"\.0$", "", regex=True)
trade["netWgt"] = pd.to_numeric(trade["netWgt"], errors="coerce")
trade["primaryValue"] = pd.to_numeric(trade["primaryValue"], errors="coerce")

trade = trade[
    (trade["refYear"] == YEAR)
    & (trade["flowDesc"] == "Import")
    & (trade["cmdCode"] == "2709")
    & (trade["reporterDesc"].isin(REPORTERS))
].copy()

partner_rows = trade[trade["partnerDesc"] != "World"].copy()
summary_rows = []
mix_rows = []

for reporter in REPORTERS:
    country = partner_rows[partner_rows["reporterDesc"] == reporter]
    net_weight_total = country["netWgt"].sum(min_count=1)

    if pd.notna(net_weight_total) and net_weight_total > 0:
        metric = "netWgt"
        metric_label = "net weight"
    else:
        metric = "primaryValue"
        metric_label = "trade value"

    by_partner = country.groupby("partnerDesc")[metric].sum(min_count=1).dropna()
    total = by_partner.sum(min_count=1)
    if pd.isna(total) or total <= 0:
        continue

    hormuz_amount = by_partner.reindex(HORMUZ_EXPORTERS).fillna(0).sum()
    middle_east_amount = by_partner.reindex(MIDDLE_EAST_EXPORTERS).fillna(0).sum()
    hormuz_share = hormuz_amount / total * 100
    middle_east_share = middle_east_amount / total * 100

    group_shares = {}
    for group, partners in ORIGIN_GROUPS.items():
        amount = by_partner.reindex(partners).fillna(0).sum()
        group_shares[group] = amount / total * 100

    display_name = DISPLAY_NAMES.get(reporter, reporter)
    group_shares["Other origins"] = max(100 - middle_east_share, 0)
    group_shares["Reporter"] = display_name
    mix_rows.append(group_shares)

    summary_rows.append({
        "Reporter": display_name,
        "Selected Middle East exporter-origin share (%)": middle_east_share,
        "Selected Hormuz-region exporter-origin share (%)": hormuz_share,
        "Difference (percentage points)": middle_east_share - hormuz_share,
        "Metric": metric_label,
    })

origin_summary = pd.DataFrame(summary_rows).sort_values(
    "Selected Hormuz-region exporter-origin share (%)"
)
origin_mix = pd.DataFrame(mix_rows).set_index("Reporter").reindex(origin_summary["Reporter"])

# Check whether partner rows approximately equal Comtrade's separate World row
coverage_rows = []
for reporter in REPORTERS:
    country = trade[trade["reporterDesc"] == reporter]
    partners = country[country["partnerDesc"] != "World"]
    world = country[country["partnerDesc"] == "World"]

    partner_weight = partners["netWgt"].sum(min_count=1)
    world_weight = world["netWgt"].sum(min_count=1)

    if pd.notna(partner_weight) and pd.notna(world_weight) and world_weight > 0:
        metric = "net weight"
        partner_total = partner_weight
        world_total = world_weight
    else:
        metric = "trade value"
        partner_total = partners["primaryValue"].sum(min_count=1)
        world_total = world["primaryValue"].sum(min_count=1)

    coverage = partner_total / world_total * 100 if world_total > 0 else float("nan")
    if pd.isna(coverage):
        status = "not available"
    elif abs(coverage - 100) <= 1:
        status = "OK (within 1%)"
    else:
        status = "review difference"

    coverage_rows.append({
        "Reporter": DISPLAY_NAMES.get(reporter, reporter),
        "Check metric": metric,
        "Partner rows / World row (%)": coverage,
        "Coverage check": status,
    })

coverage_table = pd.DataFrame(coverage_rows)


# ============================================================
# B. Domestic supply-gap proxy
# ============================================================

energy = pd.read_csv(ENERGY_FILE)
selected_energy = energy[
    (energy["Year"] == YEAR)
    & (energy["Country"].isin(ENERGY_COUNTRIES))
    & (energy["Var"].isin(["oilprod_kbd", "oilcons_kbd"]))
]

supply_gap = selected_energy.pivot(index="Country", columns="Var", values="Value")
supply_gap = supply_gap.rename(
    columns={"oilprod_kbd": "Production (kbd)", "oilcons_kbd": "Consumption (kbd)"}
)
supply_gap["Reporter"] = supply_gap.index.map(ENERGY_COUNTRIES)
supply_gap["Reporter"] = supply_gap["Reporter"].replace(DISPLAY_NAMES)
supply_gap = supply_gap.dropna(
    subset=["Production (kbd)", "Consumption (kbd)"]
).copy()
supply_gap["Domestic supply gap proxy (%)"] = (
    (supply_gap["Consumption (kbd)"] - supply_gap["Production (kbd)"]).clip(lower=0)
    / supply_gap["Consumption (kbd)"]
    * 100
)
supply_gap = supply_gap.sort_values("Domestic supply gap proxy (%)")

print("Selected exporter-origin shares of reported crude imports, 2024:")
print(origin_summary.round(1).to_string(index=False))
print("\nExporter-origin composition (%):")
print(origin_mix.round(1).to_string())
print("\nPartner-row coverage check against the Comtrade World row:")
print(coverage_table.round(1).to_string(index=False))
print("\nDomestic supply-gap proxy (reported production values only):")
print(
    supply_gap[
        ["Reporter", "Production (kbd)", "Consumption (kbd)", "Domestic supply gap proxy (%)"]
    ].round(1).to_string(index=False)
)
print("\nCaution: exporter origin does not establish physical passage through Hormuz.")
print("The supply-gap proxy is not observed gross import dependence.")

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# C. Figures 08-12
# ============================================================

# Figure 08
fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.barh(
    origin_summary["Reporter"],
    origin_summary["Selected Hormuz-region exporter-origin share (%)"],
    color="#C65D3A",
)
ax.bar_label(
    bars,
    labels=[
        f"{value:.1f}%"
        for value in origin_summary["Selected Hormuz-region exporter-origin share (%)"]
    ],
    padding=4,
)
ax.set_title("Selected Hormuz-region exporter origins of crude imports, 2024")
ax.set_xlabel("Share of reported crude-import partner total (%)")
ax.set_ylabel("")
ax.set_xlim(0, 105)
ax.grid(axis="x", alpha=0.2)
ax.spines[["top", "right", "left"]].set_visible(False)
save_chart(
    fig,
    "08_hormuz_exporter_origin_share_2024.png",
    "Exporter origin is a screening proxy; it does not show the cargo's actual route.",
    TRADE_SOURCE_NOTE,
)

# Figure 09
fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.barh(
    origin_summary["Reporter"],
    origin_summary["Selected Middle East exporter-origin share (%)"],
    color="#D77A3D",
)
ax.bar_label(
    bars,
    labels=[
        f"{value:.1f}%"
        for value in origin_summary["Selected Middle East exporter-origin share (%)"]
    ],
    padding=4,
)
ax.set_title("Selected Middle East exporter origins of crude imports, 2024")
ax.set_xlabel("Share of reported crude-import partner total (%)")
ax.set_ylabel("")
ax.set_xlim(0, 105)
ax.grid(axis="x", alpha=0.2)
ax.spines[["top", "right", "left"]].set_visible(False)
save_chart(
    fig,
    "09_middle_east_exporter_origin_share_2024.png",
    "The selected group adds Oman; exporter origin does not identify the vessel route.",
    TRADE_SOURCE_NOTE,
)

# Figure 10
fig, ax = plt.subplots(figsize=(10.5, 6.0))
positions = list(range(len(origin_summary)))
middle_east_positions = [position + 0.19 for position in positions]
hormuz_positions = [position - 0.19 for position in positions]

middle_east_bars = ax.barh(
    middle_east_positions,
    origin_summary["Selected Middle East exporter-origin share (%)"],
    height=0.36,
    label="Selected Middle East exporters",
    color="#D77A3D",
)
hormuz_bars = ax.barh(
    hormuz_positions,
    origin_summary["Selected Hormuz-region exporter-origin share (%)"],
    height=0.36,
    label="Selected Hormuz-region exporters",
    color="#4E8A67",
)
ax.bar_label(middle_east_bars, fmt="%.1f%%", padding=3, fontsize=8)
ax.bar_label(hormuz_bars, fmt="%.1f%%", padding=3, fontsize=8)
ax.set_yticks(positions, origin_summary["Reporter"])
ax.set_title("Selected Middle East vs Hormuz-region exporter origins, 2024")
ax.set_xlabel("Share of reported crude-import partner total (%)")
ax.set_ylabel("")
ax.set_xlim(0, 105)
ax.grid(axis="x", alpha=0.2)
ax.legend(frameon=False, loc="lower right")
ax.spines[["top", "right", "left"]].set_visible(False)
save_chart(
    fig,
    "10_middle_east_vs_hormuz_origin_share_2024.png",
    "Origin is not vessel route. The Hormuz-region group excludes Oman; bypass routes also exist.",
    TRADE_SOURCE_NOTE,
)

# Figure 11
fig, ax = plt.subplots(figsize=(12.5, 6.2))
left = pd.Series(0.0, index=origin_mix.index)
columns = list(ORIGIN_GROUPS) + ["Other origins"]

for column, color in zip(columns, COLORS):
    bars = ax.barh(
        origin_mix.index,
        origin_mix[column],
        left=left,
        label=column,
        color=color,
    )
    labels = [f"{value:.0f}%" if value >= 5 else "" for value in origin_mix[column]]
    ax.bar_label(bars, labels=labels, label_type="center", fontsize=8)
    left = left + origin_mix[column]

ax.set_title("Exporter mix of reported crude imports, 2024")
ax.set_xlabel("Share of reported crude-import partner total (%)")
ax.set_ylabel("")
ax.set_xlim(0, 100)
ax.legend(ncol=1, frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5))
ax.spines[["top", "right", "left"]].set_visible(False)
save_chart(
    fig,
    "11_crude_import_exporter_mix_2024.png",
    "Origin categories do not prove physical transit through the Strait of Hormuz.",
    TRADE_SOURCE_NOTE,
    right=0.80,
)

# Figure 12
fig, ax = plt.subplots(figsize=(9.5, 5.3))
bars = ax.barh(
    supply_gap["Reporter"],
    supply_gap["Domestic supply gap proxy (%)"],
    color="#2962A3",
)
ax.bar_label(
    bars,
    labels=[f"{value:.1f}%" for value in supply_gap["Domestic supply gap proxy (%)"]],
    padding=4,
)
ax.set_title("Domestic oil supply-gap proxy, 2024")
ax.set_xlabel("Positive production shortfall as share of oil consumption (%)")
ax.set_ylabel("")
ax.set_xlim(0, 105)
ax.grid(axis="x", alpha=0.2)
ax.spines[["top", "right", "left"]].set_visible(False)
save_chart(
    fig,
    "12_domestic_supply_gap_proxy_2024.png",
    "Only markets with reported production and consumption are shown; this is not gross import dependence.",
    ENERGY_SOURCE_NOTE,
)
