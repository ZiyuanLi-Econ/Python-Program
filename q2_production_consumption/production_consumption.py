"""Q2. Compare where energy is produced with where it is consumed.

The oil analysis is the main section.  Gas and coal are included as a short
extension, while nuclear and renewables are treated as domestic-use rankings.
Importing this module performs no file I/O and does not require matplotlib.
"""

from pathlib import Path

import pandas as pd


# File locations are relative to this script rather than one specific computer.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
Q2_DIR = Path(__file__).resolve().parent
TABLES_DIR = Q2_DIR / "tables"
FIGURES_DIR = Q2_DIR / "figures"

YEAR = 2024
REQUIRED_COLUMNS = {"Country", "Year", "Region", "SubRegion", "Var", "Value"}

COLOR_PRODUCTION = "#1B6F8A"
COLOR_CONSUMPTION = "#D9822B"

TRADEABLE_ENERGY_VARS = {
    "Natural gas": ("gasprod_ej", "gascons_ej"),
    "Coal": ("coalprod_ej", "coalcons_ej"),
}

DOMESTIC_USE_VARS = {
    "Nuclear": "nuclear_ej",
    "Renewables": "renewables_ej",
}


def load_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the Energy Institute narrow-format CSV."""
    if not data_path.exists():
        raise FileNotFoundError(f"Q2 data file not found: {data_path}")
    return pd.read_csv(data_path)


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate columns, numeric fields, and the Country-Year-Var key."""
    if data.empty:
        raise ValueError("Q2 input data is empty.")

    missing_columns = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing_columns:
        raise ValueError(f"Q2 input data is missing required columns: {missing_columns}")

    validated = data.copy()
    numeric_year = pd.to_numeric(validated["Year"], errors="coerce")
    if numeric_year.isna().any() or ((numeric_year % 1) != 0).any():
        raise ValueError("Q2 column 'Year' must contain integer years only.")
    validated["Year"] = numeric_year.astype(int)

    numeric_value = pd.to_numeric(validated["Value"], errors="coerce")
    if numeric_value.isna().any():
        bad_rows = validated.loc[numeric_value.isna(), ["Country", "Year", "Var"]].head(5)
        raise ValueError(
            "Q2 column 'Value' contains missing or non-numeric values. "
            f"Example keys: {bad_rows.to_dict('records')}"
        )
    validated["Value"] = numeric_value.astype(float)

    key_columns = ["Country", "Year", "Var"]
    duplicate_rows = validated.duplicated(key_columns, keep=False)
    if duplicate_rows.any():
        examples = validated.loc[duplicate_rows, key_columns].drop_duplicates().head(5)
        raise ValueError(
            "Q2 input contains duplicate Country-Year-Var records. "
            f"Example keys: {examples.to_dict('records')}"
        )

    return validated


def filter_country_series(
    data: pd.DataFrame,
    variable: str,
    value_column: str,
    year: int = YEAR,
) -> pd.DataFrame:
    """Select one annual series and remove official aggregate/other rows."""
    selected = data.loc[
        data["Year"].eq(year) & data["Var"].eq(variable),
        ["Country", "Region", "SubRegion", "Value"],
    ].copy()

    if selected.empty:
        raise ValueError(f"Q2 found no result for Year={year}, Var={variable!r}.")
    if selected["Country"].isna().any():
        raise ValueError(f"Q2 series {variable!r} contains rows without a country name.")

    # Aggregate rows would otherwise be mixed into country rankings and totals.
    is_aggregate = selected["Country"].str.startswith(("Total", "Other"), na=False)
    selected = selected.loc[~is_aggregate].copy()
    if selected.empty:
        raise ValueError(
            f"Q2 series {variable!r} has no country rows after aggregate rows are removed."
        )

    selected = selected.rename(columns={"Value": value_column})
    selected = selected.sort_values(value_column, ascending=False).reset_index(drop=True)
    return selected


def add_rank(table: pd.DataFrame, top_n: int) -> pd.DataFrame:
    """Return the first ``top_n`` rows with a one-based Rank column."""
    if table.empty:
        raise ValueError("Q2 cannot rank an empty table.")
    if top_n <= 0:
        raise ValueError("Q2 top_n must be greater than zero.")

    ranked = table.head(top_n).copy()
    ranked.insert(0, "Rank", range(1, len(ranked) + 1))
    return ranked


def build_oil_top10_comparison(
    production_top10: pd.DataFrame,
    consumption_top10: pd.DataFrame,
) -> pd.DataFrame:
    """Place the oil production and consumption rankings side by side."""
    if production_top10.empty or consumption_top10.empty:
        raise ValueError("Q2 cannot compare empty production or consumption rankings.")

    production = production_top10[
        ["Rank", "Country", "oilprod_kbd_value"]
    ].rename(
        columns={
            "Country": "Production_Top10_Country",
            "oilprod_kbd_value": "Production_kbd",
        }
    )
    consumption = consumption_top10[
        ["Rank", "Country", "oilcons_kbd_value"]
    ].rename(
        columns={
            "Country": "Consumption_Top10_Country",
            "oilcons_kbd_value": "Consumption_kbd",
        }
    )

    comparison = pd.merge(production, consumption, on="Rank", how="outer")
    comparison = comparison.sort_values("Rank").reset_index(drop=True)
    if comparison.empty:
        raise ValueError("Q2 oil Top 10 comparison returned no rows.")
    return comparison


def build_geographic_balance(
    production: pd.DataFrame,
    consumption: pd.DataFrame,
    group_column: str,
    production_value_column: str,
    consumption_value_column: str,
) -> pd.DataFrame:
    """Calculate production share, consumption share, and their gap by area."""
    if production.empty or consumption.empty:
        raise ValueError(f"Q2 cannot build a {group_column} balance from an empty table.")
    if group_column not in production.columns or group_column not in consumption.columns:
        raise ValueError(f"Q2 balance input is missing grouping column {group_column!r}.")
    if production[group_column].isna().any() or consumption[group_column].isna().any():
        raise ValueError(f"Q2 cannot group by {group_column}: some rows have no value.")

    production_by_area = production.groupby(group_column, as_index=False)[
        production_value_column
    ].sum()
    consumption_by_area = consumption.groupby(group_column, as_index=False)[
        consumption_value_column
    ].sum()

    balance = pd.merge(
        production_by_area,
        consumption_by_area,
        on=group_column,
        how="outer",
    )
    balance[[production_value_column, consumption_value_column]] = balance[
        [production_value_column, consumption_value_column]
    ].fillna(0)

    production_total = balance[production_value_column].sum()
    consumption_total = balance[consumption_value_column].sum()
    if production_total == 0:
        raise ValueError(
            f"Q2 cannot calculate {group_column} production shares: production total is zero."
        )
    if consumption_total == 0:
        raise ValueError(
            f"Q2 cannot calculate {group_column} consumption shares: consumption total is zero."
        )

    balance["production_share_percent"] = (
        balance[production_value_column] / production_total * 100
    )
    balance["consumption_share_percent"] = (
        balance[consumption_value_column] / consumption_total * 100
    )
    balance["share_gap_percent"] = (
        balance["production_share_percent"] - balance["consumption_share_percent"]
    )
    balance = balance.sort_values("share_gap_percent", ascending=False).reset_index(drop=True)

    if balance.empty:
        raise ValueError(f"Q2 {group_column} balance returned no rows.")
    return balance


def build_concentration_table(
    production: pd.DataFrame,
    consumption: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate the shares accounted for by the Top 3, 5, and 10 countries."""
    if production.empty or consumption.empty:
        raise ValueError("Q2 cannot calculate concentration from an empty table.")

    production_total = production["oilprod_kbd_value"].sum()
    consumption_total = consumption["oilcons_kbd_value"].sum()
    if production_total == 0:
        raise ValueError("Q2 cannot calculate oil concentration: production total is zero.")
    if consumption_total == 0:
        raise ValueError("Q2 cannot calculate oil concentration: consumption total is zero.")

    rows = []
    for top_n in (3, 5, 10):
        rows.append(
            {
                "Top_N": top_n,
                "Production_share_percent": (
                    production.head(top_n)["oilprod_kbd_value"].sum()
                    / production_total
                    * 100
                ),
                "Consumption_share_percent": (
                    consumption.head(top_n)["oilcons_kbd_value"].sum()
                    / consumption_total
                    * 100
                ),
            }
        )

    concentration = pd.DataFrame(rows)
    if concentration.empty:
        raise ValueError("Q2 oil concentration calculation returned no rows.")
    return concentration


def build_other_energy_summary(data: pd.DataFrame, year: int = YEAR) -> pd.DataFrame:
    """Summarise the leading countries for gas, coal, nuclear, and renewables."""
    rows = []

    for energy_name, (production_var, consumption_var) in TRADEABLE_ENERGY_VARS.items():
        production = filter_country_series(data, production_var, "production_value", year)
        consumption = filter_country_series(data, consumption_var, "consumption_value", year)
        production_top5 = production.head(5)
        consumption_top5 = consumption.head(5)
        overlap = sorted(
            set(production_top5["Country"]) & set(consumption_top5["Country"])
        )

        rows.append(
            {
                "Energy": energy_name,
                "Production_Top5": ", ".join(production_top5["Country"]),
                "Consumption_Top5": ", ".join(consumption_top5["Country"]),
                "Overlap_Top5_Count": len(overlap),
                "Overlap_Top5_Countries": ", ".join(overlap),
            }
        )

    for energy_name, variable in DOMESTIC_USE_VARS.items():
        users = filter_country_series(data, variable, "use_value", year)
        users_top5 = users.head(5)
        rows.append(
            {
                "Energy": energy_name,
                "Production_Top5": "Not suitable as trade-flow production",
                "Consumption_Top5": ", ".join(users_top5["Country"]),
                "Overlap_Top5_Count": None,
                "Overlap_Top5_Countries": "Not applicable",
            }
        )

    summary = pd.DataFrame(rows)
    if summary.empty:
        raise ValueError("Q2 other-energy summary returned no rows.")
    return summary


def calculate_analysis(data: pd.DataFrame, year: int = YEAR) -> dict[str, object]:
    """Run all Q2 calculations and return named result tables."""
    validated = validate_data(data)

    oil_production = filter_country_series(
        validated, "oilprod_kbd", "oilprod_kbd_value", year
    )
    oil_consumption = filter_country_series(
        validated, "oilcons_kbd", "oilcons_kbd_value", year
    )

    oil_production_top10 = add_rank(oil_production, 10)
    oil_consumption_top10 = add_rank(oil_consumption, 10)
    overlap_countries = sorted(
        set(oil_production_top10["Country"])
        & set(oil_consumption_top10["Country"])
    )

    region_balance = build_geographic_balance(
        oil_production,
        oil_consumption,
        "Region",
        "oilprod_kbd_value",
        "oilcons_kbd_value",
    )
    subregion_balance = build_geographic_balance(
        oil_production,
        oil_consumption,
        "SubRegion",
        "oilprod_kbd_value",
        "oilcons_kbd_value",
    )

    return {
        "oil_production": oil_production,
        "oil_consumption": oil_consumption,
        "oil_production_top10": oil_production_top10,
        "oil_consumption_top10": oil_consumption_top10,
        "overlap_countries": overlap_countries,
        "top10_comparison": build_oil_top10_comparison(
            oil_production_top10, oil_consumption_top10
        ),
        "region_balance": region_balance,
        "subregion_balance": subregion_balance,
        "concentration": build_concentration_table(oil_production, oil_consumption),
        "other_energy_summary": build_other_energy_summary(validated, year),
    }


def save_analysis_tables(
    analysis: dict[str, object],
    tables_dir: Path = TABLES_DIR,
) -> list[Path]:
    """Save all public Q2 result tables using the existing file names."""
    file_names = {
        "oil_production_top10": "q2_01_oil_production_top10.csv",
        "oil_consumption_top10": "q2_02_oil_consumption_top10.csv",
        "top10_comparison": "q2_03_oil_top10_production_vs_consumption.csv",
        "region_balance": "q2_04_oil_region_balance.csv",
        "subregion_balance": "q2_04b_oil_subregion_balance.csv",
        "concentration": "q2_05_oil_concentration.csv",
        "other_energy_summary": "q2_06_other_energy_summary.csv",
    }

    tables_dir.mkdir(parents=True, exist_ok=True)
    saved_paths = []
    for result_name, file_name in file_names.items():
        table = analysis.get(result_name)
        if not isinstance(table, pd.DataFrame) or table.empty:
            raise ValueError(f"Q2 cannot save missing or empty result table {result_name!r}.")
        output_path = tables_dir / file_name
        table.to_csv(output_path, index=False)
        saved_paths.append(output_path)
    return saved_paths


def plot_horizontal_bar(
    table: pd.DataFrame,
    value_column: str,
    title: str,
    x_label: str,
    output_path: Path,
    color: str,
) -> None:
    """Save one horizontal country-ranking chart."""
    import matplotlib.pyplot as plt

    if table.empty:
        raise ValueError(f"Q2 cannot create {output_path.name}: plot data is empty.")

    plot_data = table.sort_values(value_column, ascending=True)
    fig, ax = plt.subplots(figsize=(9, 5.8))
    bars = ax.barh(plot_data["Country"], plot_data[value_column], color=color)

    ax.set_title(title, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel(x_label)
    ax.set_ylabel("")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    ax.grid(axis="y", visible=False)

    label_offset = max(abs(plot_data[value_column]).max(), 1) * 0.015
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + label_offset,
            bar.get_y() + bar.get_height() / 2,
            f"{width:,.0f}",
            va="center",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_region_balance(balance: pd.DataFrame, year: int, output_path: Path) -> None:
    """Save the regional production-share versus consumption-share chart."""
    import matplotlib.pyplot as plt

    if balance.empty:
        raise ValueError(f"Q2 cannot create {output_path.name}: region data is empty.")

    plot_data = balance.sort_values("production_share_percent", ascending=True)
    y_positions = list(range(len(plot_data)))
    bar_height = 0.36

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.barh(
        [position - bar_height / 2 for position in y_positions],
        plot_data["production_share_percent"],
        height=bar_height,
        label="Production share",
        color=COLOR_PRODUCTION,
    )
    ax.barh(
        [position + bar_height / 2 for position in y_positions],
        plot_data["consumption_share_percent"],
        height=bar_height,
        label="Consumption share",
        color=COLOR_CONSUMPTION,
    )

    ax.set_yticks(y_positions)
    ax.set_yticklabels(plot_data["Region"])
    ax.set_xlabel("Share of world total (%)")
    ax.set_title(
        f"Oil Production vs Consumption by Region, {year}",
        fontsize=15,
        fontweight="bold",
        pad=14,
    )
    ax.legend(frameon=False, loc="lower right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    ax.grid(axis="y", visible=False)

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_concentration(
    concentration: pd.DataFrame,
    year: int,
    output_path: Path,
) -> None:
    """Save the Top 3/5/10 oil concentration chart."""
    import matplotlib.pyplot as plt

    if concentration.empty:
        raise ValueError(f"Q2 cannot create {output_path.name}: concentration data is empty.")

    fig, ax = plt.subplots(figsize=(7.8, 5.2))
    x_positions = list(range(len(concentration)))
    width = 0.34

    ax.bar(
        [position - width / 2 for position in x_positions],
        concentration["Production_share_percent"],
        width=width,
        label="Production",
        color=COLOR_PRODUCTION,
    )
    ax.bar(
        [position + width / 2 for position in x_positions],
        concentration["Consumption_share_percent"],
        width=width,
        label="Consumption",
        color=COLOR_CONSUMPTION,
    )

    ax.set_xticks(x_positions)
    ax.set_xticklabels([f"Top {top_n}" for top_n in concentration["Top_N"]])
    ax.set_ylabel("Share of world total (%)")
    ax.set_title(f"Oil Market Concentration, {year}", fontsize=15, fontweight="bold", pad=14)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    ax.grid(axis="x", visible=False)

    for position, row in concentration.reset_index(drop=True).iterrows():
        ax.text(
            position - width / 2,
            row["Production_share_percent"] + 0.8,
            f"{row['Production_share_percent']:.1f}%",
            ha="center",
            fontsize=9,
        )
        ax.text(
            position + width / 2,
            row["Consumption_share_percent"] + 0.8,
            f"{row['Consumption_share_percent']:.1f}%",
            ha="center",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def save_analysis_figures(
    analysis: dict[str, object],
    year: int = YEAR,
    figures_dir: Path = FIGURES_DIR,
) -> list[Path]:
    """Create all Q2 figures; matplotlib is loaded only inside this function."""
    import matplotlib.pyplot as plt

    try:
        plt.style.use("seaborn-v0_8-whitegrid")
    except OSError:
        pass

    figures_dir.mkdir(parents=True, exist_ok=True)
    production_path = figures_dir / "q2_01_oil_production_top10.png"
    consumption_path = figures_dir / "q2_02_oil_consumption_top10.png"
    region_path = figures_dir / "q2_04_oil_region_production_vs_consumption.png"
    concentration_path = figures_dir / "q2_05_oil_concentration.png"

    plot_horizontal_bar(
        analysis["oil_production_top10"],
        "oilprod_kbd_value",
        f"Top 10 Oil Producing Countries, {year}",
        "Thousand barrels per day",
        production_path,
        COLOR_PRODUCTION,
    )
    plot_horizontal_bar(
        analysis["oil_consumption_top10"],
        "oilcons_kbd_value",
        f"Top 10 Oil Consuming Countries, {year}",
        "Thousand barrels per day",
        consumption_path,
        COLOR_CONSUMPTION,
    )
    plot_region_balance(analysis["region_balance"], year, region_path)
    plot_concentration(analysis["concentration"], year, concentration_path)

    return [production_path, consumption_path, region_path, concentration_path]


def print_results(analysis: dict[str, object]) -> None:
    """Print the main tables and short, explainable conclusions."""
    print("\nQ2.1 Oil production Top 10")
    print(analysis["oil_production_top10"].to_string(index=False))

    print("\nQ2.2 Oil consumption Top 10")
    print(analysis["oil_consumption_top10"].to_string(index=False))

    overlap_countries = analysis["overlap_countries"]
    print("\nQ2.3 Top 10 overlap")
    print(f"Overlap count: {len(overlap_countries)}")
    print(f"Overlap countries: {', '.join(overlap_countries)}")
    print(analysis["top10_comparison"].to_string(index=False))

    print("\nQ2.4 Oil production-consumption balance by region")
    print(analysis["region_balance"].round(2).to_string(index=False))

    print("\nQ2.5 Oil concentration")
    print(analysis["concentration"].round(2).to_string(index=False))

    print("\nQ2.6 Other energy summary")
    print(analysis["other_energy_summary"].to_string(index=False))

    print("\nQ2 short takeaways")
    print("1. Oil production and consumption are led by partly different country groups.")
    print("2. Limited Top 10 overlap indicates a geographic supply-demand mismatch.")
    print("3. Regional share gaps identify supply centres and demand centres.")
    print("4. Top 3/5/10 shares show how concentrated oil supply and demand are.")
    print(
        "5. Gas and coal allow the same comparison; nuclear and renewables "
        "are domestic-use rankings."
    )


def main() -> None:
    raw_data = load_data()
    analysis = calculate_analysis(raw_data)
    table_paths = save_analysis_tables(analysis)
    print_results(analysis)
    print(f"\nTables saved to: {table_paths[0].parent}")

    try:
        figure_paths = save_analysis_figures(analysis)
    except ModuleNotFoundError as error:
        if error.name and error.name.startswith("matplotlib"):
            print("Matplotlib is not installed. Tables were saved, but figures were skipped.")
        else:
            raise
    else:
        print(f"Figures saved to: {figure_paths[0].parent}")


if __name__ == "__main__":
    main()
