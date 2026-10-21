from pathlib import Path
import sys,json,math,textwrap
sys.path.insert(0,str(Path('project').resolve()))
from bench import voltage,decode
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor,white
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader
import numpy as np
P=Path('project'); M=json.loads((P/'results/metrics.json').read_text())
OUT=Path('output/pdf/Aaron_Trujillo_ThermoBench_Interview_Project.pdf')
c=canvas.Canvas(str(OUT),pagesize=(612,792));c.setTitle('ThermoBench | Aaron Trujillo | Interview Engineering Package')
navy=HexColor('#142c40');teal=HexColor('#087f8c');muted=HexColor('#526373');light=HexColor('#edf3f6');page=0;y=0
style=ParagraphStyle('body',fontName='Helvetica',fontSize=10.3,leading=15,textColor=navy)
small=ParagraphStyle('small',parent=style,fontSize=8.5,leading=11)
def start(k,title,sub=''):
 global page,y
 if page:c.showPage()
 page+=1;c.setFillColor(navy);c.rect(0,735,612,57,fill=1,stroke=0)
 c.setFillColor(white);c.setFont('Helvetica-Bold',10);c.drawString(42,760,'THERMOBENCH  /  ENGINEERING PORTFOLIO')
 c.setFillColor(muted);c.setFont('Helvetica',8);c.drawString(42,25,'Aaron Trujillo  |  Rev A  |  19 October 2026  |  AI-assisted project')
 c.drawRightString(570,25,str(page));y=705
 c.setFillColor(teal);c.setFont('Helvetica-Bold',9);c.drawString(42,y,k.upper());y-=31
 c.setFillColor(navy);c.setFont('Helvetica-Bold',23);c.drawString(42,y,title);y-=25
 if sub:para(sub)
def para(t):
 global y
 p=Paragraph(t,style);w,h=p.wrap(528,700)
 if y-h<47:raise RuntimeError(('overflow',page,y,h,t[:30]))
 p.drawOn(c,42,y-h);y-=h+10

def heading(t):
 global y
 y-=5;c.setFont('Helvetica-Bold',12);c.setFillColor(teal);c.drawString(42,y,t);y-=20

def table(rows,widths=None):
 global y
 data=[[Paragraph(str(v),small) for v in row] for row in rows]
 t=Table(data,colWidths=widths or [528/len(rows[0])]*len(rows[0]))
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),light),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,HexColor('#cfdce3'))]))
 w,h=t.wrap(528,700)
 if y-h<45:raise RuntimeError(('table overflow',page,y,h))
 t.drawOn(c,42,y-h);y-=h+12

def pic(name,h):
 global y
 c.drawImage(str(P/'results'/name),42,y-h,width=528,height=h,mask='auto');y-=h+12

def code(lines):
 global y
 c.setFont('Courier',7.5);c.setFillColor(navy)
 for l in lines:
  c.drawString(42,y,l);y-=10

start('01 / decision','A sensor test bench you can explain','ESP32 + NTC thermistor + Python validation + SPC')
para('<b>Recommended project:</b> a small, reproducible temperature acquisition bench that converts an analog signal, logs data, detects faults, and evaluates measurement stability. Confidence: <b>high</b> as a fit for the prototype/documentation request; <b>medium</b> for the exact interview team because its role is not identified in the attached email.')
heading('Why this is the strongest practical choice')
para('It builds on your thermistor and embedded-logging work, uses the ESP32 and bench components you have described, and gives you concrete decisions to discuss: divider sizing, ADC limitations, filtering, uncertainty, fault isolation and acceptance testing. A working, understood prototype is more persuasive than a larger unverified design.')
table([['What the interviewer requested','What to bring'],['Prototype','Assembled breadboard, USB cable, DMM and laptop. Physical build remains yours to complete.'],['Schematic and spec','Wiring-level schematic, BOM, calculations, requirements and verification matrix in this report.'],['Software examples you wrote','Bring original code you actually wrote as well. New package code is AI-assisted; review, modify and explain it accurately.']], [155,373])
heading('Evidence boundary')
para('<b>Completed here:</b> design documentation, executable Python model, synthetic datasets, charts, five passing Python tests and source listings. <b>Not completed:</b> physical assembly, Arduino compilation, firmware upload, serial capture or temperature calibration. No synthetic result is a measured achievement.')
para('The attached email says Wednesday at 3 pm and asks for project prototypes if possible. Confirm the calendar invitation for the exact date and location. This report is a bench demonstration, not flight hardware or qualified aircraft ground-support equipment.')

start('02 / specification','Define success before testing')
table([['ID','Proposed requirement / acceptance criterion','Evidence status'],['R1','Measure 15 to 55 C with identified 10k B3950 NTC; report out-of-range beyond that interval.','Model only'],['R2','Target absolute error <=1.0 C at 15, 25, 35, 45 and 55 C against reference uncertainty <=0.2 C. Apply guardband.','Unverified target'],['R3','Fixed-condition repeatability: standard deviation <=0.15 C over 60 s after stabilization.','Not measured'],['R4','Nominal output 5 records/s; observe 4.5-5.5 Hz over 60 s, no malformed records.','Not measured'],['R5','<=100 mV LOW_FAULT; >=2900 mV HIGH_FAULT. Detect stable injected fault within 1 s.','Python logic tested'],['R6','HOT at >=45 C; return NORMAL at <=43 C; keep previous state in between.','Python logic tested'],['R7','CSV contains time, mV, temperature and state; invalid sensor temperature must not be treated as a valid measurement.','Parser authored'],['R8','Power from USB only; ADC signal stays within board electrical limits. No aircraft connection.','Wiring review needed']], [32,375,121])
para('<b>Do not call R2 achieved.</b> Its feasibility depends on actual thermistor tolerance, supply measurement, ADC behavior and calibration. ADC averaging reduces random noise; it does not remove systematic error.')
para('The operating band, thresholds and limits are project design choices. They are not requirements supplied by the interviewer or claims from the component manufacturer.')

start('03 / architecture','From signal to evidence')
# diagram, two rows with explicit connections
base=y-60
for x,title,detail in [(42,'Sensor + divider','Temperature -> voltage'),(224,'ADC + firmware','mV -> C -> status'),(406,'USB / Python','CSV -> review')]:
 c.setFillColor(light);c.roundRect(x,base,164,58,6,fill=1,stroke=0);c.setFillColor(navy);c.setFont('Helvetica-Bold',10);c.drawString(x+10,base+36,title);c.setFont('Helvetica',8);c.drawString(x+10,base+18,detail)
for x in [207,389]:
 c.setStrokeColor(teal);c.line(x,base+29,x+15,base+29);c.line(x+15,base+29,x+10,base+33);c.line(x+15,base+29,x+10,base+25)
y=base-25
para('<b>Data path:</b> one firmware row every nominal 200 ms. Each row averages 16 calibrated-mV ADC conversions. Temperature conversion uses the measured rail and resistor values; threshold logic runs before conversion at the fault rails.')
table([['Layer','Responsibilities','Failure response'],['Circuit','3V3 divider, series isolation resistor, ADC capacitor, common ground.','DMM check before USB logging.'],['Firmware','Acquire, convert, apply hysteresis, report fault/range state.','Fault rows carry blank temperature.'],['Python capture','Parse serial CSV, identify hardware rows, count rejected rows.','Stop on zero valid records; keep faults.'],['Analysis','Separate reference sweeps and steady-state repeatability; freeze SPC limits.','Flag changes; do not auto-adjust limits.']], [82,260,186])
heading('A deliberate limitation')
para('The firmware does not control a heater, relay or aircraft system. HOT is an informational label. There is no safety-rated shutdown, redundant sensor, watchdog validation or environmental qualification. Range faults indicate an invalid reading but cannot identify every wiring failure uniquely.')

start('04 / schematic','Breadboard wiring, Rev A','Target assumption: original ESP32-WROOM DevKit, ADC1 input GPIO34.')
# vector schematic
cy=y-90;c.setStrokeColor(navy);c.setLineWidth(1.4);c.setFillColor(navy)
def label(x,z,s):c.setFont('Helvetica',9);c.drawString(x,z,s)
def resistor(x,z,vertical=True):
 if vertical:c.rect(x-7,z-19,14,38,stroke=1,fill=0)
 else:c.rect(x-22,z-7,44,14,stroke=1,fill=0)
c.line(125,cy+58,125,cy+35);resistor(125,cy+16);c.line(125,cy-3,125,cy-35)
label(92,cy+65,'3V3 measured');label(144,cy+12,'R1 10k')
c.circle(125,cy-35,3,fill=1);label(69,cy-29,'TP1')
c.line(125,cy-35,125,cy-65);resistor(125,cy-84);c.line(125,cy-103,125,cy-135)
label(145,cy-86,'NTC 10k @25 C');label(145,cy-100,'Assumed B3950')
c.line(125,cy-35,268,cy-35);resistor(290,cy-35,False);c.line(312,cy-35,465,cy-35)
label(263,cy-20,'R2 1k');label(429,cy-18,'GPIO34');label(353,cy-29,'TP2')
c.circle(350,cy-35,3,fill=1);c.line(350,cy-35,350,cy-73)
c.line(336,cy-73,364,cy-73);c.line(336,cy-80,364,cy-80);c.line(350,cy-80,350,cy-135);label(371,cy-80,'C1 100nF')
c.line(125,cy-135,465,cy-135);label(266,cy-153,'Common GND to ESP32');c.line(290,cy-135,290,cy-142)
y=cy-180
para('USB powers the DevKit; the board 3V3 rail supplies the divider. Connect R1 from 3V3 to TP1, the thermistor from TP1 to GND, R2 from TP1 to GPIO34, and C1 from GPIO34 to GND. R2 is not a substitute for overvoltage protection.')
table([['Check','Expected before logging'],['Power off','Verify wiring and no accidental 3V3-to-GND short; confirm NTC part number.'],['Power on / DMM','Measure 3V3 and enter VS_MV. At nominal 25 C and matched 10k resistors, TP1 is half the rail.'],['Pinout','GPIO34 is for the original ESP32 assumption only. Check exact board pinout before use.'],['Fault injection','Power down before changing connections. Remove NTC for high-rail fault; bypass NTC for low-rail fault.']], [115,413])

start('05 / parts & math','Understand every component')
table([['Part','Quantity / value','Reason'],['ESP32 DevKit','1; original WROOM assumed','ADC1 GPIO34 and USB serial'],['NTC','1; 10k @25 C, B3950 assumed','Identify actual tolerance and beta interval'],['R1','1; 10k, preferably 0.1%','Match nominal NTC for useful sensitivity'],['R2 / C1','1k / 100nF ceramic','Input isolation and low-pass filtering'],['Bench supplies','Breadboard, jumpers, USB data cable, DMM','Assembly, logging and voltage verification'],['Reference / substitutions','Reference thermometer; measured 10k, 6.8k and 3.3k resistors','Thermal validation and electrical-only checks']], [120,180,228])
para('<b>Model:</b> R(T) = R25 exp[B(1/T - 1/298.15)], with T in kelvin.<br/><b>Divider:</b> V = Vs RNTC / (R1 + RNTC).<br/><b>Inverse:</b> RNTC = R1 V / (Vs - V); T(C) = 1/[1/298.15 + ln(RNTC/R25)/B] - 273.15.')
para('At 25 C with Vs = 3.20 V: V = 1.600 V, divider current = 160 microamps, NTC power = 0.256 mW. Self-heating rise is P / dissipation constant; that constant is unknown until the sensor is identified. It must be evaluated, not assumed negligible.')
para('At 25 C, R1 || RNTC = 5k. Approximate filter time constant = (5k + 1k) x 100nF = 0.60 ms, cutoff about 265 Hz. This aids ADC settling and noise suppression; it is not a complete anti-alias filter. Sensor thermal response and 5 Hz reporting dominate the visible demo.')
para('Original ESP32 documentation describes an approximate 150-3100 mV range at 11 dB attenuation. The intended 15-55 C band is inside that range; near-rail faults are coarse indicators and require physical verification. [1]')

start('06 / calculated response','Know what the meter should show')
pic('transfer.png',205)
rows=[['Temperature (C)','NTC resistance (ohm)','Sense voltage (V)']]
for t in [15,25,35,45,55]:
 v=float(voltage(t));r=10000*v/(3.2-v);rows.append([str(t),f'{r:.0f}',f'{v:.3f}'])
table(rows)
para('As temperature rises, NTC resistance falls and the measured voltage falls. This sign is a useful debugging check: increasing temperature with increasing voltage suggests the divider orientation or conversion equation is inconsistent.')
para('Resistor substitution separates the electronics from thermal effects. Replace the NTC with a measured resistor and compute expected voltage using its measured value. A nominal 10k replacement gives 1.600 V, 6.8k gives 1.295 V, and 3.3k gives 0.794 V at a 3.20 V rail. These are calculated values, not recorded readings.')

start('07 / uncertainty','Accuracy is an engineering budget')
rows=[['Illustrative contributor','At 25 C','At 55 C','Interpretation']]
for name,delta in [('ADC residual offset',.010),('Rail setting error',.010)]:
 vals=[]
 for t in [25,55]:
  v=float(voltage(t))
  if name.startswith('ADC'):err=abs(decode(v+delta)[0]-t)
  else:
   rr=10000*v/(3.21-v);tt=1/(1/298.15+math.log(rr/10000)/3950)-273.15;err=abs(tt-t)
  vals.append(f'{err:.2f} C')
 rows.append([name+' (10 mV)',*vals,'Assumed scenario, not measured bound'])
rows += [['R1 tolerance, 0.1%','~0.02 C','~0.03 C','First-order sensitivity'],['R25 tolerance, 1%','~0.23 C','~0.27 C','Part-dependent, assumed'],['Beta tolerance, 1%','~0.00 C','~0.33 C','About 25 C reference'],['Self-heating / thermal gradients','Unknown','Unknown','Needs sensor data and bench test']]
table(rows,[154,66,66,242])
para('At 25 C sensitivity is about -35.6 mV/C; at 55 C it is about -20.7 mV/C. The same ADC voltage error therefore causes more temperature error at the hot end. Do not sum these example contributors as a certified uncertainty or assume they are statistically independent.')
heading('Calibration and verification are separate')
para('First compare TP2 DMM voltage against logged mV at three resistor substitutions. Then use stable thermal points and an identified reference sensor. If correcting offset or slope, fit on one dataset and evaluate on separate points; retain raw readings and calibration coefficients.')
para('<b>Guardband example:</b> if the justified expanded uncertainty of the comparison is U = 0.3 C, accept a +/-1 C requirement only when |observed error| + U <= 1 C. Reference uncertainty <=0.2 C alone does not prove U = 0.3 C; include gradients, repeatability and the complete measurement chain.')

start('08 / validation plots','A reproducible synthetic experiment')
pic('sweep.png',210)
para('The curve uses the same nominal thermistor model, injects +10 mV at the ADC, and converts back to temperature. It demonstrates how a fixed voltage error produces a temperature-dependent error. It is not a calibration, a sensor accuracy result or an independent validation of the model.')
table([['Dataset','How it was produced','Proper use'],['synthetic_sweep.csv','Nine analytical temperatures; +10 mV voltage offset.','Discuss sensitivity and test planning.'],['synthetic_spc.csv','80 independent Gaussian errors; fixed RNG seed 20261019; +0.60 C shift from run 51.','Show monitoring calculations and drift detection.'],['hardware.csv','Created only by bench.py capture with connected hardware.','Actual bench evidence after provenance and setup are documented.']], [132,240,156])
para('For a real thermal sweep, use stable plateaus rather than a moving heat source. Keep reference and NTC close together, allow settling, and record both. Do not immerse a bare unqualified sensor or breadboard; use a rated insulated probe and suitable setup if a bath is needed. Hand warming is a qualitative response demonstration only.')

start('09 / SPC','Detect a change without hiding it')
pic('spc.png',315)
para(f'Baseline: runs 1-40. Mean error = <b>{M["mean"]:.3f} C</b>; mean moving range = <b>{M["mrbar"]:.3f} C</b>; estimated within sigma = MRbar/1.128 = <b>{M["sigma"]:.3f} C</b>. I-chart limits: <b>{M["lcl"]:.3f} to {M["ucl"]:.3f} C</b>. MR UCL = 3.267 MRbar = <b>{M["mr_ucl"]:.3f} C</b>; lower limit is zero. [2]')
para('Limits remain fixed after run 40. All 30 shifted points, runs 51-80, exceed the I-chart upper limit. The plotted rule is a single-point, three-sigma rule; it does not implement every run/trend rule. Investigate wiring, supply, sensor placement or calibration before assigning a physical cause.')
para('Use independent stabilized runs for real SPC. Adjacent 5 Hz thermal readings are commonly correlated and can understate moving-range variation. This 40-run baseline is a teaching example, not proof of long-term stability. Control limits describe variation; specification limits express acceptability.')

start('10 / capability & execution','A test plan you can defend')
para(f'For teaching only, using synthetic baseline errors and specifications -1 to +1 C: Cp = (USL-LSL)/(6 sigma) = <b>{M["cp_demo"]:.2f}</b>; Cpk = min(USL-mean, mean-LSL)/(3 sigma) = <b>{M["cpk_demo"]:.2f}</b>. These high values were generated by an assumed noise distribution. They are <b>not capability evidence for this prototype</b>. Do not pool the shifted phase into a stable-process capability claim. [3]')
table([['Test / requirement','Procedure','Acceptance / present status'],['T1 / R1, R8','Inspect wiring; measure supply and TP1/TP2 using known resistors.','Match divider prediction within justified meter/resistor uncertainty. PENDING'],['T2 / R2','Five stable thermal points; record reference and DUT; repeat independently.','|error| + U <=1 C at all points. PENDING'],['T3 / R3','Fixed environment, after settling; capture 60 s; inspect correlation.','SD <=0.15 C; characterize drift separately. PENDING'],['T4 / R4, R7','Capture 60 s; inspect timestamps, gaps and parser counters.','4.5-5.5 Hz; zero malformed records. PENDING'],['T5 / R5','Disconnect/bypass NTC; restore each time.','Correct fault <=1 s; no valid temperature on rail fault. PENDING'],['T6 / R6','Controlled values equivalent to 46, 44, 42 C.','HOT, HOT, NORMAL; then 44 C remains NORMAL. PYTHON PASS; hardware pending'],['T7 / analysis','Run python -m unittest -v; rerun deterministic demo.','5/5 tests PASS in authoring runtime. Firmware and serial path untested.']], [86,244,198])
para('Save board model, thermistor part number, measured R1 and supply, reference ID, ambient conditions, tool versions, raw CSV and code revision for each real run. A failed test is useful evidence when the root cause and next action are clear.')

start('11 / software','What was used and what remains')
table([['Tool / language','Status for this package','Role'],['Python 3, NumPy, Matplotlib','Executed here','Model, seeded synthetic data, charts and statistics'],['unittest','Executed here; 5 tests passed','Nominal conversion, round trips, faults, hysteresis and range'],['ReportLab / Poppler','Used to create and inspect PDF','Document and vector schematic rendering'],['Arduino C++ / ESP32 core','Source supplied; not compiled','Sampling, conversion, hysteresis and serial output'],['pyserial','Capture code supplied; no connected board','Actual hardware CSV logging'],['Arduino IDE / VS Code','Suggested local tools; use not verified','Compile/upload and inspect Python code'],['LTspice / KiCad','Not used to produce these results','Optional future SPICE study / PCB capture; do not claim otherwise']], [145,172,211])
heading('Windows commands')
code(['py -m venv .venv',r'.\.venv\Scripts\python -m pip install -r requirements.txt',r'.\.venv\Scripts\python -m unittest -v',r'.\.venv\Scripts\python bench.py demo --out results',r'.\.venv\Scripts\python bench.py capture --port COM5 --seconds 60', '  # Replace COM5 with your actual port; output defaults to hardware.csv'])
y-=10
para('Place thermobench.ino inside a folder named thermobench. In Arduino IDE, install the Espressif ESP32 core, select the exact board and port, set measured constants, compile and upload. Close Serial Monitor before Python opens the same port. Record the actual core and library versions; this package does not claim a verified firmware toolchain.')
para('Firmware uses analogReadMilliVolts rather than assuming 4095 codes equals 3.3 V. Espressif documents the calibrated-mV API; its availability does not establish system accuracy. Verify against the DMM. [1]')

start('12 / interview','Bring evidence, then tell the story')
heading('A truthful 60-second explanation')
para('"This project is a temperature acquisition and validation bench. The design uses an NTC divider, an ESP32 ADC and a Python logger. I focused on making the signal traceable from voltage to temperature and defining how to test it. The report separates calculated results, synthetic examples and measurements. The supplied code was developed with AI assistance. I can explain the divider equations, alarm hysteresis and the validation plan, and I will distinguish what I have actually tested from what remains."')
heading('Show these in order')
para('1. Point to the hardware and schematic; explain why voltage falls with heat.<br/>2. Show a live nominal reading and compare voltage with the DMM.<br/>3. Demonstrate gentle hand warming and an NTC disconnect fault.<br/>4. Show a real CSV if you have captured one; otherwise label the synthetic example.<br/>5. Explain the frozen SPC limits and one limitation you would address next.')
heading('Questions to practice')
table([['Question','Main answer'],['Why a 10k fixed resistor?','It matches the assumed 25 C NTC resistance and provides useful local sensitivity at modest current.'],['Why average 16 ADC readings?','Reduce random conversion noise; it does not fix gain error, nonlinearity or sensor tolerance.'],['Why 45/43 C thresholds?','Two-degree hysteresis prevents state chatter around a single threshold. These are demo design choices.'],['What does a high-rail fault mean?','Possible open NTC or low-side path, not a uniquely proven cause. Use DMM and wiring inspection.'],['What would you improve next?','Identify the actual NTC, verify ADC behavior, calibrate against a reference, then evaluate an external ADC if justified.']], [170,358])
para('<b>Before leaving:</b> bring the powered working bench only if verified, protect the breadboard, save an offline CSV, charge the laptop, pack the USB data cable and print pages 1, 2, 4, 9 and 10. Also bring an original software sample you wrote and can walk through line by line.')

start('13 / references','Sources and release record')
para('[1] Espressif Systems. Arduino-ESP32 ADC API. Consulted 19 October 2026.<br/><link href="https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html" color="#087f8c">docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html</link>')
para('[2] NIST/SEMATECH e-Handbook. Individuals Control Charts. Moving-range estimate and individual chart limits.<br/><link href="https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc322.htm" color="#087f8c">itl.nist.gov/div898/handbook/pmc/section3/pmc322.htm</link>')
para('[3] NIST/SEMATECH e-Handbook. What Is Process Capability? Stability is a prerequisite for meaningful capability interpretation.<br/><link href="https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm" color="#087f8c">itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm</link>')
para('Interview scope source: user-supplied email screenshot from Jake Sakadjian requesting project prototypes, documentation (schematic, spec), and software examples. The screenshot does not identify the employer or prove the exact job description.')
table([['Release item','Rev A status'],['Python model / charts','Executed with deterministic random seed 20261019.'],['Python tests','5 passed; no hardware or C++ equivalence claim.'],['Firmware','Authored; compilation, upload, ADC behavior and timing unverified.'],['Schematic','Vector wiring diagram; no KiCad ERC, PCB layout or SPICE run.'],['Raw data','Synthetic datasets included; no fabricated hardware measurements.'],['Authorship','AI-assisted design, source and documentation prepared for review and learning.']], [170,358])
para('Appendices contain the supplied firmware, Python analysis/logger and tests. The companion ZIP contains editable source, raw synthetic CSVs, figures and this PDF. Code snippets should be discussed only to the depth you can explain; describe your actual modifications and bench testing separately.')
# Full source appended using readable line lengths
for filename in ['thermobench.ino','bench.py','test_bench.py']:
 lines=[]
 for i,line in enumerate((P/filename).read_text().splitlines(),1):
  # visual wraps only; original source kept in ZIP
  pieces=textwrap.wrap(line,width=94,replace_whitespace=False,drop_whitespace=False) or ['']
  for j,piece in enumerate(pieces):lines.append((f'{i:03d} ' if j==0 else '    ')+piece)
 for n in range(0,len(lines),53):
  start('Appendix / complete source',filename, 'AI-assisted source. Visual line wrapping only; use original file to run.')
  code(lines[n:n+53])
c.save();print(OUT, 'pages',page)
