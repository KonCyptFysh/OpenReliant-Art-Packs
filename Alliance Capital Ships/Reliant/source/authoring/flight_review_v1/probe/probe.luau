local world=require("openreliant.world")
local hooks=require("openreliant.hooks")
local elapsed=0
local lastOrder="unset"
local carrier=nil
local lastSample=-1
local launched=false
local landing=false
local animationCount=0
local closedAgain=false
local closed=nil
local maxTravel=0
hooks.after("vm_command",function(e)
 if e.command:find("ship_animation") then
  animationCount+=1
  print("FLIGHT_PROBE animation "..e.command.." t="..elapsed.." landing="..tostring(landing))
  assert(not landing,"Review animation must not run after native landing begins")
 end
end)
hooks.add("launched",function(e) launched=true;print("FLIGHT_PROBE launched t="..elapsed) end)
hooks.add("order_land_init",function(e)
 if e.object.is_player then landing=true;print("FLIGHT_PROBE LAND_REQUEST t="..elapsed) end
end)
hooks.add("radio_say",function(e) print("FLIGHT_PROBE radio "..tostring(e.speech)) end)
return {engine_handlers={
 on_update=function(dt)
  elapsed+=dt
  local player=world.player
  if not player then return end
  if not carrier then for _,o in world.objects() do if o.type=="reliant" then carrier=o end end end
  if player.order~=lastOrder then
   lastOrder=player.order
   print("FLIGHT_PROBE ORDER "..tostring(lastOrder).." t="..elapsed.." ship="..player.type)
  end
  if math.floor(elapsed/3)~=lastSample then
   lastSample=math.floor(elapsed/3)
   local hangar=false
   for _,o in world.objects() do if o.type=="reliant_hangar" then hangar=true end end
   print("FLIGHT_PROBE sample t="..elapsed.." player="..tostring(player.position).." hangar="..tostring(hangar).." maxDoor="..maxTravel)
  end
  if carrier and launched and not landing then
   for _,p in carrier:parts() do
    if p.name=="Rel bot dr 1" then
     if not closed then closed=p.position end
     local travel=vector.magnitude(p.position-closed)
     maxTravel=math.max(maxTravel,travel)
     if travel<1 and maxTravel>2000 and not closedAgain then
      closedAgain=true;print("FLIGHT_PROBE DOORS_OPEN_CLOSE_PASS travel="..maxTravel)
     end
    end
   end
  end
 end,
 on_mission_end=function()
  assert(launched and landing and closedAgain and maxTravel>2000,"Incomplete native flight cycle")
  print("FLIGHT_PROBE PASS launch, free flight, doors, landing and mission end t="..elapsed)
 end,
}}
