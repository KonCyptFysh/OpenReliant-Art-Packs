local hud=require("openreliant.hud")
local count=0
hud.register_display("observer",{frame=function()
 count+=1
 local state=hud.window_state("radio");local b=hud.bounds("radio");local c=hud.window_state("comms")
 if count%20==0 then print("HUD_PANELS radio="..tostring(if state then state.phase else nil).." bounds="..tostring(if b then b.right else nil).." comms="..tostring(if c then c.phase else nil).." rows="..#hud.comms.." replaces="..table.concat(hud.replaced,",")) end
end})
return {}
