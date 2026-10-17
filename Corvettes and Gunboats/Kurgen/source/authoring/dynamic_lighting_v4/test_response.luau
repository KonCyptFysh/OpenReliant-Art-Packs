local response = require("./kurgen_response")
local checks = 0
local function check(value, message) checks += 1; assert(value, message) end
local function armor(h) return {h,h,h,h} end
local function run(s, a, thrust, off, seconds, dt)
    local p
    for _ = 1, math.floor(seconds / dt + 0.5) do p = response.step(s,a,thrust,off,false,true,dt) end
    return p
end
local fresh = response.new(armor(1))
local p = run(fresh,armor(1),0,false,20,0.04)
check(p[1] == 1 and p[2] == 0 and p[3] == 0, "healthy cold idle")
check(fresh.flickers == 0, "no spontaneous flicker")
local small = response.new(armor(1))
for i = 1, 10 do run(small,armor(1-i*.02),0,false,1,0.04) end
check(small.flickers == 0, "separated minor hits never flicker")
check(small.cabin < 0.8, "minor damage still dims the cabin")
local big = response.new(armor(1))
run(big,armor(.85),0,false,.16,.04)
check(big.flickers == 1 and big.cabin < big.cabin_base*.7, "large hit interrupts cabin")
run(big,armor(.7),0,false,.16,.04)
check(big.flickers == 1, "cooldown prevents strobing")
run(big,armor(.7),0,false,4,.04)
check(math.abs(big.cabin-.7^1.25)<.001, "settles to damaged brightness")
local burst = response.new(armor(1))
for i=1,4 do run(burst,armor(1-i*.02),0,false,.08,.04) end
check(burst.flickers == 1, "substantial short burst crosses threshold")
local otherQuadrant = response.new({.5,1,1,1})
run(otherQuadrant,{.5,.85,1,1},0,false,.04,.04)
check(otherQuadrant.flickers == 1, "heavy hit on a stronger quadrant is detected")
local hot = response.new(armor(1))
run(hot,armor(1),1,false,24,.04)
check(hot.drive > .999 and hot.heat > .94, "sustained power heats nozzle")
p = run(hot,armor(1),0,false,1,.04)
check(p[2] < .02 and p[3] > .75, "broad light dies quickly while nozzle retains heat")
p = run(hot,armor(1),1,true,6,.04)
check(p[2] < .0001 and p[3] < .4, "engine disable forces cold decay even at high command")
local quick = response.new(armor(1))
run(quick,armor(1),1,false,.2,.04)
check(quick.heat < .03, "short blip cannot leave a fully hot nozzle")
p = response.step(hot,armor(1),1,false,true,true,.04)
check(p[1]==0 and p[2]==0 and p[3]==0, "destroyed ship has no powered effect")
p = response.step(fresh,armor(1),1,false,false,false,.04)
check(p[1]==0 and p[2]==0 and p[3]==0, "mission lights-off and cloak honored")
local a,b = response.new(armor(1)),response.new(armor(1))
run(a,armor(1),1,false,5,.01); run(b,armor(1),1,false,5,.1)
check(math.abs(a.drive-b.drive)<1e-6 and math.abs(a.heat-b.heat)<1e-6,"frame-rate independent thermal response")
local saved = {drive=a.drive,heat=a.heat,time=a.time}
response.step(a,armor(1),1,false,false,true,0)
check(a.drive==saved.drive and a.heat==saved.heat and a.time==saved.time,"pause leaves response unchanged")
local half = response.new(armor(.5))
check(math.abs(half.cabin-.420448)<.00001, "damaged spawn starts correctly without false impact")
check(half.flickers==0,"load/spawn causes no flicker")
print(string.format("PASS %d response checks",checks))
