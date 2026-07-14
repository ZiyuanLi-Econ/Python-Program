"""Q4: domestic oil supply gaps and origin-based Hormuz exposure proxies.

This script deliberately keeps two concepts separate:

1. Production minus consumption is a domestic supply-gap proxy.  It is not a
   direct measure of gross imports or import dependency because inventories,
   product trade, and other balance items are not modelled.
2. The share imported from selected exporters is an origin-based proxy.  An
   exporter's location does not prove that its cargo physically transited the
   Strait of Hormuz; Saudi Arabia and the UAE, for example, have bypass routes.

Run ``python oil_import_exposure.py`` to save tables and (when matplotlib is
installed) figures. Use ``python oil_import_exposure.py --no-plots`` for a
data-only run.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data_raw"
TABLES_DIR = SCRIPT_DIR / "tables"
FIGURES_DIR = SCRIPT_DIR / "figures"

ENERGY_FILE = DATA_DIR / "Statistical Review of World Energy Narrow format.csv"
TRADE_FILE = DATA_DIR / "TradeData.csv"
ANALYSIS_YEAR = 2024
CRUDE_OIL_HS_CODE = "2709"

ENERGY_COUNTRIES = [
    "US",
    "China",
    "Germany",
    "Total EU",
    "Japan",
    "India",
    "South Korea",
]
COUNTRY_NAME_MAP = {
    "US": "USA",
    "Total EU": "European Union",
    "South Korea": "Rep. of Korea",
}
TRADE_COUNTRIES = [
    "USA",
    "China",
    "Germany",
    "European Union",
    "Japan",
    "India",
    "Rep. of Korea",
]

MIDDLE_EAST_EXPORTERS = [
    "Saudi Arabia",
    "Iraq",
    "United Arab Emirates",
    "Kuwait",
    "Qatar",
    "Iran",
    "Oman",
    "Bahrain",
]
HORMUZ_RELATED_EXPORTERS = [
    "Saudi Arabia",
    "Iraq",
    "United Arab Emirates",
    "Kuwait",
    "Qatar",
    "Iran",
    "Bahrain",
]

ORIGIN_PROXY_NOTE = (
    "Exporter origin proxy only; it does not establish that cargo physically "
    "transited the Strait of Hormuz."
)
SUPPLY_GAP_NOTE = (
    "Production-consumption balance proxy; it is not observed gross imports "
    "or a complete oil balance."
)


def require_columns(data: pd.DataFrame, required: set[str], dataset_name: str) -> None:
    """Raise a clear error when a source file does not contain expected columns."""

    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {sorted(missing)}"
        )


def load_energy_data(path: Path = ENERGY_FILE) -> pd.DataFrame:
    """Load and validate the Energy Institute narrow-format data."""

    data = pd.read_csv(path)
    require_columns(data, {"Country", "Year", "Var", "Value"}, path.name)
    return data


def load_trade_data(path: Path = TRADE_FILE) -> pd.DataFrame:
    """Load and validate UN Comtrade data.

    ``index_col=False`` is intentional: the downloaded CSV has a trailing field,
    and without this argument pandas can shift the columns during parsing.
    """

    data = pd.read_csv(path, encoding="latin1", index_col=False)
    required = {
        "refYear",
        "reporterDesc",
        "partnerDesc",
        "cmdCode",
        "flowDesc",
        "netWgt",
        "primaryValue",
    }
    require_columns(data, required, path.name)
    return data


def _single_value(
    data: pd.DataFrame, country: str, variable: str
) -> float | None:
    """Return one numeric observation, rejecting conflicting duplicates."""

    values = pd.to_numeric(
        data.loc[
            data["Country"].eq(country) & data["Var"].eq(variable), "Value"
        ],
        errors="coerce",
    ).dropna()

    unique_values = values.unique()
    if len(unique_values) == 0:
        return None
    if len(unique_values) > 1:
        raise ValueError(
            f"Multiple {variable} values found for {country}: "
            f"{unique_values.tolist()}"
        )
    return float(unique_values[0])


def build_supply_gap_table(
    energy_data: pd.DataFrame,
    year: int = ANALYSIS_YEAR,
    production_assumptions: Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """Build a production-consumption gap proxy without silently filling data.

    Missing production remains missing by default.  A caller may provide an
    explicit assumption keyed by the Energy Institute country name; those rows
    are clearly flagged in the output.
    """

    assumptions = dict(production_assumptions or {})
    unknown_assumptions = set(assumptions).difference(ENERGY_COUNTRIES)
    if unknown_assumptions:
        raise ValueError(
            "Production assumptions contain unknown countries: "
            f"{sorted(unknown_assumptions)}"
        )
    if any(value < 0 for value in assumptions.values()):
        raise ValueError("Production assumptions must be non-negative.")

    year_values = pd.to_numeric(energy_data["Year"], errors="coerce")
    selected = energy_data.loc[
        year_values.eq(year)
        & energy_data["Country"].isin(ENERGY_COUNTRIES)
        & energy_data["Var"].isin(["oilprod_kbd", "oilcons_kbd"])
    ].copy()
    duplicate_keys = selected.duplicated(
        ["Country", "Year", "Var"], keep=False
    )
    if duplicate_keys.any():
        examples = (
            selected.loc[duplicate_keys, ["Country", "Year", "Var"]]
            .drop_duplicates()
            .head(5)
            .to_dict("records")
        )
        raise ValueError(
            "Energy data contains duplicate Country-Year-Var records in the "
            f"Q4 scope. Example keys: {examples}"
        )

    rows: list[dict[str, object]] = []
    for source_country in ENERGY_COUNTRIES:
        production = _single_value(selected, source_country, "oilprod_kbd")
        consumption = _single_value(selected, source_country, "oilcons_kbd")
        assumption_used = False

        if production is None and source_country in assumptions:
            production = float(assumptions[source_country])
            production_status = "explicit_assumption"
            assumption_used = True
        elif production is None:
            production_status = "missing_not_assumed"
        else:
            production_status = "reported"

        if consumption is None:
            consumption_status = "missing"
        elif consumption <= 0:
            consumption_status = "invalid_nonpositive"
        else:
            consumption_status = "reported"

        if production is not None and consumption is not None and consumption > 0:
            balance = production - consumption
            gap = max(consumption - production, 0.0)
            gap_pct = gap / consumption * 100
            proxy_status = (
                "calculated_with_explicit_production_assumption"
                if assumption_used
                else "calculated_reported_data"
            )
        else:
            balance = float("nan")
            gap = float("nan")
            gap_pct = float("nan")
            if production is None:
                proxy_status = "not_calculated_missing_production"
            else:
                proxy_status = "not_calculated_missing_or_invalid_consumption"

        rows.append(
            {
                "year": year,
                "country_name": COUNTRY_NAME_MAP.get(source_country, source_country),
                "energy_data_country_name": source_country,
                "oil_production_kbd": production,
                "oil_consumption_kbd": consumption,
                "production_data_status": production_status,
                "production_assumption_used": assumption_used,
                "consumption_data_status": consumption_status,
                "domestic_supply_balance_kbd": balance,
                "domestic_supply_gap_proxy_kbd": gap,
                "domestic_supply_gap_proxy_pct_of_consumption": gap_pct,
                "supply_gap_proxy_status": proxy_status,
                "supply_gap_method_note": SUPPLY_GAP_NOTE,
            }
        )

    return pd.DataFrame(rows).sort_values(
        "domestic_supply_gap_proxy_pct_of_consumption",
        ascending=False,
        na_position="last",
    )


def select_trade_scope(
    trade_data: pd.DataFrame, year: int = ANALYSIS_YEAR
) -> pd.DataFrame:
    """Select annual crude-oil imports for the reporters in this analysis."""

    selected = trade_data[
        [
            "refYear",
            "reporterDesc",
            "partnerDesc",
            "cmdCode",
            "flowDesc",
            "netWgt",
            "primaryValue",
        ]
    ].copy()
    selected["refYear"] = pd.to_numeric(selected["refYear"], errors="coerce")
    selected["netWgt"] = pd.to_numeric(selected["netWgt"], errors="coerce")
    selected["primaryValue"] = pd.to_numeric(
        selected["primaryValue"], errors="coerce"
    )
    command_code = selected["cmdCode"].astype(str).str.replace(
        r"\.0$", "", regex=True
    )

    selected = selected.loc[
        selected["refYear"].eq(year)
        & selected["flowDesc"].eq("Import")
        & command_code.eq(CRUDE_OIL_HS_CODE)
        & selected["reporterDesc"].isin(TRADE_COUNTRIES)
    ].copy()
    if selected.empty:
        raise ValueError(
            f"No HS {CRUDE_OIL_HS_CODE} import records found for {year}."
        )
    return selected


def _sum_or_nan(values: pd.Series) -> float:
    """Sum numeric data, returning NaN rather than zero when all values are missing."""

    return float(values.sum(min_count=1))


def build_import_source_table(trade_scope: pd.DataFrame) -> pd.DataFrame:
    """Calculate exporter-origin shares from non-World partner rows.

    Net weight is preferred.  Primary value is used only when a reporter has no
    usable partner net weights, and the selected metric is recorded by country.
    """

    partner_rows = trade_scope.loc[trade_scope["partnerDesc"].ne("World")].copy()
    partner_rows = (
        partner_rows.groupby(
            ["refYear", "reporterDesc", "partnerDesc"], as_index=False
        )
        .agg(netWgt=("netWgt", _sum_or_nan), primaryValue=("primaryValue", _sum_or_nan))
    )

    output_parts: list[pd.DataFrame] = []
    for country in TRADE_COUNTRIES:
        country_data = partner_rows.loc[
            partner_rows["reporterDesc"].eq(country)
        ].copy()
        weight_total = country_data["netWgt"].sum(min_count=1)
        value_total = country_data["primaryValue"].sum(min_count=1)

        if pd.notna(weight_total) and weight_total > 0:
            metric = "netWgt"
            denominator = float(weight_total)
        elif pd.notna(value_total) and value_total > 0:
            metric = "primaryValue"
            denominator = float(value_total)
        else:
            continue

        country_data["origin_share_pct"] = (
            country_data[metric] / denominator * 100
        )
        country_data["origin_share_metric"] = metric
        country_data["origin_share_denominator"] = denominator
        output_parts.append(country_data)

    if not output_parts:
        raise ValueError("No usable non-World trade partner rows were found.")

    sources = pd.concat(output_parts, ignore_index=True).rename(
        columns={
            "refYear": "year",
            "reporterDesc": "country_name",
            "partnerDesc": "partner_name",
            "netWgt": "net_weight_kg",
            "primaryValue": "primary_value_usd",
        }
    )
    sources["is_middle_east_origin"] = sources["partner_name"].isin(
        MIDDLE_EAST_EXPORTERS
    )
    sources["is_hormuz_related_origin"] = sources["partner_name"].isin(
        HORMUZ_RELATED_EXPORTERS
    )
    sources["origin_proxy_method_note"] = ORIGIN_PROXY_NOTE

    return sources.sort_values(
        ["country_name", "origin_share_pct"], ascending=[True, False]
    )


def reconcile_partner_rows_with_world(
    trade_scope: pd.DataFrame,
    year: int = ANALYSIS_YEAR,
) -> pd.DataFrame:
    """Independently compare partner-row totals with Comtrade's World row.

    Net weight is preferred.  If the World-row net weight is missing, the
    comparison falls back to primary value.  This is a genuine reconciliation,
    unlike summing already-normalised partner shares back to 100%.
    """

    rows: list[dict[str, object]] = []
    for country in TRADE_COUNTRIES:
        country_data = trade_scope.loc[
            trade_scope["reporterDesc"].eq(country)
        ]
        partners = country_data.loc[country_data["partnerDesc"].ne("World")]
        world = country_data.loc[country_data["partnerDesc"].eq("World")]

        partner_weight = partners["netWgt"].sum(min_count=1)
        world_weight = world["netWgt"].sum(min_count=1)
        partner_value = partners["primaryValue"].sum(min_count=1)
        world_value = world["primaryValue"].sum(min_count=1)

        if (
            pd.notna(world_weight)
            and world_weight > 0
            and pd.notna(partner_weight)
        ):
            metric = "netWgt"
            partner_total = float(partner_weight)
            world_total = float(world_weight)
            metric_note = "preferred net weight comparison"
        elif (
            pd.notna(world_value)
            and world_value > 0
            and pd.notna(partner_value)
        ):
            metric = "primaryValue"
            partner_total = float(partner_value)
            world_total = float(world_value)
            metric_note = "fallback: World-row net weight unavailable"
        else:
            metric = "unavailable"
            partner_total = float("nan")
            world_total = float("nan")
            metric_note = "no comparable World and partner totals"

        if metric == "unavailable":
            coverage_ratio = float("nan")
            absolute_difference = float("nan")
            status = "not_reconcilable"
        else:
            coverage_ratio = partner_total / world_total
            absolute_difference = partner_total - world_total
            status = (
                "reconciled_within_1pct"
                if abs(coverage_ratio - 1) <= 0.01
                else "difference_over_1pct"
            )

        rows.append(
            {
                "year": year,
                "country_name": country,
                "reconciliation_metric": metric,
                "partner_rows_total": partner_total,
                "world_row_total": world_total,
                "partner_minus_world": absolute_difference,
                "coverage_ratio": coverage_ratio,
                "coverage_pct": coverage_ratio * 100,
                "coverage_status": status,
                "metric_selection_note": metric_note,
            }
        )

    return pd.DataFrame(rows)


def build_origin_share_summary(import_sources: pd.DataFrame) -> pd.DataFrame:
    """Summarise Middle East and Hormuz-related exporter-origin shares."""

    rows: list[dict[str, object]] = []
    for country in TRADE_COUNTRIES:
        country_data = import_sources.loc[
            import_sources["country_name"].eq(country)
        ]
        if country_data.empty:
            rows.append(
                {
                    "country_name": country,
                    "middle_east_origin_share_pct": float("nan"),
                    "origin_based_hormuz_related_share_pct": float("nan"),
                    "origin_share_metric": "unavailable",
                    "origin_share_data_status": "no_usable_partner_rows",
                    "origin_proxy_method_note": ORIGIN_PROXY_NOTE,
                }
            )
            continue

        rows.append(
            {
                "country_name": country,
                "middle_east_origin_share_pct": country_data.loc[
                    country_data["is_middle_east_origin"], "origin_share_pct"
                ].sum(),
                "origin_based_hormuz_related_share_pct": country_data.loc[
                    country_data["is_hormuz_related_origin"], "origin_share_pct"
                ].sum(),
                "origin_share_metric": country_data["origin_share_metric"].iloc[0],
                "origin_share_data_status": "calculated_from_partner_rows",
                "origin_proxy_method_note": ORIGIN_PROXY_NOTE,
            }
        )

    return pd.DataFrame(rows)


def build_combined_proxy_table(
    supply_gap: pd.DataFrame,
    origin_shares: pd.DataFrame,
    reconciliation: pd.DataFrame,
) -> pd.DataFrame:
    """Combine the two proxies only for rows with valid or explicit inputs."""

    combined = supply_gap.merge(origin_shares, on="country_name", how="left")
    combined = combined.merge(reconciliation, on=["year", "country_name"], how="left")

    gap_col = "domestic_supply_gap_proxy_pct_of_consumption"
    origin_col = "origin_based_hormuz_related_share_pct"
    combined_col = "combined_supply_gap_hormuz_origin_proxy_pct"
    valid = combined[gap_col].notna() & combined[origin_col].notna()
    combined[combined_col] = float("nan")
    combined.loc[valid, combined_col] = (
        combined.loc[valid, gap_col] * combined.loc[valid, origin_col] / 100
    )

    combined["combined_proxy_status"] = "not_calculated_missing_input"
    combined.loc[
        combined[gap_col].isna(), "combined_proxy_status"
    ] = "not_calculated_supply_gap_unavailable"
    combined.loc[
        combined[gap_col].notna() & combined[origin_col].isna(),
        "combined_proxy_status",
    ] = "not_calculated_origin_share_unavailable"
    combined.loc[
        valid & ~combined["production_assumption_used"], "combined_proxy_status"
    ] = "calculated_complete_reported_case"
    combined.loc[
        valid & combined["production_assumption_used"], "combined_proxy_status"
    ] = "calculated_with_explicit_production_assumption"

    return combined.sort_values(combined_col, ascending=False, na_position="last")


def save_tables(
    supply_gap: pd.DataFrame,
    import_sources: pd.DataFrame,
    origin_shares: pd.DataFrame,
    reconciliation: pd.DataFrame,
    combined: pd.DataFrame,
    year: int = ANALYSIS_YEAR,
) -> list[Path]:
    """Save one canonical, year-labelled copy of each Q4 output table."""

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    middle_east = origin_shares[
        [
            "country_name",
            "middle_east_origin_share_pct",
            "origin_share_metric",
            "origin_share_data_status",
        ]
    ]
    hormuz = origin_shares[
        [
            "country_name",
            "origin_based_hormuz_related_share_pct",
            "origin_share_metric",
            "origin_share_data_status",
            "origin_proxy_method_note",
        ]
    ]
    outputs = {
        TABLES_DIR / f"q4_oil_supply_gap_proxy_{year}.csv": supply_gap,
        TABLES_DIR / f"q4_crude_import_sources_{year}.csv": import_sources,
        TABLES_DIR / f"q4_middle_east_origin_share_{year}.csv": middle_east,
        TABLES_DIR / f"q4_hormuz_related_origin_share_{year}.csv": hormuz,
        TABLES_DIR / f"q4_trade_world_reconciliation_{year}.csv": reconciliation,
        TABLES_DIR / f"q4_supply_gap_origin_exposure_proxy_{year}.csv": combined,
    }
    for path, table in outputs.items():
        table.to_csv(path, index=False)
    return list(outputs)


def _finish_bar_chart(plt, ax, path: Path, horizontal: bool = False) -> None:
    """Apply common formatting, save, and close a chart without displaying it."""

    ax.grid(axis="x" if horizontal else "y", alpha=0.2)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def save_figures(combined: pd.DataFrame, year: int = ANALYSIS_YEAR) -> list[Path]:
    """Save Q4 figures; matplotlib is imported only when this function is called."""

    import matplotlib.pyplot as plt

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    gap_col = "domestic_supply_gap_proxy_pct_of_consumption"
    plot_data = combined.dropna(subset=[gap_col]).sort_values(gap_col)
    if not plot_data.empty:
        path = FIGURES_DIR / f"q4_domestic_supply_gap_proxy_{year}.png"
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.barh(plot_data["country_name"], plot_data[gap_col], color="steelblue")
        ax.bar_label(bars, labels=[f"{value:.1f}%" for value in plot_data[gap_col]], padding=3)
        ax.set_title(f"Domestic Oil Supply-Gap Proxy, {year}")
        ax.set_xlabel("Production shortfall as % of oil consumption")
        ax.set_ylabel("Country")
        _finish_bar_chart(plt, ax, path, horizontal=True)
        paths.append(path)

    origin_col = "origin_based_hormuz_related_share_pct"
    plot_data = combined.dropna(subset=[origin_col]).sort_values(origin_col)
    if not plot_data.empty:
        path = FIGURES_DIR / f"q4_origin_based_hormuz_related_share_{year}.png"
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.barh(plot_data["country_name"], plot_data[origin_col], color="#2CA25F")
        ax.bar_label(bars, labels=[f"{value:.1f}%" for value in plot_data[origin_col]], padding=3)
        ax.set_title(f"Origin-Based Hormuz-Related Share of Crude Imports, {year}")
        ax.set_xlabel("Share of reported partner imports")
        ax.set_ylabel("Country")
        ax.text(0, -0.18, ORIGIN_PROXY_NOTE, transform=ax.transAxes, fontsize=8)
        _finish_bar_chart(plt, ax, path, horizontal=True)
        paths.append(path)

    combined_col = "combined_supply_gap_hormuz_origin_proxy_pct"
    plot_data = combined.dropna(subset=[combined_col]).sort_values(combined_col)
    if not plot_data.empty:
        path = FIGURES_DIR / f"q4_combined_supply_gap_hormuz_origin_proxy_{year}.png"
        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.barh(plot_data["country_name"], plot_data[combined_col], color="darkorange")
        ax.bar_label(bars, labels=[f"{value:.1f}" for value in plot_data[combined_col]], padding=3)
        ax.set_title(f"Combined Supply-Gap and Exporter-Origin Proxy, {year}")
        ax.set_xlabel("Combined proxy (percentage points)")
        ax.set_ylabel("Country")
        _finish_bar_chart(plt, ax, path, horizontal=True)
        paths.append(path)

    return paths


def main(make_plots: bool = True) -> None:
    """Run Q4, print the core results, and save canonical outputs."""

    energy_data = load_energy_data()
    trade_data = load_trade_data()
    trade_scope = select_trade_scope(trade_data)

    supply_gap = build_supply_gap_table(energy_data)
    import_sources = build_import_source_table(trade_scope)
    reconciliation = reconcile_partner_rows_with_world(trade_scope)
    origin_shares = build_origin_share_summary(import_sources)
    combined = build_combined_proxy_table(
        supply_gap, origin_shares, reconciliation
    )
    table_paths = save_tables(
        supply_gap,
        import_sources,
        origin_shares,
        reconciliation,
        combined,
    )

    print("\nQ4 domestic oil supply-gap proxy:")
    print(
        supply_gap[
            [
                "country_name",
                "oil_production_kbd",
                "oil_consumption_kbd",
                "production_data_status",
                "domestic_supply_gap_proxy_pct_of_consumption",
                "supply_gap_proxy_status",
            ]
        ].to_string(index=False)
    )
    print("\nQ4 exporter-origin shares and combined proxy:")
    print(
        combined[
            [
                "country_name",
                "origin_based_hormuz_related_share_pct",
                "domestic_supply_gap_proxy_pct_of_consumption",
                "combined_supply_gap_hormuz_origin_proxy_pct",
                "combined_proxy_status",
            ]
        ].to_string(index=False)
    )
    print("\nUN Comtrade partner rows versus independent World rows:")
    print(
        reconciliation[
            [
                "country_name",
                "reconciliation_metric",
                "coverage_pct",
                "coverage_status",
            ]
        ].to_string(index=False)
    )
    print(f"\nMethod note: {SUPPLY_GAP_NOTE}")
    print(f"Method note: {ORIGIN_PROXY_NOTE}")
    print(f"Saved {len(table_paths)} tables to {TABLES_DIR}")

    if make_plots:
        try:
            figure_paths = save_figures(combined)
        except ModuleNotFoundError as error:
            if error.name and error.name.startswith("matplotlib"):
                print("matplotlib is not installed; tables were saved and plots skipped.")
            else:
                raise
        else:
            print(f"Saved {len(figure_paths)} figures to {FIGURES_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="save data tables without importing matplotlib",
    )
    arguments = parser.parse_args()
    main(make_plots=not arguments.no_plots)
