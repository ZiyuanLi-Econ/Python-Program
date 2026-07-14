"""Q1. Global energy supply and energy mix in 2024.

The script keeps the analysis steps deliberately small and explicit so that the
calculation is easy to explain.  Importing this module does not read data or
load matplotlib; call ``main()`` to run the complete analysis.
"""

from pathlib import Path

import pandas as pd


# Paths are based on this file, so the project works after it is moved or cloned.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data_raw" / "Statistical Review of World Energy Narrow format.csv"
Q1_DIR = Path(__file__).resolve().parent
TABLES_DIR = Q1_DIR / "tables"
FIGURES_DIR = Q1_DIR / "figures"

COUNTRY = "Total World"
YEAR = 2024
TOTAL_ENERGY_VAR = "tes_ej"
REQUIRED_COLUMNS = {"Country", "Year", "Var", "Value"}

# Raw variable name -> reader-friendly label used in tables and charts.
ENERGY_VARS = {
    "oilcons_ej": "Oil",
    "coalcons_ej": "Coal",
    "gascons_ej": "Natural gas",
    "nuclear_ej": "Nuclear",
    "renewables_ej": "Renewables",
}

ENERGY_COLORS = {
    "Oil": "#D46A2C",
    "Coal": "#2B2B2B",
    "Natural gas": "#1F77B4",
    "Nuclear": "#8E6BBE",
    "Renewables": "#2CA25F",
}


def load_data(data_path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the Energy Institute narrow-format CSV."""
    if not data_path.exists():
        raise FileNotFoundError(f"Q1 data file not found: {data_path}")
    return pd.read_csv(data_path)


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate the columns and unique key needed by the analysis."""
    if data.empty:
        raise ValueError("Q1 input data is empty.")

    missing_columns = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing_columns:
        raise ValueError(f"Q1 input data is missing required columns: {missing_columns}")

    validated = data.copy()
    numeric_year = pd.to_numeric(validated["Year"], errors="coerce")
    if numeric_year.isna().any() or ((numeric_year % 1) != 0).any():
        raise ValueError("Q1 column 'Year' must contain integer years only.")
    validated["Year"] = numeric_year.astype(int)

    numeric_value = pd.to_numeric(validated["Value"], errors="coerce")
    if numeric_value.isna().any():
        bad_rows = validated.loc[numeric_value.isna(), ["Country", "Year", "Var"]].head(5)
        raise ValueError(
            "Q1 column 'Value' contains missing or non-numeric values. "
            f"Example keys: {bad_rows.to_dict('records')}"
        )
    validated["Value"] = numeric_value.astype(float)

    key_columns = ["Country", "Year", "Var"]
    duplicate_rows = validated.duplicated(key_columns, keep=False)
    if duplicate_rows.any():
        examples = validated.loc[duplicate_rows, key_columns].drop_duplicates().head(5)
        raise ValueError(
            "Q1 input contains duplicate Country-Year-Var records. "
            f"Example keys: {examples.to_dict('records')}"
        )

    return validated


def get_energy_value(
    data: pd.DataFrame,
    variable: str,
    country: str = COUNTRY,
    year: int = YEAR,
) -> float:
    """Return the single value for one country, year, and variable."""
    selected = data.loc[
        data["Country"].eq(country)
        & data["Year"].eq(year)
        & data["Var"].eq(variable),
        "Value",
    ]

    if selected.empty:
        raise ValueError(
            f"Q1 found no result for Country={country!r}, Year={year}, Var={variable!r}."
        )
    if len(selected) > 1:
        raise ValueError(
            f"Q1 expected one result for Country={country!r}, Year={year}, "
            f"Var={variable!r}, but found {len(selected)}."
        )

    return float(selected.iloc[0])


def calculate_energy_mix(
    data: pd.DataFrame,
    country: str = COUNTRY,
    year: int = YEAR,
) -> tuple[float, pd.DataFrame]:
    """Calculate total energy supply and the share of each selected source."""
    validated = validate_data(data)
    total_energy_ej = get_energy_value(validated, TOTAL_ENERGY_VAR, country, year)

    if total_energy_ej == 0:
        raise ValueError("Q1 cannot calculate energy shares: total energy supply is zero.")
    if total_energy_ej < 0:
        raise ValueError("Q1 total energy supply cannot be negative.")

    rows = []
    for variable, energy_name in ENERGY_VARS.items():
        value_ej = get_energy_value(validated, variable, country, year)
        rows.append(
            {
                "Energy": energy_name,
                "Var": variable,
                "Value_EJ": value_ej,
                "Share_percent": value_ej / total_energy_ej * 100,
            }
        )

    energy_mix = pd.DataFrame(rows)
    if energy_mix.empty:
        raise ValueError("Q1 energy-mix calculation returned no rows.")

    energy_mix = energy_mix.sort_values("Share_percent", ascending=False).reset_index(drop=True)
    return total_energy_ej, energy_mix


def save_energy_mix_table(
    energy_mix: pd.DataFrame,
    year: int = YEAR,
    tables_dir: Path = TABLES_DIR,
) -> Path:
    """Save the calculated table and return its path."""
    if energy_mix.empty:
        raise ValueError("Q1 cannot save an empty energy-mix table.")

    tables_dir.mkdir(parents=True, exist_ok=True)
    output_path = tables_dir / f"global_energy_mix_{year}.csv"
    energy_mix.round({"Value_EJ": 2, "Share_percent": 2}).to_csv(output_path, index=False)
    return output_path


def plot_energy_mix_bar(
    energy_mix: pd.DataFrame,
    year: int = YEAR,
    figures_dir: Path = FIGURES_DIR,
) -> Path:
    """Save the bar chart.  Matplotlib is imported only when plotting."""
    import matplotlib.pyplot as plt

    if energy_mix.empty:
        raise ValueError("Q1 cannot plot an empty energy-mix table.")

    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_data = energy_mix.sort_values("Share_percent", ascending=False)
    colors = plot_data["Energy"].map(ENERGY_COLORS)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(plot_data["Energy"], plot_data["Share_percent"], color=colors)
    ax.set_title(f"Global Energy Mix by Source, {year}", fontsize=14, fontweight="bold")
    ax.set_ylabel("Share of total energy supply (%)")
    ax.tick_params(axis="x", rotation=25)
    ax.bar_label(bars, labels=[f"{share:.1f}%" for share in plot_data["Share_percent"]], padding=3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    output_path = figures_dir / f"global_energy_mix_{year}_bar.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_energy_mix_donut(
    energy_mix: pd.DataFrame,
    year: int = YEAR,
    figures_dir: Path = FIGURES_DIR,
) -> Path:
    """Save the donut chart.  Matplotlib is imported only when plotting."""
    import matplotlib.pyplot as plt

    if energy_mix.empty:
        raise ValueError("Q1 cannot plot an empty energy-mix table.")

    figures_dir.mkdir(parents=True, exist_ok=True)
    plot_data = energy_mix.sort_values("Share_percent", ascending=False)
    colors = plot_data["Energy"].map(ENERGY_COLORS)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        plot_data["Share_percent"],
        labels=plot_data["Energy"],
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
    )
    ax.set_title(f"Global Energy Mix, {year}", fontsize=14, fontweight="bold")

    output_path = figures_dir / f"global_energy_mix_{year}_donut.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> None:
    raw_data = load_data()
    total_energy_ej, energy_mix = calculate_energy_mix(raw_data)
    table_path = save_energy_mix_table(energy_mix)

    print(f"Q1.1 Global total energy supply in {YEAR}: {total_energy_ej:.2f} EJ")
    print("\nQ1.2 Global energy mix:")
    print(energy_mix.round(2).to_string(index=False))
    print(f"\nTable saved to: {table_path}")

    try:
        bar_path = plot_energy_mix_bar(energy_mix)
        donut_path = plot_energy_mix_donut(energy_mix)
    except ModuleNotFoundError as error:
        if error.name and error.name.startswith("matplotlib"):
            print("Matplotlib is not installed. The table was saved, but figures were skipped.")
        else:
            raise
    else:
        print(f"Figures saved to: {bar_path.parent}")


if __name__ == "__main__":
    main()
