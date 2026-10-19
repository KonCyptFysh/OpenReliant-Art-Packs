-- Test controls only exist in mission 959. Hold the ship in place while using real throttle
-- and armor fields, so the production lighting follows the same state as a normal mission.
local world = require("openreliant.world")
local records = require("openreliant.records")
local hooks = require("openreliant.hooks")
local homes = {}
local thrust = 0
local engine_off = false
local function ships(fn)
    for _, ship in world.objects() do if ship.type == "reliant" then fn(ship) end end
end
local function quiet()
    ships(function(ship)
        local key = tostring(ship.slot)
        if not homes[key] then
            homes[key] = ship.position
            ship.side = "friendly"; ship.invulnerable = "full"
            ship.guns_disabled = true; ship.missiles_disabled = true; ship.eject_disabled = true
        end
        ship.engines_disabled = engine_off
        ship.throttle = if engine_off then 0 else thrust
        ship.velocity = vector.create(0,0,0)
        ship.position = homes[key]
    end)
end
-- Player control updates otherwise overwrite the review throttle before lighting samples it.
hooks.after("player_controls", function() quiet() end)
return {
    engine_handlers = {on_mission_start = quiet, on_step = quiet},
    event_handlers = {reliant_review = function(data)
        if data.key == "f5" then thrust = (thrust + 0.5) % 1.5; engine_off = false
        elseif data.key == "f9" then engine_off = not engine_off
        elseif data.key == "f12" then
            ships(function(ship)
                for _, part in ship:parts() do
                    if part.class == "engine" and part.component ~= nil and not part.destroyed then ship:destroy_component(part.component) end
                end
            end)
        elseif data.key == "f6" or data.key == "f7" or data.key == "f8" or data.key == "f10" then
            ships(function(ship)
                local full = records.ships[ship.type].armor_class * 6 - 1
                local a = table.clone(ship.armor)
                if data.key == "f10" then
                    ship.armor = {left=full*.25,right=full*.25,fore=full*.25,aft=full*.25}
                elseif data.key == "f8" then
                    ship.armor = {left=full, right=full, fore=full, aft=full}
                else
                    local amount = full * (if data.key == "f6" then 0.02 else 0.15)
                    a.aft = math.max(full * 0.05, a.aft - amount)
                    ship.armor = a
                end
            end)
        end
        quiet()
    end},
}
