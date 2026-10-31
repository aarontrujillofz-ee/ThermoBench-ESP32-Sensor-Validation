# ThermoBench — Engineering Calculations and Design Reasoning

**Project:** ESP32 temperature sensing and validation  
**Purpose:** Explain the circuit equations, their inputs, and the difference between model predictions, simulator evidence, and physical measurements.  
**Status:** Educational design calculations. **Not** a temperature calibration certificate or a completed physical-PCB verification report.

> **Read first:** This document describes several **different configurations**. Do not combine their supply voltages, resistor values, or ADC conversions as though they were one verified device.

## 1. Which version of the circuit are we calculating?

| Configuration | Values from the actual source | What it establishes |
|---|---|---|
| **LTspice external-NTC circuit** | Supply 3.20 V; R1 = **9.82 kΩ** from VCC to SENSE; nominal NTC = **10 kΩ at 25 °C** from SENSE to GND; R2 = **990 Ω** from SENSE to ADC; C1 = **100 nF** from ADC to GND; NTC Beta = **3950 K** | Predicts analog voltage and filter behavior |
| **Archived physical ESP32 firmware prototype** | `VS_MV = 3200`, `RF = 10000`, `R25 = 10000`, `BETA = 3950`; reads voltage through `analogReadMilliVolts(GPIO34)` | Source-code assumptions; **not guaranteed to match the flashed firmware** for every archived physical CSV |
| **Wokwi ESP32 model** | 3.30 V nominal supply; **built-in 10 kΩ resistor** in the three-pin NTC module; NTC 10 kΩ at 25 °C, Beta 3950; uses raw `analogRead` counts and nominal scaling | Virtual firmware behavior, **not** an LTspice/KiCad analog circuit reproduction |

**Primary files:** [LTspice temperature netlist](../09_LTspice_Simulation/Original_Circuits_and_Results/ThermoBench_LTspice.cir), [LTspice filter netlist](../09_LTspice_Simulation/Original_Circuits_and_Results/ThermoBench_Filter_AC.cir), [KiCad schematic](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_sch), [archived ESP32 firmware](../04_Firmware_and_Python/thermobench.ino), and [Wokwi firmware](../10_Wokwi_Simulation/sketch.ino).

### External analog signal chain

```text
3.20 V (nominal LTspice source)
  |
 R1 = 9.82 kΩ
  |
  +-------- SENSE -------- R2 = 990 Ω -------- ADC (ESP32 GPIO34)
  |                                            |
 NTC (10 kΩ @ 25 °C)                         C1 = 100 nF
  |                                            |
 GND                                          GND
```

This is a **simplified functional diagram**. Open the actual [schematic PDF](../03_CAD_Visuals/KiCad_Schematic_Original_A4.pdf) to inspect pin assignments and connections.

## 2. NTC resistance as temperature changes

For the **assumed** Beta model:

$$
R_{NTC}(T) = R_{25}\exp\left[B\left(\frac{1}{T_K}-\frac{1}{298.15}\right)\right]
$$

- $R_{25} = 10{,}000\ \Omega$ at $25\ ^\circ\mathrm{C}$ (nominal assumption).
- $B = 3950\ \mathrm{K}$ (nominal Beta assumption).
- $T_K = T_{^\circ C} + 273.15$.
- $298.15\ \mathrm{K}$ corresponds to 25 °C.

**Worked example at 26 °C:**

1. Convert temperature to Kelvin: $T_K = 26 + 273.15 = 299.15\ \mathrm{K}$.
2. Substitute into the model:

$$
R_{NTC}(26^\circ\mathrm{C}) = 10000\exp\left[3950\left(\frac{1}{299.15}-\frac{1}{298.15}\right)\right]
\approx 9566.8\ \Omega
$$

The assumed NTC resistance **decreases** as temperature rises. Without the specific sensor datasheet or independent temperature-reference calibration, these resistance values are **model predictions**.

## 3. Thermistor voltage divider — expected voltage

At steady state, assume the ESP32 ADC input draws negligible DC current and the capacitor is fully settled. The 990 Ω series resistor therefore has approximately zero DC voltage drop. The divider equation is:

$$
V_{SENSE} \approx V_{ADC} = V_{CC}\frac{R_{NTC}}{R_1+R_{NTC}}
$$

For the **LTspice** configuration, $V_{CC}=3.20\ \mathrm{V}$ and $R_1=9820\ \Omega$.

**Worked example at 25 °C:**

$$
V_{ADC}=3.20\frac{10000}{9820+10000}=\boxed{1.614531\ \mathrm{V}}
$$

**Worked example at 26 °C:**

$$
V_{ADC}=3.20\frac{9566.8}{9820+9566.8}=\boxed{1.579103\ \mathrm{V}}
$$

### Comparison with the saved LTspice temperature run

| Simulated temperature | Model NTC resistance | Calculated ADC DC voltage | Saved LTspice `.meas` result |
|---|---:|---:|---:|
| 25 °C | 10,000.0 Ω | 1.614531 V | 1.614530802 V |
| 26 °C | 9,566.8 Ω | 1.579103 V | 1.579102993 V |
| 27 °C | 9,155.1 Ω | 1.543932 V | 1.543931484 V |

The saved simulation **actually steps 25, 26, and 27 °C**. A stale comment in the `.cir` file mentions a wider range, but the `.step` directive controls what was run. A separately supplied wider-range model is a **calculated or optional scenario**, not evidence of a completed wider-range LTspice run.

**Interpretation:** This agreement checks the calculation against the simulation **using the same idealized assumptions**. It does not prove physical temperature accuracy.

## 4. Converting an ADC voltage back into a modeled temperature

Rearrange the divider equation to infer thermistor resistance:

$$
R_{NTC} \approx R_1\frac{V_{ADC}}{V_{CC}-V_{ADC}}
$$

Then invert the Beta model:

$$
T_{^\circ C}=\left[\frac{1}{298.15}+\frac{\ln(R_{NTC}/R_{25})}{B}\right]^{-1}-273.15
$$

**Example using the 25 °C LTspice prediction:**

1. $V_{ADC}=1.614531\ \mathrm{V}$, $V_{CC}=3.20\ \mathrm{V}$, and $R_1=9820\ \Omega$.
2. $R_{NTC}\approx 9820\times 1.614531/(3.20-1.614531)\approx 10000\ \Omega$.
3. Substituting $R_{NTC}\approx R_{25}$ into the inverse Beta equation yields **25 °C (nominal modeled equivalent)**.

**Important distinction:** The archived `thermobench.ino` code uses `RF = 10000.0f`, while the original LTspice/PCB divider uses **9.82 kΩ**. For real hardware comparisons, use the **actual installed and measured** resistor value, the actual rail voltage, and the firmware version used for the recording. Otherwise, even internally consistent mathematics can produce the wrong inferred temperature.

## 5. RC filter cutoff frequency — include the divider's source resistance

The filter is **not simply** a 990 Ω resistor and 100 nF capacitor driven by an ideal zero-impedance voltage source. With the source supply treated as AC ground, the NTC divider has a Thevenin resistance:

$$
R_{TH}=R_1\parallel R_{NTC}=\frac{R_1R_{NTC}}{R_1+R_{NTC}}
$$

At nominal 25 °C:

$$
R_{TH}=\frac{9820\times10000}{9820+10000}=4954.59\ \Omega
$$

The capacitor sees approximately:

$$
R_{EQ}=R_2+R_{TH}=990+4954.59=5944.59\ \Omega
$$

The corresponding first-order cutoff frequency is:

$$
f_c = \frac{1}{2\pi R_{EQ}C_1} =
\frac{1}{2\pi(5944.59)(100\times10^{-9})}
=\boxed{267.73\ \mathrm{Hz}}
$$

The DC transfer gain for the complete supply-to-ADC path at 25 °C is:

$$
G_0=\frac{10000}{9820+10000}=0.504541\ \mathrm{V/V}
$$

$$
20\log_{10}(G_0) = -5.942\ \mathrm{dB}
$$

At the filter's cutoff, the transfer magnitude is about 3.01 dB lower than the DC gain, **approximately -8.95 dB overall**. The stored LTspice AC analysis reports a cutoff near **267.73 Hz** and has **501 frequency points from 1 Hz to 100 kHz**. See [LTspice analysis notes](../09_LTspice_Simulation/README_LTspice.md) and [AC response figure](../09_LTspice_Simulation/Graphs_and_Evidence/LTspice_AC_Bode_Magnitude_Phase.png).

**Why it matters:** The capacitor helps attenuate higher-frequency changes before the ADC. This calculation uses a 25 °C nominal thermistor; $R_{TH}$ and therefore $f_c$ vary with thermistor resistance. A cutoff frequency is **not** evidence by itself that the circuit has a specified measurement accuracy or sampled-data anti-aliasing performance.

## 6. ADC conversion — physical firmware versus Wokwi

The archived **physical ESP32 firmware** uses:

```cpp
float mv = 0;
for (int i = 0; i < 16; i++) {
    mv += analogReadMilliVolts(34);
    delay(1);
}
mv /= 16;
```

This obtains millivolt estimates from the configured ESP32 ADC API. It **does not** directly use the `4095`-count/3.3-V formula in its source.

The **Wokwi firmware**, by contrast, uses a nominal raw-count conversion:

$$
V_{mV,\ Wokwi}=\frac{\mathrm{average\ counts}}{4095}\times3300
$$

For a *hypothetical* 12-bit midpoint code of 2047.5 counts, the nominal Wokwi conversion would be **1650 mV**. This is only an arithmetic illustration of the **simulator's chosen scaling**; it is not a measured ESP32 transfer-function calibration.

For the actual hardware, check supply voltage, ADC attenuation, sensor resistors, and independent DMM measurement. ADC conversion uncertainty, nonlinearity, input loading, and analog noise can affect agreement.

## 7. Sampling, averaging, and timing

The two available firmware examples report at a nominal period of **200 ms**:

$$
f_{report} = 1/(0.200\ \mathrm{s}) = \boxed{5\ \mathrm{reports/s}}
$$

Each report averages **16 ADC readings**. Averaging may reduce random noise but does not automatically remove offset, scale error, drift, or correlated disturbances. Both firmware examples also have work inside the loop, so **measure actual timing** rather than assuming ideal scheduling.

The four archived physical CSV recordings have **16 + 133 + 641 + 544 = 1,334 rows** total. Their timestamp differences are recorded as 200 ms in the analysis archive. See [original CSV folder](../05_Hardware_CSV/) and [analysis methodology](../06_Analysis/Analysis_Methodology.md).

## 8. Alarm states and hysteresis

The **documented Wokwi firmware** sets:

- `HOT` when modeled temperature rises to **45 °C or higher**.
- Return to `NORMAL` when it falls to **43 °C or lower**.
- Between 43 and 45 °C, retain the previous hot/normal state (hysteresis).
- For readings outside the modeled 15–55 °C operating range or when fault thresholds are tripped, report a fault/range state and clear the current HOT latch.

The hysteresis width is:

$$
45-43=\boxed{2\ ^\circ\mathrm{C}}
$$

The 45 °C and 43 °C threshold voltages **would be about 0.982 V and 1.036 V**, respectively, in the separate **3.20-V / 9.82-kΩ LTspice divider**. These are computed analog-design predictions, **not** observed Wokwi voltages or physical alarm-trip measurements. The Wokwi module and supply differ from the LTspice circuit.

See [Wokwi test procedure](../10_Wokwi_Simulation/WOKWI_TEST_CASES.md) and [selected observed simulator evidence](../10_Wokwi_Simulation/Evidence/). The archived physical CSV captures all have `NORMAL` status; they **do not** demonstrate a measured hardware alarm trip.

## 9. How the real-data graphs were calculated

The original physical captures are in [`05_Hardware_CSV`](../05_Hardware_CSV/). Analysis results are in [`06_Analysis`](../06_Analysis/). Recorded temperatures are **firmware-model estimates**, not calibrated thermometer readings.

For $n$ readings $x_i$, compute the mean:

$$
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i
$$

Sample standard deviation (with $n-1$ in the denominator) is:

$$
s=\sqrt{\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}}
$$

From the saved [measurement metrics](../06_Analysis/measurement_metrics.json):

| Archived physical run | Rows | Duration | Summary from stored analysis |
|---|---:|---:|---|
| `hardware_20261019_234715_916346.csv` (stable capture) | 641 | 128.0 s | Mean estimated temperature **22.3765 °C**, sample SD **0.0412 °C** |
| `hardware_20261019_235231_403927.csv` (dynamic response) | 544 | 108.6 s | Maximum estimated temperature **30.829 °C** at **57.2 s** elapsed |

See the [thermal-response plot](../06_Analysis/thermal_response.png), [steady-state plot](../06_Analysis/steady_state_temperature.png), and [voltage-versus-temperature plot](../06_Analysis/voltage_vs_temperature.png).

**Interpretation:** Repeatability in one stable modeled-temperature stream is **not** the same as reference-calibrated absolute temperature accuracy. A dynamic warming test should not be treated as a stationary noise test.

## 10. How to reproduce these calculations and results

1. Open the [LTspice temperature `.cir`](../09_LTspice_Simulation/Original_Circuits_and_Results/ThermoBench_LTspice.cir). Run and inspect the `.meas` results for the saved 25, 26, 27 °C steps.
2. Independently calculate $R_{NTC}$ and $V_{ADC}$ at those temperatures using Sections 2 and 3; compare rounded results to the simulator log.
3. Open [LTspice AC `.cir`](../09_LTspice_Simulation/Original_Circuits_and_Results/ThermoBench_Filter_AC.cir). Run an AC analysis and plot `V(ADC)/V(VCC)`. Compare against the theoretical **267.73 Hz** 25 °C cutoff.
4. Open the [KiCad project](../02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pro). Trace R1, NTC, R2, C1 and ADC connections against the schematic. This is **design inspection**, not physical-board testing.
5. Use the [firmware and Python build instructions](../04_Firmware_and_Python/BUILD_STEPS.md) to understand the software, but verify board identity, components, and actual source versions before hardware testing.
6. Recompute the analysis from the [physical CSVs](../05_Hardware_CSV/) and compare against the [stored metrics](../06_Analysis/measurement_metrics.json). Do not mix in the separately labeled [synthetic demo data](../08_Synthetic_Demo_Only/).

## 11. Important limitations and next engineering checks

- **PCB:** The KiCad PCB was **designed but not fabricated or tested**. Preliminary Gerber files are marked [NOT FOR MANUFACTURING](../07_Reference_Exports/Preliminary_Gerbers/NOT_FOR_MANUFACTURING.txt).
- **Firmware provenance:** The exact firmware binary that generated the physical CSV recordings was not preserved. Avoid attributing the archived readings to a specific current source version without evidence.
- **Calibration:** The approximately 1.58 V DMM observation and a roughly 1.609 V ADC observation were **not synchronized, traceable measurements**. A model value near 1.579 V at 26 °C does not validate a temperature reference.
- **NTC parameters:** A 10-kΩ/3950-Beta model is assumed. Confirm the actual NTC part number, datasheet, tolerance, and Beta parameters before making accuracy claims.
- **Further evidence needed:** Build/compile logs, reference-thermometer comparisons, synchronized ADC/DMM readings, controlled fault tests on real hardware, and eventual PCB assembly and measured bring-up.

---

**Evidence labels used in this document:** *CALCULATED* = an arithmetic/model prediction; *LTSPICE* = simulated analog circuit response; *WOKWI* = simulator behavior; *HARDWARE* = original physical CSV or bench observation. None of those labels, alone, means externally calibrated temperature accuracy.

**Navigation:** [Back to main project README](../README.md) · [Final engineering report](../01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf) · [Graphs and analysis](../06_Analysis/) · [Schematic and PCB sources](../02_KiCad_Source/)
