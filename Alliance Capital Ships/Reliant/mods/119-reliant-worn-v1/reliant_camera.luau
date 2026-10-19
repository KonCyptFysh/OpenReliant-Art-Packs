-- Review-only detail camera through the official camera API.
local core=require("openreliant.core")
local camera=require("openreliant.camera")
local input=require("openreliant.input")
local util=require("openreliant.util")
local self=require("openreliant.self")
local hud=require("openreliant.hud")
local motion=require("reliant_camera_motion")
local active=false
local pending=false
local state=nil
local focus=1
local labels={"Whole ship","Bridge / comms","Engines"}
local function reset()
 state=motion.new(if self:is_valid() then self.radius else 1)
 focus=1
end
local function anchor(ship)
 if focus>1 then
  local wanted=if focus==2 then "Reliant Comms" else "Reliant Eng"
  for _,part in ship:parts() do
   if part.name==wanted and not part.destroyed and part.position then return part.position end
  end
  for _,part in ship:parts() do
   if part.name==wanted.." DEST" and part.position then return part.position end
  end
 end
 return ship.position
end
local view=camera.register_view("reliant_detail",{
 letterbox=false,
 frame=function(ship,seconds)
  if not state then state=motion.new(ship.radius) end
  local orientation=util.look_at(-motion.offset(state))
  if not (input.key_down("left_alt") or input.key_down("right_alt")) then motion.step(state,ship.radius,seconds,{
   left=input.key_down("left"),right=input.key_down("right"),
   up=input.key_down("up"),down=input.key_down("down"),
   shift=input.key_down("left_shift") or input.key_down("right_shift"),
   control=input.key_down("left_control") or input.key_down("right_control"),
  },orientation) end
  local offset=motion.offset(state)
  return {position=anchor(ship)+state.pan+offset,orientation=util.look_at(-offset)}
 end,
})
local function next_focus(direction)
 focus=(focus-1+direction)%#labels+1
 state=motion.new(self.radius)
 if focus==2 then state.distance=self.radius*.32;state.yaw=.9;state.pitch=-.25
 elseif focus==3 then state.distance=self.radius*.38;state.yaw=math.pi+.22;state.pitch=-.16 end
 pending=true
end
return {engine_handlers={
 on_mission_start=function(mission)
  active=mission.number==958 or mission.number==959
  if active then reset();pending=true end
 end,
 on_mission_end=function()active=false;pending=false;state=nil end,
 on_key_press=function(key)
  if not active or not self:is_valid() then return end
  if key=="f4" then
   if camera.view==view then camera.set_view("external",self);pending=false else pending=true end
  elseif key=="home" then
   if input.key_down("left_alt") or input.key_down("right_alt") then core.send_global_event("reliant_rotate",{reset=true}) else reset();pending=true end
  elseif key=="page_down" then next_focus(1)
  elseif key=="page_up" then next_focus(-1) end
 end,
 on_frame=function(dt)
  if not active or not self:is_valid() then return end
  if pending and camera.set_view(view,self) then pending=false end
  if input.key_down("left_alt") or input.key_down("right_alt") then
   local yaw=(if input.key_down("right") then 1 else 0)-(if input.key_down("left") then 1 else 0)
   local pitch=(if input.key_down("down") then 1 else 0)-(if input.key_down("up") then 1 else 0)
   local roll=(if input.key_down("period") then 1 else 0)-(if input.key_down("comma") then 1 else 0)
   if yaw~=0 or pitch~=0 or roll~=0 then core.send_global_event("reliant_rotate",{yaw=yaw,pitch=pitch,roll=roll,seconds=math.clamp(dt,0,.1)}) end
  end
  if hud.shown then
   if camera.view==view then
    hud.text(vector.create(18,94,0),"DETAIL CAMERA   Arrows orbit   Shift+Up/Down zoom   Ctrl+Arrows pan   PgUp/PgDn focus   Home reset   F4 standard camera",{scale=.8})
    hud.text(vector.create(18,116,0),"Focus: "..labels[focus].."   Alt+Arrows rotate ship   Alt+,/. roll   Alt+Home reset ship",{scale=.8})
   else
    hud.text(vector.create(18,94,0),"F4: detail camera with close zoom and panning",{scale=.8})
   end
  end
 end,
}}
