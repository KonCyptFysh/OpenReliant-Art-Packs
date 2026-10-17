local response = require("./prowler_response")
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
check(p[2] < .0001 and p[3] > .5 and p[3] < .65, "engine disable cuts drive while heat cools more slowly")
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
local cooling = response.new(armor(1), 123)
run(cooling,armor(1),1,false,80,.04)
local fullyHot = cooling.heat
run(cooling,armor(1),0,false,14,.04)
check(math.abs(cooling.heat / fullyHot - math.exp(-1)) < 1e-6, "14-second cooling time constant")

local function clone(t)
    local copy = {}
    for k,v in t do copy[k] = if type(v)=="table" then clone(v) else v end
    return copy
end
local critical = response.new(armor(.3), 19873)
local events, depths, patterns, quiet, longestQuiet, dimFrames = {}, {}, {}, 0, 0, 0
for _=1,24000 do
    local oldCount = critical.disruptions
    response.step(critical,armor(.3),0,false,false,true,.01)
    if critical.disruptions > oldCount then
        table.insert(events, critical.last_disruption)
        table.insert(patterns, #critical.disruption_pulses)
        table.insert(depths, critical.disruption_pulses[1][3])
        local gap = critical.next_disruption - critical.disruption_end
        assert(gap >= 3 and gap <= 6, "quiet interval bounds")
    end
    if critical.cabin < critical.cabin_base*.99 then quiet=0; dimFrames+=1 else quiet+=.01 end
    longestQuiet=math.max(longestQuiet,quiet)
end
check(critical.flickers==0 and #events>15, "30% damaged spawn has sustained faults without any hits")
check(longestQuiet<7, "never more than 7 seconds of uninterrupted light at critical health")
check(dimFrames/24000 < .2 and dimFrames>100, "brief visible disruptions, mostly steady light")
local irregular=false
for i=3,#events do if math.abs((events[i]-events[i-1])-(events[2]-events[1]))>.5 then irregular=true end end
check(irregular, "burst intervals have no fixed period")
local variedDepth, variedCount=false,false
for i=2,#depths do
    variedDepth = variedDepth or math.abs(depths[i]-depths[1])>.1
    variedCount = variedCount or patterns[i]~=patterns[1]
end
check(variedDepth and variedCount, "pulse strengths and counts also vary")
local stable=response.new(armor(.301), 19873)
run(stable,armor(.301),0,false,180,.04)
check(stable.disruptions==0, "above 30% remains free of spontaneous outages")
local crossed=response.new(armor(.32), 911)
run(crossed,armor(.30),0,false,15,.01)
check(crossed.disruptions>=1 and crossed.flickers==0, "minor hit crossing 30% enables faults")
local earlier=critical.disruptions
run(critical,armor(.5),0,false,30,.04)
check(critical.disruptions==earlier and critical.next_disruption==nil and #critical.disruption_pulses==0,
      "repair above threshold cancels all sustained outages")
check(math.abs(critical.cabin-.5^1.25)<1e-6,"repair returns to steady health-based light")
local original=response.new(armor(.25), 444)
run(original,armor(.25),0,false,8,.01)
local restored=clone(original)
local saveMatched=true
for _=1,6000 do
    local x=response.step(original,armor(.25),0,false,false,true,.01)
    local y=response.step(restored,armor(.25),0,false,false,true,.01)
    saveMatched = saveMatched and x[1]==y[1] and original.rng==restored.rng
end
check(saveMatched,"saved state preserves the complete future fault sequence")
local pause=clone(restored)
response.step(restored,armor(.25),0,false,false,true,0)
check(restored.time==pause.time and restored.rng==pause.rng and restored.next_disruption==pause.next_disruption
      and restored.disruptions==pause.disruptions and restored.cabin==pause.cabin,"pause does not reroll or advance faults")
local other=response.new(armor(.25),445)
run(other,armor(.25),0,false,68,.01)
check(other.next_disruption~=original.next_disruption, "different ships have independent sequences")
local slow,fast=response.new(armor(.25),99),response.new(armor(.25),99)
run(slow,armor(.25),0,false,180,.1);run(fast,armor(.25),0,false,180,.01)
check(slow.disruptions==fast.disruptions and math.abs(slow.next_disruption-fast.next_disruption)<1e-8,
      "fault event schedule is independent of simulation timestep")
local old=response.new(armor(.25),1)
old.rng=nil;old.disruptions=nil;old.disruption_pulses=nil
run(old,armor(.25),0,false,15,.01)
check(old.disruptions>=1,"earlier saved PoC states migrate without losing the response")
local dark=response.step(fast,armor(.25),0,false,false,false,.01)
check(dark[1]==0,"critical disruptions cannot override lights-off")
local was=fast.disruptions
run(fast,armor(.25),0,false,.2,.01)
local dead=response.step(fast,armor(.25),1,false,true,true,30)
check(dead[1]==0 and dead[2]==0 and dead[3]==0 and fast.next_disruption==nil,
      "destruction cancels random power faults")
print(string.format("PASS %d response checks; %d random outages over 240s; longest steady interval %.2fs; dim duty %.1f%%",
                    checks,#events,longestQuiet,100*dimFrames/24000))
