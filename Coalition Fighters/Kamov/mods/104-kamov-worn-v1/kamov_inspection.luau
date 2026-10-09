-- Only the four Kamov inspection missions load this diagnostic script.
local world = require("openreliant.world")
local util = require("openreliant.util")
local hooks = require("openreliant.hooks")
local steps = 0
local allow_launch = false
local seen = {}
local function configure(object)
    if seen[object.slot] then return end
    seen[object.slot] = true
    object.side = "friendly"
    object.invulnerable = "full"
    object.guns_disabled = true
    if object.is_player then
        object.engines_disabled = true
        object.missiles_disabled = not allow_launch
        object.eject_disabled = true
    end
end
hooks.after("object_damage", function(e)
    print("KAMOV_DAMAGE", steps, e.object.slot, e.kind, e.value)
end)
hooks.after("vm_command", function(e)
    if e.command == "start_ship_animation" or e.command == "start_ship_animation_reverse" then
        print("KAMOV_ANIMATION", steps, e.command)
    end
end)
return {engine_handlers = {
on_mission_start = function(mission)
    allow_launch = mission.number == 984
    for _, object in world.objects() do configure(object) end
    if world.player then world.player.missiles_disabled = not allow_launch end
end,
on_mission_end = function(outcome) print("KAMOV_MISSION_END", steps, outcome.ending) end,
on_step = function()
    steps += 1
    for _, object in world.objects() do configure(object) end
    if steps % 25 ~= 0 or not world.player then return end
    for _, object in world.objects() do
        if object.type == "russian_torpedo" then
            local p = util.to_local(world.player.position, world.player.orientation, object.position)
            print("KAMOV_TORPEDO", steps, object.slot, object.order, p.x, p.y, p.z)
        end
    end
end}}
