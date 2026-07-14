"""Focused unit tests for the ordinary Q4 and Q5 analysis scripts."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType


sys.dont_write_bytecode = True

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_script(module_name: str, relative_path: str) -> ModuleType:
    """Dynamically load a script without requiring package boilerplate."""

    path = PROJECT_ROOT / relative_path
    specification = importlib.util.spec_from_file_location(module_name, path)
    if specification is None or specification.loader is None:
        raise ImportError(f"Could not load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


Q4 = load_script(
    "ordinary_q4",
    "q4_oil_import_dependency/oil_import_exposure.py",
)
Q5 = load_script(
    "ordinary_q5",
    "q5_hormuz_chokepoints/hormuz_chokepoints.py",
)


class Q4SupplyGapTests(unittest.TestCase):
    """Test missing-data and explicit-assumption behaviour."""

    @staticmethod
    def energy_data():
        return Q4.pd.DataFrame(
            [
                {
                    "Country": "China",
                    "Year": 2024,
                    "Var": "oilprod_kbd",
                    "Value": 100.0,
                },
                {
                    "Country": "China",
                    "Year": 2024,
                    "Var": "oilcons_kbd",
                    "Value": 200.0,
                },
                {
                    "Country": "Germany",
                    "Year": 2024,
                    "Var": "oilcons_kbd",
                    "Value": 100.0,
                },
            ]
        )

    @staticmethod
    def origin_share(country: str, share_pct: float):
        return Q4.pd.DataFrame(
            [
                {
                    "country_name": country,
                    "origin_based_hormuz_related_share_pct": share_pct,
                }
            ]
        )

    @staticmethod
    def reconciliation(country: str):
        return Q4.pd.DataFrame(
            [
                {
                    "year": 2024,
                    "country_name": country,
                    "coverage_status": "reconciled_within_1pct",
                }
            ]
        )

    def test_missing_production_stays_nan_and_combined_proxy_is_not_calculated(self):
        gap = Q4.build_supply_gap_table(self.energy_data())
        germany = gap.loc[gap["country_name"].eq("Germany")].iloc[0]

        self.assertEqual(germany["production_data_status"], "missing_not_assumed")
        self.assertFalse(bool(germany["production_assumption_used"]))
        self.assertTrue(Q4.pd.isna(germany["oil_production_kbd"]))
        self.assertTrue(
            Q4.pd.isna(
                germany["domestic_supply_gap_proxy_pct_of_consumption"]
            )
        )

        combined = Q4.build_combined_proxy_table(
            gap,
            self.origin_share("Germany", 50.0),
            self.reconciliation("Germany"),
        )
        germany_combined = combined.loc[
            combined["country_name"].eq("Germany")
        ].iloc[0]
        self.assertTrue(
            Q4.pd.isna(
                germany_combined[
                    "combined_supply_gap_hormuz_origin_proxy_pct"
                ]
            )
        )
        self.assertEqual(
            germany_combined["combined_proxy_status"],
            "not_calculated_supply_gap_unavailable",
        )

    def test_explicit_production_assumption_is_flagged_and_combined(self):
        gap = Q4.build_supply_gap_table(
            self.energy_data(), production_assumptions={"Germany": 25.0}
        )
        germany = gap.loc[gap["country_name"].eq("Germany")].iloc[0]

        self.assertEqual(germany["production_data_status"], "explicit_assumption")
        self.assertTrue(bool(germany["production_assumption_used"]))
        self.assertAlmostEqual(
            germany["domestic_supply_gap_proxy_pct_of_consumption"], 75.0
        )

        combined = Q4.build_combined_proxy_table(
            gap,
            self.origin_share("Germany", 40.0),
            self.reconciliation("Germany"),
        )
        germany_combined = combined.loc[
            combined["country_name"].eq("Germany")
        ].iloc[0]
        self.assertAlmostEqual(
            germany_combined["combined_supply_gap_hormuz_origin_proxy_pct"],
            30.0,
        )
        self.assertEqual(
            germany_combined["combined_proxy_status"],
            "calculated_with_explicit_production_assumption",
        )

    def test_duplicate_energy_key_is_rejected(self):
        data = self.energy_data()
        duplicated = Q4.pd.concat([data, data.iloc[[0]]], ignore_index=True)

        with self.assertRaisesRegex(ValueError, "duplicate Country-Year-Var"):
            Q4.build_supply_gap_table(duplicated)


class Q4TradeTests(unittest.TestCase):
    """Test exporter-origin shares and independent World reconciliation."""

    def test_middle_east_and_hormuz_origin_shares(self):
        trade_scope = Q4.pd.DataFrame(
            [
                {
                    "refYear": 2024,
                    "reporterDesc": "USA",
                    "partnerDesc": "Saudi Arabia",
                    "netWgt": 50.0,
                    "primaryValue": 500.0,
                },
                {
                    "refYear": 2024,
                    "reporterDesc": "USA",
                    "partnerDesc": "Oman",
                    "netWgt": 20.0,
                    "primaryValue": 200.0,
                },
                {
                    "refYear": 2024,
                    "reporterDesc": "USA",
                    "partnerDesc": "Canada",
                    "netWgt": 30.0,
                    "primaryValue": 300.0,
                },
            ]
        )

        sources = Q4.build_import_source_table(trade_scope)
        summary = Q4.build_origin_share_summary(sources)
        usa = summary.loc[summary["country_name"].eq("USA")].iloc[0]

        self.assertEqual(usa["origin_share_metric"], "netWgt")
        self.assertAlmostEqual(usa["middle_east_origin_share_pct"], 70.0)
        self.assertAlmostEqual(
            usa["origin_based_hormuz_related_share_pct"], 50.0
        )

    def test_world_reconciliation_prefers_weight_and_falls_back_to_value(self):
        trade_scope = Q4.pd.DataFrame(
            [
                {
                    "reporterDesc": "USA",
                    "partnerDesc": "Canada",
                    "netWgt": 60.0,
                    "primaryValue": 600.0,
                },
                {
                    "reporterDesc": "USA",
                    "partnerDesc": "Saudi Arabia",
                    "netWgt": 40.0,
                    "primaryValue": 400.0,
                },
                {
                    "reporterDesc": "USA",
                    "partnerDesc": "World",
                    "netWgt": 100.0,
                    "primaryValue": 1000.0,
                },
                {
                    "reporterDesc": "European Union",
                    "partnerDesc": "Norway",
                    "netWgt": 70.0,
                    "primaryValue": 700.0,
                },
                {
                    "reporterDesc": "European Union",
                    "partnerDesc": "Iraq",
                    "netWgt": 30.0,
                    "primaryValue": 300.0,
                },
                {
                    "reporterDesc": "European Union",
                    "partnerDesc": "World",
                    "netWgt": float("nan"),
                    "primaryValue": 1000.0,
                },
            ]
        )

        reconciliation = Q4.reconcile_partner_rows_with_world(
            trade_scope, year=2024
        )
        usa = reconciliation.loc[
            reconciliation["country_name"].eq("USA")
        ].iloc[0]
        european_union = reconciliation.loc[
            reconciliation["country_name"].eq("European Union")
        ].iloc[0]

        self.assertEqual(usa["reconciliation_metric"], "netWgt")
        self.assertAlmostEqual(usa["coverage_ratio"], 1.0)
        self.assertEqual(usa["coverage_status"], "reconciled_within_1pct")

        self.assertEqual(
            european_union["reconciliation_metric"], "primaryValue"
        )
        self.assertAlmostEqual(european_union["coverage_ratio"], 1.0)
        self.assertEqual(
            european_union["coverage_status"], "reconciled_within_1pct"
        )
        self.assertIn("fallback", european_union["metric_selection_note"])


class Q5ShareAndValidationTests(unittest.TestCase):
    """Test headline share calculations and source-table validation."""

    def test_2024_and_first_half_2025_shares(self):
        shares = Q5.calculate_hormuz_global_shares(
            Q5.build_eia_chokepoint_table()
        ).set_index("period")

        self.assertAlmostEqual(
            shares.loc["2024", "hormuz_share_of_world_maritime_trade_pct"],
            26.0,
        )
        self.assertAlmostEqual(
            shares.loc["2024", "hormuz_share_of_world_total_supply_pct"],
            20.0,
        )
        self.assertAlmostEqual(
            shares.loc["1H25", "hormuz_share_of_world_maritime_trade_pct"],
            26.2,
        )
        self.assertAlmostEqual(
            shares.loc["1H25", "hormuz_share_of_world_total_supply_pct"],
            20.0,
        )

    def test_missing_period_column_is_rejected(self):
        table = Q5.build_eia_chokepoint_table().drop(columns="2024")
        with self.assertRaisesRegex(ValueError, "missing columns"):
            Q5.validate_eia_table(table)

    def test_invalid_flow_relationship_is_rejected(self):
        table = Q5.build_eia_chokepoint_table()
        table.loc[table["location"].eq("Strait of Hormuz"), "2024"] = 200.0
        with self.assertRaisesRegex(ValueError, "Expected Strait of Hormuz"):
            Q5.validate_eia_table(table)

    def test_duplicate_location_is_rejected(self):
        table = Q5.build_eia_chokepoint_table()
        duplicated = Q5.pd.concat([table, table.iloc[[0]]], ignore_index=True)

        with self.assertRaisesRegex(ValueError, "duplicate locations"):
            Q5.validate_eia_table(duplicated)


if __name__ == "__main__":
    unittest.main()
