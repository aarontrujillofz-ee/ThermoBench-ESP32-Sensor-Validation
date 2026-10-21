# Figure and design index

## Master report
Pages 3-6: block architecture, real KiCad schematic, PCB layout and 3D model.
Pages 9-11: actual hardware repeatability, warming/cooling, voltage/temperature response.
Pages 14-16: nominal LTspice circuit model, temperature predictions, frequency response.
Page 18: virtual Wokwi three-wire sensor and ESP32 GPIO34 connection diagram.
Page 19: observed Wokwi 25/35/46 C signal changes and evidence table.
Page 20: HOT alarm state-transition diagram and observed hysteresis plot.
Page 21: observed out-of-range event and engineering limitation.
Page 22: source-to-evidence verification matrix.

## Editable and exported design files
- `02_KiCad_Source/*.kicad_*` editable native project;
- `03_CAD_Visuals/` schematic PDF, copper, silkscreen and mechanical outline PDFs, 3D imagery;
- `09_LTspice_Simulation/` netlists, original RAW and logs, numerical tables, sweep plots;
- `10_Wokwi_Simulation/diagram.json` and `sketch.ino` editable browser simulation; `Figures/` exported diagrams and graphs;
- `05_Hardware_CSV/` physical ESP32 CSV sources and `06_Analysis/` measured-data images.

**Important**: Wokwi virtual test results and synthetic demonstration samples are not physical hardware measurements.
