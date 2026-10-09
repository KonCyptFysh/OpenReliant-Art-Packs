local hud=require("openreliant.hud")
local camera=require("openreliant.camera")
local count=0
local function show(name,value)
 if type(value)=="table" then
  local parts={}
  for k,v in value do table.insert(parts,tostring(k).."="..tostring(v)) end
  table.sort(parts);print("HUD_API "..name.." {"..table.concat(parts,",").."}")
 else print("HUD_API "..name.." "..tostring(value)) end
end
return {engine_handlers={on_frame=function()
 count+=1
 if count==60 then print("HUD_API switch_to_chase "..tostring(camera.set_view("chase"))) end
 if count~=30 and count~=180 then return end
 print("HUD_API_FRAME "..count)
 show("camera_view",camera.view)
 show("instruments_shown",hud.instruments_shown)
 for _,name in {"guns","missiles","radar","gauges","fuel","countermeasures","kills","ship_status","lights","clock","view_name","caption"} do
  local ok,value=pcall(function() return hud[name] end)
  if not ok then error(name..": "..tostring(value)) end
  show(name,value)
  if name=="ship_status" and value then show("shields",value.shields);show("armor",value.armor) end
 end
end}}
