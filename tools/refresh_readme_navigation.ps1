# Phase 6: update only the Quick Access table; leave all other README sections intact.
# Requires branch cleanup/final-portfolio-organization and clean README before patch.
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $root
$branch = (git branch --show-current).Trim()
if ($branch -ne 'cleanup/final-portfolio-organization') {
    throw "Wrong branch: $branch. Stop before changing README."
}
$changed = @(git status --porcelain -- README.md)
if ($changed.Count -gt 0) { throw 'README already has local changes; review them before patching.' }
if (-not (Test-Path -LiteralPath (Join-Path $root 'docs/file-index.md'))) {
    throw 'Missing docs/file-index.md; extract ZIP into repository root first.'
}
$readmePath = Join-Path $root 'README.md'
$content = [System.IO.File]::ReadAllText($readmePath)
$start = [regex]::Matches($content, '(?m)^## Quick access[^\r\n]*\r?\n')
$end = [regex]::Matches($content, '(?m)^## Project in 60 seconds')
if ($start.Count -ne 1 -or $end.Count -ne 1 -or $end[0].Index -le $start[0].Index) {
    throw 'Unexpected README headings; nothing changed.'
}
$newline = if ($content.Contains("`r`n")) { "`r`n" } else { "`n" }
$table = @'
| What you need | Direct link | What it contains |
| --- | --- | --- |
| **Final report** | [23-page PDF](01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf) | Start here for the complete project |
| **Circuit schematic** | [View PDF](03_CAD_Visuals/KiCad_Schematic_Original_A4.pdf) | Review the external analog circuit |
| **PCB design** | [KiCad board](02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pcb) / [3D render](03_CAD_Visuals/3D_Angled_Original.png) | Designed, not fabricated |
| **ESP32 firmware** | [thermobench.ino](04_Firmware_and_Python/thermobench.ino) | Embedded source code |
| **Python code** | [Python folder](04_Firmware_and_Python/) / [Code walkthrough](docs/firmware-python-guide.md) | Dashboard, CSV parsing and tests |
| **Calculations** | [Worked calculations](docs/calculations.md) | NTC, voltage divider, RC filter, ADC |
| **Graphs and results** | [Thermal response](06_Analysis/thermal_response.png) / [Results guide](docs/results-validation-guide.md) | Physical-recording analysis |
| **Original measurements** | [Four hardware CSV files](05_Hardware_CSV/) | 1,334 archived physical rows |
| **Simulations** | [LTspice](09_LTspice_Simulation/) / [Wokwi](10_Wokwi_Simulation/) | Different virtual models, not physical proof |
| **All project files** | [Complete file index](docs/file-index.md) | Reports, schematics, PCB, code, images, tests and history |
'@
$replacement = $table.TrimEnd() -replace '\r?\n', $newline
$before = $content.Substring(0, $start[0].Index + $start[0].Length)
$after = $content.Substring($end[0].Index)
$updated = $before + $newline + $replacement + $newline + $newline + $after
$backup = Join-Path $env:TEMP ('ThermoBench_README_Phase6_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.md')
[System.IO.File]::Copy($readmePath, $backup)
[System.IO.File]::WriteAllText($readmePath, $updated, [System.Text.UTF8Encoding]::new($false))
Write-Host "README Quick Access table updated. Backup: $backup"
git diff -- README.md
