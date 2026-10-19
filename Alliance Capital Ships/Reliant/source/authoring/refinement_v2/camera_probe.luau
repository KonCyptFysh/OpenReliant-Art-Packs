local base=require("reliant_camera").engine_handlers
local n=0
return {engine_handlers={on_mission_start=base.on_mission_start,on_mission_end=base.on_mission_end,on_frame=function(dt)
 n+=1;base.on_frame(dt)
 if n==15 then base.on_key_press("page_up") end
end}}
