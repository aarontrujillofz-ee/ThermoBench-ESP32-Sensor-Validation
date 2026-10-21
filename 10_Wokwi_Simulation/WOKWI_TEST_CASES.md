# User-run Wokwi test cases and outcomes

| Case | Actual user-provided serial result | Decision |
|---|---|---|
| Baseline 25C | 1650.40 mV / 24.989 C / NORMAL | PASS |
| Warm 35C | 1300.66 mV / 35.000 C / NORMAL | PASS |
| Heating to ~46C | 973.48 mV / 45.987 C / HOT | PASS |
| Keep HOT at 44C | 1027.47 mV / 44.003 C / HOT | PASS |
| Keep HOT above 43C | 1052.45 mV / 43.112 C / HOT | PASS |
| Reset at/below 43C | 1055.68 mV / 42.998 C / NORMAL | PASS |
| Return to 25C | 1650.40 mV / 24.989 C / NORMAL | PASS |
| Out of range | 597.95 mV / 63.304 C / OUT_OF_RANGE | STATE OBSERVED; not a safety certification |
| Voltage fault branches | No isolated injected test records supplied | NOT TESTED |

Real Wokwi serial output was supplied as conversation text. Evidence CSV is a selection of exact lines, not a complete archived raw log. User-operated slider changes can create transients and overshoot. The generated graphs use observed numeric values only; they don't interpolate hidden measurements.
