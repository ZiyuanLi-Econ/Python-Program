"""Q3: compare the 2024 energy mix of selected economies and markets.

``Total EU`` is a regional aggregate in the source data, not a country.  It is
kept in the comparison because it is a useful market benchmark, and is labelled
as such in the generated figures.
"""

from pathlib import Path
from typing import Sequence

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PROJECT_DIR.parent
DATA_FILE = (
    PROJECT_ROOT
    / "data_raw"
    / "Statistical Review of World Energy Narrow format.csv"
)
TABLES_DIR = PROJECT_DIR / "tables"
FIGURES_DIR = PROJECT_DIR / "figures"

YEAR = 2024

ECONOMIES = (
    "China",
    "US",
    "India",
    "Japan",
    "South Korea",
    "Germany",
    "Total EU",
)

ENERGY_VARS = (
    "tes_ej",
    "oilcons_ej",
    "gascons_ej",
    "coalcons_ej",
    "nuclear_ej",
    "renewables_ej",
)

SOURCE_VARS = (
    "oilcons_ej",
    "gascons_ej",
    "coalcons_ej",
    "nuclear_ej",
    "renewables_ej",
)

ENERGY_LABELS = {
    "oilcons_ej": "Oil",
    "gascons_ej": "Natural gas",
    "coalcons_ej": "Coal",
    "nuclear_ej": "Nuclear",
    "renewables_ej": "Renewables",
}

PLOT_ECONOMY_LABELS = {
    "Total EU": "Total EU (regional aggregate)",
}

REQUIRED_COLUMNS = {"Country", "Year", "Var", "Value"}
KEY_COLUMNS = ["Country", "Year", "Var"]


def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the source data without creating outputs or importing plotting tools."""

    if not path.is_file():
        raise FileNotFoundError(f"Energy data file not found: {path}")
    return pd.read_csv(path)


def validate_data(
    df: pd.DataFrame,
    year: int = YEAR,
    economies: Sequence[str] = ECONOMIES,
    variables: Sequence[str] = ENERGY_VARS,
) -> None:
    """Fail fast when the requested comparison cannot be calculated reliably."""

    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    numeric_year = pd.to_numeric(df["Year"], errors="coerce")
    year_data = df.loc[numeric_year.eq(year)].copy()
    available_economies = set(year_data["Country"].dropna())
    missing_economies = [name for name in economies if name not in available_economies]

    scoped = year_data.loc[
        year_data["Country"].isin(economies)
        & year_data["Var"].isin(variables),
        ["Country", "Year", "Var", "Value"],
    ].copy()

    available_variables = set(scoped["Var"].dropna())
    missing_variables = [var for var in variables if var not in available_variables]

    present_pairs = set(zip(scoped["Country"], scoped["Var"]))
    missing_by_economy = {
        economy: [var for var in variables if (economy, var) not in present_pairs]
        for economy in economies
    }
    missing_by_economy = {
        economy: vars_missing
        for economy, vars_missing in missing_by_economy.items()
        if vars_missing and economy in available_economies
    }

    duplicate_keys = (
        scoped.loc[scoped.duplicated(KEY_COLUMNS, keep=False), KEY_COLUMNS]
        .drop_duplicates()
        .to_dict("records")
    )

    numeric_values = pd.to_numeric(scoped["Value"], errors="coerce")
    invalid_value_rows = scoped.loc[
        numeric_values.isna(), ["Country", "Year", "Var"]
    ].to_dict("records")

    total_supply_rows = scoped.loc[scoped["Var"].eq("tes_ej")].copy()
    total_supply_values = pd.to_numeric(
        total_supply_rows["Value"], errors="coerce"
    )
    invalid_totals = total_supply_rows.loc[
        total_supply_values.isna() | total_supply_values.le(0),
        ["Country", "Year", "Value"],
    ].to_dict("records")

    problems = []
    if missing_economies:
        problems.append(f"missing economies/markets for {year}: {missing_economies}")
    if missing_variables:
        problems.append(f"missing variables for {year}: {missing_variables}")
    if missing_by_economy:
        problems.append(
            "missing economy-variable observations: "
            f"{missing_by_economy}"
        )
    if duplicate_keys:
        problems.append(f"duplicate Country-Year-Var keys: {duplicate_keys}")
    if invalid_value_rows:
        problems.append(
            "non-numeric or missing values in required observations: "
            f"{invalid_value_rows}"
        )
    if invalid_totals:
        problems.append(
            "total energy supply (tes_ej) must be non-missing and greater than "
            f"zero: {invalid_totals}"
        )

    if problems:
        details = "\n- ".join(problems)
        raise ValueError(f"Data validation failed:\n- {details}")


def select_data(
    df: pd.DataFrame,
    year: int = YEAR,
    economies: Sequence[str] = ECONOMIES,
    variables: Sequence[str] = ENERGY_VARS,
) -> pd.DataFrame:
    """Select and order the observations used in the Q3 comparison."""

    numeric_year = pd.to_numeric(df["Year"], errors="coerce")
    selected = df.loc[
        numeric_year.eq(year)
        & df["Country"].isin(economies)
        & df["Var"].isin(variables),
        ["Country", "Year", "Var", "Value"],
    ].copy()
    selected["Year"] = year
    selected["Value"] = pd.to_numeric(selected["Value"], errors="raise")

    economy_order = {name: position for position, name in enumerate(economies)}
    variable_order = {name: position for position, name in enumerate(variables)}
    selected["_economy_order"] = selected["Country"].map(economy_order)
    selected["_variable_order"] = selected["Var"].map(variable_order)
    selected = selected.sort_values(["_economy_order", "_variable_order"])
    return selected.drop(columns=["_economy_order", "_variable_order"])


def pivot_data(
    selected: pd.DataFrame,
    economies: Sequence[str] = ECONOMIES,
    variables: Sequence[str] = ENERGY_VARS,
) -> pd.DataFrame:
    """Pivot validated long-form observations to one row per economy/market."""

    amount_table = selected.pivot(
        index="Country", columns="Var", values="Value"
    )
    return amount_table.reindex(index=economies, columns=variables)


def calculate_shares(amount_table: pd.DataFrame) -> pd.DataFrame:
    """Calculate each source as a percentage of total energy supply."""

    required = {"tes_ej", *SOURCE_VARS}
    missing_columns = sorted(required.difference(amount_table.columns))
    if missing_columns:
        raise ValueError(f"Amount table is missing variables: {missing_columns}")

    total_supply = pd.to_numeric(amount_table["tes_ej"], errors="coerce")
    invalid_totals = total_supply.isna() | total_supply.le(0)
    if invalid_totals.any():
        invalid_economies = amount_table.index[invalid_totals].tolist()
        raise ValueError(
            "Total energy supply (tes_ej) must be non-missing and greater than "
            f"zero for: {invalid_economies}"
        )

    source_columns = list(SOURCE_VARS)
    share_table = amount_table.loc[:, source_columns].div(total_supply, axis=0) * 100
    share_table["share_sum"] = share_table.loc[:, source_columns].sum(axis=1)
    return share_table


def build_summary(
    share_table: pd.DataFrame,
) -> tuple[pd.Series, pd.DataFrame]:
    """Build the oil-share ranking and dominant-source summary."""

    oil_share_rank = share_table["oilcons_ej"].sort_values(ascending=False)
    oil_share_rank.name = "oil_share_pct"

    source_shares = share_table.loc[:, list(SOURCE_VARS)]
    main_energy_table = pd.DataFrame(
        {
            "main_energy_source": source_shares.idxmax(axis=1).map(ENERGY_LABELS),
            "main_energy_share": source_shares.max(axis=1),
        }
    )
    return oil_share_rank, main_energy_table


def save_tables(
    amount_table: pd.DataFrame,
    share_table: pd.DataFrame,
    main_energy_table: pd.DataFrame,
    output_dir: Path = TABLES_DIR,
) -> tuple[Path, Path, Path]:
    """Save the three CSV outputs using the original ordinary-version names."""

    output_dir.mkdir(parents=True, exist_ok=True)
    amount_path = output_dir / "q3_country_energy_amount_2024.csv"
    share_path = output_dir / "q3_country_energy_share_2024.csv"
    main_source_path = output_dir / "q3_main_energy_source_2024.csv"

    amount_table.to_csv(amount_path)
    share_table.to_csv(share_path)
    main_energy_table.to_csv(main_source_path)
    return amount_path, share_path, main_source_path


def plot_results(
    amount_table: pd.DataFrame,
    share_table: pd.DataFrame,
    output_dir: Path = FIGURES_DIR,
) -> tuple[Path, ...]:
    """Save Q3 figures; return no paths when matplotlib is unavailable."""

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nMatplotlib is not installed; tables were calculated but plots skipped.")
        return ()

    output_dir.mkdir(parents=True, exist_ok=True)

    total_path = output_dir / "q3_total_energy_supply_2024.png"
    amount_path = output_dir / "q3_energy_amount_by_source_2024.png"
    share_path = output_dir / "q3_energy_mix_share_2024.png"

    plot_index = {
        economy: PLOT_ECONOMY_LABELS.get(economy, economy)
        for economy in amount_table.index
    }
    total_plot = amount_table["tes_ej"].rename(index=plot_index)
    amount_plot = (
        amount_table.loc[:, list(SOURCE_VARS)]
        .rename(index=plot_index)
        .rename(columns=ENERGY_LABELS)
    )
    share_plot = (
        share_table.loc[:, list(SOURCE_VARS)]
        .rename(index=plot_index)
        .rename(columns=ENERGY_LABELS)
    )

    def save_bar_chart(
        data: pd.Series | pd.DataFrame,
        path: Path,
        title: str,
        ylabel: str,
        *,
        stacked: bool = False,
    ) -> None:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        try:
            data.plot(
                kind="bar",
                stacked=stacked,
                ax=ax,
                color="steelblue" if isinstance(data, pd.Series) else None,
                legend=isinstance(data, pd.DataFrame),
            )
            ax.set_title(title)
            ax.set_xlabel("Economy / market")
            ax.set_ylabel(ylabel)
            ax.tick_params(axis="x", rotation=45)
            for label in ax.get_xticklabels():
                label.set_ha("right")
            if isinstance(data, pd.DataFrame):
                ax.legend(
                    title="Energy type",
                    bbox_to_anchor=(1.02, 1),
                    loc="upper left",
                )
            fig.tight_layout()
            fig.savefig(path, dpi=300, bbox_inches="tight")
        finally:
            plt.close(fig)

    save_bar_chart(
        total_plot,
        total_path,
        "Total Energy Supply by Economy/Market, 2024",
        "Total energy supply (EJ)",
    )
    save_bar_chart(
        amount_plot,
        amount_path,
        "Energy Consumption by Source and Economy/Market, 2024",
        "Energy consumption (EJ)",
        stacked=True,
    )
    save_bar_chart(
        share_plot,
        share_path,
        "Energy Mix Share by Economy/Market, 2024",
        "Share of total energy supply (%)",
        stacked=True,
    )
    return total_path, amount_path, share_path


def main(make_plots: bool = True) -> None:
    """Run the validated Q3 analysis and save its existing outputs."""

    data = load_data()
    validate_data(data)
    selected = select_data(data)
    amount_table = pivot_data(selected)
    share_table = calculate_shares(amount_table)
    oil_share_rank, main_energy_table = build_summary(share_table)

    save_tables(amount_table, share_table, main_energy_table)
    if make_plots:
        plot_results(amount_table, share_table)

    print("\nEnergy amount table, EJ:")
    print(amount_table)
    print("\nEnergy share table, %:")
    print(share_table)
    print("\nOil share ranking, %:")
    print(oil_share_rank)
    print("\nMain energy source by economy/market:")
    print(main_energy_table)
    print("\nNote: 'Total EU' is a regional aggregate, not a country.")
    print(f"\nTables saved to: {TABLES_DIR}")
    if make_plots:
        print(f"Figures directory: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
