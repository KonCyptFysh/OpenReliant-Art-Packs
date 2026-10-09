local hud=require("openreliant.hud")
local last=""
hud.register_display("frame_observer",{frame=function()
    local r,c=hud.window_state("radio"),hud.window_state("comms")
    local phase=tostring(if r then r.phase else nil).."/"..tostring(if c then c.phase else nil)
    if phase~=last then print("HUD_PANELS="..phase);last=phase end
end})
return {}
