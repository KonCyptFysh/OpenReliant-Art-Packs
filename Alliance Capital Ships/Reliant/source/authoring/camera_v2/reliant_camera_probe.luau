local motion=require("reliant_camera_motion")
local t=0
local zoomStart,zoomEnd,panLength
local step=motion.step
local exercised=false
motion.step=function(s,r,dt,keys,orientation)
 if not exercised then
  local before=s.distance
  step(s,r,.1,{shift=true,up=true},orientation)
  assert(s.distance<before and s.distance<r*1.8,"closer than native clamp")
  step(s,r,.1,{control=true,right=true},orientation)
  assert(vector.magnitude(s.pan)>0)
  print("RELIANT_CAMERA frame PASS distance="..s.distance.." radius="..r)
  exercised=true
 end
 return step(s,r,dt,keys,orientation)
end

local camera=require("openreliant.camera")
local base=require("reliant_camera").engine_handlers
-- Frame-driven checks allow texture-loading stalls before the first rendered view.
local frames=0
local function detail() assert(type(camera.view)=="string" and string.find(camera.view,"reliant_detail")) end
return {engine_handlers={
 on_mission_start=base.on_mission_start,
 on_mission_end=base.on_mission_end,
 on_frame=function(dt)
  frames+=1
  base.on_frame()
  if frames==20 then detail();assert(exercised);print("RELIANT_CAMERA default detail")
  elseif frames==30 then base.on_key_press("f4");assert(camera.view=="external");print("RELIANT_CAMERA standard toggle")
  elseif frames==40 then base.on_key_press("f4")
  elseif frames==50 then detail();print("RELIANT_CAMERA detail toggle");base.on_key_press("page_down")
  elseif frames==60 then detail();print("RELIANT_CAMERA bridge focus");base.on_key_press("page_down")
  elseif frames==70 then detail();print("RELIANT_CAMERA engine focus");base.on_key_press("home")
  elseif frames==80 then detail();print("RELIANT_CAMERA reset");base.on_key_press("page_up")
  elseif frames==90 then detail();print("RELIANT_CAMERA reverse engine focus")
  elseif frames==120 then detail();print("RELIANT_CAMERA PASS") end
 end,
}}
