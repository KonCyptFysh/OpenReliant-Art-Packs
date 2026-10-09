local hud=require("openreliant.hud")
local done=false
return {engine_handlers={on_frame=function()
 if done or not hud.shown then return end
 done=true
 for _,base in {"default","hud","menu_small","menu_large"} do
  local ok,value=pcall(hud.measure,"H",{font="BLUFONT.ttf",base_font=base})
  print("HUDPROBE custom TTF base "..base..": "..tostring(ok).." "..tostring(value))
 end
 local ok,value=pcall(hud.measure,"H",{font="hud",scale=1.5})
 print("HUDPROBE builtin hud (native TTF replacement): "..tostring(ok).." "..tostring(value))
end}}
