"""AI-assisted ThermoBench model, deterministic demo, SPC, serial logger.
Python 3 + numpy + matplotlib; pyserial only needed for capture.
All demo rows are SYNTHETIC. No hardware accuracy claim.
"""
from pathlib import Path
import argparse, csv, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
VS=3.2; RF=10000.; R25=10000.; BETA=3950.

def voltage(t):
    r=R25*np.exp(BETA*(1/(np.asarray(t)+273.15)-1/298.15))
    return VS*r/(RF+r)

def decode(v, previous='NORMAL'):
    if not math.isfinite(v): return None,'INVALID'
    if v<=.1: return None,'LOW_FAULT'
    if v>=2.9: return None,'HIGH_FAULT'
    r=RF*v/(VS-v)
    t=1/(1/298.15+math.log(r/R25)/BETA)-273.15
    if t<15 or t>55: return t,'OUT_OF_RANGE'
    return t, 'HOT' if t>=45 else ('NORMAL' if t<=43 else previous)

def capture(port,seconds,out):
    import serial, time
    valid={'NORMAL','HOT','LOW_FAULT','HIGH_FAULT','OUT_OF_RANGE'}
    with serial.Serial(port,115200,timeout=1) as s, open(out,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['source','ms','mv','temp_c','status'])
        end=time.monotonic()+seconds; count=0; rejected=0
        while time.monotonic()<end:
            fields=s.readline().decode('ascii',errors='replace').strip().split(',')
            if fields==['ms','mv','temp_c','status']: continue
            try:
                if len(fields)!=4 or fields[3] not in valid: raise ValueError()
                ms=int(fields[0]); mv=float(fields[1])
                if ms<0 or not math.isfinite(mv): raise ValueError()
                if fields[2] and not math.isfinite(float(fields[2])): raise ValueError()
                if fields[3] in {'NORMAL','HOT','OUT_OF_RANGE'} and not fields[2]:
                    raise ValueError()
            except ValueError:
                rejected+=1; continue
            w.writerow(['HARDWARE',*fields]); f.flush(); count+=1
    print(json.dumps({'captured':count,'rejected':rejected,'file':out}))
    if count==0: raise SystemExit('No valid records received')

def demo(out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(20261019)
    # Independent demonstration errors, not ADC samples or actual chamber data.
    errors=rng.normal(.12,.10,80); errors[50:]+=.60
    baseline=errors[:40]; mr=np.abs(np.diff(baseline))
    mean=float(baseline.mean()); mrbar=float(mr.mean()); sigma=mrbar/1.128
    lcl=mean-3*sigma; ucl=mean+3*sigma
    imr=np.abs(np.diff(errors)); mrucl=3.267*mrbar
    alarms=(np.flatnonzero((errors<lcl)|(errors>ucl))+1).tolist()
    cp=2/(6*sigma); cpk=min(1-mean,mean+1)/(3*sigma)
    metrics=dict(mean=mean,mrbar=mrbar,sigma=sigma,lcl=lcl,ucl=ucl,
                 mr_ucl=mrucl,cp_demo=cp,cpk_demo=cpk,i_alarms=alarms)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    with (out/'synthetic_spc.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['source','run','reference_c','error_c','measured_c','phase'])
        for i,e in enumerate(errors):
            w.writerow(['SYNTHETIC',i+1,25,e,25+e,'BASELINE' if i<40 else 'MONITOR'])
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    t=np.linspace(15,55,401)
    fig,ax=plt.subplots(figsize=(8,3));ax.plot(t,voltage(t),color='#087f8c',lw=2)
    ax.set(xlabel='Temperature (C)',ylabel='Sense voltage (V)',title='Calculated transfer curve | 3.20 V, 10k / B3950 model')
    ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'transfer.png',dpi=180);plt.close(fig)
    fig,axs=plt.subplots(2,1,figsize=(8,5),sharex=True)
    axs[0].plot(np.arange(1,81),errors,'.-',ms=4)
    for y,c,label in [(mean,'#087f8c','Mean'),(ucl,'#b53b45','UCL'),(lcl,'#b53b45','LCL')]:
        axs[0].axhline(y,color=c,ls='--',label=f'{label}: {y:.3f}')
    axs[0].set(ylabel='Error (C)',title='SYNTHETIC I-MR | limits frozen from runs 1-40')
    axs[0].legend(ncol=3,fontsize=8)
    axs[1].plot(np.arange(2,81),imr,'.-',ms=4)
    axs[1].axhline(mrucl,color='#b53b45',ls='--',label=f'MR UCL: {mrucl:.3f}')
    axs[1].axhline(mrbar,color='#087f8c',ls='--');axs[1].legend(fontsize=8)
    axs[1].set(xlabel='Independent simulated run',ylabel='Moving range (C)')
    for ax in axs: ax.axvline(40.5,color='gray',ls=':');ax.axvline(50.5,color='orange',ls=':');ax.grid(alpha=.15)
    fig.tight_layout();fig.savefig(out/'spc.png',dpi=180);plt.close(fig)
    # Inject an offset in voltage, then show independent temperature points.
    refs=np.array([15.,20,25,30,35,40,45,50,55])
    measured=np.array([decode(float(voltage(x)+.010))[0] for x in refs])
    with (out/'synthetic_sweep.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['source','reference_c','mv','measured_c','error_c'])
        for r,m in zip(refs,measured): w.writerow(['SYNTHETIC',r,1000*(voltage(r)+.010),m,m-r])
    fig,ax=plt.subplots(figsize=(8,3));ax.plot(refs,measured-refs,'o-',color='#087f8c')
    ax.axhline(1,color='gray',ls='--');ax.axhline(-1,color='gray',ls='--')
    ax.set(xlabel='Reference temperature (C)',ylabel='Indicated error (C)',title='SYNTHETIC sweep | injected +10 mV offset, no calibration fit')
    ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'sweep.png',dpi=180);plt.close(fig)
    return metrics

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True)
    d=sub.add_parser('demo');d.add_argument('--out',default='results')
    c=sub.add_parser('capture');c.add_argument('--port',required=True)
    c.add_argument('--seconds',type=int,default=60);c.add_argument('--out',default='hardware.csv')
    a=p.parse_args()
    if a.mode=='demo': print(json.dumps(demo(a.out),indent=2))
    else: capture(a.port,a.seconds,a.out)
