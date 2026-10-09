local hud = require("openreliant.hud")
local player = require("openreliant.self")
local count, last, lines = 0, "", {}
local function flat(t)
    if type(t) ~= "table" then return tostring(t) end
    local parts = {}
    for k,v in t do
        if type(v) ~= "table" and type(v) ~= "userdata" then table.insert(parts,tostring(k).."="..tostring(v)) end
    end
    table.sort(parts)
    return table.concat(parts, ", ")
end
local function show(name,value)
    table.insert(lines,name..": "..flat(value))
end
local function snapshot()
    lines = {}
    show("hud.power",hud.power)
    local radar=hud.radar
    show("radar range/zoom",if radar then {range=radar.range,zooming=radar.zooming} else nil)
    show("hud.missiles",hud.missiles)
    show("hud.open_windows",hud.open_windows)
    local state = table.concat(lines," | ")
    if state ~= last then print("HUD_FREEZE "..state);last=state end
end
hud.register_display("hud-freeze-observer",{frame=function()
    if not hud.instruments_shown then return end
    local p=vector.create
    hud.rectangle(p(280,80),p(1640,230),{colour=p(0,0,0),alpha=0.85})
    for i,line in lines do
        hud.text(p(300,88+(i-1)*24),line,{font="hud",scale=0.75})
    end
end})
return {engine_handlers={on_frame=function()
    count+=1
    if count % 20 == 0 then snapshot() end
end}}
