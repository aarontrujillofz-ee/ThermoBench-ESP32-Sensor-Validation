# THERMOBENCH | Full engineering portfolio, Rev 2.0 (21 Oct 2026)

## Start here
**Master verified report**: `01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf` (23 pages). This replaces the earlier 19-page PDF's two unexecuted-Wokwi pages with six new pages documenting the user-executed Wokwi tests and adds a revised cover.

**Interview study guide**: `01_Report/ThermoBench_Interview_Study_Guide.pdf` (7 pages, earlier standalone guide; the updated Wokwi results are in the 23-page master report).

**Editable KiCad project**: `02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pro`, matched .kicad_sch and .kicad_pcb.

**Wokwi virtual test bench**: `10_Wokwi_Simulation/sketch.ino` + `diagram.json` (user-executed). Read `10_Wokwi_Simulation/README_WOKWI.md` and `WOKWI_TEST_CASES.md`.

**LTspice**: `09_LTspice_Simulation/Original_Circuits_and_Results/` includes original user-run .cir, .raw, .log; extracted data and figures are in adjoining folders.

**Real ESP32 data**: four original HARDWARE CSV files, `05_Hardware_CSV`; regenerated measured charts and metrics in `06_Analysis`.

## Full folder map
01_Report - revised 23-page report, interview study guide.
02_KiCad_Source - native PCB/schematic/project.
03_CAD_Visuals - schematic, PCB layers and 3D renders; report visual figures.
04_Firmware_and_Python - physical prototype ESP32 firmware, Python GUI/processing, tests and build notes.
05_Hardware_CSV - original physically measured CSV traces (four files).
06_Analysis - physical-source analysis PNGs, metrics and method.
07_Reference_Exports - preliminary Gerbers/historical material, not manufacturing-approved.
08_Synthetic_Demo_Only - synthetic demonstration records, clearly segregated.
09_LTspice_Simulation - original user-run files, extracted simulations and plots.
10_Wokwi_Simulation - VERIFIED virtual Wokwi sensor + ESP32 firmware, test logs excerpts, state diagrams, plots, source and screenshots; historical untested starter archived separately.

## Validated Wokwi outcomes (virtual, not hardware)
25 C: 24.989 C / 1650.40 mV / NORMAL.
35 C: 35.000 C / 1300.66 mV / NORMAL.
46 C: 45.987 C / 973.48 mV / HOT.
44.003 C: HOT maintained; 43.112 C: HOT maintained; 42.998 C: NORMAL reset.
Over-range: OUT_OF_RANGE up to 63.304 C recorded, but sketch clears HOT latch during faults - future fail-safe design review recommended.

Evidence CSV contains selected exact transcribed lines, NOT complete raw logs. Original user-supplied screenshots are included; Wokwi figures derived from logged selected points.

## Critical limitations
Breadboard data comes from physical hardware. PCB is UNFABRICATED and not hardware-tested. KiCad reportedly had zero active DRC errors but 5 ignored rule categories; no manufacturing signoff. Wokwi simulates a three-pin NTC sensor with built-in divider, NOT R1=9.82k/R2=990/C1=100nF analog front end. LTspice models that analog circuit; it is not proof of real temperature accuracy. No reference thermometer or demonstrated physical board assembly. The archived bench firmware is not proven byte-identical to every flashed binary.

All files in the bundle (excluding manifest itself) are recorded in MANIFEST_SHA256.txt.
