#!/usr/bin/env python3
"""Read-only local audit of ThermoBench project navigation and core files.
Run from the repository root: py tools/audit_repository.py
Does not rename, delete, modify, stage, commit, or upload files.
"""
import csv
import os
import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORE = {'.git', '.venv', '__pycache__', '.pytest_cache', 'node_modules', 'captures', 'analysis'}

REQUIRED = [
    'README.md',
    'docs/file-index.md',
    'docs/calculations.md',
    'docs/hardware-pcb-guide.md',
    'docs/firmware-python-guide.md',
    'docs/results-validation-guide.md',
    '01_Report/ThermoBench_Engineering_Design_and_Validation_Report.pdf',
    '03_CAD_Visuals/KiCad_Schematic_Original_A4.pdf',
    '02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pro',
    '02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_sch',
    '02_KiCad_Source/ThermoBench_Sensor_Adapter.kicad_pcb',
    '04_Firmware_and_Python/thermobench.ino',
    '04_Firmware_and_Python/dashboard.py',
    '04_Firmware_and_Python/station.py',
    '04_Firmware_and_Python/BUILD_STEPS.md',
    '06_Analysis/Analysis_Methodology.md',
    '06_Analysis/measurement_metrics.json',
    '06_Analysis/thermal_response.png',
    '08_Synthetic_Demo_Only/README_SYNTHETIC.md',
    '09_LTspice_Simulation/README_LTspice.md',
    '10_Wokwi_Simulation/README_WOKWI.md',
    'tools/verify_hardware_csv.py',
]


def local_inventory():
    files, dirs = set(), {''}
    for base, child_dirs, child_files in os.walk(ROOT):
        child_dirs[:] = [d for d in child_dirs if d not in IGNORE]
        folder = Path(base)
        rel = folder.relative_to(ROOT).as_posix()
        dirs.add('' if rel == '.' else rel)
        for name in child_files:
            files.add((folder / name).relative_to(ROOT).as_posix())
    return files, dirs


def links_in(markdown):
    # Standard inline Markdown links and images. Also strips fenced code blocks.
    text = re.sub(r'(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$', '', markdown)
    return re.findall(r'!?\[[^\]\n]*\]\(([^)]+)\)', text)


def audit():
    files, dirs = local_inventory()
    errors = []
    for path in REQUIRED:
        if path not in files:
            errors.append(f'REQUIRED FILE MISSING: {path}')

    inspected, links_checked, external = 0, 0, 0
    for path in sorted(f for f in files if f.lower().endswith('.md')):
        inspected += 1
        contents = (ROOT / path).read_text(encoding='utf-8-sig')
        for raw_target in links_in(contents):
            raw_target = raw_target.strip()
            if raw_target.startswith('<') and '>' in raw_target:
                raw_target = raw_target[1:raw_target.index('>')]
            else:
                raw_target = raw_target.split(' "')[0].split(" '")[0]
            if not raw_target or raw_target.startswith('#'):
                continue
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', raw_target) or raw_target.startswith('//'):
                external += 1
                continue
            parsed = urlsplit(raw_target)
            rel = unquote(parsed.path).replace('\\', '/')
            if not rel:
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(path), rel))
            links_checked += 1
            if target == '..' or target.startswith('../'):
                errors.append(f'LINK OUTSIDE REPO: {path} -> {raw_target}')
            elif target not in files and target not in dirs:
                near = [s for s in files | dirs if s.casefold() == target.casefold()]
                hint = f' (case mismatch: {near[0]})' if near else ''
                errors.append(f'BROKEN LINK: {path} -> {raw_target}{hint}')

    csv_folder = ROOT / '05_Hardware_CSV'
    captures = sorted(csv_folder.glob('hardware_*.csv')) if csv_folder.is_dir() else []
    total_rows = 0
    for file in captures:
        with file.open(newline='', encoding='utf-8-sig') as fp:
            reader = csv.DictReader(fp)
            expected_cols = {'source','ms','mv','temp_c','status'}
            if not expected_cols.issubset(set(reader.fieldnames or [])):
                errors.append(f'BAD CSV COLUMNS: {file.name}')
                continue
            for n, row in enumerate(reader, start=2):
                total_rows += 1
                if row['source'] != 'HARDWARE':
                    errors.append(f'UNEXPECTED SOURCE: {file.name} row {n}')
                if row['status'] != 'NORMAL':
                    errors.append(f'UNEXPECTED STATUS: {file.name} row {n}')
    if len(captures) != 4:
        errors.append(f'EXPECTED 4 HARDWARE CSV FILES, FOUND {len(captures)}')
    if total_rows != 1334:
        errors.append(f'EXPECTED 1334 HARDWARE ROWS, FOUND {total_rows}')

    readme = (ROOT / 'README.md').read_text(encoding='utf-8-sig') if (ROOT / 'README.md').exists() else ''
    if 'not fabricated' not in readme.lower() and 'not fabricated/tested' not in readme.lower():
        errors.append('README LACKS EXPLICIT UNFABRICATED PCB STATUS')
    if 'calibrat' not in readme.lower():
        errors.append('README LACKS CALIBRATION LIMITATION')

    print(f'Markdown files inspected: {inspected}')
    print(f'Local Markdown file/folder links checked: {links_checked}')
    print(f'External links skipped: {external}')
    print(f'Physical CSV recordings: {len(captures)} | rows: {total_rows}')
    print('This is a file/link/archival audit, NOT firmware compilation or physical validation.')
    for issue in errors[:100]:
        print('FAIL', issue)
    if len(errors) > 100:
        print(f'... {len(errors)-100} additional issues')
    print(f'RESULT: {"PASS" if not errors else "FAIL"} ({len(errors)} issues)')
    return 0 if not errors else 1


if __name__ == '__main__':
    raise SystemExit(audit())
