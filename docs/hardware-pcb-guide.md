# ThermoBench — Hardware and PCB Design Walkthrough

**Project:** ESP32 temperature sensing and validation
**Scope:** External NTC sensor interface, KiCad schematic, PCB layout, connectors, component functions, and proposed bring-up tests.
**Evidence status:** **Designed in KiCad; no manufactured or electrically tested PCB.** The repository does contain separate **physical breadboard measurements**. Neither LTspice nor Wokwi data is assembled-PCB test evidence.

> **Start here:** [Main project README](../README.md) · [Final engineering report](../01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf) · [Worked calculations](calculations.md)

## 1. What does this board do?

ThermoBench uses a negative-temperature-coefficient (NTC) thermistor: its resistance decreases as its temperature increases. A resistor and the NTC form a voltage divider. An analog RC network conditions that divider voltage before the ESP32 reads it at **ADC1 GPIO34**. Firmware can convert the sensed voltage into a **model-based temperature estimate**, record it, and evaluate alarm thresholds.

The **50 × 35 mm KiCad board is a sensor adapter**, not an ESP32 development board. It provides resistors, capacitor, headers, test points, and mounting holes. The NTC sensor connects **externally at J2**; it is *not* a populated on-board thermistor footprint in this design. The ESP32 connects externally at **J1**.

### Functional signal path (nominal external-divider design)

```text
External regulated 3.2–3.3 V rail (verify before connecting)
      |
      R1 = 9.82 kΩ      (upper divider resistor)
      |
      +---- SENSE / TP1 ---- R2 = 990 Ω ---- ADC / TP2 ----> ESP32 GPIO34
      |                                            |
      |                                         C1 = 100 nF
      |                                            |
   External NTC                                     GND
   via J2: pin 1
      |
   J2 pin 2 --------------------------------------- GND / TP3
```

The diagram is explanatory; **follow the native schematic for actual wiring and connector orientation**. Supply values used in examples are not a substitute for measuring your real ESP32 3V3 rail.

![Schematic detail](../03_CAD_Visuals/Report_Figures/Schematic_Detail.png)

**Source files:** [View PDF schematic](../03_CAD_Visuals/KiCad_Schematic_Original_A4.pdf) · [Open KiCad schematic](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_sch) · [Open complete KiCad project](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pro)

## 2. Component-by-component explanation

This table reflects the **native KiCad schematic and PCB footprint assignments**, not a verified purchased bill of materials.

| Reference | Value / footprint in KiCad | Function | Why it matters |
|---|---|---|---|
| **R1** | **9.82 kΩ**, axial **through-hole** resistor, 7.62 mm lead pitch | Upper thermistor voltage-divider resistor, from +3V3 to SENSE | Sets voltage-versus-temperature relationship together with the external NTC |
| **R2** | **990 Ω**, axial **through-hole** resistor, 7.62 mm lead pitch | Series resistor between SENSE and ADC | Works with C1 and the divider's source resistance to filter high-frequency signals |
| **C1** | **100 nF**, radial/disc **through-hole** capacitor, 5.00 mm pitch | Connected between ADC and ground | Attenuates higher-frequency variations at the ADC node |
| **J1** | 3-pin 2.54 mm through-hole header | Interface to external ESP32: +3V3, GND and ADC | Carries power, ground and analog signal between boards |
| **J2** | 2-pin 2.54 mm through-hole header | Connection for external NTC sensor | Places sensor between SENSE and GND |
| **TP1** | Through-hole test pad, 2.0 mm pad / 1.0 mm drill | SENSE-node measurement | Compare divider voltage against the predicted value |
| **TP2** | Through-hole test pad, 2.0 mm pad / 1.0 mm drill | ADC-node measurement | Compare filtered ADC input with SENSE at steady state |
| **TP3** | Through-hole test pad, 2.0 mm pad / 1.0 mm drill | Ground reference | Reference point for DMM/scope measurements |
| **H1, H2** | Two non-plated 2.2 mm mounting holes | Mechanical mounting | Screw-head, standoff and component clearances still require verification |

**Important:** This particular PCB uses **through-hole resistors and capacitor**, not 0805 SMD footprints. Your separate 0805 soldering-practice work should not be described as assembly of this PCB.

### Why is the thermistor external?

On the current KiCad design, **J2 connects an external two-wire NTC** to SENSE and GND. Locating the thermistor away from the ESP32 can help avoid bias from the microcontroller's heat. This does not establish accuracy: sensor identity, mounting, ambient reference temperature, tolerances, and calibration remain open questions.

## 3. Connector pinout and electrical test points

The following assignments were inspected in the **native `.kicad_pcb` net connections**. Read the schematic/footprint pin numbers rather than assuming a left-to-right physical orientation in a photograph.

| Connector / test point | Pin | KiCad net | Expected connection |
|---|---:|---|---|
| **J1** | 1 | `/+3V3` | Regulated 3.3 V supply from suitable ESP32 3V3 output (measure actual rail) |
| **J1** | 2 | `GND` | ESP32 ground |
| **J1** | 3 | `/ADC` | ESP32 ADC1 **GPIO34**, on a compatible original ESP32 board |
| **J2** | 1 | `/Sense` | NTC terminal 1 |
| **J2** | 2 | `GND` | NTC terminal 2 |
| **TP1** | 1 | `/Sense` | Divider output before R2 |
| **TP2** | 1 | `/ADC` | ADC input after R2 |
| **TP3** | 1 | `GND` | DMM/scope ground reference |

For a nominal **10 kΩ NTC at 25 °C**, **R1 = 9.82 kΩ**, and a **3.20 V supply**, the settled ideal divider prediction is **1.61453 V**. This is a *calculation*, not a previously recorded TP1/TP2 measurement on this unbuilt PCB. At DC, TP1 and TP2 should be close if the ADC's input loading is small; transients and ADC sampling can create differences.

See the [step-by-step calculations](calculations.md) for the NTC Beta equation, divider voltage and RC cutoff (about **267.73 Hz** at nominal 25 °C with the divider source resistance included).

## 4. How to explore the PCB design in KiCad

Keep these three files **together in the same folder**:

- [ThermoBench_Sensor_Adapter.kicad_pro](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pro) — KiCad project settings.
- [ThermoBench_Sensor_Adapter.kicad_sch](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_sch) — editable circuit schematic.
- [ThermoBench_Sensor_Adapter.kicad_pcb](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pcb) — editable board layout.

1. Open the `.kicad_pro` file with a compatible **KiCad 10** installation.
2. Open **Schematic Editor** and trace the supply → R1 → SENSE → external J2 NTC/GND path. Trace SENSE → R2 → ADC and C1 → GND. Compare pin numbers in the schematic against J1/J2 on the PCB.
3. Open **PCB Editor**. Locate R1, R2, C1, J1, J2, TP1, TP2, TP3 and H1/H2. Inspect the copper traces, pad assignments, silkscreen, mounting-hole clearance, and board outline.
4. Use **3D Viewer** to examine the visual component arrangement. The 3D render is an illustration of CAD, not a photo of a manufactured board.
5. Run **ERC** (schematic) and **DRC** (PCB) in your local KiCad version; save the results including ignored checks, warnings and errors. Historical statements of “zero active DRC errors” are *not* a fresh validation or manufacturing signoff.
6. Confirm the outline dimensions, component body dimensions, hole placements, copper clearances, and intended connector mating parts against datasheets before any fabrication decision.

### View the design directly on GitHub (no KiCad installation needed)

| File | What to inspect |
|---|---|
| [3D angled render](../03_CAD_Visuals/3D_Angled_Original.png) | Position of through-hole resistors, capacitor, connectors and test pads |
| [3D top render](../03_CAD_Visuals/3D_Top_Original.png) | Top-down component placement and silkscreen |
| [Top copper PDF](../03_CAD_Visuals/Layer_PDFs/F_Cu.pdf) | Front copper geometry |
| [Bottom copper PDF](../03_CAD_Visuals/Layer_PDFs/B_Cu.pdf) | Back copper geometry |
| [Front silkscreen PDF](../03_CAD_Visuals/Layer_PDFs/F_Silkscreen.pdf) | Visible labels and reference designators |
| [Board outline PDF](../03_CAD_Visuals/Layer_PDFs/Edge_Cuts.pdf) | Board perimeter and mechanical layout |

![Designed PCB, angled KiCad 3D render](../03_CAD_Visuals/3D_Angled_Original.png)

### PCB dimensions and stack-up

- **Nominal outline:** 50 × 35 mm, as drawn by a rectangular `Edge.Cuts` outline.
- **Thickness in `.kicad_pcb`:** 1.6 mm **design setting**, not verified as manufactured.
- **Front and back copper layers:** present in CAD. This does not confirm production layer count, fab stack-up, impedance or acceptable clearances.
- **Two mounting holes:** 2.2 mm non-plated holes in the saved footprint design; mechanical hardware fit is unverified.

## 5. Proposed safe inspection and bring-up plan — not completed PCB results

The steps below apply **if the design is later independently reviewed, fabricated and assembled**. They are future-work procedures, **not a claim that the PCB exists**.

| Stage | Action | Evidence to capture |
|---|---|---|
| **Design review** | Check ERC/DRC, ignored-rule categories, pin/net mapping, clearances, footprints, 3D geometry, and mounting | KiCad reports, screenshots, revision and review notes |
| **Parts and assembly** | Verify actual resistor values, capacitor value, NTC part/datasheet and header orientation before soldering | Actual BOM, component IDs, assembly photos |
| **Unpowered safety** | Inspect for bridges, damaged pads and incorrect connections; use DMM continuity/resistance only with all power disconnected | Inspection checklist, continuity measurements, corrections |
| **Power-up** | Use an appropriate low-voltage 3V3 source. Check for shorts and confirm rail voltage and current before attaching an ESP32 ADC | DMM readings, board/revision ID, setup photos |
| **Electrical check** | At a stable known resistor substitution, compare calculated TP1 vs DMM TP1; compare TP1 and TP2, and then GPIO34 ADC output | Nominal calculation, actual supply/resistors, synchronized DMM/ADC rows |
| **Thermal response** | Install identified external NTC, record gentle warming/cooling and model-equivalent temperature response | Raw physical CSV, plots, sensor and firmware provenance |
| **Fault behavior** | Power off before disconnecting or restoring sensor wiring; document low/high/open sensor outcomes | Test procedure, actual status logs, pass/fail evidence |
| **Accuracy characterization** | If available, compare with a traceable or specified-uncertainty reference thermometer at controlled stable temperatures | Reference, uncertainty budget, comparison error by point |

**Safety notes:** Do not feed **5 V/VIN** into GPIO34 or the ADC pin. Do not measure resistance on a powered circuit. Disconnect power before rewiring, swapping parts, or performing continuity checks. Do not assume the 990 Ω series resistor makes an ESP32 input 5-V-tolerant. Verify the particular ESP32 model and its valid ADC pins before using GPIO34.

## 6. Manufacturing files: archived, not approved

The repository retains [preliminary Gerber exports](../07_Reference_Exports/Preliminary_Gerbers/) **only as a historical CAD artifact**. The [manufacturing warning](../07_Reference_Exports/Preliminary_Gerbers/NOT_FOR_MANUFACTURING.txt) explicitly states that component fit and screw clearance are unverified, and validated Excellon drill files were not found in the recovered archive.

**Do not submit these archived Gerbers for fabrication.** If you choose to manufacture this board, first finish design verification and mechanically check it, then generate and inspect a **new** fabrication package, including copper/soldermask/silkscreen, outline, drill files, and fab documentation, from the finalized native PCB. Have that package reviewed before ordering.

## 7. Keep the three evidence sources separate

| Environment | Actual evidence | What it does **not** prove |
|---|---|---|
| **Breadboard physical hardware** | [Four recorded CSV captures](../05_Hardware_CSV/), including original voltage/temperature-model readings | A populated-PCB test, independent thermometer calibration, or actual PCB manufacturability |
| **LTspice analog circuit** | [Saved netlists and analog results](../09_LTspice_Simulation/) | Physical electrical performance or temperature accuracy |
| **Wokwi firmware model** | [Three-pin NTC simulation and observed cases](../10_Wokwi_Simulation/) | Faithful reproduction of this R1/R2/C1 external analog circuit |

A further provenance limitation: one archived physical ESP32 sketch uses **10 kΩ** for its assumed fixed resistor constant, while the KiCad/LTspice divider uses **9.82 kΩ**. The exact firmware flashed for every stored hardware CSV was not preserved. Do not combine these sources into a single claimed calibrated result.

## 8. Questions to answer in an engineering interview

- **Why use an NTC thermistor?** Its resistance responds predictably under an assumed model, enabling a simple low-cost temperature-sensing circuit. Accuracy depends on its actual properties and validation.
- **Why R1?** It forms the voltage divider with the NTC and sets sensitivity across temperature.
- **Why R2 and C1?** They provide a first-order analog low-pass path; the divider's Thevenin resistance also affects cutoff.
- **Why TP1/TP2/TP3?** They enable independent debugging of the divider, conditioned ADC input, and shared ground.
- **What remains to finish?** A verified BOM, design-rule/mechanical review, optional new fab package, physical assembly, board bring-up, and measured validation.

## Source index

- [Main README](../README.md) · [Final report](../01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf)
- [KiCad source folder](../02_KiCad_Source/) · [Schematic PDF](../03_CAD_Visuals/KiCad_Schematic_Original_A4.pdf)
- [Calculations guide](calculations.md) · [LTspice methodology](../09_LTspice_Simulation/README_LTspice.md)
- [Hardware measurements](../05_Hardware_CSV/) · [Plots](../06_Analysis/)

**Scope statement:** Compiled from the repository's native KiCad files, public source code, archive notices, and documented measurements. All planned tests in Section 5 are proposals; no new measurements, board fabrication, or KiCad DRC run was performed for this guide.
