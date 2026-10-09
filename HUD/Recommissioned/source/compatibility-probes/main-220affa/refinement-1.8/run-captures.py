from pathlib import Path
import subprocess,sys
w=Path(__file__).resolve().parent
cases=[('final-both-1080','991','1920x1080','150'),
       ('final-comms-1080','992','1920x1080','150'),
       ('final-portrait-1080','990','1920x1080','150'),
       ('final-both-720','991','1280x720','150'),
       ('final-comms-720','992','1280x720','150'),
       ('final-emblem','991','1920x1080','80'),
       ('final-comms-restored','993','1920x1080','450'),
       ('final-radio-shut','993','1920x1080','600')]
for name,mission,size,ticks in cases:
    subprocess.run([sys.executable,str(w/'capture.py'),name,'--game',str(w/'test-game'),'--mission',mission,'--ship','2','--sound','--size',size,'--ticks',ticks],check=True)
