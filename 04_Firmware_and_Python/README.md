# ThermoBench Rev B - Automated Sensor Validation Station
AI-assisted interview project prepared for Aaron Trujillo.
Start with BUILD_STEPS.md, the complete numbered Windows/build/test guide.

## Files
- thermobench.ino: ESP32-WROOM firmware; GPIO34 ADC1 assumed.
- dashboard.py: desktop USB dashboard, labeled demo, CSV recording.
- station.py: shared parser and CSV analysis with optional DMM comparison.
- bench.py: original nominal model, serial capture, synthetic SPC examples.
- test_bench.py / test_station.py: 9 Python tests.
- results/: analytical and SYNTHETIC examples, not hardware results.
- requirements.txt: Python dependencies.
- build_report.py: original Rev A report generator; run from extracted ZIP root
  with reportlab installed, and create output/pdf first. Rev A does not describe
  the new dashboard/analyzer. Use BUILD_STEPS.md / Rev B guide for those tools.

## Quick Windows commands (from project folder)
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest -v
.\.venv\Scripts\python dashboard.py

## Verification boundary
9 Python tests passed; source syntax checked. Dashboard window/USB, Arduino
compilation/upload, physical circuit and thermal accuracy remain unverified here.
A synthetic PASS checks software behavior, not the physical prototype.
The Rev A PDF remains the circuit/specification reference; the Rev B guide
adds build steps and clearly identifies automated versus manual checks.
