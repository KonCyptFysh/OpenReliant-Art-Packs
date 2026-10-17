-- Pure response model. All time is simulation time; pause does not cool engines.
local M = {}
M.config = {
    hit_threshold = 0.08, hit_window = 0.35, flicker_seconds = 1.15,
    flicker_cooldown = 3.0, drive_rise = 0.45, drive_fall = 0.22,
    heat_rise = 8.0, heat_fall = 14.0, cabin_response = 0.30,
    critical_health = 0.30, disruption_wait_min = 3.0, disruption_wait_max = 14.0,
}
local function clamp(x) return math.clamp(x, 0, 1) end
local function approach(value, target, dt, tau)
    return target + (value - target) * math.exp(-dt / tau)
end
-- A saved, per-ship random stream, seeded once from the game's mission RNG.
-- Integer products stay exact in Luau doubles. Do not reseed the game's generator.
local function seed_value(seed)
    return math.max(1, math.floor(seed or math.random(1, 2147483646)) % 2147483647)
end
local function random_between(s, first, last)
    s.rng = (s.rng * 48271) % 2147483647
    return first + (last - first) * ((s.rng - 1) / 2147483646)
end
local function next_disruption(s, after)
    return after + random_between(s, M.config.disruption_wait_min, M.config.disruption_wait_max)
end
local function disruption(s, dead, dt)
    -- Also accepts states saved by the earlier PoC, which had no random outages.
    s.rng = s.rng or seed_value()
    s.disruptions = s.disruptions or 0
    s.disruption_pulses = s.disruption_pulses or {}
    if dead or s.health > M.config.critical_health then
        s.next_disruption = nil; s.disruption_pulses = {}
        return 1
    end
    if dt > 0 and not s.next_disruption then s.next_disruption = next_disruption(s, s.time - dt) end
    -- Absolute event times prevent frame-rate-dependent scheduling, including a
    -- delayed update. Every burst varies in pulse count, depth, width and spacing.
    while dt > 0 and s.next_disruption and s.time >= s.next_disruption do
        local start = s.next_disruption
        local cursor = start
        local count = math.floor(random_between(s, 1, 4))
        s.disruption_pulses = {}
        for _ = 1, count do
            local width = random_between(s, 0.035, 0.090)
            local center = cursor + 2.5 * width
            table.insert(s.disruption_pulses, {center, width, random_between(s, 0.60, 0.96)})
            cursor = center + 2.5 * width + random_between(s, 0.05, 0.23)
        end
        s.last_disruption = start; s.disruption_end = cursor
        s.disruptions += 1
        s.next_disruption = next_disruption(s, cursor)
    end
    local level = 1
    for _, pulse in s.disruption_pulses do
        local age = (s.time - pulse[1]) / pulse[2]
        if math.abs(age) < 2.5 then level -= pulse[3] * math.exp(-age * age) end
    end
    return math.max(0.04, level)
end
function M.new(armor, seed)
    local health = math.min(armor[1], armor[2], armor[3], armor[4])
    return { time = 0, previous = table.clone(armor), hits = {}, last_flicker = -100,
        flicker_left = 0, flickers = 0, drive = 0, heat = 0,
        cabin_base = clamp(health) ^ 1.25, cabin = clamp(health) ^ 1.25, health = health,
        rng = seed_value(seed), disruptions = 0, disruption_pulses = {} }
end
function M.step(s, armor, throttle, engine_off, dead, lights_on, dt)
    dt = math.max(dt, 0)
    s.time += dt
    local loss = 0
    for i = 1, 4 do
        loss = math.max(loss, s.previous[i] - armor[i])
        s.previous[i] = armor[i]
    end
    if loss > 0.000001 then table.insert(s.hits, {s.time, loss}) end
    local kept, total = {}, 0
    for _, hit in s.hits do
        if s.time - hit[1] <= M.config.hit_window then
            table.insert(kept, hit); total += hit[2]
        end
    end
    s.hits = kept
    if total + 0.000001 >= M.config.hit_threshold and s.time - s.last_flicker >= M.config.flicker_cooldown and not dead then
        s.last_flicker = s.time; s.flicker_left = M.config.flicker_seconds
        s.flickers += 1; s.hits = {}
    end
    s.health = clamp(math.min(armor[1], armor[2], armor[3], armor[4]))
    local demand = if engine_off or dead then 0 else clamp(throttle)
    s.drive = approach(s.drive, demand, dt, if demand > s.drive then M.config.drive_rise else M.config.drive_fall)
    s.heat = approach(s.heat, demand, dt, if demand > s.heat then M.config.heat_rise else M.config.heat_fall)
    s.cabin_base = approach(s.cabin_base, s.health ^ 1.25, dt, M.config.cabin_response)
    -- Large-hit interruption remains independent of the low-health fault sequence.
    local age = M.config.flicker_seconds - s.flicker_left
    local function dip(center, width, amount)
        return amount * math.exp(-((age - center) / width) ^ 2)
    end
    local flicker = 1
    if s.flicker_left > 0 then
        flicker = 1 - dip(0.08, 0.045, 0.78) - dip(0.31, 0.065, 0.55) - dip(0.70, 0.10, 0.27)
    end
    s.flicker_left = math.max(0, s.flicker_left - dt)
    local fault = disruption(s, dead, dt)
    s.cabin = s.cabin_base * math.min(math.max(0.05, flicker), fault)
    if dead then s.cabin = 0; s.drive = 0; s.heat = 0 end
    local visible = if lights_on and not dead then 1 else 0
    return {s.cabin * visible, s.drive * visible, s.heat * visible, visible}
end
return M
