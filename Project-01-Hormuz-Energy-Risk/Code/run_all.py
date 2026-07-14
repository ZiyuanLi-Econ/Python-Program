"""Run the five project scripts in order."""

from pathlib import Path
import subprocess
import sys


code_folder = Path(__file__).resolve().parent
scripts = [
    "01_global_energy.py",
    "02_oil_geography.py",
    "03_market_energy_mix.py",
    "04_import_exposure.py",
    "05_hormuz_chokepoint.py",
]

for script in scripts:
    print(f"\nRunning {script}...")
    subprocess.run([sys.executable, str(code_folder / script)], check=True)

print("\nAll five analyses are complete.")
