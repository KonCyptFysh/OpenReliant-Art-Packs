-- Recommissioned HUD using official upstream player-script APIs (#833, #864, #866, #868).
-- rects, assets and gunArtTop are generated from preserved sources by tools/build_script.py.
local hud = require("openreliant.hud")
local ship = require("openreliant.self")

-- The films and instrument parts in this pack require official 0.9.0.
local supported, parts, powerBall = pcall(function() return hud.part_bounds, hud.power_ball end)
if not supported or type(parts) ~= "function" or type(powerBall) ~= "function" then
    print("Recommissioned HUD 1.10 requires OpenReliant 0.9.0. Restore the previous complete HUD on older engines.")
    return {}
end

local orange = vector.create(1, 0.42, 0)
local function point(x, y) return vector.create(x, y, 0) end
local windowFactor = 1
-- Where an authored height stands on the screen, for a panel authored at panelY.
-- As the game anchors its own instruments, a panel in the top third keeps its
-- distance from the top edge, one in the bottom third from the foot, and the
-- rest from the middle. On a 16:9 screen the three agree; on a taller one, such
-- as 16:10, the top and bottom panels stay at their edges.
local function anchoredY(y, panelY, s)
    if panelY < 360 then return y * s end
    if panelY > 720 then return hud.height - (1080 - y) * s end
    return hud.height / 2 + (y - 540) * s
end
local function screenRect(name)
    local r = rects[name]
    local panel = rects[string.match(name, "^[^.]+")]
    local s = math.min(hud.width / 1920, hud.height / 1080)
    local y = anchoredY(r[2], panel[2], s)
    -- Native windows grow away from the screen center as they close.
    return {hud.width / 2 + (r[1] - 960) * s * windowFactor,
        hud.height / 2 + (y - hud.height / 2) * windowFactor,
        r[3] * s * windowFactor, r[4] * s * windowFactor}
end

local function picture(key, r, alpha)
    local path = assets[key]
    assert(path, "Missing HUD artwork: " .. key)
    hud.picture(point(r[1] - r[3] / 2, r[2] - r[4] / 2), path, point(r[3], r[4]), {alpha = alpha or 1})
end

local function label(words, r, height, font, align)
    words = tostring(words)
    font = font or "BLUFONT.ttf"
    -- BLUFONT has 17 rows, capitals in rows 4..11. Size by visible ink.
    -- The engine's outline replacement uses the same baseline and cap height.
    -- Separate script fonts from native text and separate counters from labels.
    -- Upstream 0.8 keeps current-frame font atlases alive (#902). Retain the
    -- panel aliases so the established text metrics stay unchanged.
    local measured = hud.measure(words, {font = font, base_font = "hud"})
    local scale = math.min(height / (8 / 17 * measured.height), r[3] / math.max(1, measured.width))
    hud.text(point(if align == "left" then r[1] - r[3] / 2 elseif align == "right" then r[1] + r[3] / 2 else r[1],
        r[2] - measured.height * scale * 8 / 17), words,
        {font = font, base_font = "hud", align = align or "center", scale = scale, color = orange})
end

local function visible(window)
    local state = if window then hud.window_state(window) else nil
    windowFactor = if state then 2 - state.opened else 1
    return hud.instruments_shown and ship ~= nil and ship:is_valid()
        and (window == nil or (state ~= nil and state.phase ~= "shut"))
end

-- The renderer loads PNGs synchronously and limits each script callback to
-- 100 ms. Queue the current frame's unique images, then load one per callback
-- before any panel draws. All callbacks finish before that frame is presented:
-- no native flash, no partial panel, and no multiframe warm-up delay.
-- A fixed pool also keeps the work bounded below the engine's 128-file cache.
local failed, queued, pending, loaded = {}, {}, {}, {}
local function queue(keys)
    if not keys then return false end
    for _, key in keys do
        local path = assets[key]
        if not path or failed[path] then return false end
        if not queued[path] then
            if #pending == 112 then return false end
            queued[path] = true
            table.insert(pending, path)
        end
    end
    return true
end
local function prepare(keys)
    for _, key in keys do
        if not loaded[assets[key]] then return false end
    end
    return true
end
for slot = 1, 112 do
    hud.register_display("image_load_" .. slot, {frame = function()
        local path = pending[slot]
        if not path then return end
        local ok, message = pcall(hud.picture, point(-2, -2), path, point(1, 1))
        if ok then loaded[path] = true else
            failed[path] = true
            print("Recommissioned HUD: keeping native instrument; " .. tostring(message))
        end
    end})
end

local readouts
readouts = hud.register_display("readouts", {
    replaces = {"fuel", "kills", "countermeasures"},
    frame = function()
        if not visible(nil) then return end
        if not prepare({"indicators/Afterburner", "indicators/KillCount", "indicators/Countermeasures"}) then
            hud.set_display_enabled(readouts, false); return
        end
        local okFuel, fuel = pcall(function() return hud.fuel end)
        local okCM, countermeasures = pcall(function() return hud.countermeasures end)
        local values = {
            {"afterburner", "Afterburner", if okFuel and fuel ~= nil then fuel else math.max(0, math.floor(ship.afterburner_fuel))},
            {"kill_count", "KillCount", hud.kills or 0},
            {"countermeasures", "Countermeasures", if okCM and countermeasures ~= nil then countermeasures else ship.countermeasures},
        }
        for _, entry in values do
            if entry[1] == "countermeasures" and not hud.countermeasures_lit then continue end
            local r = screenRect(entry[1])
            picture("indicators/" .. entry[2], r)
            local height = r[3] / 4
            label(entry[3], {r[1], r[2] + r[4] / 2 + height / 3 + height / 2, r[3], height}, height, "rc_readouts.ttf")
        end
    end,
})
hud.set_display_enabled(readouts, false)

-- Unknown/mod-added ships retain their complete native gunnery panel.
local gunShips = {coyote = 1, crusader = 1, mirage = 2, naginata = 1,
    patriot = 2, phoenix = 3, predator = 1, shroud = 1, tempest = 2,
    grendal = 2, wolverine = 3, reaper = 2}
local gunNames = {laser_cannon = "LASER CANNON", pulse_cannon = "PULSE CANNON",
    messon_blaster = "MESON BLASTER", proton_cannon = "PROTON CANNON",
    gattling_lasers = "GATTLING LASERS", tachyon_cannon = "TACHYON CANNON",
    neutron_particle_gun = "NEUTRON PARTICLE GUN", collapser_guns = "COLLAPSER GUNS",
    gattling_plasma_cannon = "GATTLING PLASMA CANNON", vulcan_battery = "VULCAN BATTERY",
    nova_cannon = "NOVA CANNON"}
local function shipName()
    -- Later-mission t_* variants share their corresponding fighter's art.
    local kind = string.gsub(tostring(ship.type), "^t_", "")
    return if kind == "grendel" then "grendal" else kind
end
local function gunKey(guns, kind, group)
    local on = guns.all or guns.group == group - 1
    if kind == "phoenix" and group == 3 and guns.all then on = false end
    return "gunnery/ship_wireframes/" .. kind .. "/gun_group_" .. group .. (if on then "_on" else "_off")
end
local function gunKeys(guns, kind)
    if not guns or gunShips[kind] ~= guns.groups then return nil end
    local keys = {"wireframes/gunnery_floor", "wireframes/frame_123", "gunnery/ship_wireframes/" .. kind .. "/wireframe"}
    for group = 1, gunShips[kind] do table.insert(keys, gunKey(guns, kind, group)) end
    return keys
end
local gunsDisplay
gunsDisplay = hud.register_display("gunnery", {
    replaces = {"gunnery"},
    frame = function()
        if not visible("gunnery") then return end
        local guns = hud.guns
        local keys = gunKeys(guns, shipName())
        if not keys or not prepare(keys) then
            hud.set_display_enabled(gunsDisplay, false); return
        end
        -- Match the legacy renderer's vertical mirror using a lossless export.
        picture("wireframes/gunnery_floor", screenRect("gunnery_display.child_floor"))
        picture("wireframes/frame_123", screenRect("gunnery_display.child_grid"))
        local r = screenRect("gunnery_display.child_ship")
        local kind = shipName()
        local prefix = "gunnery/ship_wireframes/" .. kind .. "/"
        local name = screenRect("gunnery_display.child_name")
        -- Tall silhouettes (notably Mirage and Tempest) need a little more
        -- clearance under the heading. Move their gun layers with the ship.
        local inkTop = r[2] - r[4] / 2 + gunArtTop[prefix .. "wireframe"] * r[4]
        r[2] += math.max(0, name[2] + name[4] / 2 + name[4] / 2 - inkTop)
        picture(prefix .. "wireframe", r)
        for group = 1, gunShips[kind] do
            picture(gunKey(guns, kind, group), r)
        end
        label(if guns.all then "FULL GUNS" else gunNames[guns.gun] or "GUNS",
            name, name[4], nil, "left")
        -- Legacy gunnery.zig uses shapes 0xF0/0xF1 at the left edge,
        -- eight native pixels below the side grid's top. Reuse the actual
        -- shaped artwork, at the grid's 2x native scale, rather than flat bars.
        -- FULL GUNS and the charging Nova group have no pairing indicator.
        if guns.paired then
            local mode = screenRect("gunnery_display.child_mode")
            -- shape scales are in native HUD units, unlike picture pixel sizes.
            local nativeUnit = hud.measure("H", {font = "BLUFONT.ttf", base_font = "hud"}).height / 17
            hud.shape(point(mode[1] - mode[3] / 2, mode[2] - mode[4] / 2),
                if guns.synchronized then 0xF0 else 0xF1, {scale = mode[3] / 28 / nativeUnit})
        end
        if guns.rounds ~= nil then
            local ammo = screenRect("gunnery_display.child_ammo")
            local unit = hud.measure("H", {font = "BLUFONT.ttf", base_font = "hud"}).height / 17
            local s = ammo[4] / 8
            hud.shape(point(ammo[1] - ammo[3]/2, ammo[2] - ammo[4]/2 + 2*s), 0xEE, {scale=s/unit})
            label(guns.rounds, {ammo[1]+17*s/2,ammo[2],ammo[3]-17*s,ammo[4]},ammo[4],nil,"left")
        end
    end,
})
hud.set_display_enabled(gunsDisplay, false)

local missileNames = {screamer = "screamer", raptor = "raptor", havoc = "havoc",
    jack_hammer = "jackhammer", bandit = "bandit", vagabond = "vagabond",
    solomon = "solomon", imp = "torpedo", hawk = "hawk"}
local function missileKeys(missiles)
    local keys = {"wireframes/frame_124", "wireframes/frame_126"}
    if not missiles.armed then return keys end
    for _, entry in missiles.ring do
        if not missileNames[entry.type] then return nil end
        -- Native Ring.turn is immediate; the API supplies its ten-place pose.
        local place = entry.place
        table.insert(keys, string.format("missiles/%s/slot_%02d_%s", missileNames[entry.type],
            place, if place == 0 then "gold" else "red"))
    end
    return keys
end
local missilesDisplay
missilesDisplay = hud.register_display("missiles", {
    replaces = {"missiles"},
    frame = function()
        if not visible("missiles") then return end
        local missiles = hud.missiles
        local keys = if missiles then missileKeys(missiles) else nil
        if not keys or not prepare(keys) then
            hud.set_display_enabled(missilesDisplay, false); return
        end
        picture("wireframes/frame_124", screenRect("missile_display.child_upper_grid"))
        picture("wireframes/frame_126", screenRect("missile_display.child_main_grid"))
        if not missiles.armed then return end
        for index = 3, #keys do
            picture(keys[index], screenRect("missile_display.child_carousel"))
        end
        local ammo, name = screenRect("missile_display.child_ammo"), screenRect("missile_display.child_name")
        label(missiles.left, ammo, ammo[4])
        label(if missiles.armed == "imp" then "IMP" else string.upper(missileNames[missiles.armed]), name, name[4])
    end,
})
hud.set_display_enabled(missilesDisplay, false)

-- ADDITIONAL_INSTRUMENTS

hud.register_display("mission_clock", {
    replaces = {"clock"},
    frame = function()
        if not visible(nil) or not hud.clock then return end
        local r = screenRect("mission_clock")
        label(string.format("%d:%02d",hud.clock.minutes,hud.clock.seconds),r,r[4],"rc_readouts.ttf")
    end,
})

print("Recommissioned HUD: upstream mod API active; expanded instruments enabled where supported.")
return {engine_handlers = {on_frame = function()
    if not hud.shown or ship == nil or not ship:is_valid() then return end
    queued, pending, loaded = {}, {}, {}
    hud.set_display_enabled(readouts, queue({"indicators/Afterburner", "indicators/KillCount", "indicators/Countermeasures"}))
    hud.set_display_enabled(gunsDisplay, queue(gunKeys(hud.guns, shipName())))
    local missiles = hud.missiles
    hud.set_display_enabled(missilesDisplay, missiles ~= nil and queue(missileKeys(missiles)))
    updateInstruments()
end}}
