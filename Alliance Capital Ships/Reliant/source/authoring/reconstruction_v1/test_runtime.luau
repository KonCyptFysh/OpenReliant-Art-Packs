-- Integration fixture only; not distributed. The observer clock is accelerated 10x
-- in the probe copy. Native doors and destruction still run through the real engine.
local world=require("openreliant.world")
local storage=require("openreliant.storage")
local core=require("openreliant.core")
local bus=storage.game_section("reliant_lighting")
local t=0
local done={}
local minCabin,maxCabin=1,0
local doorClosed,doorOpen
local maxDoorTravel=0
local animationCommands=0
local hooks=require("openreliant.hooks")
hooks.after("vm_command",function(e)
 if string.find(e.command,"ship_animation") then animationCommands+=1;print("RELIANT_VM "..e.command.." t="..tostring(t)) end
end)
local function command(k) core.send_global_event("reliant_review",{key=k}) end
local function state() return assert((bus.objects or {})[tostring(world.player.slot)],"Reliant lighting state") end
local function once(at,label,fn)
 if t>=at and not done[label] then done[label]=true; fn(); print("RELIANT_TEST "..label) end
end
local function door()
 for _,p in world.player:parts() do if p.name=="Rel bot dr 1" then return assert(p.position) end end
 error("native door absent")
end
return {engine_handlers={on_update=function(dt)
 t+=dt*10
 if doorClosed then maxDoorTravel=math.max(maxDoorTravel,vector.magnitude(door()-doorClosed)) end
 if t>40 and t<75 then local c=state().parameters[1]; minCabin=math.min(minCabin,c); maxCabin=math.max(maxCabin,c) end
 once(.5,"cold",function()
  assert(world.player.type=="reliant")
  local s=state(); assert(s.parameters[1]>.999 and s.parameters[2]==0 and s.engine_health==1 and not s.engine_off)
  local engines=0
  for _,p in world.player:parts() do
   if p.class=="engine" and p.component~=nil then engines+=1; print("RELIANT_ENGINE "..p.name.." component="..p.component.." armor="..p.armor); assert(p.component==4) end
  end
  assert(engines==1); doorClosed=door(); command("f5")
 end)
 once(4,"half",function() local s=state(); assert(math.abs(s.parameters[2]-.5)<.001);command("f5") end)
 once(35,"doors_open",function() doorOpen=door();print("RELIANT_DOOR travel="..vector.magnitude(doorOpen-doorClosed));assert(vector.magnitude(doorOpen-doorClosed)>2000) end)
 once(28,"hot",function() local s=state();assert(s.parameters[2]>.999 and s.parameters[3]>.94);command("f5") end)
 once(29.5,"cooling",function()local s=state();assert(s.parameters[2]<.01 and s.parameters[3]>.78);command("f6") end)
 once(31,"minor_hit",function()local s=state();assert(s.flickers==0 and s.health>.979 and s.health<.981);command("f7") end)
 once(34,"heavy_hit",function()assert(state().flickers==1);command("f8");command("f5");command("f9") end)
 once(75,"doors_closed",function()assert(vector.magnitude(door()-doorClosed)<1) end)
 once(38,"disabled",function()local s=state();assert(s.engine_off and s.parameters[2]<.001);command("f9");command("f5");command("f10") end)
 once(105,"doors_reopen",function()assert(vector.magnitude(door()-doorOpen)<1) end)
 once(76,"critical_surges",function()local s=state();assert(s.critical and s.disruptions>=3 and minCabin==0 and maxCabin==1);print("RELIANT_SURGE 0..100% faults="..s.disruptions);command("f8") end)
 once(80,"repaired",function()assert(state().parameters[1]>.999 and not state().critical);command("f12") end)
 once(84,"real_engine_destroyed",function()local s=state();assert(s.engine_destroyed and s.engine_off and s.engine_health==0 and s.parameters[2]<.001); print("RELIANT_ANIMATION commands="..animationCommands.." max_travel="..maxDoorTravel); print("RELIANT_TEST lighting PASS") end)
 once(108,"PASS",function()assert(animationCommands==12 and maxDoorTravel>2000); print("RELIANT_TEST PASS native engine destruction, open-close-open doors, cabin faults and thermal response") end)
end}}
