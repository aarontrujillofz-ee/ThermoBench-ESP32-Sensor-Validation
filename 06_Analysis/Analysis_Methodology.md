# Recomputed analysis - original hardware evidence

- Source: four `HARDWARE` CSV files in `05_Hardware_CSV/`.
- `ms`: integer device timestamp in milliseconds. Duration = last `ms` minus first `ms`; all adjacent sample deltas are 200 ms.
- Temperature and ADC voltage summaries use arithmetic sample mean, min, max, and **sample standard deviation (ddof=1)**.
- Stable run: `hardware_20261019_234715_916346.csv`, n=641, duration 128.0 s, sample SD 0.0412 C. Preliminary repeatability target <=0.15 C.
- Dynamic run: `hardware_20261019_235231_403927.csv`, n=544, duration 108.6 s, initial-20-s mean 22.5134 C, peak 30.829 C at 57.2 s elapsed, final value 24.661 C.
- Plots are generated from the original rows without smoothing, resampling, interpolating or adding synthetic data.
- These temperatures are **firmware model equivalents**, not calibrated absolute temperatures. The archived firmware has nominal 3200-mV/10000-ohm constants; the exact flashed build for the data was not captured in this archive.
- The four CSV captures all report NORMAL, so they do not demonstrate hardware fault handling or alarm-state transitions.
- The prior DMM readings around 1.58 V vs ADC around 1.609 V were described during the live bench work, but are not present as synchronized rows in the uploaded CSV archive. They are context, not a formal calibration run.

Use the `measurement_metrics.json` file for numeric results and the original CSV files for traceability.
