local hud=require("openreliant.hud")
local self=require("openreliant.self")
local reported=false
return {engine_handlers={on_frame=function()
 if not hud.shown then return end
 local s=math.min(hud.width/1920,hud.height/1080)
 local function p(x,y) return vector.create(x*s,y*s,0) end
 hud.picture(p(785,855),"rc_radar_00_353_short.png",p(350,221))
 hud.text(p(40,280),"MOD SCRIPT: image placement + large text work",{scale=1.5,font="hud"})
 hud.text(p(40,320),"Fuel: "..tostring(self.afterburner_fuel).." / Countermeasures: "..tostring(self.countermeasures),{scale=1.5})
 if not reported then
  reported=true
  print("HUDPROBE: picture, scaled text and live fuel/countermeasures drawn")
  for _,key in {"gun_mode","gun_energy","selected_missile","selected_target","radar_range","kill_count"} do
   local ok,value=pcall(function() return self[key] end)
   print("HUDPROBE field "..key..": "..tostring(ok).." "..tostring(value))
  end
  print("HUDPROBE disable unregistered stock radar: "..tostring(hud.set_display_enabled("radar",false)))
 end
end}}
