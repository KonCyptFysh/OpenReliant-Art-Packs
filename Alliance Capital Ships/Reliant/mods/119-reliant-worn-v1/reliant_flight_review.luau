-- Mission 957 only. Finish an inspection door cycle before native landing
-- samples the centre between the doors. Never change either ship's transform.
local world = require("openreliant.world")
local hooks = require("openreliant.hooks")
local landing = false
local pending = false
local phase = "closed"
local stopped = 0
local component = nil
local animationCommands = {
    start_ship_animation = true,
    start_ship_animation_reverse = true,
    stop_ship_animation = true,
}

hooks.add("order_push", function(e)
    if not e.object.is_player or e.order ~= "land" then return end
    local carrier = e.target.object
    if not carrier or carrier.type ~= "reliant" then return end
    if not landing and phase ~= "closed" then
        -- Keep normal player controls while the existing cycle closes. Reporting
        -- acceptance preserves the native permission-to-land radio response.
        pending = true
        component = e.target.component
        e.result = "taken"
        return false
    end
end)

hooks.add("order_land_init", function(e)
    if e.object.is_player then landing = true; pending = false end
end)

hooks.add("vm_command", function(e)
    if not animationCommands[e.command] then return end
    local player = world.player
    if landing or (player and player.order == "land") then return false end
    if player and player.order == "launch" then
        e.result = "hold"
        return false
    end
    -- No new opening may begin between closure and the queued landing order.
    if pending and phase == "closed" and e.command == "start_ship_animation" then
        e.result = "hold"
        return false
    end
end)

hooks.after("vm_command", function(e)
    if e.command == "start_ship_animation" then
        phase = "opening"; stopped = 0
    elseif e.command == "start_ship_animation_reverse" then
        phase = "closing"; stopped = 0
    elseif e.command == "stop_ship_animation" then
        stopped += 1
        if stopped == 2 then
            phase = if phase == "closing" then "closed" else "open"
        end
    end
end)

return { engine_handlers = {
    on_mission_start = function()
        landing = false; pending = false; phase = "closed"; stopped = 0; component = nil
    end,
    on_update = function()
        if not pending or phase ~= "closed" then return end
        local player = world.player
        if not player then return end
        for _, carrier in world.objects() do
            if carrier.type == "reliant" then
                if player:give_order("land", carrier, component) then pending = false end
                return
            end
        end
    end,
    on_mission_end = function() landing = false; pending = false end,
    on_save = function()
        return { landing = landing, pending = pending, phase = phase,
            stopped = stopped, component = component }
    end,
    on_load = function(saved)
        saved = saved or {}
        landing = saved.landing == true
        pending = saved.pending == true
        phase = saved.phase or "closed"
        stopped = saved.stopped or 0
        component = saved.component
    end,
} }
