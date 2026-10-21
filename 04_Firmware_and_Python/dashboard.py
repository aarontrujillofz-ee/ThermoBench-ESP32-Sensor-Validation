"""ThermoBench desktop station: live USB serial, labeled demo, CSV capture.
Run: python dashboard.py. Requires Tkinter (standard Windows Python install).
AI-assisted; serial hardware path remains unverified until bench use.
"""
import csv,math,queue,random,threading,time
from collections import deque
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk,messagebox
import serial
from serial.tools import list_ports
from station import parse_line

class Dashboard:
    def __init__(self,root):
        self.root=root;root.title('ThermoBench | Sensor Validation Station');root.geometry('980x680')
        self.events=queue.Queue(maxsize=5000);self.stop_event=threading.Event();self.thread=None
        self.data=deque(maxlen=300);self.writer=None;self.file=None;self.source=None;self.last_rx=0
        self.count=0;self.rejected=0;self.last_ms=None
        self.port=tk.StringVar();self.mode=tk.StringVar(value='Disconnected')
        self.reading=tk.StringVar(value='Temperature -- C   |   ADC -- mV')
        self.state=tk.StringVar(value='NO DATA');self.notes=tk.StringVar(value='Choose a port or use the labeled demo.')
        frame=ttk.Frame(root,padding=20);frame.pack(fill='both',expand=True)
        ttk.Label(frame,text='THERMOBENCH',font=('Segoe UI',23,'bold')).pack(anchor='w')
        ttk.Label(frame,textvariable=self.mode,font=('Segoe UI',12,'bold')).pack(anchor='w',pady=5)
        controls=ttk.Frame(frame);controls.pack(fill='x',pady=12)
        self.combo=ttk.Combobox(controls,textvariable=self.port,width=20);self.combo.pack(side='left')
        for label,command in [('Refresh',self.refresh),('Connect USB',self.connect),('Demo',self.demo),('Disconnect',self.disconnect)]:
            ttk.Button(controls,text=label,command=command).pack(side='left',padx=4)
        ttk.Label(frame,textvariable=self.reading,font=('Segoe UI',20)).pack(anchor='w',pady=8)
        ttk.Label(frame,textvariable=self.state,font=('Segoe UI',15,'bold')).pack(anchor='w')
        self.canvas=tk.Canvas(frame,bg='#f0f5f8',height=290,highlightthickness=0)
        self.canvas.pack(fill='both',expand=True,pady=12)
        bottom=ttk.Frame(frame);bottom.pack(fill='x')
        ttk.Button(bottom,text='Start CSV recording',command=self.record).pack(side='left')
        ttk.Button(bottom,text='Stop recording',command=self.stop_record).pack(side='left',padx=5)
        ttk.Label(frame,textvariable=self.notes,wraplength=920).pack(anchor='w',pady=10)
        self.refresh();root.protocol('WM_DELETE_WINDOW',self.close);root.after(100,self.poll)

    def refresh(self):
        ports=[p.device for p in list_ports.comports()];self.combo['values']=ports
        if ports and not self.port.get():self.port.set(ports[0])

    def start(self,source):
        if self.thread and self.thread.is_alive():
            messagebox.showinfo('Active session','Disconnect the current session first.');return False
        self.stop_record();self.stop_event=threading.Event();self.source=source;self.data.clear()
        self.count=0;self.rejected=0;self.last_ms=None;self.last_rx=0
        while not self.events.empty():
            try:self.events.get_nowait()
            except queue.Empty:break
        self.mode.set(source+' | '+('Simulated data' if source=='SYNTHETIC' else self.port.get()))
        self.state.set('WAITING FOR DATA');return True

    def connect(self):
        port=self.port.get().strip()
        if not port:messagebox.showerror('Port','Select your actual COM port.');return
        if not self.start('HARDWARE'):return
        def worker():
            try:
                with serial.Serial(port,115200,timeout=.2) as conn:
                    while not self.stop_event.is_set():
                        line=conn.readline()
                        if not line:continue
                        try:
                            row=parse_line(line.decode('ascii',errors='replace'))
                            if row is not None:self.events.put_nowait(('row',row))
                        except (ValueError,UnicodeError):self.events.put_nowait(('reject',None))
            except (serial.SerialException,OSError,queue.Full) as e:
                try:self.events.put_nowait(('error',str(e)))
                except queue.Full:pass
        self.thread=threading.Thread(target=worker,daemon=True);self.thread.start()

    def demo(self):
        if not self.start('SYNTHETIC'):return
        def worker():
            start=time.monotonic();rng=random.Random(7)
            while not self.stop_event.wait(.2):
                elapsed=time.monotonic()-start;t=25+.07*math.sin(elapsed)+rng.gauss(0,.03)
                r=10000*math.exp(3950*(1/(t+273.15)-1/298.15));mv=3200*r/(10000+r)
                try:self.events.put_nowait(('row',{'ms':round(elapsed*1000),'mv':mv,'temp_c':t,'status':'NORMAL'}))
                except queue.Full:return
        self.thread=threading.Thread(target=worker,daemon=True);self.thread.start()

    def record(self):
        if self.writer:return
        if not self.source or not self.last_rx or time.monotonic()-self.last_rx>2:
            messagebox.showinfo('Recording','Start a session and wait for fresh data.');return
        Path('captures').mkdir(exist_ok=True)
        self.record_path=Path('captures')/(self.source.lower()+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.csv')
        try:self.file=self.record_path.open('x',newline='')
        except OSError as e:messagebox.showerror('Recording',str(e));return
        self.writer=csv.writer(self.file);self.writer.writerow(['source','ms','mv','temp_c','status'])
        self.notes.set('Recording '+str(self.record_path));self.file.flush()

    def stop_record(self):
        if self.file:self.file.close();self.notes.set('Saved '+str(self.record_path))
        self.file=None;self.writer=None

    def disconnect(self):
        self.stop_event.set()
        if self.thread:self.thread.join(timeout=1.5)
        self.stop_record();self.source=None;self.mode.set('Disconnected');self.state.set('NO DATA')
        self.reading.set('Temperature -- C   |   ADC -- mV')

    def poll(self):
        for _ in range(1000):
            try:kind,value=self.events.get_nowait()
            except queue.Empty:break
            if kind=='error':self.disconnect();self.notes.set('Connection error: '+value);break
            if kind=='reject':self.rejected+=1;continue
            if self.source is None:continue
            row=value
            if self.last_ms is not None and row['ms']<=self.last_ms:
                self.stop_record();self.notes.set('Timestamp restarted. Recording closed; start a new recording.')
                self.data.clear()
            self.last_ms=row['ms'];self.last_rx=time.monotonic();self.count+=1;self.data.append(row)
            temp=row['temp_c'];temp_text='--' if temp is None else f'{temp:.2f}'
            self.reading.set(f'Temperature {temp_text} C   |   ADC {row["mv"]:.1f} mV')
            self.state.set(row['status']+f'  |  Rows {self.count}  |  Rejected {self.rejected}')
            if self.writer:
                try:
                    self.writer.writerow([self.source,row['ms'],row['mv'],'' if temp is None else temp,row['status']]);self.file.flush()
                except OSError as e:self.stop_record();self.notes.set('Recording stopped: '+str(e))
        if self.source and self.last_rx and time.monotonic()-self.last_rx>2:
            self.state.set('STALE DATA | Check connection');self.reading.set('Temperature -- C   |   ADC -- mV')
        self.draw();self.root.after(100,self.poll)

    def draw(self):
        cv=self.canvas;cv.delete('all');w=cv.winfo_width();h=cv.winfo_height()
        cv.create_text(15,15,anchor='nw',text='Temperature trend | last 300 records | 15-55 C',fill='#142c40')
        for t in [15,25,35,45,55]:
            yy=h-30-(t-15)/40*(h-65);cv.create_line(48,yy,w-15,yy,fill='#cfdce3')
            cv.create_text(35,yy,text=str(t),fill='#526373')
        data=list(self.data)
        if len(data)<2:return
        t0=data[0]['ms'];span=max(1,data[-1]['ms']-t0);previous=None
        for row in data:
            t=row['temp_c']
            if t is None or row['status'] not in {'NORMAL','HOT'}:previous=None;continue
            x=48+(row['ms']-t0)/span*(w-65);yy=h-30-(t-15)/40*(h-65)
            if previous:cv.create_line(*previous,x,yy,fill='#087f8c',width=2)
            previous=(x,yy)

    def close(self):self.disconnect();self.root.destroy()

if __name__=='__main__':
    root=tk.Tk();Dashboard(root);root.mainloop()
