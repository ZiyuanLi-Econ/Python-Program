"""Run the five project analyses in order."""

from pathlib import Path
import subprocess
import sys


CODE_DIR = Path(__file__).resolve().parent
SCRIPTS = [
    "01_global_energy.py",
    "02_oil_geography.py",
    "03_market_energy_mix.py",
    "04_import_exposure.py",
    "05_hormuz_chokepoint.py",
]


for number, script in enumerate(SCRIPTS, start=1):
    print(f"\n[{number}/5] Running {script}...", flush=True)
    subprocess.run([sys.executable, str(CODE_DIR / script)], check=True)

print("\nAll five analyses and figures are complete.")
