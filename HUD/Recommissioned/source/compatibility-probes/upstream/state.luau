local hud=require('openreliant.hud')
local ship=require('openreliant.self')
local supported=pcall(function() return hud.bounds end)
if not supported then return {} end
local count=0
return {engine_handlers={on_frame=function()
 if not hud.shown then return end
 count+=1
 if count~=30 then return end
 print('HUD_STATE type='..tostring(ship.type)..' groups='..tostring(hud.guns.groups)..' gun='..tostring(hud.guns.gun)..' group='..tostring(hud.guns.group)..' all='..tostring(hud.guns.all)..' synchronised='..tostring(hud.guns.synchronised))
 for _,name in hud.replaced do print('HUD_REPLACED '..name) end
 for _,name in {'radar','clock','gunnery','missiles'} do
  local box=hud.bounds(name)
  if box then print('HUD_BOUNDS '..name..' '..box.left..' '..box.top..' '..box.right..' '..box.bottom) end
 end
end}}
