"""Run the five analysis sections in order.

Each section remains independently executable and testable. This runner is a
convenient single entry point for reproducing the complete project.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

ANALYSIS_SCRIPTS = {
    "q1": PROJECT_ROOT / "q1_global_energy_overview" / "global_overview.py",
    "q2": PROJECT_ROOT
    / "q2_production_consumption"
    / "production_consumption.py",
    "q3": PROJECT_ROOT
    / "q3_country_energy_structure"
    / "country_energy_structure.py",
    "q4": PROJECT_ROOT
    / "q4_oil_import_dependency"
    / "oil_import_exposure.py",
    "q5": PROJECT_ROOT / "q5_hormuz_chokepoints" / "hormuz_chokepoints.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the complete Hormuz energy analysis."
    )
    parser.add_argument(
        "--only",
        nargs="+",
        choices=ANALYSIS_SCRIPTS,
        metavar="Q",
        help="Run selected sections only, for example: --only q1 q4 q5",
    )
    return parser.parse_args()


def run_script(section: str, script_path: Path) -> None:
    if not script_path.is_file():
        raise FileNotFoundError(f"Missing {section.upper()} script: {script_path}")

    print(
        f"\n{'=' * 72}\n"
        f"Running {section.upper()}: {script_path.name}\n"
        f"{'=' * 72}",
        flush=True,
    )
    subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT,
        check=True,
    )


def main() -> None:
    args = parse_args()
    selected_sections = args.only or list(ANALYSIS_SCRIPTS)

    for section in selected_sections:
        run_script(section, ANALYSIS_SCRIPTS[section])


if __name__ == "__main__":
    main()
