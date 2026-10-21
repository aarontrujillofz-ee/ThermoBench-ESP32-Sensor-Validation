# ThermoBench | Wokwi ESP32 NTC simulation (new candidate)

**Status: Prepared source, NOT remotely executed or validated in Wokwi in this bundle.**
This is an optional virtual firmware exercise added after the original LTspice project.
It does not replace the physical breadboard recordings or the KiCad design.

## Quick start (web simulator)
1. Go to https://wokwi.com/projects/new/esp32 .
2. Replace the default Arduino sketch with the complete `sketch.ino` from this folder.
3. Replace the default `diagram.json` with this folder's `diagram.json`.
4. Press the green Run / Play control. Open the serial monitor.
5. Click the NTC temperature sensor and change its temperature (e.g. 25, 35, 45, 50°C).
6. Observe the `ms,mv,temp_c,status` output at a nominal interval of 200 ms.
7. If you export serial data, label it **SYNTHETIC / WOKWI**. Never merge it into `05_Hardware_CSV`.

## Scope and known differences from the physical ThermoBench
- Wokwi's `wokwi-ntc-temperature-sensor` has a **built-in 10 kΩ series resistor** and nominal 10 kΩ/B3950 NTC. Its analog OUT connects straight to ESP32 GPIO34 here.
- Real KiCad ThermoBench has **R1 = 9.82 kΩ**, R2 = 990 Ω and C1 = 100 nF; the module and simulator do NOT faithfully simulate this entire front end. Use `09_LTspice_Simulation` for the actual circuit response and filter calculations.
- The 3.3 V scaling from ADC counts to `mv` is **nominal**, not an ESP32 ADC calibration. Simulator ADC behavior may differ from a physical ESP32.
- This is a newly prepared sketch modeled on the archived firmware interface. It is **not proof that the previously recorded real ESP32 runs used this binary**, and it has not yet been run online by the assistant.
- Sampling averages 16 `analogRead` calls and formats the firmware's four-column serial message, but it is not a byte-for-byte copy of the actual 04_Firmware_and_Python/thermobench.ino.
- Earlier Arduino Uno/potentiometer and NTC Wokwi exercises were discussed previously, but their original project assets were not supplied in this bundle and are **not recreated as past test evidence**.

## Suggested virtual test cases (not claimed as run)
| Sensor temperature | Expected model action |
| --- | --- |
| 25°C | `NORMAL` |
| 35°C | `NORMAL` |
| 45°C | `HOT` (may depend on analog quantization) |
| 50°C | `HOT` |
| 60°C | `OUT_OF_RANGE` |

Validation checklist after user runs Wokwi: sketch compiles, NTC temperature can be changed, serial format is valid, data updates approximately every 200ms, HOT and OUT_OF_RANGE behavior matches model. Report any mismatches honestly.

## Documentation
- Wokwi NTC module details: https://docs.wokwi.com/parts/wokwi-ntc-temperature-sensor
- Wokwi resistor/analog simulation limitation: https://docs.wokwi.com/parts/wokwi-resistor
- Wokwi diagram format: https://docs.wokwi.com/diagram-format
