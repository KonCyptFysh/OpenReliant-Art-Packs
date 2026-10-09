local hud=require("openreliant.hud")
local at=0
return {engine_handlers={on_frame=function()
 if not hud.shown then return end
 for _=1,4 do
  if at>=129 then return end
  at+=1
  local ok,value=pcall(hud.picture,vector.zero,string.format("probe_%03d.png",at),vector.create(1,1,0))
  if at>=127 or not ok then print("HUDPROBE asset "..tostring(at)..": "..tostring(ok).." "..tostring(value)) end
 end
end}}
