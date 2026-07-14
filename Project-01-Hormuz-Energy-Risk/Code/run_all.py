"""Run the five project analyses in order."""

from pathlib import Path
import subprocess
import sys


CODE_DIR = Path(__file__).resolve().parent
REQUIRED_DATA = [
    "Statistical Review of World Energy Narrow format.csv",
    "TradeData.csv",
]
SCRIPTS = [
    "01_global_energy.py",
    "02_oil_geography.py",
    "03_market_energy_mix.py",
    "04_import_exposure.py",
    "05_hormuz_chokepoint.py",
]

missing_data = [
    filename for filename in REQUIRED_DATA if not (CODE_DIR / "data_raw" / filename).exists()
]
if missing_data:
    missing_list = "\n".join(f"- {filename}" for filename in missing_data)
    raise SystemExit(
        "Missing source data in Code/data_raw/:\n"
        f"{missing_list}\n\n"
        "Download the files described in Code/DATA_NOTES.md, then run this command again."
    )


for number, script in enumerate(SCRIPTS, start=1):
    print(f"\n[{number}/5] Running {script}...", flush=True)
    subprocess.run([sys.executable, str(CODE_DIR / script)], check=True)

print("\nAll five analyses and figures are complete.")
