-- Instrumented mission-only integration test; never included in the distributable mod.
local world = require("openreliant.world")
local storage = require("openreliant.storage")
local core = require("openreliant.core")
local bus = storage.game_section("prowler_lighting")
local time = 0
local done = {}
local lowestCabin = 1
local coolingHeat = 0
local faultsBeforeRepair = 0
local function once(at, label, fn)
    if time >= at and not done[label] then done[label] = true; fn(); print("PROWLER_TEST " .. label) end
end
local function command(key) core.send_global_event("prowler_review", {key=key}) end
local function state()
    assert(world.player.type == "prowler", "native type identity")
    return assert((bus.objects or {})[tostring(world.player.slot)], "response bus has Prowler")
end
return {engine_handlers={on_update=function(dt)
    time += dt * 2 -- Match the probe-only acceleration in the controller adapter.
    if time > 27 and time < 28.7 then lowestCabin = math.min(lowestCabin, state().parameters[1]) end
    once(.25,"cold",function()
        local s=state(); assert(s.parameters[1]>.999 and s.parameters[2]==0 and s.parameters[3]==0)
        local components, engines=0,0
        for _, part in world.player:parts() do
            print("PROWLER_PART name="..tostring(part.name).." class="..tostring(part.class).." component="..tostring(part.component).." armor="..tostring(part.armor))
            if part.component ~= nil then components+=1 end
            if part.class == "engine" then engines+=1 end
        end
        assert(components==5 and engines==0,"four turrets plus hull, no separate engines")
        print("PROWLER_NATIVE components="..components.." engine_components="..engines)
    end)
    once(.5,"throttle_half",function() command("f5") end)
    once(3,"half_response",function()
        local s=state(); print(string.format("PROWLER_VALUES half throttle=%.4f drive=%.4f heat=%.4f",s.throttle,s.parameters[2],s.parameters[3]))
        assert(math.abs(s.throttle-.5)<.001 and s.parameters[2]>.49 and s.parameters[2]<.51)
        command("f5")
    end)
    once(25,"hot",function()
        local s=state(); assert(s.parameters[2]>.999 and s.parameters[3]>.93)
        print(string.format("PROWLER_VALUES hot cabin=%.4f drive=%.4f heat=%.4f",s.parameters[1],s.parameters[2],s.parameters[3]))
        command("f5")
    end)
    once(26.1,"cooling",function()
        local s=state(); assert(s.parameters[2]<.02 and s.parameters[3]>.75)
        print(string.format("PROWLER_VALUES cooling drive=%.4f heat=%.4f",s.parameters[2],s.parameters[3]))
        command("f6")
    end)
    once(27,"minor_hit",function()
        local s=state(); assert(s.health>.979 and s.health<.981 and s.flickers==0)
        command("f7")
    end)
    once(28.7,"heavy_hit",function()
        local s=state(); print(string.format("PROWLER_VALUES heavy lowest_cabin=%.4f health=%.4f flickers=%d",lowestCabin,s.health,s.flickers))
        assert(s.flickers==1 and lowestCabin<.65)
    end)
    once(29,"recovered",function()
        local s=state(); assert(s.parameters[1]>.78 and s.parameters[1]<.81 and s.flickers==1)
        command("f8");command("f5");command("f9")
    end)
    once(30,"disabled",function()
        local s=state(); assert(s.engine_off and s.parameters[2]<.01 and s.parameters[1]>.99)
        command("f9");command("f5")
    end)
    once(34,"initial_pass",function()
        local s=state(); assert(not s.engine_off and s.parameters[2]>.999)
        print(string.format("PROWLER_VALUES final cabin=%.4f drive=%.4f heat=%.4f",s.parameters[1],s.parameters[2],s.parameters[3]))
    end)
    once(35,"critical_start",function()
        coolingHeat=state().parameters[3]
        command("f5"); command("f8")
        for _=1,5 do command("f7") end
    end)
    once(36,"critical_health",function()
        local s=state(); assert(s.critical and s.health>.249 and s.health<.251)
    end)
    once(42,"slow_cooldown",function()
        local s=state(); local ratio=s.parameters[3]/coolingHeat
        print(string.format("PROWLER_VALUES 7-second cooling ratio=%.4f",ratio))
        assert(s.parameters[2]<.001 and ratio>.58 and ratio<.64)
    end)
    once(78,"critical_disruptions",function()
        local s=state(); assert(s.critical and s.disruptions>=2)
        print(string.format("PROWLER_VALUES sustained faults=%d health=%.4f",s.disruptions,s.health))
        faultsBeforeRepair=s.disruptions;command("f8")
    end)
    once(82,"PASS",function()
        local s=state(); assert(not s.critical and s.disruptions==faultsBeforeRepair and s.parameters[1]>.999)
    end)
end}}
