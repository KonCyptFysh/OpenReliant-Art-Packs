local m=require("./reliant_camera_motion")
local basis={right=vector.create(1,0,0),down=vector.create(0,1,0)}
local r=30000
local s=m.new(r)
local initial=s.distance
for _=1,100 do m.step(s,r,.1,{shift=true,up=true},basis) end
assert(s.distance==r*m.minimum_radius and s.distance<r*1.8/50,"close detail zoom bypasses native radius clamp")
assert(s.yaw==.68 and s.pitch==-.45,"zoom preserves angle")
local d=s.distance
m.step(s,r,.1,{control=true,right=true,up=true},basis)
assert(s.pan.x>0 and s.pan.y<0 and s.pan.z==0 and s.distance==d,"panning moves focus in screen plane only")
for _=1,200 do m.step(s,r,.1,{shift=true,down=true},basis) end
assert(s.distance==r*m.maximum_radius,"bounded zoom out")
for _=1,100 do m.step(s,r,.1,{down=true},basis) end
assert(s.pitch==1.55,"stable pole limit")
assert(math.abs(vector.magnitude(m.offset(s))-s.distance)<.1,"orbit offset retains distance")
local a,b=m.new(r),m.new(r)
for _=1,100 do m.step(a,r,.01,{shift=true,up=true},basis) end
for _=1,10 do m.step(b,r,.1,{shift=true,up=true},basis) end
assert(math.abs(a.distance-b.distance)<.001,"frame-rate independent zoom")
assert(m.new(r).distance==initial and vector.magnitude(m.new(r).pan)==0,"reset restores full view")
local old=s.distance;m.step(s,r,0,{shift=true,up=true},basis);assert(s.distance==old,"zero time leaves view unchanged")
print("PASS 9 camera checks: close zoom, orbit bounds, pan, reset and timestep independence")
