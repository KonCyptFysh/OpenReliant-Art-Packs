-- Only mission957 uses this controller. Native launch and landing own the camera,
-- flight, carrier relocation and cutaway; never pin either ship's transform.
local world = require("openreliant.world")
local hooks = require("openreliant.hooks")
local landing = false
local animationCommands = {
    start_ship_animation = true,
    start_ship_animation_reverse = true,
    stop_ship_animation = true,
}

hooks.add("order_land_init", function(e)
    if e.object.is_player then landing = true end
end)

hooks.add("vm_command", function(e)
    if not animationCommands[e.command] then return end
    local player = world.player
    if landing or (player and player.order == "land") then return false end
    -- Also guard against a premature launch event. Hold the first door command
    -- until control is released; do not modify native animation routines.
    if player and player.order == "launch" then
        e.result = "hold"
        return false
    end
end)

return { engine_handlers = {
    on_mission_start = function() landing = false end,
    on_mission_end = function() landing = false end,
    on_save = function() return { landing = landing } end,
    on_load = function(saved) landing = saved and saved.landing == true end,
} }
