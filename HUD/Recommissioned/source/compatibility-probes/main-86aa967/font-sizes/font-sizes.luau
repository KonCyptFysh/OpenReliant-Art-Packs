local hud=require("openreliant.hud")
local p=vector.create
hud.register_display("font-sizes",{frame=function()
 hud.rectangle(p(0,0),p(1920,1080),{colour=p(0,0,0)})
 for i,scale in {1,1.2,1.4,1.6,1.8,2} do
  local y=40+(i-1)*140
  hud.text(p(40,y),"PROTON CANNON 0123456789",{font="shared.ttf",base_font="hud",scale=scale})
  hud.text(p(1000,y),"PROTON CANNON 0123456789",{font="control"..i..".ttf",base_font="hud",scale=scale})
 end
end})
return {}
