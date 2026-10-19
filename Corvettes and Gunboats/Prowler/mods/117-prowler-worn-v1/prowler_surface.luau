local shaders = require("openreliant.shaders")
local nearby = require("openreliant.nearby")
local self = require("openreliant.self")
local storage = require("openreliant.storage")
local bus = storage.game_section("prowler_lighting")
local running = false
local name = shaders.register_surface({name = "prowler_systems", shader = "prowler_systems.glsl", bloom = 0.40})
return { engine_handlers = {
    on_mission_start = function() running = true end,
    on_mission_end = function() running = false end,
    on_frame = function()
        if not running or not self:is_valid() then return end
        local outputs = bus.objects or {}
        local ships = nearby.objects(1e12)
        if self:is_valid() then table.insert(ships, self) end
        for _, ship in ships do
            if ship.type ~= "prowler" then continue end
            local state = outputs[tostring(ship.slot)]
            local p = if state then state.parameters else {1, 0, 0, 1}
            if ship.exploding or ship.ejected or ship.cloaked or not ship.lights then p = {0,0,0,0} end
            ship:set_surface(name, p)
        end
    end,
}}
