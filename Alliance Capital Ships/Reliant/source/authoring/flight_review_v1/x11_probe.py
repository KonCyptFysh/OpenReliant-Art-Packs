# Local runtime validation only; never included in the mod.
import ctypes as C, sys, time
from pathlib import Path
X=C.CDLL('libX11.so.6'); T=C.CDLL('libXtst.so.6')
X.XOpenDisplay.argtypes=[C.c_char_p]; X.XOpenDisplay.restype=C.c_void_p
X.XDefaultRootWindow.argtypes=[C.c_void_p];X.XDefaultRootWindow.restype=C.c_ulong
X.XQueryTree.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_ulong),C.POINTER(C.POINTER(C.c_ulong)),C.POINTER(C.c_uint)]
X.XFetchName.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_char_p)]
X.XFree.argtypes=[C.c_void_p]
X.XSetInputFocus.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_ulong]
X.XRaiseWindow.argtypes=[C.c_void_p,C.c_ulong]
X.XStringToKeysym.argtypes=[C.c_char_p];X.XStringToKeysym.restype=C.c_ulong
X.XKeysymToKeycode.argtypes=[C.c_void_p,C.c_ulong];X.XKeysymToKeycode.restype=C.c_uint
X.XFlush.argtypes=[C.c_void_p]
T.XTestFakeKeyEvent.argtypes=[C.c_void_p,C.c_uint,C.c_int,C.c_ulong]
d=X.XOpenDisplay(None);assert d,'X display unavailable'
def search(w):
 name=C.c_char_p();X.XFetchName(d,w,C.byref(name));s=name.value.decode(errors='replace') if name.value else '';X.XFree(name)
 if s: print('WINDOW',w,s,flush=True)
 if 'StarLancer' in s or s.startswith('OpenReliant'): return w,s
 root=C.c_ulong();parent=C.c_ulong();children=C.POINTER(C.c_ulong)();count=C.c_uint()
 if X.XQueryTree(d,w,C.byref(root),C.byref(parent),C.byref(children),C.byref(count)):
  ws=[children[i] for i in range(count.value)];X.XFree(children)
  for child in ws:
   r=search(child)
   if r:return r
r=search(X.XDefaultRootWindow(d));assert r,'No OpenReliant window';w,name=r
print('Selected',w,name,flush=True)
X.XRaiseWindow(d,w);X.XSetInputFocus(d,w,1,0);X.XFlush(d);time.sleep(.25)
def key(name,down):
 code=X.XKeysymToKeycode(d,X.XStringToKeysym(name.encode()));assert code,name
 T.XTestFakeKeyEvent(d,code,down,0);X.XFlush(d)
if sys.argv[1]=='shot':
 from PIL import ImageGrab
 ImageGrab.grab(xdisplay=':0').save(sys.argv[2])
elif sys.argv[1]=='tap':
 for name in sys.argv[2:]:key(name,1);time.sleep(.15);key(name,0);time.sleep(.6)
elif sys.argv[1]=='hold':
 key(sys.argv[2],1);time.sleep(float(sys.argv[3]));key(sys.argv[2],0)
