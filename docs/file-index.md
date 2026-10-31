# ThermoBench - Complete File Index

[Back to project homepage](../README.md)

This index is for readers who want to locate and reproduce the engineering work. **Start with the final report or a specific file below.** The public repository preserves historical package names and file paths for traceability.

> Evidence key: **HARDWARE** = archived breadboard ESP32 CSV recordings. **SIMULATION** = LTspice or Wokwi. **SYNTHETIC** = software demonstration only. **DESIGN ONLY** = PCB not fabricated or bench tested. Estimated temperatures from the firmware are not independently calibrated thermometer measurements.

## 1. Final reports and overview

| What to open | File | Why it matters |
| --- | --- | --- |
| **Final report (23 pages)** | [ThermoBench engineering report](../01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf) | Best complete project narrative, results, limitations |
| Interview presentation | [Interview study guide](../01_Report/ThermoBench_Interview_Study_Guide.pdf) | Explaining the work during an interview |
| Historical project map | [README_START_HERE](../README_START_HERE.md) | Original evidence package inventory |
| Figure/page map | [Figures and schematics index](../FIGURES_AND_SCHEMATICS_INDEX.md) | Report pages and related figures |

## 2. Electrical schematic, PCB, and calculations

| What to open | File | Status |
| --- | --- | --- |
| **Schematic PDF** | [Open schematic without KiCad](../03_CAD_Visuals/KiCad_Schematic_Original_A4.pdf) | Design illustration |
| KiCad project | [Editable `.kicad_pro`](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pro) | DESIGN ONLY |
| KiCad schematic | [Editable `.kicad_sch`](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_sch) | DESIGN ONLY |
| **PCB layout** | [Editable `.kicad_pcb`](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pcb) | DESIGN ONLY |
| PCB 3D render | [Angled view](../03_CAD_Visuals/3D_Angled_Original.png) | Render, not a physical PCB photo |
| PCB 3D render | [Top view](../03_CAD_Visuals/3D_Top_Original.png) | Render, not manufacturing proof |
| Component / PCB guide | [Hardware and PCB walkthrough](hardware-pcb-guide.md) | Read first to understand connector pins and test points |
| **Worked calculations** | [NTC, divider, filter and ADC](calculations.md) | Assumptions, formulas, examples and source mapping |
| Preliminary Gerbers | [Manufacturing warning](../07_Reference_Exports/Preliminary_Gerbers/NOT_FOR_MANUFACTURING.txt) | **NOT APPROVED FOR FABRICATION** |

The KiCad project, schematic, and PCB source files are kept together in `02_KiCad_Source/`. Do not relocate them separately.

## 3. Firmware, software, and how to run it

| What to open | File | Purpose |
| --- | --- | --- |
| **ESP32 source** | [thermobench.ino](../04_Firmware_and_Python/thermobench.ino) | Nominal firmware model, ADC and serial output |
| **Python dashboard** | [dashboard.py](../04_Firmware_and_Python/dashboard.py) | Live serial or labeled demo display |
| Shared CSV analysis | [station.py](../04_Firmware_and_Python/station.py) | Parser, checks, plots and JSON summary |
| Serial capture + synthetic demo | [bench.py](../04_Firmware_and_Python/bench.py) | Modes and data provenance must not be confused |
| Software tests | [test_station.py](../04_Firmware_and_Python/test_station.py) / [test_bench.py](../04_Firmware_and_Python/test_bench.py) | Existing Python tests |
| Dependencies | [requirements.txt](../04_Firmware_and_Python/requirements.txt) | Python packages |
| **Build / run instructions** | [BUILD_STEPS.md](../04_Firmware_and_Python/BUILD_STEPS.md) | Windows setup and test instructions |
| **Code explanation** | [Firmware and Python guide](firmware-python-guide.md) | Code walkthrough and verification boundaries |

Archived firmware compilation, USB live behavior and physical alarm triggering are not independently proven by the documentation.

## 4. Physical measurements and graphs

| What to open | File | Purpose |
| --- | --- | --- |
| **Original hardware CSV folder** | [05_Hardware_CSV](../05_Hardware_CSV/) | Four archived files, **1,334 HARDWARE-labeled readings** total |
| **Results walkthrough** | [Results and validation guide](results-validation-guide.md) | How to read the graphs and statistics |
| Measurement methodology | [Analysis_Methodology.md](../06_Analysis/Analysis_Methodology.md) | Source, sample SD and traceability |
| Numerical results | [measurement_metrics.json](../06_Analysis/measurement_metrics.json) | Per-file summary statistics |
| **Thermal response graph** | [thermal_response.png](../06_Analysis/thermal_response.png) | Measured-run temperature estimate trend |
| Voltage vs. temperature | [voltage_vs_temperature.png](../06_Analysis/voltage_vs_temperature.png) | Estimated temperature versus ADC voltage |
| Steady-state graph | [steady_state_temperature.png](../06_Analysis/steady_state_temperature.png) | 641-row stable capture |
| Thermal vs. voltage | [thermal_voltage.png](../06_Analysis/thermal_voltage.png) | Voltage behavior in physical data |
| Initial warming | [initial_warming.png](../06_Analysis/initial_warming.png) | Early temperature response |
| **Read-only CSV verifier** | [verify_hardware_csv.py](../tools/verify_hardware_csv.py) | Rechecks archived CSV counts and statistics |

All four archived CSVs report `NORMAL`. They do not demonstrate a physical `HOT` transition or physical injected fault.

## 5. Simulations — separate from physical data

| Environment | Open | Evidence boundary |
| --- | --- | --- |
| **LTspice** | [Simulation guide](../09_LTspice_Simulation/README_LTspice.md) | Analog model, not measured temperature accuracy |
| LTspice netlists and raw outputs | [Original circuits and results](../09_LTspice_Simulation/Original_Circuits_and_Results/) | Inspect source model and original outputs |
| LTspice numeric data | [Extracted data](../09_LTspice_Simulation/Extracted_Data/) | 25–27°C values and filter frequency response |
| LTspice plots | [Graphs and evidence](../09_LTspice_Simulation/Graphs_and_Evidence/) | Simulated circuit response |
| **Wokwi** | [Virtual firmware validation guide](../10_Wokwi_Simulation/README_WOKWI.md) | Three-pin virtual NTC module with internal divider |
| Wokwi firmware | [sketch.ino](../10_Wokwi_Simulation/sketch.ino) | Virtual circuit firmware, not proof of flashed ESP32 binary |
| Wokwi circuit | [diagram.json](../10_Wokwi_Simulation/diagram.json) | Virtual sensor layout |
| Wokwi evidence | [Observed excerpts and screenshots](../10_Wokwi_Simulation/Evidence/) | Selected observed simulator rows, not complete run |
| Wokwi plots | [Figures](../10_Wokwi_Simulation/Figures/) | Figures derived from virtual observations |
| **SYNTHETIC demo only** | [Synthetic sample data](../08_Synthetic_Demo_Only/) | Not physical evidence |

## 6. Historic exports and caveats

The files under [07_Reference_Exports](../07_Reference_Exports/) preserve preliminary manufacturing exports and historical documents. Do not send preliminary Gerbers for manufacturing without a fresh design review and fabrication checks.

The original [README_START_HERE.md](../README_START_HERE.md) references a historic `MANIFEST_SHA256.txt` from the source package. It should **not** be treated as a hash manifest covering documentation added later through Git pull requests. Use Git commits and/or generate a new versioned release manifest if a full current snapshot is needed.

[Return to README](../README.md)
