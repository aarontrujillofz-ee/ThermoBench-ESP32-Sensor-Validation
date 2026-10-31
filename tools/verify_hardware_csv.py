"""Verify archived ThermoBench hardware CSV statistics against saved metrics.

Read-only; Python standard library only. Run from any working directory:
    py tools/verify_hardware_csv.py
This verifies archival consistency, not external temperature accuracy.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "05_Hardware_CSV"
METRICS_FILE = ROOT / "06_Analysis" / "measurement_metrics.json"
REQUIRED = {"source", "ms", "mv", "temp_c", "status"}


def check_close(errors: list[str], label: str, actual: float, expected: float,
                tolerance: float = 0.00011) -> None:
    if not math.isclose(actual, expected, abs_tol=tolerance, rel_tol=0):
        errors.append(f"{label}: calculated {actual:.6f}, archived {expected:.6f}")


def verify_one(info: dict) -> tuple[int, list[str]]:
    name = info["file"]
    if Path(name).name != name:
        return 0, [f"Unsafe filename in metrics: {name}"]
    path = DATA_DIR / name
    errors: list[str] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not REQUIRED.issubset(set(reader.fieldnames or [])):
                return 0, [f"{name}: required columns missing"]
            records = list(reader)
        if len(records) < 2:
            return len(records), [f"{name}: need at least two rows"]
        timestamps = [int(x["ms"]) for x in records]
        temps = [float(x["temp_c"]) for x in records]
        volts = [float(x["mv"]) for x in records]
        if not all(map(math.isfinite, temps + volts)):
            return len(records), [f"{name}: nonfinite temperature/voltage"]
    except (OSError, ValueError, TypeError, KeyError, csv.Error) as e:
        return 0, [f"{name}: cannot parse source CSV: {e}"]

    count = len(records)
    deltas = [b - a for a, b in zip(timestamps, timestamps[1:])]
    mean_temp = statistics.mean(temps)
    sd_temp = statistics.stdev(temps)
    mean_mv = statistics.mean(volts)
    sd_mv = statistics.stdev(volts)
    duration = (timestamps[-1] - timestamps[0]) / 1000
    peak_index = temps.index(max(temps))
    peak_elapsed = (timestamps[peak_index] - timestamps[0]) / 1000
    first20 = [t for ms, t in zip(timestamps, temps)
               if ms - timestamps[0] <= 20_000]
    is_hardware = all(x["source"] == "HARDWARE" for x in records)
    is_normal = all(x["status"] == "NORMAL" for x in records)

    if count != info["samples"]:
        errors.append(f"{name}: row count {count}, expected {info['samples']}")
    if sorted(set(deltas)) != info["sample_interval_ms_unique"]:
        errors.append(f"{name}: sample intervals {sorted(set(deltas))}, "
                      f"expected {info['sample_interval_ms_unique']}")
    if not all(delta > 0 for delta in deltas):
        errors.append(f"{name}: timestamps not strictly increasing")
    if is_hardware != info["source_hardware"]:
        errors.append(f"{name}: source label differs from metrics")
    if is_normal != info["all_status_normal"]:
        errors.append(f"{name}: state labels differ from metrics")

    comparisons = {
        "duration_s": duration,
        "temperature_mean_c": mean_temp,
        "temperature_sd_c": sd_temp,
        "temperature_min_c": min(temps),
        "temperature_max_c": max(temps),
        "temperature_start_c": temps[0],
        "temperature_end_c": temps[-1],
        "voltage_mean_mv": mean_mv,
        "voltage_sd_mv": sd_mv,
        "peak_time_s": peak_elapsed,
        "first20_temperature_mean_c": statistics.mean(first20),
        "first20_temperature_sd_c": statistics.stdev(first20),
    }
    for key, actual in comparisons.items():
        # The archived mean millivolts field is rounded to three decimals;
        # most other reported statistics are rounded to four decimals.
        tolerance = 0.00051 if key == "voltage_mean_mv" else 0.00011
        check_close(errors, f"{name} / {key}", actual, float(info[key]), tolerance)

    print(f"{'PASS' if not errors else 'FAIL'}  {name}  "
          f"n={count}, span={duration:.1f}s, mean={mean_temp:.4f}C, "
          f"sample_SD={sd_temp:.4f}C")
    return count, errors


def main() -> int:
    try:
        metadata = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        datasets = metadata["datasets"]
    except (OSError, ValueError, KeyError) as e:
        print(f"FAIL: cannot read archived metrics: {e}", file=sys.stderr)
        return 1
    total = 0
    errors: list[str] = []
    for info in datasets:
        count, issues = verify_one(info)
        total += count
        errors.extend(issues)
    expected_total = sum(info["samples"] for info in datasets)
    if total != expected_total:
        errors.append(f"Total rows {total}, expected {expected_total}")
    print(f"\nFiles checked: {len(datasets)} | rows: {total} | "
          f"result: {'PASS' if not errors else 'FAIL'}")
    if errors:
        for problem in errors:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("Archival consistency only; calibrated accuracy and physical fault testing NOT verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
