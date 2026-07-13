"""Unit tests for the ordinary Q1-Q3 analysis scripts.

The scripts are loaded from their file paths because the analysis directories
are intentionally not Python packages.  These tests exercise calculation and
validation code only: they neither import matplotlib nor write output files.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script(module_name: str, relative_path: str):
    """Load one ordinary analysis script without requiring package metadata."""
    script_path = PROJECT_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load analysis script: {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Q1 = load_script("ordinary_q1", "q1_global_energy_overview/global_overview.py")
Q2 = load_script(
    "ordinary_q2",
    "q2_production_consumption/production_consumption.py",
)
Q3 = load_script(
    "ordinary_q3",
    "q3_country_energy_structure/country_energy_structure.py",
)


class Q1EnergyMixTests(unittest.TestCase):
    @staticmethod
    def make_data(total_energy: float = 100.0) -> pd.DataFrame:
        values = {
            "tes_ej": total_energy,
            "oilcons_ej": 32.0,
            "coalcons_ej": 26.0,
            "gascons_ej": 24.0,
            "nuclear_ej": 6.0,
            "renewables_ej": 12.0,
        }
        return pd.DataFrame(
            [
                {
                    "Country": "Total World",
                    "Year": 2024,
                    "Var": variable,
                    "Value": value,
                }
                for variable, value in values.items()
            ]
        )

    def test_calculate_energy_mix_returns_correct_shares(self) -> None:
        total_energy, energy_mix = Q1.calculate_energy_mix(self.make_data())
        shares = energy_mix.set_index("Energy")["Share_percent"]

        self.assertEqual(total_energy, 100.0)
        self.assertAlmostEqual(shares["Oil"], 32.0)
        self.assertAlmostEqual(shares["Coal"], 26.0)
        self.assertAlmostEqual(shares["Natural gas"], 24.0)
        self.assertAlmostEqual(shares["Nuclear"], 6.0)
        self.assertAlmostEqual(shares["Renewables"], 12.0)
        self.assertAlmostEqual(shares.sum(), 100.0)

    def test_missing_required_column_is_rejected(self) -> None:
        data = self.make_data().drop(columns="Var")

        with self.assertRaisesRegex(ValueError, "missing required columns"):
            Q1.validate_data(data)

    def test_duplicate_country_year_variable_key_is_rejected(self) -> None:
        data = self.make_data()
        duplicated = pd.concat([data, data.iloc[[0]]], ignore_index=True)

        with self.assertRaisesRegex(ValueError, "duplicate Country-Year-Var"):
            Q1.validate_data(duplicated)

    def test_zero_total_energy_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "total energy supply is zero"):
            Q1.calculate_energy_mix(self.make_data(total_energy=0.0))


class Q2ProductionConsumptionTests(unittest.TestCase):
    @staticmethod
    def make_rank_input(value_column: str, values: list[float]) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "Country": [f"Country {position}" for position in range(1, len(values) + 1)],
                value_column: values,
            }
        )

    def test_add_rank_honours_top_n(self) -> None:
        table = self.make_rank_input("oilprod_kbd_value", [50.0, 40.0, 30.0, 20.0])

        ranked = Q2.add_rank(table, 2)

        self.assertEqual(ranked["Rank"].tolist(), [1, 2])
        self.assertEqual(ranked["Country"].tolist(), ["Country 1", "Country 2"])
        self.assertEqual(len(ranked), 2)

    def test_region_shares_each_sum_to_one_hundred_percent(self) -> None:
        production = pd.DataFrame(
            {
                "Country": ["Producer A", "Producer B"],
                "Region": ["Region A", "Region B"],
                "oilprod_kbd_value": [60.0, 40.0],
            }
        )
        consumption = pd.DataFrame(
            {
                "Country": ["Consumer A", "Consumer B"],
                "Region": ["Region A", "Region B"],
                "oilcons_kbd_value": [20.0, 80.0],
            }
        )

        balance = Q2.build_geographic_balance(
            production,
            consumption,
            "Region",
            "oilprod_kbd_value",
            "oilcons_kbd_value",
        )
        by_region = balance.set_index("Region")

        self.assertAlmostEqual(balance["production_share_percent"].sum(), 100.0)
        self.assertAlmostEqual(balance["consumption_share_percent"].sum(), 100.0)
        self.assertAlmostEqual(by_region.loc["Region A", "production_share_percent"], 60.0)
        self.assertAlmostEqual(by_region.loc["Region A", "consumption_share_percent"], 20.0)
        self.assertAlmostEqual(by_region.loc["Region A", "share_gap_percent"], 40.0)

    def test_duplicate_country_year_variable_key_is_rejected(self) -> None:
        data = pd.DataFrame(
            [
                {
                    "Country": "Country A",
                    "Year": 2024,
                    "Region": "Region A",
                    "SubRegion": "Subregion A",
                    "Var": "oilprod_kbd",
                    "Value": 10.0,
                },
                {
                    "Country": "Country A",
                    "Year": 2024,
                    "Region": "Region A",
                    "SubRegion": "Subregion A",
                    "Var": "oilprod_kbd",
                    "Value": 10.0,
                },
            ]
        )

        with self.assertRaisesRegex(ValueError, "duplicate Country-Year-Var"):
            Q2.validate_data(data)

    def test_fewer_than_ten_rows_can_be_compared_without_length_error(self) -> None:
        production = self.make_rank_input("oilprod_kbd_value", [50.0, 30.0, 20.0])
        consumption = self.make_rank_input("oilcons_kbd_value", [70.0, 30.0])
        production_top10 = Q2.add_rank(production, 10)
        consumption_top10 = Q2.add_rank(consumption, 10)

        comparison = Q2.build_oil_top10_comparison(
            production_top10,
            consumption_top10,
        )

        self.assertEqual(production_top10["Rank"].tolist(), [1, 2, 3])
        self.assertEqual(consumption_top10["Rank"].tolist(), [1, 2])
        self.assertEqual(comparison["Rank"].tolist(), [1, 2, 3])
        self.assertEqual(len(comparison), 3)
        self.assertTrue(pd.isna(comparison.loc[2, "Consumption_Top10_Country"]))


class Q3CountryEnergyStructureTests(unittest.TestCase):
    @staticmethod
    def make_amount_table() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "tes_ej": [100.0, 50.0],
                "oilcons_ej": [40.0, 10.0],
                "gascons_ej": [25.0, 20.0],
                "coalcons_ej": [20.0, 10.0],
                "nuclear_ej": [5.0, 5.0],
                "renewables_ej": [10.0, 5.0],
            },
            index=["Alpha", "Total EU"],
        )

    @staticmethod
    def make_long_data() -> pd.DataFrame:
        amount_table = Q3CountryEnergyStructureTests.make_amount_table()
        rows = []
        for economy, values in amount_table.iterrows():
            for variable, value in values.items():
                rows.append(
                    {
                        "Country": economy,
                        "Year": 2024,
                        "Var": variable,
                        "Value": value,
                    }
                )
        return pd.DataFrame(rows)

    def test_share_sum_and_reader_friendly_labels(self) -> None:
        share_table = Q3.calculate_shares(self.make_amount_table())
        _, main_energy_table = Q3.build_summary(share_table)

        for economy in share_table.index:
            self.assertAlmostEqual(share_table.loc[economy, "share_sum"], 100.0)
        self.assertEqual(main_energy_table.loc["Alpha", "main_energy_source"], "Oil")
        self.assertEqual(
            main_energy_table.loc["Total EU", "main_energy_source"],
            "Natural gas",
        )
        self.assertEqual(
            Q3.PLOT_ECONOMY_LABELS["Total EU"],
            "Total EU (regional aggregate)",
        )

    def test_missing_economy_variable_combination_is_rejected(self) -> None:
        data = self.make_long_data()
        missing_pair = data["Country"].eq("Total EU") & data["Var"].eq("gascons_ej")
        data = data.loc[~missing_pair].copy()

        with self.assertRaisesRegex(ValueError, "missing economy-variable observations"):
            Q3.validate_data(
                data,
                year=2024,
                economies=("Alpha", "Total EU"),
                variables=Q3.ENERGY_VARS,
            )

    def test_zero_total_energy_supply_is_rejected(self) -> None:
        amount_table = self.make_amount_table()
        amount_table.loc["Alpha", "tes_ej"] = 0.0

        with self.assertRaisesRegex(ValueError, "greater than zero"):
            Q3.calculate_shares(amount_table)


if __name__ == "__main__":
    unittest.main()
