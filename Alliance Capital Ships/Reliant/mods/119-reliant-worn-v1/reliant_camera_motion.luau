-- Pure camera motion. Distances scale with the actual model radius; physics is untouched.
local M={minimum_radius=.025,maximum_radius=4}
function M.new(radius)
 return {yaw=.68,pitch=-.45,distance=math.max(radius,1)*1.25,pan=vector.create(0,0,0)}
end
function M.offset(s)
 local cp=math.cos(s.pitch)
 return vector.create(math.sin(s.yaw)*cp,math.sin(s.pitch),math.cos(s.yaw)*cp)*s.distance
end
function M.step(s,radius,seconds,keys,orientation)
 local dt=math.clamp(seconds,0,.1)
 local horizontal=(if keys.right then 1 else 0)-(if keys.left then 1 else 0)
 local vertical=(if keys.down then 1 else 0)-(if keys.up then 1 else 0)
 if keys.control then
  s.pan+=(orientation.right*horizontal+orientation.down*vertical)*(s.distance*.65*dt)
 elseif keys.shift then
  s.distance*=math.exp(vertical*1.1*dt)
 else
  s.yaw=(s.yaw+horizontal*.9*dt)%(math.pi*2)
  s.pitch=math.clamp(s.pitch+vertical*.9*dt,-1.55,1.55)
 end
 s.distance=math.clamp(s.distance,math.max(25,radius*M.minimum_radius),math.max(100,radius*M.maximum_radius))
 return s
end
return M
