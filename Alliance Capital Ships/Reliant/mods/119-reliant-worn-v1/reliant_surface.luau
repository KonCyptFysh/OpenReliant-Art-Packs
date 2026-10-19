local shaders = require("openreliant.shaders")
local nearby = require("openreliant.nearby")
local self = require("openreliant.self")
local storage = require("openreliant.storage")
local core = require("openreliant.core")
local hud = require("openreliant.hud")
local bus = storage.game_section("reliant_lighting")
local review = false
local running = false
local name = shaders.register_surface({name = "reliant_systems", shader = "reliant_systems.glsl", bloom = 0.40})
return { engine_handlers = {
    on_mission_start = function(mission) running = true; review = mission.number == 959 or mission.number == 958 end,
    on_mission_end = function() running = false; review = false end,
    on_key_press = function(key)
        if review and (key == "f5" or key == "f6" or key == "f7" or key == "f8" or key == "f9" or key == "f10" or key == "f12") then
            core.send_global_event("reliant_review", {key = key})
        end
    end,
    on_frame = function()
        if not running or not self:is_valid() then return end
        local outputs = bus.objects or {}
        local ships = nearby.objects(1e12)
        if self:is_valid() then table.insert(ships, self) end
        for _, ship in ships do
            if ship.type ~= "reliant" then continue end
            local state = outputs[tostring(ship.slot)]
            local p = if state then state.parameters else {1, 0, 0, 0}
            if ship.exploding or ship.ejected or ship.cloaked or not ship.lights then p = {0,0,0,0} end
            ship:set_surface(name, p)
            if review and ship.is_player and state and hud.shown then
                hud.text(vector.create(18, 50, 0), "RELIANT LIGHTING TEST   F5 thrust 0/50/100%   F6 small hit   F7 heavy hit   F8 restore   F9 engines   F10 critical   F12 destroy engine", {scale = 0.8})
                hud.text(vector.create(18, 72, 0), string.format("Hull %.0f%%   Cabin %.0f%%   Thrust %.0f%%   Drive %.0f%%   Core %.0f%%   Petals %.0f%%   Engines %s",
                    state.health * 100, p[1] * 100, math.max(0, state.throttle) * 100,
                    p[2] * 100, p[3] * 100, p[4] * 100, if state.engine_off then "OFF" else "ON"), {scale = 0.8})
            end
        end
    end,
}}
