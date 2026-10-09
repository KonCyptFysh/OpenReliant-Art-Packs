from pathlib import Path
import base64,json,hashlib
w=Path(__file__).resolve().parent
r=w.parents[1]/'mods/recommissioned-hud'
items=[]
def image(name,x,y,width,height,opacity=1):
 p=r/name; items.append({'file':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 data=base64.b64encode(p.read_bytes()).decode()
 return f'<image x="{x}" y="{y}" width="{width}" height="{height}" opacity="{opacity}" href="data:image/png;base64,{data}"/>'
s=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">','<rect width="1600" height="900" fill="#070707"/>']
s += [image('rc_wireframes_frame_123.png',825,180,122,490),image('rc_wireframes_gunnery_floor.png',825,666,580,112),image('rc_gunnery_ship_wireframes_predator_wireframe.png',902,191,460,464),image('rc_gunnery_ship_wireframes_predator_gun_group_1_on.png',902,191,460,464)]
s += ['<g font-family="Oxanium, monospace" fill="#ff8800">','<text x="88" y="230" font-size="27" letter-spacing="7">STARLANCER</text>','<text x="84" y="308" font-size="37" font-weight="600" letter-spacing="2">RECOMMISSIONED</text>','<text x="77" y="470" font-size="186" font-weight="700" letter-spacing="-3">HUD</text>','<text x="90" y="535" font-size="25" letter-spacing="5">BETA  /  1.8</text>','</g>','<path d="M88 568 H540" stroke="#7d1006" stroke-width="2"/>']
s+=['<text x="90" y="798" font-family="Oxanium, monospace" font-size="19" letter-spacing="3" fill="#b45714">KONCYPTFYSH  /  ART PACKS</text>','</svg>']
(w/'hud-cover.svg').write_text('\n'.join(s))
(w/'cover-assets.json').write_text(json.dumps({'method':'SVG editorial composition using unchanged HUD export artwork; no generated artwork','assets':items},indent=2)+'\n')
(w/'fonts.conf').write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><include>/etc/fonts/fonts.conf</include><dir>{r.resolve()}</dir><cachedir>{w.resolve()}/fontcache</cachedir></fontconfig>')
