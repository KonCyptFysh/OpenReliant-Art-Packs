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
 for _,name in {"guns","missiles","radar","gauges","fuel","countermeasures","kills","ship_status","lights","clock","view_name","caption","target_display"} do
  local ok,value=pcall(function() return hud[name] end)
  if not ok then error(name..": "..tostring(value)) end
  show(name,value)
  if name=="radar" and value then
   show("radar_contacts_count",#value.contacts)
   local looks={}
   for i,c in value.contacts do
    looks[c.look]=(looks[c.look] or 0)+1
    if i<=8 then show("radar_contact_"..i,{at=c.at,height=c.height,look=c.look,object_present=c.object~=nil}) end
   end
   show("radar_looks",looks)
  end
  if name=="target_display" and value then show("target_shields",value.shields);show("target_armor",value.armor) end
  if name=="ship_status" and value then show("shields",value.shields);show("armor",value.armor) end
 end
end}}
