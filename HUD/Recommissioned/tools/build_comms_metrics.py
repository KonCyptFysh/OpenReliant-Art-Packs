#!/usr/bin/env python3
"""Measure visible glyph bearings for the HUD's comms columns; no artwork edits.

Uses the game's original BLUFONT.FNT layout and the chosen outline font. The
engine centres outline ink on bitmap ink rather than using TrueType advances.
Run with --native-font pointing to an extracted original BLUFONT.FNT.
"""
import argparse, hashlib, json, struct
from pathlib import Path
import numpy as np
from PIL import ImageFont


def measure(native, outline):
    raw=native.read_bytes()
    count,height=struct.unpack_from('<II',raw,4)
    glyphs={};end=16+count*4
    for code in range(count):
        at=struct.unpack_from('<I',raw,16+code*4)[0]
        if not at: continue
        width=struct.unpack_from('<I',raw,at)[0]
        end=max(end,at+4+width*height)
        if width and code<255: glyphs[code]=np.frombuffer(raw[at+4:at+4+width*height],np.uint8).reshape(height,width)
    assert len(raw)-end==768, 'Expected original BLUFONT palette'
    palette=np.frombuffer(raw[end:],np.uint8).reshape(256,3).astype(int)
    palette=(palette<<2)|(palette>>4)
    indices={int(x) for c in b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' for x in glyphs[c].flat if x}
    ink=max((palette[i] for i in indices),key=lambda rgb:rgb@rgb)
    cover=np.clip(palette@ink/(ink@ink),0,1);cover[0]=0
    def span(mask,axis=0):
        peaks=mask.max(axis=axis);used=np.flatnonzero(peaks>0)
        if not len(used):return None
        return used[0]+1-peaks[used[0]],used[-1]+peaks[used[-1]]
    # A large measurement makes subpixel raster rounding negligible. No PNGs
    # are generated. The resulting values are in original HUD font pixels.
    font=ImageFont.truetype(str(outline),size=512)
    mask=font.getmask('H'); hspan=span(np.asarray(mask).reshape(mask.size[1],mask.size[0])/255,1)
    bspan=span(cover[glyphs[ord('H')]],1)
    fit=(bspan[1]-bspan[0])/(hspan[1]-hspan[0])
    bearings={}
    for code,pixels in glyphs.items():
        if code<32:continue
        try: char=bytes([code]).decode('cp1252')
        except UnicodeDecodeError:continue
        bounds=span(cover[pixels]);mask=font.getmask(char)
        if not bounds or not mask.size[0] or not mask.size[1]:continue
        outlined=span(np.asarray(mask).reshape(mask.size[1],mask.size[0])/255)
        if outlined:
            bearings[str(ord(char))]=round(sum(bounds)/2-(outlined[1]-outlined[0])*fit/2,6)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    return {'native_font_sha256':sha(native),'outline_font_sha256':sha(outline),
            'measurement':'native bitmap ink midpoint minus half fitted outline ink width',
            'units':'original HUD font pixels','ink_bearings':bearings}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-font',required=True,type=Path)
    p.add_argument('--outline-font',type=Path,default=root/'source/runtime-meta/rc_comms.ttf')
    p.add_argument('--output',type=Path,default=root/'source/scripts/comms-ink-metrics.json')
    a=p.parse_args();a.output.write_text(json.dumps(measure(a.native_font,a.outline_font),indent=2)+'\n')
