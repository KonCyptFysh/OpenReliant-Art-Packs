-- Only the Loki inspection missions load this diagnostic script.
local world = require("openreliant.world")
local function configure(object)
    object.side = "friendly"
    object.invulnerable = "full"
    object.guns_disabled = true
    object.engines_disabled = true
    object.missiles_disabled = true
    object.eject_disabled = true
end
return {engine_handlers = {
on_mission_start = function()
    for _, object in world.objects() do configure(object) end
end,
on_step = function()
    for _, object in world.objects() do configure(object) end
end}}
