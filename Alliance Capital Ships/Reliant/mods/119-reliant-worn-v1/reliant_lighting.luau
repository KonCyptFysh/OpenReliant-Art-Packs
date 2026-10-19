-- Observe every Reliant, AI and player. This script changes no flight/combat values.
local world = require("openreliant.world")
local records = require("openreliant.records")
local storage = require("openreliant.storage")
local response = require("reliant_response")
local bus = storage.game_section("reliant_lighting")
local states = {}
local function normalized(ship)
    local full = math.max(1, records.ships[ship.type].armor_class * 6 - 1)
    local a = ship.armor
    -- The Reliant also has a separately counted hull component. Its real damage
    -- must dim cabins even when the four armour fields have not changed.
    local hull = 1
    for _, part in ship:parts() do
        if part.class == "hull" and part.component ~= nil and part.full_armor and part.full_armor > 0 then
            hull = math.min(hull, (part.armor or 0) / part.full_armor)
        end
    end
    return {math.min(hull,a.left/full), math.min(hull,a.right/full),
        math.min(hull,a.fore/full), math.min(hull,a.aft/full)}
end
local function update(dt)
    local present, outputs = {}, {}
    for _, ship in world.objects() do
        if ship.type ~= "reliant" then continue end
        local key = tostring(ship.slot)
        local armor = normalized(ship)
        local state = states[key]
        if not state then state = response.new(armor); states[key] = state end
        local engine_health = 1
        local engine_destroyed = false
        for _, part in ship:parts() do
            if part.class == "engine" and part.component ~= nil then
                engine_destroyed = engine_destroyed or part.destroyed
                if part.full_armor and part.full_armor > 0 then
                    engine_health = math.min(engine_health, math.clamp((part.armor or 0) / part.full_armor, 0, 1))
                end
            end
        end
        local engine_off = ship.engines_disabled or engine_destroyed or engine_health <= 0
        local dead = ship.exploding or ship.ejected
        local p = response.step(state, armor, ship.throttle * engine_health, engine_off,
            dead, ship.lights and not ship.cloaked, dt)
        outputs[key] = {parameters = p, health = state.health, throttle = ship.throttle,
            engine_off = engine_off, engine_health = engine_health, engine_destroyed = engine_destroyed, flickers = state.flickers,
            disruptions = state.disruptions, critical = state.health <= response.config.critical_health}
        present[key] = true
    end
    for key in states do if not present[key] then states[key] = nil end end
    bus.objects = outputs
end
return { engine_handlers = {
    on_mission_start = function() states = {}; bus.objects = {} end,
    on_mission_end = function() states = {}; bus.objects = {} end,
    on_object_removed = function(ship) states[tostring(ship.slot)] = nil end,
    on_update = update,
    on_save = function() return states end,
    on_load = function(saved) states = saved or {} end,
}}
