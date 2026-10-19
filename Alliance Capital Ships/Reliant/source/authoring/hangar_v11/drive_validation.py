"""Exercise actual default COMMS keys after one complete door cycle."""
from pathlib import Path
import subprocess,os,time
W=Path(__file__).parent;log=W/'validated-flight-landing.log'
engine='${OPENRELIANT_HOME}/releases/openreliant-v0.18.0-linux-x86_64/openreliant'
with log.open('w') as output:
    game=subprocess.Popen([engine,'/tmp/reliant-hangar-v11','--mods','119-reliant-worn-v1,96-patriot-worn-v1,118-patriot-cockpit-v1,120-flight-probe','--mission','957','--ship','7','--view','0','--no-sound','--size','1280x720','--no-update-check','--seed','1','--fps','60'],stdout=output,stderr=subprocess.STDOUT,env=dict(os.environ,SDL_VIDEODRIVER='x11'))
    deadline=time.monotonic()+40
    while 'started probe_hud.luau' not in log.read_text():
        assert game.poll() is None and time.monotonic()<deadline
        time.sleep(.2)
    helper=W.parent/'flight_review_v1/x11_probe.py'
    exec(helper.read_text().split("if sys.argv[1]=='shot':")[0])
    # The window may disappear between poll and focus on mission completion.
    callback=C.CFUNCTYPE(C.c_int,C.c_void_p,C.c_void_p)
    ignore=callback(lambda display,event:0);X.XSetErrorHandler(ignore)
    deadline=time.monotonic()+110;requested=False;lastshot=0
    def tap(k):
        key(k,1);time.sleep(.12);key(k,0);time.sleep(.35)
    while game.poll() is None and time.monotonic()<deadline:
        X.XSetInputFocus(d,w,1,0);X.XFlush(d)
        content=log.read_text()
        if 'DOORS_OPEN_CLOSE_PASS' in content and not requested:
            tap('c');tap('1');tap('1');requested=True
        if 'CAMERA landing_tube' in content and time.monotonic()-lastshot>1.3:
            tap('0');lastshot=time.monotonic()
        time.sleep(.1)
    assert game.poll()==0,'Mission did not finish normally'
    assert 'FLIGHT_PROBE PASS launch, free flight, doors, landing and mission end' in log.read_text()
    assert requested
print('COMPLETE NATIVE FLIGHT AND COMMS LANDING VALIDATED',flush=True)
