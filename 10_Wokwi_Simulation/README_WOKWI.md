# ThermoBench - Wokwi Virtual Firmware Validation (user-executed, 21 Oct 2026)

## Run these files
- `sketch.ino` and `diagram.json`: the corrected working Wokwi ESP32/NTC simulation files used for the observed test series. Paste into https://wokwi.com/projects/new/esp32.
- Wiring: NTC VCC -> ESP32 3V3; NTC GND -> ESP32 GND.1; NTC OUT -> ESP32 GPIO34.
- Serial: 115200 baud with `ms,mv,temp_c,status` at nominal 200 ms intervals.

## Observed and verified
- 25 C: 1650.40 mV, 24.989 C, NORMAL.
- 35 C: 1300.66 mV, 35.000 C, NORMAL.
- 46 C: 973.48 mV, 45.987 C, HOT.
- At 44.003 C on cooling: HOT maintained.
- At 43.112 C: HOT maintained; at 42.998 C: NORMAL reset.
- Cooling to 24.989 C: NORMAL restored.
- Out-of-range event observed up to 63.304 C with OUT_OF_RANGE status. The sketch resets HOT latch on out-of-range; review before any safety-critical use.

## Evidence origin and scope
`Evidence/Wokwi_Observed_Log_Excerpts.csv` contains exact selected user-provided serial output rows (NOT a complete session export). The three sessions have independent timestamps. `Figures/` contains newly generated graphs *derived solely from these rows*. Original screenshots are saved in `Evidence/`.

Wokwi's virtual thermistor module has an internal 10k divider. It does NOT emulate the physically-built 9.82k R1, 990-ohm R2, 100 nF C1 network. The KiCad/physical data and LTspice analyses remain authoritative for that separate circuit. This module is a firmware-functionality demonstration only. These results are not real device temperature-accuracy measurements.

## Re-run test
1. Paste the two source files into Wokwi ESP32 project and start simulation.
2. Observe 25 C NORMAL and then change to 35 C NORMAL.
3. Move to 46 C; wait for HOT.
4. Lower to 44 C, check HOT holds. Lower to 42 C, check NORMAL.
5. Return to 25 C and check baseline.
6. Save full fresh serial logs/screenshots if repeatability studies are needed.

## Future work
- Validate low-voltage/high-voltage fault injection separately.
- Improve the out-of-range response to use a latched FAULT alarm with explicit operator handling if relevant.
- Test firmware on real ESP32 and validate temperature with a calibrated reference.
