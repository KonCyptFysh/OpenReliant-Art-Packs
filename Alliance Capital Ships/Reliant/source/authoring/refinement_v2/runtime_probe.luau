-- Integration fixture only. Physical preview clock remains normal; thermal observer is accelerated.
local world=require("openreliant.world")
local storage=require("openreliant.storage")
local bus=storage.game_section("reliant_lighting")
local core=require("openreliant.core")
local t=0
local done={}
local function once(at,fn) if t>=at and not done[at] then done[at]=true;fn() end end
local original
local function command(k)core.send_global_event("reliant_review",{key=k})end
local function state()return assert(bus.objects[tostring(world.player.slot)])end
return {engine_handlers={on_update=function(dt)
 t+=dt*10
 once(.5,function()
  original=world.player.orientation
  core.send_global_event("reliant_rotate",{yaw=1,pitch=.4,roll=.2,seconds=.1})
 end)
 once(1,function()
  assert(vector.magnitude(world.player.orientation.forward-original.forward)>.01,"ship can rotate under lighting")
  core.send_global_event("reliant_rotate",{reset=true})
 end)
 once(1.5,function()
  assert(vector.magnitude(world.player.orientation.forward-original.forward)<.0001,"ship rotation reset")
  command("f5");command("f5");print("RELIANT_V2 rotation PASS")
 end)
 once(40,function()
  local p=state().parameters;assert(p[2]>.99 and p[3]>.98 and p[4]>.99,"both thermal zones hot");print("RELIANT_V2 hot PASS");command("f5")
 end)
 once(46,function()
  local p=state().parameters;assert(p[2]<.01 and p[3]>p[4]*2 and p[3]>.65,"core retains heat after petals cool");print("RELIANT_V2 cooling PASS")
 end)
 once(50,function()
  command("f5");command("f5");print("RELIANT_V2 PASS")
 end)
end}}
