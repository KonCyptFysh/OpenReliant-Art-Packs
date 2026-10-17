-- Observe every Kurgen, AI and player. This script changes no flight/combat values.
local world = require("openreliant.world")
local records = require("openreliant.records")
local storage = require("openreliant.storage")
local response = require("kurgen_response")
local bus = storage.game_section("kurgen_lighting")
local states = {}
local function normalized(ship)
    local full = math.max(1, records.ships[ship.type].armor_class * 6 - 1)
    local a = ship.armor
    return {a.left / full, a.right / full, a.fore / full, a.aft / full}
end
local function update(dt)
    local present, outputs = {}, {}
    for _, ship in world.objects() do
        if ship.type ~= "kurgan" then continue end
        local key = tostring(ship.slot)
        local armor = normalized(ship)
        local state = states[key]
        if not state then state = response.new(armor); states[key] = state end
        local dead = ship.exploding or ship.ejected
        local p = response.step(state, armor, ship.throttle, ship.engines_disabled,
            dead, ship.lights and not ship.cloaked, dt)
        outputs[key] = {parameters = p, health = state.health, throttle = ship.throttle,
            engine_off = ship.engines_disabled, flickers = state.flickers}
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
