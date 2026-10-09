-- Presentation readings belong to a player script.
local hud=require("openreliant.hud")
local camera=require("openreliant.camera")
local count=0
return {engine_handlers={on_frame=function()
 count+=1
 if count==260 then assert(camera.set_view("chase")) end
 if count==330 then assert(camera.set_view("cockpit")) end
 if count%60==0 then
  print("HUD_API sweep frame="..count.." shown="..tostring(hud.instruments_shown).." speed="..tostring(hud.gauges.speed).." shield_left="..tostring(hud.ship_status.shields.left).." damage="..tostring(hud.damage.weapons).." fuel="..tostring(hud.fuel).." replaced="..table.concat(hud.replaced,","))
 end
end}}
