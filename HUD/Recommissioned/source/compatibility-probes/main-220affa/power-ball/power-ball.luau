-- Set false for the same reading with the complete native power panel visible.
local replace = true
local hud = require("openreliant.hud")
local p = vector.create
hud.register_display("power-ball-probe", {
    replaces = if replace then {"power"} else {},
    frame = function()
        if not hud.instruments_shown or not hud.power then return end
        local s = math.min(hud.width/1920,hud.height/1080)
        local state = hud.power
        hud.rectangle(p(20*s,300*s),p(580*s,420*s),{color=p(0,0,0),alpha=0.85})
        hud.text(p(35*s,315*s),if replace then "REPLACED POWER WINDOW" else "NATIVE POWER WINDOW",{font="hud",scale=s})
        hud.text(p(35*s,355*s),string.format("Weapons %d%%  Engines %d%%  Shields %d%%",state.weapons,state.engines,state.shields),{font="hud",scale=s})
        -- The values are available. There is no documented draw-native-ball call.
    end,
})
return {}
