-- Official upstream #864/#866/#868. Concatenated into the player script.
-- No engine changes, private INI reader, or synthetic gameplay state.
local records = require("openreliant.records")
local function nativeUnit()
    return hud.measure("H", {font = "rc_status.ttf", base_font = "hud"}).height / 17
end
local function read(field)
    local ok, value = pcall(function() return hud[field] end)
    return if ok then value else nil
end
local function relative(r, x, y, w, h, baseW, baseH)
    return {r[1] + x * r[3] / baseW, r[2] + y * r[4] / baseH, w * r[3] / baseW, h * r[4] / baseH}
end
local function fill(r, color, alpha)
    hud.rectangle(point(r[1]-r[3]/2,r[2]-r[4]/2), point(r[1]+r[3]/2,r[2]+r[4]/2),
        {color = color or orange, alpha = alpha or 1})
end
local function segments(r, share, count, vertical)
    local lit = math.floor(math.clamp(share, 0, 1) * count + 0.5)
    local pitch = (if vertical then r[4] else r[3]) / count
    for i = 0, count-1 do
        local b = if vertical then {r[1], r[2]+r[4]/2-(i+0.5)*pitch, r[3], pitch*0.68}
            else {r[1]-r[3]/2+(i+0.5)*pitch, r[2], pitch*0.68, r[4]}
        fill(b, if i < lit then orange else vector.create(0.19,0.015,0))
    end
end
local function artType(object)
    return (string.gsub(tostring(object.type), "^t_", ""))
end
local function fitted(key, r)
    local b = artBounds[key]
    local size = math.clamp(math.min(0.76/(b[3]-b[1]), 0.8/(b[4]-b[2])), 0.7, 1.2)
    return {r[1]-(b[1]+b[3]-1)*r[3]*size/2, r[2]-(b[2]+b[4]-1)*r[4]*size/2, r[3]*size, r[4]*size}
end
-- Prepare only the current panel, inside its own bounded display callback.
local extraDisplays = {}
local function instrument(name, replaces, keys, draw)
    local entry = {keys = keys}
    entry.id = hud.register_display(name, {replaces = replaces, frame = function()
        if not entry.current or not prepare(entry.current) then
            hud.set_display_enabled(entry.id, false); return
        end
        draw()
    end})
    hud.set_display_enabled(entry.id, false)
    table.insert(extraDisplays, entry)
end

-- Radio owns the shared frame while a portrait/emblem is visible. Its native
-- draw order is frame -> speaker name/portrait -> scripted comms text. Never
-- draw a second comms frame on top of that native picture.
-- Both paths use the same two HUDHARD replacements, scale and rounded positions.
local radioLayouts, radioLayout = {}, nil
local function fitRadioFrame()
    local s = math.min(hud.width / 1920, hud.height / 1080)
    local unit = nativeUnit()
    local upper = rects["comms.child_upper_grid"]
    -- HUDHARD 120/121 both have SPR origin (-1,-1). Include it when
    -- fitting the native pieces to the authored upper-grid rectangle.
    local size = upper[3] * s / 129
    local x = hud.width/2 + (upper[1]-960-upper[3]/2)*s - 11*size
    local y = anchoredY(upper[2]-upper[4]/2, rects["comms"][2], s)
    local scale, dx, dy = size/unit, (x-16*size)/unit, (y-16*size)/unit
    local key = string.format("%.4f/%.4f/%.4f",scale,dx,dy)
    local nextLayout = nil
    for _, entry in radioLayouts do
        if entry.key == key then nextLayout = entry; break end
    end
    if not nextLayout and #radioLayouts < 24 then
        nextLayout = {key=key, scale=scale, dx=dx, dy=dy}
        nextLayout.id = hud.register_display("radio_frame_"..(#radioLayouts+1), {
            layout={radio={scale=scale, offset=point(dx,dy)}}, frame=function() end,
        })
        table.insert(radioLayouts,nextLayout)
    end
    -- Registrations cannot be edited or removed. Keep the cache bounded across
    -- repeated aspect/UI-scale changes; even at the bound both frames still use
    -- the same active geometry. A new session clears the cache.
    if nextLayout and nextLayout ~= radioLayout then
        if radioLayout then hud.set_display_enabled(radioLayout.id,false) end
        radioLayout = nextLayout
        hud.set_display_enabled(radioLayout.id,true)
    end
end
-- The speaker's name at the foot of the portrait, short and long names ending at
-- the same point. Offsets are in the radio window's own pixels, so they follow
-- its layout: the face stands at (13, 19), 120 by 100, the name at (1, 2), and
-- BLUFONT's capitals fill rows 4 to 11 of its 17.
hud.register_display("radio_parts", {
    parts = {radio_speaker = {offset = point(128, 101), align = "right"}},
    frame = function() end,
})
local function sharedFrame(factor)
    local unit = nativeUnit()
    local layout = radioLayout or {scale=1,dx=0,dy=0}
    local size = unit * layout.scale
    -- windows.anchor + Placement.shift, including the original 33-pixel inset.
    local x = math.round((hud.width-33*size)*(1-factor)/2) + math.round(16*size) + math.round(layout.dx*unit)
    local y = math.round((hud.height-33*size)*(1-factor)/2) + math.round(16*size) + math.round(layout.dy*unit)
    return x,y,size*factor,unit
end
local function sharedFrameRect(upper, factor)
    local x,y,size = sharedFrame(factor)
    local w,h = (if upper then 129 else 34)*size, (if upper then 25 else 122)*size
    return {x+math.round((if upper then 12 else 0)*size)-size+w/2,
        y+math.round((if upper then 1 else 14)*size)-size+h/2,w,h}
end
local function commsFrame()
    local radio = hud.window_state("radio")
    if radio and radio.phase ~= "shut" then return end
    local x,y,size,unit = sharedFrame(windowFactor)
    hud.shape(point(x,y+math.round(14*size)),121,{scale=size/unit})
    hud.shape(point(x+math.round(12*size),y+math.round(size)),120,{scale=size/unit})
end
local function damageFrame(key, rectangle, upper)
    local r = screenRect(rectangle)
    local shared = sharedFrameRect(upper,windowFactor)
    r[2],r[3],r[4] = shared[2],shared[3],shared[4]
    picture(key,r)
end

-- The authored 43 frames cover rings=0..2, including the native range transition.
-- HUDHARD.SPR global palette block119, matching hud.Radar.Look.line.
local radarColours = {target = vector.create(203/255,85/255,4/255), speaker = vector.create(93/255,48/255,20/255),
    hostile = vector.create(182/255,8/255,0), other = vector.create(8/255,215/255,0)}
local radarShapes = {target = 0x130, speaker = 0xE6, hostile = 0xE5, other = 0xE4}
instrument("radar_art", {"radar"}, function()
    local r = read("radar")
    if not r then return nil end
    return {radarArt[math.clamp(math.round(r.rings*21)+1,1,#radarArt)]}
end, function()
    if not visible(nil) then return end
    local state = hud.radar
    if not state then return end
    local r = screenRect("wireframe_00")
    local sx, sy = r[3]/350, r[4]/221
    local cx, cy = r[1]+4*sx, r[2]-sy
    -- Elliptical dark backing stays inside the actual transparent radar ring.
    for y = -80, 80 do
        local half = 164*math.sqrt(math.max(0, 1-(y/80)^2))
        fill({cx,cy+y*sy,half*2*sx,sy}, vector.create(0,0,0), 0.62745)
    end
    local function contacts(above)
        for _, c in state.contacts do
            if (c.look == "nav_point" or c.height < 0) == above then
                local x, y = cx+c.at.x*2.52*sx, math.clamp(cy+c.at.y*2.30*sy,0,hud.height-2)
                if c.look == "nav_point" then
                    hud.line(point(x-2*sx,y),point(x+2*sx,y),{color=vector.create(1,1,1)})
                    hud.line(point(x,y-2*sy),point(x,y+2*sy),{color=vector.create(1,1,1)})
                else
                    if c.height ~= 0 then
                        local other = y-c.height*2.30*sy
                        fill({x+1.5*sx,(y+other)/2,math.max(1,3*sx),math.abs(y-other)},radarColours[c.look])
                    end
                    hud.shape(point(x+2*sx,y),radarShapes[c.look],{scale=2.6*math.min(sx,sy)/nativeUnit()})
                end
            end
        end
    end
    contacts(false)
    picture(radarArt[math.clamp(math.round(state.rings*21)+1,1,#radarArt)],r)
    contacts(true)
end)

local arcNames = {"left","right","fore","aft"}
local function statusKeys(object, target, state)
    local kind = smallShipArt[artType(object)]
    if not kind then return nil end
    local role = "player_dam"
    if target then
        local record = records.ship_types[object.type]
        role = if record and record.side == "friendly" then "ally_target" else "enemy_target"
    end
    local key = "schems/"..role.."/"..kind
    if not assets[key] then return nil end
    local keys = {key}
    -- Keep all four hit overlays ready: these flashes last only one frame.
    for i = 1, 4 do
        local hit = "schems/"..role.."/damage_layers/"..kind.."_"..i
        if not assets[hit] then return nil end
        table.insert(keys,hit)
    end
    local bases = if target then {{163,173,158,168},{143,153,138,148}} else {{173,163,158,168},{153,143,138,148}}
    for layer, arcs in {state.shields,state.armor} do
        if arcs then
            for index, name in arcNames do
                local level=math.clamp(arcs[name],0,5)
                if level>0 then table.insert(keys,"damage/ring/frame_"..(bases[layer][index]-level)..(if target then "_mirror_x" else "")) end
            end
        end
    end
    return keys
end
local function drawStatus(object, state, target)
    local keys = statusKeys(object,target,state)
    if not keys then return end
    local prefix = if target then "target_schematic" else "player_schematic"
    local schematic = fitted(keys[1],screenRect(prefix..".child_schematic"))
    picture(keys[1], schematic)
    for _, quadrant in state.hits do
        local index = table.find(arcNames,quadrant)
        if index then picture(keys[index+1],schematic) end
    end
    local ring = screenRect(prefix..".child_damage_ring")
    local bases = if target then {{163,173,158,168},{143,153,138,148}} else {{173,163,158,168},{153,143,138,148}}
    for layer, arcs in {state.shields,state.armor} do
        if arcs then
            for index, name in arcNames do
                local level = math.clamp(arcs[name],0,5)
                if level > 0 then picture("damage/ring/frame_"..(bases[layer][index]-level)..(if target then "_mirror_x" else ""),ring) end
            end
        end
    end
    if not target then
        local s = ring[3]/80
        for _, arc in {{178,-26,-36,state.reserve_fore},{183,-38,29,state.reserve_aft}} do
            if arc[4] > 0 then hud.shape(point(ring[1]+arc[2]*s,ring[2]+arc[3]*s),arc[1]-math.min(arc[4],5),{scale=s/nativeUnit()}) end
        end
    end
end
instrument("player_status", {"ship_status"}, function()
    return if read("ship_status") then statusKeys(ship,false,hud.ship_status) else nil
end, function()
    if visible(nil) and hud.ship_status then drawStatus(ship,hud.ship_status,false) end
end)
instrument("small_target", {"target_display"}, function()
    local facts, target = read("target_display"), read("target")
    if not facts or facts.form ~= "small" or not target or not target.object then return nil end
    return statusKeys(target.object,true,facts)
end, function()
    if not visible("target_display") then return end
    local facts, target = hud.target_display, hud.target
    if not facts or not target or not target.object then return end
    drawStatus(target.object,facts,true)
    local r = screenRect("target_schematic.child_readout")
    local h = 11*r[4]/52
    local pitch = (r[4]-h)/3
    for i, text in {facts.name or "",facts.pilot or "",tostring(facts.range).."k",tostring(facts.speed).." kps"} do
        label(text,{r[1],r[2]-r[4]/2+h/2+(i-1)*pitch,r[3],h},h,"rc_status.ttf","left")
    end
end)
-- Stable PartClass values map to the approved native frame identities.
-- Fuel pod 410 has no approved replacement; it retains the native panel.
local subtargetFrames = {comms_transmitter=393,engine=394,gravity_drive=395,
    turret=396,laser_turret=396,missile_turret=397,power_core=398,satellite_dish=399,
    service_door=400,shaft=401,shield_generator=402,surface_building=403,
    twin_power_cores=404,vent_hatch=405,ion_cannon=406,armored_plate=407,
    cap_gun=408,warp_projector=409}
local function subtargetKey(facts)
    local frame = subtargetFrames[facts.subtarget_class]
    return if frame then "target/subtargets/frame_"..frame else nil
end
instrument("large_target", {"big_target_display"}, function()
    local facts, target = read("target_display"), read("target")
    if not facts or facts.form ~= "large" or not target or not target.object then return nil end
    local image = largeShipArt[artType(target.object)]
    if not image then return nil end
    local keys = {"wireframes/frame_123_mirror_x","wireframes/frame_125","schems/large_target/"..image}
    if facts.subtarget then
        local key = subtargetKey(facts)
        if not key then return nil end
        table.insert(keys,key)
    end
    return keys
end, function()
    if not visible("big_target_display") then return end
    local facts, target = hud.target_display, hud.target
    if not facts or not target or not target.object then return end
    picture("wireframes/frame_123_mirror_x",screenRect("large_target_display.child_side_grid"))
    picture("wireframes/frame_125",screenRect("large_target_display.child_floor_grid"))
    picture("schems/large_target/"..largeShipArt[artType(target.object)],screenRect("large_target_display.child_schematic"))
    for _, item in {{"name",facts.name or ""},{"range",tostring(facts.range).."k"},{"speed",tostring(facts.speed).." kps"}} do
        local r=screenRect("large_target_display.child_"..item[1])
        label(item[2],r,if item[1]=="name" then r[4] else r[4]*11/15,"rc_large_target.ttf","right")
    end
    if facts.hull then segments(screenRect("large_target_display.child_target_health"),facts.hull,22,true) end
    if facts.subtarget then
        picture(subtargetKey(facts),screenRect("large_target_display.child_subtarget"))
        local r=screenRect("large_target_display.child_subtarget_label")
        label(facts.subtarget,r,r[4],"rc_large_target.ttf","right")
        if facts.subtarget_armor then segments(screenRect("large_target_display.child_subtarget_health"),facts.subtarget_armor,12,true) end
    end
end)

-- Authored fixed positions, with the native visible flash phase and device charge.
local lightArt = {match_speed={"speed_match","Speed_Match"},blind_fire={"blind_fire","Blind_Fire"},
    smart_targeting={"smart_targeting","Smart_Targeting"},enemy_lock={"enemy_locked","Enemy_Locked"},
    missile_incoming={"missile_inbound","Missile_Inbound"},ecm={"ecm","ECM"},
    cloak={"cloaking","Cloaking"},spectral_shields={"spectral_shield","Spectral_Shield"},
    reverse_thrust={"reverse_thrust","Reverse_Thrust"}}
instrument("status_lights", {"lights"}, function()
    local keys = {}
    for _, item in lightArt do table.insert(keys,"indicators/"..item[2]) end
    return keys
end,function()
    if not visible(nil) then return end
    for _, kind in hud.lights_lit do
        local item=lightArt[kind]
        if item then picture("indicators/"..item[2],screenRect(item[1])) end
    end
    local charges=hud.charges
    if charges then for _, kind in hud.lights do
        local charge=charges[kind]
        if charge~=nil and lightArt[kind] then
            local r=screenRect(lightArt[kind][1])
            segments({r[1],r[2]+r[4]/2+r[3]/16,r[3]*0.8,r[3]/16},charge,20,false)
        end
    end end
end)

-- Lossless composed fills retain the native one-row steps. Only the current
-- left/right image is requested, keeping well below upstream's 128-file cache.
local function markerOffset(share)
    local angle=math.rad(310-share*100)
    return math.round(math.sin(angle)*124),math.round(math.cos(angle)*94)
end
local function gaugeFill(g,side)
    local _, y=markerOffset(g.speed_share)
    local split=if side==1 then math.clamp(y+80,0,138) else math.clamp(math.round((1-g.charge)*138),0,138)
    return string.format("gauge_fill/%s/%03d",if side==1 then "left" else "right",split)
end
instrument("flight_gauges", {"gauges"}, function()
    local g=read("gauges")
    return if g then {"frame_127","frame_127_mirrored_right","flight_gauge_pointer",gaugeFill(g,1),gaugeFill(g,2)} else nil
end,function()
    if not visible(nil) then return end
    local g=hud.gauges
    if not g then return end
    for side, name in {"throttle_gauge","energy_gauge"} do
        local r=screenRect(name)
        local s=r[4]/146
        picture(if side==1 then "frame_127" else "frame_127_mirrored_right",{r[1],r[2],68*s,141*s})
        local left=r[1]-34*s+(if side==1 then -10 else 14)*s
        local top=r[2]-70.5*s
        picture(gaugeFill(g,side),{left+32.5*s,top+69*s,65*s,138*s})
    end
    local r=screenRect("throttle_gauge")
    local s=r[4]/146
    local function marker(value,share,alpha)
        local x,y=markerOffset(share)
        x,y=r[1]+(x+67)*s,r[2]+(y+11)*s
        picture("flight_gauge_pointer",{x-3.5*s,y+0.5*s,11*s,7*s},alpha)
        -- Native markers fade by brightness; the requested-speed number follows it.
        local words=tostring(value)
        local measured=hud.measure(words,{font="rc_gauges.ttf",base_font="hud"})
        local scale=math.min(10*s/(measured.height*8/17),48*s/math.max(1,measured.width))
        hud.text(point(x-9*s,y-measured.height*scale*8/17),words,{font="rc_gauges.ttf",base_font="hud",align="right",scale=scale,color=orange,alpha=alpha})
    end
    if g.throttle_brightness then marker(g.asked,g.throttle_share,g.throttle_brightness) end
    marker(g.speed,g.speed_share,1)
end)

instrument("damage_panel", {"damage"},function()
    return if read("damage") then {"wireframes/frame_120_mirror_x","wireframes/frame_121_mirror_x","indicators/Guns","indicators/Engine","indicators/Shields"} else nil
end,function()
    if not visible("damage") then return end
    local state=hud.damage
    if not state then return end
    damageFrame("wireframes/frame_120_mirror_x","systems_damage.child_upper_grid",true)
    damageFrame("wireframes/frame_121_mirror_x","systems_damage.child_side_grid",false)
    local title=screenRect("systems_damage.child_title")
    label("DAMAGE",title,18*title[4]/22,"rc_damage.ttf","right")
    for _, item in {{"weapons","Guns","WEAPONS"},{"engines","Engine","ENGINES"},{"shields","Shields","SHIELDS"}} do
        local r=screenRect("systems_damage.child_"..item[1])
        picture("indicators/"..item[2],relative(r,-48,-5,32,32,142,38))
        label(item[3],relative(r,15,-10,90,14,142,38),9*r[4]/38,"rc_damage.ttf","left")
        for _, line in {{16,1,90,1},{-29,7,1,12},{-45,12,32,1}} do fill(relative(r,line[1],line[2],line[3],line[4],142,38)) end
        segments(relative(r,13,7,78,6,142,38),state[item[1]],20,false)
    end
end)
instrument("power_panel", {"power"},function()
    return if read("power") then {"wireframes/power_distribution_grid","indicators/Guns","indicators/Engine","indicators/Shields"} else nil
end,function()
    if not visible("power") then return end
    local state=hud.power
    if not state then return end
    picture("wireframes/power_distribution_grid",screenRect("power_distribution.child_grid"))
    local title=screenRect("power_distribution.child_title")
    label("POWER DISTRIBUTION",title,18*title[4]/22,"rc_power.ttf")
    for _, item in {{"weapons","weapons","Guns","WEAPONS"},{"engines","engines","Engine","ENGINES"},{"shields","shields","Shields","SHIELDS"}} do
        local r=screenRect("power_distribution.child_"..item[1])
        picture("indicators/"..item[3],relative(r,0,-27,64,64,68,118))
        label(item[4],relative(r,0,16,68,14,68,118),14*r[3]/68,"rc_power.ttf")
        label(tostring(state[item[2]]).."%",relative(r,0,39,68,18,68,118),18*r[3]/68,"rc_power_values.ttf")
    end
    -- The native ball, turning with the power setting, in its authored rectangle.
    local r=screenRect("power_distribution.child_orb")
    hud.power_ball(point(r[1]-r[3]/2,r[2]-r[4]/2),point(r[3],r[4]))
end)

instrument("wing_panel", {"wing_status"},function()
    local state=read("wingmen")
    if not state then return nil end
    local keys={"wireframes/wing_status_grid_mirror_x"}
    for _, entry in state do
        local kind=smallShipArt[artType(entry.object)]
        if not kind or not assets["squadron/"..kind] then return nil end
        table.insert(keys,"squadron/"..kind)
    end
    return keys
end,function()
    if not visible("wing_status") then return end
    picture("wireframes/wing_status_grid_mirror_x",screenRect("wing_status.child_grid"))
    local title=screenRect("wing_status.child_name")
    label("THE 45TH",title,20*title[4]/16,"rc_wing.ttf")
    for _, entry in hud.wingmen do
        local slot=screenRect("wing_status.child_ship_"..entry.number)
        local r={slot[1],slot[2],slot[3]*76/96,slot[4]*76/92}
        picture("squadron/"..smallShipArt[artType(entry.object)],r)
        label(entry.number,{r[1],r[2]-r[4]/2-r[3]*30/76,r[3],r[3]*24/76},r[3]*24/76,"rc_wing.ttf")
        segments({r[1]+r[3]*0.6,r[2],r[3]/16,r[4]*0.75},entry.armor,10,true)
    end
end)

-- Wrap at a readable cap height with separate line spacing. Reflow if a
-- longer objective needs smaller text, keeping every line inside its rectangle.
local function wrapped(words,r,height,font)
    local m=hud.measure("H",{font=font,base_font="hud"})
    local measured={}
    local function width(text)
        if not measured[text] then measured[text]=hud.measure(text,{font=font,base_font="hud"}).width end
        return measured[text]
    end
    local function layout(h)
        local lines={}
        local scale=h/(m.height*8/17)
        for paragraph in string.gmatch(words.."\n","(.-)\n") do
            local line=""
            for word in string.gmatch(paragraph,"%S+") do
                local candidate=if line=="" then word else line.." "..word
                if line~="" and width(candidate)*scale>r[3] then
                    table.insert(lines,line);line=word
                else line=candidate end
            end
            table.insert(lines,line)
        end
        local across=0
        for _,line in lines do across=math.max(across,width(line)*scale) end
        return lines,across<=r[3] and h+(#lines-1)*h*1.4<=r[4]
    end
    local h=height
    local lines,fits=layout(h)
    if not fits then
        -- Wrapping changes at word boundaries. Find the largest size that fits,
        -- rather than shrinking once from an overlong first set of line breaks.
        local low,high=0,height
        for attempt=1,10 do
            local trial=(low+high)/2
            local candidate,ok=layout(trial)
            if ok then low=trial;lines=candidate else high=trial end
        end
        h=low
    end
    local scale=h/(m.height*8/17)
    for i,text in lines do
        hud.text(point(r[1]-r[3]/2,r[2]-r[4]/2+(i-1)*h*1.4-m.height*scale*4/17),text,
            {font=font,base_font="hud",scale=scale,color=orange})
    end
end
instrument("objectives_panel", {"objectives"},function()
    return if read("objectives") then {"wireframes/mission_objectives_grid_mirror_x"} else nil
end,function()
    if not visible("objectives") then return end
    local state=hud.objectives
    if not state then return end
    picture("wireframes/mission_objectives_grid_mirror_x",screenRect("mission_objectives.child_grid"))
    local title=screenRect("mission_objectives.child_title")
    label("MISSION OBJECTIVES",title,24*title[4]/26,"rc_objectives.ttf","left")
    local selected=nil
    for _,entry in state.list do if entry.number==state.showing then selected=entry; break end end
    local status=screenRect("mission_objectives.child_status")
    label(if selected then (if selected.current then "CURRENT OBJECTIVE" else "OBJECTIVE") else "NO CURRENT OBJECTIVES",status,14*status[4]/18,"rc_objectives.ttf","left")
    if selected then
        local r=screenRect("mission_objectives.child_body")
        wrapped(selected.name or "No objectives available.",r,20*r[4]/136,"rc_objectives.ttf")
    end
end)
instrument("comms_menu", {"comms"},function()
    return if read("comms") then {"wireframes/frame_120","wireframes/frame_121"} else nil
end,function()
    if not visible("comms") then return end
    commsFrame()
    local title=screenRect("comms.child_menu_text")
    label("COMMS",title,13*title[4]/18,"rc_comms.ttf","left")
    local r,content=screenRect("comms.child_command_text"),screenRect("comms.child_content")
    local h=r[3]*12/222
    r[1]=title[1]-title[3]/2+r[3]/2+r[1]-content[1]+content[3]/225
    local start=title[2]+title[4]/2+h+r[2]-content[2]+content[3]*2/225
    -- Match the native menu's separate number and label columns. Drawing a
    -- whole "1. Label" uses native proportional spacing. Separate columns keep
    -- the period clear and every option label aligned, including after 10.
    local measured=hud.measure("H",{font="rc_comms.ttf",base_font="hud"})
    local numberWidth,wordsWidth=1,1
    for i,text in hud.comms do
        numberWidth=math.max(numberWidth,hud.measure(tostring(i),{font="rc_comms.ttf",base_font="hud"}).width)
        wordsWidth=math.max(wordsWidth,hud.measure(text,{font="rc_comms.ttf",base_font="hud"}).width)
    end
    local gap=measured.height*2/17
    local dotWidth=hud.measure(".",{font="rc_comms.ttf",base_font="hud"}).width
    local prefixWidth=numberWidth+dotWidth+3*gap
    local scale=math.min(h*0.75/(measured.height*8/17),r[3]/(prefixWidth+wordsWidth))
    local left=r[1]-r[3]/2
    -- Align visible ink, not the legacy glyph advance boxes. In particular,
    -- the native '1' advances only three pixels and otherwise appears indented.
    local style={font="rc_comms.ttf",base_font="hud",scale=scale,color=orange}
    local function column(text, x, y)
        local ink=hud.measure(text,style).ink
        hud.text(point(x-(if ink then ink.left else 0),y),text,style)
    end
    for i,text in hud.comms do
        local top=start+(i-1)*h-measured.height*scale*8/17
        column(tostring(i),left,top)
        column(".",left+(numberWidth+gap)*scale,top)
        column(text,left+prefixWidth*scale,top)
    end
end)
local function updateInstruments()
    fitRadioFrame()
    for _, entry in extraDisplays do
        entry.current=entry.keys()
        hud.set_display_enabled(entry.id,queue(entry.current))
    end
end
