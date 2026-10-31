# ThermoBench — ESP32 Firmware & Python Code Walkthrough

**Project:** ESP32 Temperature Sensing & Hardware Validation
**Purpose:** Help a reader locate, understand, and reproduce each software component.
**Evidence boundary:** This guide documents the repository's source code. It does **not** certify that the archived ESP32 sketch was compiled, that the desktop GUI and USB workflow were exercised on hardware, or that any temperature readings were calibrated.

[← Main project README](../README.md) · [Final engineering report](../01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf) · [Circuit calculations](calculations.md) · [Hardware and PCB guide](hardware-pcb-guide.md)

## 1. Choose what you want to examine

| If you want to… | Open this file | What you will learn |
|---|---|---|
| Understand the real-hardware ESP32 sketch | [`thermobench.ino`](../04_Firmware_and_Python/thermobench.ino) | GPIO34 ADC, averaging, NTC model, serial output, fault and HOT states |
| Inspect the desktop measurement interface | [`dashboard.py`](../04_Firmware_and_Python/dashboard.py) | USB connection, labeled synthetic demo, live display, CSV recording |
| Understand CSV validation and plotted results | [`station.py`](../04_Firmware_and_Python/station.py) | Row parsing, provenance checks, acceptance logic, summary JSON and PNG |
| Explore the original mathematical demo | [`bench.py`](../04_Firmware_and_Python/bench.py) | 10k nominal model, CLI serial capture, explicitly **synthetic** demonstrations |
| Examine automated unit tests | [`test_bench.py`](../04_Firmware_and_Python/test_bench.py), [`test_station.py`](../04_Firmware_and_Python/test_station.py) | Nine tests covering nominal math, faults, hysteresis, data validation and analysis |
| Set up the project in Windows | [`BUILD_STEPS.md`](../04_Firmware_and_Python/BUILD_STEPS.md) | Full hardware/software workflow, prerequisites, checks and cautions |
| Inspect the independently configured Wokwi simulation | [`sketch.ino`](../10_Wokwi_Simulation/sketch.ino) and [`diagram.json`](../10_Wokwi_Simulation/diagram.json) | Virtual NTC module, ESP32 behavior and separate simulator evidence |
| Find dependency names | [`requirements.txt`](../04_Firmware_and_Python/requirements.txt) | `numpy`, `matplotlib`, `pyserial` (Tkinter comes from suitable Python installs) |
| Inspect historical report builders | [`build_guide.py`](../04_Firmware_and_Python/build_guide.py), [`build_report.py`](../04_Firmware_and_Python/build_report.py) | Legacy ReportLab-based PDF generators; not the recommended first-run route |

Start with `BUILD_STEPS.md` before applying power, flashing firmware, or connecting the serial port. If you only want to explore software, run the **SYNTHETIC** demo first.

## 2. The software data flow

```text
[NTC + external voltage divider + RC filter]  (physical breadboard circuit)
                        |
                        v
               ESP32 GPIO34 (ADC)
                        |
              thermobench.ino (archived)
                        |
          serial: ms,mv,temp_c,status
                        |
                        v
               dashboard.py (USB mode)
                |                  |
          live display          CSV capture
                                   |
                      source,ms,mv,temp_c,status
                                   |
                                   v
                             station.py
                                   |
                         summary.json + capture.png
```

In its alternative **Demo** mode, `dashboard.py` creates simulated readings with a `SYNTHETIC` source label. `bench.py` can also make separate deterministic synthetic datasets and plots. Neither should be presented as new hardware measurements.

## 3. The ESP32 sketch — what each section actually does

**Source:** [`04_Firmware_and_Python/thermobench.ino`](../04_Firmware_and_Python/thermobench.ino)

1. **Board assumption:** `PIN = 34` selects GPIO34 on an original ESP32-WROOM-style development board. GPIO availability and ADC behavior must be checked for the actual module.
2. **Nominal constants:** `VS_MV = 3200`, `RF = 10000`, `R25 = 10000`, `BETA = 3950`. These are *source-code assumptions*, not proven calibration constants.
3. **ADC setup:** `analogReadResolution(12)` and `analogSetPinAttenuation(PIN, ADC_11db)` configure the Arduino-ESP32 readout. The code uses `analogReadMilliVolts()`, not simple `raw_count/4095 * 3300` scaling.
4. **Sampling:** The loop schedules roughly every **200 ms** and averages **16** millivolt readings with `delay(1)` between readings. Nominal report rate: **5 rows per second**; assess real timing from logs.
5. **Voltage-to-resistance:** For the source's assumed divider orientation, `r = RF * mv / (VS_MV - mv)`. The next line inverts the Beta model to estimate thermistor temperature.
6. **Classification:** It sets `LOW_FAULT` for 100 mV or below; `HIGH_FAULT` for 2900 mV or above; `OUT_OF_RANGE` when the computed value is outside 15–55°C or nonfinite. For valid temperatures, `HOT` activates at 45°C and clears at 43°C.
7. **Serial format:** The firmware prints header `ms,mv,temp_c,status` at 115200 baud. A fault with nonfinite temperature can have an **empty** `temp_c` field.

**Important configuration difference:** The archived sketch assumes a **10,000-ohm fixed resistor**, while the separately documented LTspice/KiCad circuit uses **9.82 kΩ for R1**, with **990 Ω R2** and **100 nF C1**. Do not combine the sketch's default constants and circuit predictions without identifying the physical parts and firmware version. The precise flashed binary for all archived hardware CSVs was not preserved.

**State behavior note:** On a fault or out-of-range reading, the firmware resets the stored HOT state to `NORMAL`. That behavior is in the current source; it has not been qualified as appropriate for a safety-critical temperature alarm.

## 4. The desktop dashboard — `dashboard.py`

The [Tkinter desktop program](../04_Firmware_and_Python/dashboard.py) provides a COM-port selector, Refresh, Connect USB, Demo, Disconnect, a temperature trend chart, and Start/Stop CSV recording.

- **Connect USB:** opens the selected port at **115200 baud**, reads serial lines on a worker thread, passes decoded records through `station.parse_line`, and queues updates to the Tkinter UI.
- **Demo:** generates a nominal ~25°C signal with small simulated variations, labeled `SYNTHETIC`. It does not access physical equipment.
- **Recording:** creates `captures/hardware_*.csv` or `captures/synthetic_*.csv` files with fields `source,ms,mv,temp_c,status`.
- **Session protection:** refuses to start a second active session; stops an active recording on a non-increasing device timestamp; displays stale-data status after about two seconds without a fresh row; tracks rejected rows.
- **Trend view:** displays valid `NORMAL`/`HOT` temperatures from the most recent 300 records, not a calibrated temperature chart.

The dashboard reads the **four-column serial protocol** but saves the **five-column capture protocol** by adding the origin label. That distinction matters when selecting input for `station.py`.

The source documents that GUI-window and live USB operation were not independently verified in the original software authoring environment. Run them yourself before describing them as tested.

## 5. CSV analyzer — `station.py`

**Source:** [`04_Firmware_and_Python/station.py`](../04_Firmware_and_Python/station.py)

`parse_line` validates the firmware's `ms,mv,temp_c,status` values, including finite numbers, valid states, fault/temperature consistency, and voltage bounds. `load_csv` expects a **five-column** dashboard/capture CSV with a `source` column, and **rejects mixed `HARDWARE` + `SYNTHETIC` provenance in one file**.

`analyze` writes:

- `summary.json`: input source, row counts, rejects, elapsed duration, estimated sample rate, mean voltage, optional DMM difference, modeled-temperature standard deviation and check results.
- `capture.png`: ADC millivolts and modeled temperature against elapsed time.

| Analyzer check | What the code checks | Interpretation |
|---|---|---|
| `timestamps_increasing` | Strictly increasing device times | Detects resets/nonmonotonic input; not a timing accuracy certificate |
| `cadence_4p5_to_5p5_hz` | Average rate within 4.5–5.5 Hz | A preliminary cadence check |
| `parser_clean` | No rejected CSV rows | Input-format consistency, not measurement accuracy |
| `continuous_valid_temperature` | All states are `NORMAL` or `HOT` | No faults/out-of-range in that recording |
| `steady_repeatability_sd_le_0p15_c` | SD ≤ 0.15°C for an eligible ≥59-second recording | Only meaningful for a **settled fixed-input** run |
| `voltage_mean_vs_dmm` (optional) | Absolute difference from entered DMM mV within chosen tolerance (default 30 mV) | User-selected electrical agreement threshold; **not** calibrated uncertainty |

**Caveat:** The analyzer does not automatically prove that a session was genuinely stationary. A programmatic `PASS` is insufficient if the input was warming/cooling or the reference was not synchronized.

## 6. `bench.py` — model, serial capture and synthetic teaching examples

This [original script](../04_Firmware_and_Python/bench.py) contains `voltage(t)` and `decode(v)` functions for a nominal 3.2-V, 10k fixed-resistor, 10k/Beta-3950 model. It also offers two CLI modes:

- `demo`: outputs **synthetic** transfer, sweep and statistical process control examples (CSV, PNG and JSON). These are teaching datasets, not real process capability measurements.
- `capture`: reads the four-column serial stream from a specified COM port and saves a five-column CSV explicitly labeled `HARDWARE`.

Do not compare its nominal 10k divider curve to the separate 9.82k LTspice model without accounting for the parameter difference. Do not use a synthetic Cp/Cpk value as a hardware performance claim.

## 7. Windows quick start — software only first

Open **PowerShell** in the repository, then change into the code directory. This avoids the path assumptions used by the scripts.

```powershell
Set-Location .\04_Firmware_and_Python

py --version
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest discover -v -p "test_*.py"
```

The repository contains **five `test_bench.py` methods** and **four `test_station.py` methods** = **nine unit tests**. Older documentation reports that nine passed in its authoring environment; **these commands must be executed locally to verify your current Windows environment**.

To inspect the GUI in labeled software-only mode:

```powershell
.\.venv\Scripts\python -m tkinter
.\.venv\Scripts\python dashboard.py
```

Close the small Tkinter test window. In the dashboard click **Demo**. Record a synthetic session, then Stop recording and Disconnect. Use the **exact filename created on your computer** for analysis:

```powershell
.\.venv\Scripts\python station.py "captures\synthetic_YYYYMMDD_HHMMSS_ffffff.csv" --out analysis_demo
```

Replace the placeholder with the actual `captures\synthetic_*.csv` file name. The results will appear in `analysis_demo/summary.json` and `analysis_demo/capture.png`. A synthetic PASS demonstrates software rules only.

You can separately create a deterministic software demonstration:

```powershell
.\.venv\Scripts\python bench.py demo --out results_demo
```

This generates `SYNTHETIC` examples; do **not** add those to the original hardware dataset directory.

## 8. USB/hardware procedure — only after wiring checks

Follow the full [build and electrical-test guide](../04_Firmware_and_Python/BUILD_STEPS.md) and [hardware/PCB walkthrough](hardware-pcb-guide.md) for power-off wiring, component identity, correct GPIO34 board, and DMM checks before using a live port. With a known resistor in place of the thermistor, first compare the predicted divider voltage with a DMM reading.

```powershell
.\.venv\Scripts\python -m serial.tools.list_ports
.\.venv\Scripts\python dashboard.py
```

Select your actual COM port, click **Connect USB**, and make a new `HARDWARE` capture after readings settle. Do not simultaneously open the Arduino Serial Monitor and dashboard on one COM port.

For an independently *measured and simultaneously recorded* DMM value (example command uses 1600 mV **only if your DMM really measured that**):

```powershell
.\.venv\Scripts\python station.py "captures\hardware_ACTUAL_FILE.csv" --out analysis_hardware --dmm-mv 1600 --tolerance-mv 30
```

The 30-mV threshold is a preliminary user choice, not a certified instrument accuracy. Avoid asserting that a firmware comparison is calibrated without part identification, traceable reference data and uncertainty analysis.

## 9. Wokwi virtual firmware is a separate configuration

[Wokwi source](../10_Wokwi_Simulation/sketch.ino) + [wiring diagram JSON](../10_Wokwi_Simulation/diagram.json) use a **three-pin NTC module with its own internal 10-kΩ fixed divider** and a nominal 3.3-V supply. That sketch uses **16 raw `analogRead` counts**, then converts by `avg_counts/4095 × 3300 mV`, unlike the archived physical sketch's `analogReadMilliVolts()`.

The [user-executed Wokwi test evidence](../10_Wokwi_Simulation/README_WOKWI.md) includes selected 25°C/35°C/46°C cases, hysteresis observations, and an out-of-range event. The [CSV excerpts](../10_Wokwi_Simulation/Evidence/Wokwi_Observed_Log_Excerpts.csv) contain **selected transcribed output rows**, not complete raw logs. This is simulator evidence, **not** physical sensor calibration or proof of the external KiCad analog network.

## 10. Tests, known gaps and defensible portfolio claims

**Source-backed accomplishments:** The repository includes executable Python unit-test definitions, a desktop dashboard implementation, CSV validation code, a nominal sensor/temperature model, archived real ESP32 data, and separate Wokwi test evidence. The source files are inspectable and the workflow can be reproduced subject to the requirements and hardware availability.

**Not established by this guide:** Arduino compile/upload of the archived `thermobench.ino`; a successful GUI+USB run on the user’s exact current machine; a byte-for-byte match between archived source and firmware used for all physical CSVs; externally calibrated absolute temperature accuracy; fabricated-board tests; safety-qualified fault/alarm behavior.

**Useful next verification work:** Run the nine local tests and save output; compile firmware for your identified ESP32 board and record versions; capture a fresh DMM-correlated electrical test; document a hardware fault and recovery; distinguish calculated, simulated, synthetic and physical evidence in all graphs and reports.

**Historical PDF builders:** `build_guide.py` and `build_report.py` require `reportlab`, which is **not included** in the present `requirements.txt`. `build_report.py` also expects a historical `project/` and `output/pdf/` layout, so do not treat it as a ready-to-run command from the current repository root without inspecting and adapting its paths. The current 23-page [master report](../01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf) is the presentation artifact to read first.

---

**Navigation:** [Back to homepage](../README.md) · [Engineering calculations](calculations.md) · [Hardware and PCB](hardware-pcb-guide.md) · [Physical CSV files](../05_Hardware_CSV/) · [Measured-data figures](../06_Analysis/) · [Original software directory](../04_Firmware_and_Python/)
