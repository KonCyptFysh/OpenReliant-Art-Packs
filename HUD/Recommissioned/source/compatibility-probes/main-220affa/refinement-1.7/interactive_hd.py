"""Use only the isolated process's own X11 window for HUD control checks."""
import ctypes as C, os, subprocess, time, shutil, json, hashlib
from pathlib import Path
b=Path(__file__).resolve().parent
x=C.CDLL('libX11.so.6');U=C.c_ulong;P=C.c_void_p
x.XOpenDisplay.argtypes=[C.c_char_p];x.XOpenDisplay.restype=P
x.XDefaultRootWindow.argtypes=[P];x.XDefaultRootWindow.restype=U
x.XInternAtom.argtypes=[P,C.c_char_p,C.c_int];x.XInternAtom.restype=U
x.XGetWindowProperty.argtypes=[P,U,U,C.c_long,C.c_long,C.c_int,U,C.POINTER(U),C.POINTER(C.c_int),C.POINTER(U),C.POINTER(U),C.POINTER(P)]
x.XFree.argtypes=[P];x.XFlush.argtypes=[P];x.XCloseDisplay.argtypes=[P]
x.XStringToKeysym.argtypes=[C.c_char_p];x.XStringToKeysym.restype=U
x.XKeysymToKeycode.argtypes=[P,U];x.XKeysymToKeycode.restype=C.c_ubyte
x.XSetInputFocus.argtypes=[P,U,C.c_int,U]
x.XGetInputFocus.argtypes=[P,C.POINTER(U),C.POINTER(C.c_int)]
xt=C.CDLL('libXtst.so.6');xt.XTestFakeKeyEvent.argtypes=[P,C.c_uint,C.c_int,U]
class Key(C.Structure):
 _fields_=[('type',C.c_int),('serial',U),('send_event',C.c_int),('display',P),('window',U),('root',U),('subwindow',U),('time',U),('x',C.c_int),('y',C.c_int),('x_root',C.c_int),('y_root',C.c_int),('state',C.c_uint),('keycode',C.c_uint),('same_screen',C.c_int)]
class Client(C.Structure):
 _fields_=[('type',C.c_int),('serial',U),('send_event',C.c_int),('display',P),('window',U),('message_type',U),('format',C.c_int),('data',C.c_long*5)]
class Event(C.Union):_fields_=[('key',Key),('client',Client),('pad',C.c_long*24)]
x.XSendEvent.argtypes=[P,U,C.c_int,C.c_long,C.POINTER(Event)]
d=x.XOpenDisplay(None);assert d;root=x.XDefaultRootWindow(d)
def prop(w,name):
 typ=U();fmt=C.c_int();n=U();left=U();data=P()
 x.XGetWindowProperty(d,w,x.XInternAtom(d,name,0),0,4096,0,0,C.byref(typ),C.byref(fmt),C.byref(n),C.byref(left),C.byref(data))
 try:return list(C.cast(data,C.POINTER(U))[:n.value]) if data and fmt.value==32 else []
 finally:
  if data:x.XFree(data)
def send(name,down,state=0):
 x.XSetInputFocus(d,window,1,0);x.XFlush(d);time.sleep(.03)
 focus=U();revert=C.c_int();x.XGetInputFocus(d,C.byref(focus),C.byref(revert))
 assert focus.value==window, 'Test window lost focus; stopping input'
 code=x.XKeysymToKeycode(d,x.XStringToKeysym(name.encode()))
 assert xt.XTestFakeKeyEvent(d,code,int(down),0);x.XFlush(d)
def tap(name,ctrl=False):
 if ctrl:send('Control_L',True)
 send(name,True,4 if ctrl else 0);time.sleep(.12);send(name,False,4 if ctrl else 0)
 if ctrl:send('Control_L',False)
 time.sleep(.2)
def shot(name):
 out=b/'evidence'/('interactive-'+name+'.png')
 subprocess.run(['import','-window',str(window),str(out)],check=True,timeout=8)
 return {'case':name,'capture':out.name,'capture_sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
env=os.environ.copy();env.pop('XDG_ACTIVATION_TOKEN',None);env['SDL_VIDEODRIVER']='x11';env['SDL_AUDIODRIVER']='dummy'
log=b/'evidence/interactive-hd-comms.log';cases=[]
binary=b.parent/'hud-release-review-2026-10-09/main-files/openreliant-220affa78729a2ce7dcb49602e4f38a4a53d5dc1/zig-out/bin/openreliant'
with log.open('w') as stream:
 p=subprocess.Popen([str(binary),str(b/'test-hd-interactive'),'--mission','991','--ship','4','--view','2','--size','1920x1080','--fps','60'],stdout=stream,stderr=subprocess.STDOUT,env=env)
 try:
  window=None;end=time.monotonic()+40
  while time.monotonic()<end and p.poll() is None:
   for w in prop(root,b'_NET_CLIENT_LIST'):
    if prop(w,b'_NET_WM_PID')==[p.pid]:window=w;break
   if window and 'HUD_PANELS' in log.read_text():break
   time.sleep(.2)
  assert window and p.poll() is None
  activate=Event();activate.client=Client(33,0,1,d,window,x.XInternAtom(d,b'_NET_ACTIVE_WINDOW',0),32,(C.c_long*5)(1,0,0,0,0))
  x.XSendEvent(d,root,0,(1<<20)|(1<<19),C.byref(activate));x.XFlush(d);time.sleep(1)
  x.XSetInputFocus(d,window,1,0);x.XFlush(d);time.sleep(3)
  cases.append(shot('hd-portrait-before'))
  tap('c');time.sleep(.6);cases.append(shot('hd-portrait-comms'))
  tap('1');time.sleep(.4);cases.append(shot('hd-portrait-option1'))
  tap('Pause');cases.append(shot('hd-paused'));time.sleep(1);tap('Pause');time.sleep(20);cases.append(shot('hd-after-portrait'))
  tap('c');time.sleep(.6);cases.append(shot('hd-after-comms-toggle'))
  print(json.dumps({'cases':len(cases),'status':'captured'}),flush=True)
 finally:
  if p.poll() is None and window:
   e=Event();e.client=Client(33,0,1,d,window,x.XInternAtom(d,b'WM_PROTOCOLS',0),32,(C.c_long*5)(x.XInternAtom(d,b'WM_DELETE_WINDOW',0),0,0,0,0));x.XSendEvent(d,window,0,0,C.byref(e));x.XFlush(d)
  code=p.wait(timeout=15);x.XCloseDisplay(d)
text=log.read_text()
record={'exit_code':code,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'cases':cases,'diagnostics':[l for l in text.splitlines() if 'warning(scripts)' in l or 'error' in l.lower() or 'HUD_API' in l]}
(b/'evidence/interactive-hd-comms.json').write_text(json.dumps(record,indent=2)+'\n')
assert code==0
assert not any('warning(scripts)' in l or 'error' in l.lower() for l in record['diagnostics'])
