local hud=require("openreliant.hud")
local camera=require("openreliant.camera")
local oldMenu="unset"
local oldView="unset"
return {engine_handlers={on_frame=function()
 local menu=table.concat(hud.comms," | ")
 if menu~=oldMenu then oldMenu=menu;print("FLIGHT_PROBE COMMS "..menu) end
 if camera.view~=oldView then oldView=camera.view;print("FLIGHT_PROBE CAMERA "..tostring(oldView)) end
end}}
