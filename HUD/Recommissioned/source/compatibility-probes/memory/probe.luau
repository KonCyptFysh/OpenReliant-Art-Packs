local files={"rc_missiles_bandit_slot_00_gold.png", "rc_missiles_bandit_slot_01_red.png", "rc_missiles_bandit_slot_02_red.png", "rc_missiles_bandit_slot_03_red.png", "rc_missiles_bandit_slot_04_red.png", "rc_missiles_bandit_slot_05_red.png", "rc_missiles_bandit_slot_06_red.png", "rc_missiles_bandit_slot_07_red.png", "rc_missiles_bandit_slot_08_red.png", "rc_missiles_bandit_slot_09_red.png", "rc_missiles_havoc_slot_00_gold.png", "rc_missiles_havoc_slot_01_red.png", "rc_missiles_havoc_slot_02_red.png", "rc_missiles_havoc_slot_03_red.png", "rc_missiles_havoc_slot_04_red.png", "rc_missiles_havoc_slot_05_red.png", "rc_missiles_havoc_slot_06_red.png"}
local hud=require("openreliant.hud")
local at=0
return {engine_handlers={on_frame=function()
 if not hud.shown or at>=#files then return end
 at+=1
 local ok,value=pcall(hud.picture,vector.zero,files[at],vector.create(1,1,0))
 print("HUDPROBE asset "..tostring(at)..": "..tostring(ok).." "..tostring(value))
end}}
