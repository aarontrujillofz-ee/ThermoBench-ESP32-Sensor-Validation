"""ThermoBench Rev B: shared CSV validation and evidence-based checks.
AI-assisted. Electrical tolerance is user-selected, not a certified accuracy.
"""
import argparse,csv,json,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
STATES={'NORMAL','HOT','LOW_FAULT','HIGH_FAULT','OUT_OF_RANGE'}
FAULTS={'LOW_FAULT','HIGH_FAULT'}

def parse_line(line):
    f=line.strip().split(',')
    if f==['ms','mv','temp_c','status']: return None
    if len(f)!=4 or f[3] not in STATES: raise ValueError('Bad CSV row or state')
    ms=int(f[0]);mv=float(f[1]);temp=None if f[2]=='' else float(f[2])
    if ms<0 or not math.isfinite(mv) or not 0<=mv<=3600:
        raise ValueError('Invalid time or voltage')
    if temp is not None and not math.isfinite(temp): raise ValueError('Nonfinite temperature')
    if (f[3] in FAULTS)!=(temp is None): raise ValueError('Fault/temperature mismatch')
    if f[3] in {'NORMAL','HOT'} and not 15<=temp<=55:
        raise ValueError('Temperature outside operating band')
    if f[3]=='LOW_FAULT' and mv>100: raise ValueError('Low fault inconsistent with voltage')
    if f[3]=='HIGH_FAULT' and mv<2900: raise ValueError('High fault inconsistent with voltage')
    if f[3] not in FAULTS and not 100<mv<2900: raise ValueError('Missing rail fault')
    return {'ms':ms,'mv':mv,'temp_c':temp,'status':f[3]}

def load_csv(path):
    rows=[];rejected=0
    with open(path,newline='') as f:
        reader=csv.DictReader(f)
        required={'source','ms','mv','temp_c','status'}
        if not required<=set(reader.fieldnames or []): raise ValueError('Required CSV fields missing')
        for row in reader:
            try:
                if row['source'] not in {'HARDWARE','SYNTHETIC'}: raise ValueError('Unknown source')
                parsed=parse_line(','.join(row[x] for x in ['ms','mv','temp_c','status']))
                if parsed is None: raise ValueError('Unexpected header')
                parsed['source']=row['source'];rows.append(parsed)
            except (ValueError,TypeError,KeyError):rejected+=1
    if not rows: raise ValueError('No usable rows')
    if len({r['source'] for r in rows})!=1: raise ValueError('Mixed data provenance')
    return rows,rejected

def analyze(path,out,dmm_mv=None,tolerance_mv=30.0):
    if tolerance_mv<=0 or not math.isfinite(tolerance_mv): raise ValueError('Positive tolerance required')
    if dmm_mv is not None and (not math.isfinite(dmm_mv) or not 0<=dmm_mv<=3600):
        raise ValueError('DMM reference must be finite mV in range 0-3600')
    rows,rejected=load_csv(path);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    times=np.array([r['ms'] for r in rows],dtype=float)
    dt=np.diff(times);monotonic=len(dt)>0 and bool(np.all(dt>0))
    duration=float((times[-1]-times[0])/1000)
    hz=float(1000/np.mean(dt)) if monotonic else None
    temps=np.array([np.nan if r['temp_c'] is None else r['temp_c'] for r in rows])
    mv=np.array([r['mv'] for r in rows]);all_valid=all(r['status'] in {'NORMAL','HOT'} for r in rows)
    std=float(np.std(temps,ddof=1)) if len(rows)>1 and all_valid else None
    checks={'timestamps_increasing':'PASS' if monotonic else 'FAIL',
            'cadence_4p5_to_5p5_hz':'PASS' if hz is not None and 4.5<=hz<=5.5 else 'FAIL',
            'parser_clean':'PASS' if rejected==0 else 'FAIL',
            'continuous_valid_temperature':'PASS' if all_valid else 'FAIL'}
    # 59 seconds of time span supports a nominal 60-second capture at 5 Hz.
    checks['steady_repeatability_sd_le_0p15_c']=(
        'PASS' if std<=.15 else 'FAIL') if std is not None and duration>=59 and monotonic else 'NOT_EVALUATED'
    delta=None
    if dmm_mv is not None:
        delta=float(mv.mean()-dmm_mv)
        checks['voltage_mean_vs_dmm']='PASS' if abs(delta)<=tolerance_mv else 'FAIL'
    summary={'source':rows[0]['source'],'file':str(path),'rows':len(rows),'rejected':rejected,
             'duration_s':duration,'rate_hz':hz,'mean_mv':float(mv.mean()),'mean_error_vs_dmm_mv':delta,
             'dmm_reference_mv':dmm_mv,'selected_voltage_tolerance_mv':tolerance_mv,
             'sd_c':std,'fault_rows':sum(r['status'] in FAULTS for r in rows),'checks':checks,
             'limits':'Steady-state checks assume fixed input and settled conditions. No thermal accuracy, uncertainty, long-term stability or capability claim.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    fig,axs=plt.subplots(2,1,figsize=(9,5),sharex=True)
    seconds=(times-times[0])/1000
    axs[0].plot(seconds,mv,color='#087f8c');axs[0].set_ylabel('ADC (mV)')
    axs[1].plot(seconds,temps,color='#142c40');axs[1].set(ylabel='Temperature (C)',xlabel='Time since first row (s)')
    for ax in axs:ax.grid(alpha=.2)
    fig.suptitle(f'{summary["source"]} | {Path(path).name}')
    fig.tight_layout();fig.savefig(out/'capture.png',dpi=180);plt.close(fig)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('csv');p.add_argument('--out',default='analysis')
    p.add_argument('--dmm-mv',type=float);p.add_argument('--tolerance-mv',type=float,default=30)
    a=p.parse_args()
    try: print(json.dumps(analyze(a.csv,a.out,a.dmm_mv,a.tolerance_mv),indent=2))
    except (OSError,ValueError) as e: p.exit(2,f'Analysis stopped: {e}\n')
