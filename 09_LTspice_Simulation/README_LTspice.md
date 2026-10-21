# ThermoBench | LTspice analysis and file guide

Updated 21 October 2026. These files augment the full ThermoBench report.

## Original user-run simulations
- `Original_Circuits_and_Results/ThermoBench_LTspice.cir` and its `.raw` and `.log` were uploaded from LTspice 26.0.2 on Windows. The actual saved run steps **25, 26, 27 °C** (despite a stale comment above the directive). The log returns 1.614530802 V, 1.579102993 V, 1.543931484 V.
- `Original_Circuits_and_Results/ThermoBench_Filter_AC.cir` and its `.raw` and `.log` were uploaded. 501 complex frequency points from 1 Hz to 100 kHz are present.
- `ThermoBench_LTspice_15_55_Optional.cir` is a derived, *not-yet-run* optional wide-range step configuration. The values in `Temperature_15_55_Calculated_Nominal_Model.csv` are calculated using the model equation, **not measurements and not data from the latest 25–27 °C raw file**.

## Engineering values
- Low-frequency divider transfer gain = 0.50454087 V/V = -5.942 dB.
- At 25°C, Rth = 9.82k || 10k = 4954.59 ohms.
- Analog filter R_eq = R2 + Rth = 5944.59 ohms.
- fc = 1/[2 pi (R2 + Rth) C1] = 267.73 Hz; measured (simulated) AC gain near fc = -8.953 dB, i.e., 3.01 dB below DC gain.
- Approximately 1.58 V was observed on the user's *actual thermistor* circuit earlier. The 26°C model step is 1.579103 V, only 0.897 mV different **as an assumed-temperature model match**. The actual thermistor temperature at that measurement was not determined with an independent reference. This is not proof of thermometry accuracy.
- The ADC baseline near 1.609 V versus DMM near 1.58 V was not recorded under traceable simultaneous conditions and is a further calibration question.

## How to re-run in LTspice
1. Open a `.cir` source in the `Original_Circuits_and_Results` folder; click Run.
2. Temperature test: click V(adc) or add trace; open View > SPICE Error Log to see stepped `.meas` results.
3. AC test: plot `V(ADC)/V(VCC)` **without a nested dB()**; LTspice already renders AC amplitude in dB.
4. Compare your result against the supplied screenshots, exported raw datasets and plots.
5. Use the `Extracted_Data` and `Graphs_and_Evidence` folders in your engineering presentation.

## Physical-design boundaries
No actual PCB was manufactured or tested, and a traceable reference thermometer has not established absolute accuracy. The KiCad project contains 5 categories of ignored tests; DRC = 0 on active checks is not a mechanical or manufacturing certification.
