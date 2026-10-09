local hud=require("openreliant.hud")
local last=""
return {engine_handlers={on_frame=function()
 local g,r,p,m,t=hud.guns,hud.radar,hud.power,hud.missiles,hud.target_display
 if not g or not r or not p or not m then return end
 local state="range="..r.range.." zoom="..tostring(r.zooming).." radar_custom="..tostring(table.find(hud.replaced,"radar")~=nil).." power="..p.guns..","..p.engines..","..p.shields.." full="..tostring(g.all).." synchronised="..tostring(g.synchronised).." missile="..tostring(m.armed).." subtarget="..tostring(if t then t.subtarget else nil).." charge="..math.floor(hud.gauges.charge*10)
 if state~=last then last=state;print("HUD_API "..state) end
end}}
