//! Optional HUD renderer for the editor's 1920 by 1080 layout. It reads live
//! instruments through the native HUD and resolves artwork through enabled mods.
const std = @import("std");
const hud = @import("../hud.zig");
const bigfile = @import("../bigfile.zig");
const srtexture = @import("../../surrender/surrenderlib/srtexture.zig");
const create = @import("../create.zig");
const gameobj = @import("../gameobj.zig");
const input_power = @import("../../input/power.zig");
const geometry = @import("recommissioned_layout.zig");
const defs = @import("recommissioned_layout_defs.zig");
const Rect = geometry.Rect;
const Root = geometry.Root;
const Child = geometry.Child;
const log = std.log.scoped(.hud_layout);

pub const Renderer = struct {
    layout: geometry.Layout,
    files: srtexture.Files,
    images: std.StringHashMapUnmanaged(?*srtexture.Image) = .empty,

    bounds: std.AutoHashMapUnmanaged(*srtexture.Image, [4]i32) = .empty,

    pub fn load(gpa: std.mem.Allocator, mods: *const bigfile.Mods) !?*Renderer {
        const layout = geometry.load(gpa, mods) catch |err| {
            log.err("hud_layout.ini rejected: {s}; using the native HUD", .{@errorName(err)});
            return null;
        } orelse return null;
        const result = try gpa.create(Renderer);
        result.* = .{ .layout = layout, .files = mods.pictures() };
        log.info("loaded hud_layout.ini: {d} roots, {d} child placements on 1920x1080", .{ layout.roots.len, layout.children.len });
        return result;
    }

    fn texture(self: *Renderer, pen: hud.Pen, key: []const u8) std.mem.Allocator.Error!?*srtexture.Image {
        var buffer: [256]u8 = undefined;
        if (key.len + 8 > buffer.len) return null;
        @memcpy(buffer[0..3], "rc_");
        for (key, 3..) |ch, i| buffer[i] = if (std.ascii.isAlphanumeric(ch)) std.ascii.toLower(ch) else '_';
        @memcpy(buffer[3 + key.len ..][0..4], ".png");
        const name = buffer[0 .. 7 + key.len];
        if (self.images.get(name)) |cached| return cached;
        const owned = try pen.gpa.dupe(u8, name);
        const entry = try self.images.getOrPut(pen.gpa, owned);
        entry.value_ptr.* = null;
        if (try self.files.picture(pen.gpa, name)) |read| {
            clearTransparentMatte(read.rgba);
            const img = try pen.gpa.create(srtexture.Image);
            img.* = try srtexture.mipmapped(pen.gpa, read);
            entry.value_ptr.* = img;
            return img;
        }
        log.warn("no custom picture {s}; using a native picture where available", .{name});
        return null;
    }

    pub fn picture(self: *Renderer, pen: hud.Pen, key: []const u8, rect: Rect, how: hud.Draw) hud.Error!bool {
        const img = try self.texture(pen, key) orelse return false;
        image(pen, img, rect, how);
        return true;
    }

    fn image(pen: hud.Pen, img: *srtexture.Image, rect: Rect, how: hud.Draw) void {
        const r = rect.onScreen(pen.screen);
        hud.drawImageAs(pen.device, img, .{ @intCast(rect.w), @intCast(rect.h) }, .{ r[0] - @as(f32, @floatFromInt(@divTrunc(rect.w, 2))) * screenScale(pen), r[1] - @as(f32, @floatFromInt(@divTrunc(rect.h, 2))) * screenScale(pen) }, pen.colour, screenScale(pen), how);
    }

    fn native(pen: hud.Pen, index: usize, rect: Rect, how: hud.Draw) hud.Error!void {
        const img = try pen.art.image(pen.gpa, index) orelse return;
        image(pen, img, rect, how);
    }

    /// Fit the visible silhouette inside its ring using the editor's 76%/80%
    /// margins. Soft black shadows do not count toward the silhouette bounds.
    fn fitted(self: *Renderer, gpa: std.mem.Allocator, img: *srtexture.Image, r: Rect) !Rect {
        const entry = try self.bounds.getOrPut(gpa, img);
        if (!entry.found_existing) entry.value_ptr.* = silhouetteBounds(img.levels[0]);
        const b = entry.value_ptr.*;
        const w: i32 = @intCast(img.width());
        const h: i32 = @intCast(img.height());
        const x0 = @divTrunc(b[0] * r.w, w);
        const y0 = @divTrunc(b[1] * r.h, h);
        const x1 = @divTrunc(b[2] * r.w, w);
        const y1 = @divTrunc(b[3] * r.h, h);
        const size = std.math.clamp(@min(@divTrunc(@divTrunc(r.w * 76, 100) * 1000, @max(1, x1 - x0)), @divTrunc(@divTrunc(r.h * 80, 100) * 1000, @max(1, y1 - y0))), 700, 1200);
        const nw = @max(1, @divTrunc(r.w * size, 1000));
        const nh = @max(1, @divTrunc(r.h * size, 1000));
        return .{ .x = r.x - @divTrunc((x0 + x1 - r.w) * nw, r.w * 2), .y = r.y - @divTrunc((y0 + y1 - r.h) * nh, r.h * 2), .w = nw, .h = nh };
    }

    fn childImage(self: *Renderer, pen: hud.Pen, child: Child, key: []const u8, mirror: hud.Mirror) hud.Error!void {
        _ = try self.picture(pen, key, self.layout.child(child), .{ .mirror = mirror });
    }

    fn text(pen: hud.Pen, words: []const u8, rect: Rect, height: f32, alignment: hud.Align) std.mem.Allocator.Error!void {
        const r = rect.onScreen(pen.screen);
        const wanted = height * screenScale(pen);
        const width: f32 = @floatFromInt(pen.font.textWidth(words));
        const scale = @min(wanted / @as(f32, @floatFromInt(pen.font.font.header.height)), if (width > 0) r[2] / width else 1);
        const x = r[0] + switch (alignment) {
            .left => -r[2] / 2,
            .right => r[2] / 2,
            .centre => @as(f32, 0),
            else => -r[2] / 2,
        };
        _ = try hud.drawText(pen.font, pen.gpa, pen.device, .{ hud.round(x), hud.round(r[1] - wanted / 2) }, words, pen.colour, alignment, scale);
    }

    /// Size the requested readouts by visible capitals, excluding the bitmap
    /// font's empty rows. The outline font uses the same cap height and baseline.
    fn inkText(pen: hud.Pen, words: []const u8, rect: Rect, height: f32, alignment: hud.Align) std.mem.Allocator.Error!void {
        const glyph = pen.font.font.glyph('H') orelse return text(pen, words, rect, height, alignment);
        const span = inkRows(glyph.pixels, glyph.width, glyph.height);
        const r = rect.onScreen(pen.screen);
        const width: f32 = @floatFromInt(pen.font.textWidth(words));
        const scale = @min(height * screenScale(pen) / @as(f32, @floatFromInt(span[1] - span[0])), if (width > 0) r[2] / width else 1);
        const x = r[0] + switch (alignment) {
            .right => r[2] / 2,
            .centre => @as(f32, 0),
            else => -r[2] / 2,
        };
        const top = r[1] - @as(f32, @floatFromInt(span[0] + span[1])) * scale / 2;
        _ = try hud.drawText(pen.font, pen.gpa, pen.device, .{ hud.round(x), hud.round(top) }, words, pen.colour, alignment, scale);
    }

    fn childText(self: *Renderer, pen: hud.Pen, child: Child, words: []const u8, height: f32, alignment: hud.Align) std.mem.Allocator.Error!void {
        const r = self.layout.child(child);
        const base = defs.children[@intFromEnum(child)].size;
        try text(pen, words, r, height * @as(f32, @floatFromInt(r.h)) / @as(f32, @floatFromInt(base[1])), alignment);
    }

    fn string(self: *Renderer, pen: hud.Pen, child: Child, id: u32, height: f32, alignment: hud.Align) std.mem.Allocator.Error!void {
        try self.childText(pen, child, pen.strings.string(id) orelse "", height, alignment);
    }

    fn number(self: *Renderer, pen: hud.Pen, child: Child, comptime format: []const u8, args: anytype, height: f32, alignment: hud.Align) std.mem.Allocator.Error!void {
        var buffer: [64]u8 = undefined;
        try self.childText(pen, child, std.fmt.bufPrint(&buffer, format, args) catch return, height, alignment);
    }

    pub fn reticle(self: *Renderer, pen: hud.Pen, index: usize, at: [2]i32, how: hud.Draw) hud.Error!bool {
        if (index != 215 and index != 216) return false;
        const img = try self.texture(pen, if (index == 215) "Aim_Red" else "Aim_Yellow") orelse return false;
        const scale = screenScale(pen);
        hud.drawImageAs(pen.device, img, .{ 44, 43 }, .{ @as(f32, @floatFromInt(at[0])) - 22 * scale, @as(f32, @floatFromInt(at[1])) - 21 * scale }, pen.colour, scale, how);
        return true;
    }

    pub fn indicator(self: *Renderer, pen: hud.Pen, shape: usize) hud.Error!bool {
        const found: struct { Root, []const u8 } = switch (shape) {
            194 => .{ .eject, "Eject" },
            201 => .{ .warp_jump, "Warp_Jump" },
            206 => .{ .jump, "Jump" },
            204 => .{ .speed_match, "Speed_Match" },
            203 => .{ .blind_fire, "Blind_Fire" },
            197 => .{ .smart_targeting, "Smart_Targeting" },
            195 => .{ .enemy_locked, "Enemy_Locked" },
            196 => .{ .missile_inbound, "Missile_Inbound" },
            198 => .{ .ecm, "ECM" },
            199 => .{ .cloaking, "Cloaking" },
            202 => .{ .spectral_shield, "Spectral_Shield" },
            200 => .{ .reverse_thrust, "Reverse_Thrust" },
            else => return false,
        };
        var name: [64]u8 = undefined;
        _ = try self.picture(pen, std.fmt.bufPrint(&name, "indicators/{s}", .{found[1]}) catch unreachable, self.layout.root(found[0]), .{});
        return true;
    }

    pub fn readout(self: *Renderer, pen: hud.Pen, which: hud.Readout, value: i32) hud.Error!void {
        const root: Root, const key: []const u8 = switch (which) {
            .fuel => .{ .afterburner, "Afterburner" },
            .skull => .{ .kill_count, "KillCount" },
            .coil => .{ .countermeasures, "Countermeasures" },
        };
        var r = self.layout.root(root);
        var buffer: [64]u8 = undefined;
        _ = try self.picture(pen, std.fmt.bufPrint(&buffer, "indicators/{s}", .{key}) catch unreachable, r, .{});
        const height = @max(20, @divTrunc(r.w, 4));
        r.y += @divTrunc(r.h, 2) + @max(4, @max(@divTrunc(r.w, 16), @divTrunc(height, 3))) + @divTrunc(height, 2);
        r.h = height;
        try inkText(pen, std.fmt.bufPrint(&buffer, "{d}", .{unsigned(value)}) catch return, r, @floatFromInt(height), .centre);
    }

    pub fn clock(self: *Renderer, pen: hud.Pen, minutes: u16, seconds: u16) std.mem.Allocator.Error!void {
        var buffer: [32]u8 = undefined;
        const r = self.layout.root(.mission_clock);
        try text(pen, std.fmt.bufPrint(&buffer, "{d:0>2}:{d:0>2}", .{ minutes, seconds }) catch return, r, @floatFromInt(r.h), .centre);
    }

    pub fn charge(self: *Renderer, pen: hud.Pen, kind: hud.Device, length: i32) void {
        const r = self.layout.root(switch (kind) {
            .ecm => .ecm,
            .cloak => .cloaking,
            .spectral_shields => .spectral_shield,
        });
        filled(pen, .{ .x = r.x, .y = r.y + @divTrunc(r.h, 2) + 3, .w = @max(1, @divTrunc(r.w * std.math.clamp(length, 0, 32), 32)), .h = 3 }, .{ 1, 0.55, 0, 1 });
    }

    pub fn cluster(self: *Renderer, pen: hud.Pen, gauges: hud.Cluster.Gauges) hud.Error!void {
        const throttle, const speed = hud.Cluster.shares(gauges);
        for ([_]bool{ false, true }) |right| {
            const r = self.layout.root(if (right) .energy_gauge else .throttle_gauge);
            const scale: f32 = @as(f32, @floatFromInt(r.h)) / 146;
            const sw = hud.round(68 * scale);
            const sh = hud.round(141 * scale);
            _ = try self.picture(pen, if (right) "frame_127_mirrored_right" else "frame_127", .{ .x = r.x, .y = r.y, .w = sw, .h = sh }, .{});
            const w = hud.round(65 * scale);
            const h = hud.round(138 * scale);
            const left = r.x - @divTrunc(sw, 2) + hud.round((if (right) @as(f32, 14) else -10) * scale);
            const top = r.y - @divTrunc(sh, 2);
            const at: Rect = .{ .x = left + @divTrunc(w, 2), .y = top + @divTrunc(h, 2), .w = w, .h = h };
            const offset = hud.Cluster.markerOffset(speed);
            const level = if (right) gauges.unlit() else offset[1] + hud.Cluster.circle[1];
            const split = std.math.clamp(@as(f32, @floatFromInt(level)) / 138, 0, 1);
            const projected = at.onScreen(pen.screen);
            const x = projected[0] - projected[2] / 2;
            const y = projected[1] - projected[3] / 2;
            _ = try self.picture(pen, if (right) "frame_248" else "frame_184", at, .{ .clip = .{ .left = x, .right = x + projected[2], .top = y + split * projected[3], .bottom = y + projected[3] } });
            _ = try self.picture(pen, if (right) "frame_249" else "frame_185", at, .{ .clip = .{ .left = x, .right = x + projected[2], .top = y, .bottom = y + split * projected[3] } });
            if (!right) {
                if (@abs(throttle - speed) > 0.01) try self.speedMarker(pen.dimmed(@min(@abs(throttle - speed) * 10, 1)), r, scale, throttle, gauges.max_speed * gauges.throttle);
                try self.speedMarker(pen, r, scale, speed, gauges.speed);
            }
        }
    }

    fn speedMarker(self: *Renderer, pen: hud.Pen, r: Rect, scale: f32, share: f32, value: f32) hud.Error!void {
        const offset = hud.Cluster.markerOffset(share);
        const x = r.x + hud.round(@as(f32, @floatFromInt(offset[0] + 67)) * scale);
        const y = r.y + hud.round(@as(f32, @floatFromInt(offset[1] + 11)) * scale);
        _ = try self.picture(pen, "flight_gauge_pointer", .{ .x = x - hud.round(3.5 * scale), .y = y + hud.round(0.5 * scale), .w = hud.round(11 * scale), .h = hud.round(7 * scale) }, .{});
        var buffer: [32]u8 = undefined;
        try text(pen, std.fmt.bufPrint(&buffer, "{d}", .{unsigned(hud.round(value))}) catch return, .{ .x = x - hud.round(33 * scale), .y = y, .w = hud.round(48 * scale), .h = hud.round(10 * scale) }, 10 * scale, .right);
    }
    pub fn status(self: *Renderer, pen: hud.Pen, shown: hud.ShipStatus.Shown, mode: hud.ShipStatus.Mode) hud.Error!void {
        const child: Child = if (mode == .player) .player_schematic_child_schematic else .target_schematic_child_schematic;
        const ring = self.layout.child(if (mode == .player) .player_schematic_child_damage_ring else .target_schematic_child_damage_ring);
        const role: []const u8 = if (mode == .player) "player_dam" else if (shown.mirrored) "ally_target" else "enemy_target";
        const ship = shipName(shown.kind);
        var buffer: [160]u8 = undefined;
        var rect = self.layout.child(child);
        const key = std.fmt.bufPrint(&buffer, "schems/{s}/{s}", .{ role, ship }) catch unreachable;
        if (try self.texture(pen, key)) |img| {
            rect = try self.fitted(pen.gpa, img, rect);
            image(pen, img, rect, .{});
        } else {
            if (shown.schematic) |schematic| try native(pen.drawing(schematic), 0, rect, .{ .mirror = .{ .across = shown.mirrored } });
        }
        var hits = shown.hits.iterator();
        while (hits.next()) |quadrant| {
            const frame = @as(usize, @intFromEnum(quadrant)) + 1;
            if (!try self.picture(pen, std.fmt.bufPrint(&buffer, "schems/{s}/damage_layers/{s}_{d}", .{ role, ship, frame }) catch unreachable, rect, .{})) {
                if (shown.schematic) |schematic| try native(pen.drawing(schematic), frame, rect, .{ .mirror = .{ .across = shown.mirrored } });
            }
        }
        const found = shown.rings orelse return;
        const arcs = hud.ShipStatus.layouts.get(mode);
        for (arcs.shields ++ arcs.armor, found.shields ++ found.armor) |arc, level| {
            if (level <= 0) continue;
            const frame = arc.base - @as(u16, @intCast(std.math.clamp(level, 1, 5)));
            _ = try self.picture(pen, std.fmt.bufPrint(&buffer, "damage/ring/frame_{d}", .{frame}) catch unreachable, ring, .{ .mirror = .{ .across = mode == .target } });
        }
        // Reserve arcs have no replacement masters; preserve their real shield state.
        if (shown.reserves) |reserves| {
            const scale = @as(f32, @floatFromInt(ring.w)) / 80 * screenScale(pen);
            var own = pen.sized(scale);
            own.custom_hud = null;
            const projected = ring.onScreen(pen.screen);
            for ([_]hud.ShipStatus.Arc{ hud.ShipStatus.reserve_arcs.fore, hud.ShipStatus.reserve_arcs.aft }, reserves) |arc, value| {
                if (value > 0) try own.shape(@as(usize, arc.base) - @as(usize, @intCast(@min(value, 5))), own.moved(.{ hud.round(projected[0]), hud.round(projected[1]) }, arc.offset));
            }
        }
    }

    pub fn radar(self: *Renderer, pen: hud.Pen, state: *const hud.State, all: *const create.Objects, speaker: ?u16) hud.Error!void {
        const rect = self.layout.root(.wireframe_00);
        const r = rect.onScreen(pen.screen);
        const point: [2]f32 = .{ r[0] + 4 * r[2] / 350, r[1] - r[3] / 221 };
        // The authored ring's active ellipse is 328 by 161, centered at +4,-1.
        const rx = r[2] * 164 / 350;
        const ry = r[3] * 80.5 / 221;
        var row: i32 = -hud.round(ry);
        while (row <= hud.round(ry)) : (row += 1) {
            const dy = @as(f32, @floatFromInt(row));
            const dx = rx * @sqrt(@max(0, 1 - dy * dy / (ry * ry)));
            hud.drawFilled(pen.device, .{ .left = point[0] - dx, .right = point[0] + dx, .top = point[1] + dy, .bottom = point[1] + dy + 1 }, .{ 0, 0, 0, 0.62745 * pen.colour[3] });
        }
        try radarContacts(pen, point, r[2] / 350, r[3] / 221, .of(all, state.radar_range, speaker), .below);
        const paths = @import("recommissioned_assets.zig").radar;
        // The 43 authored frames span the same two native zoom intervals.
        const index: usize = if (state.radar_rings <= 358)
            @intCast(@divTrunc((@as(i32, state.radar_rings) - 353) * 21, 5))
        else
            @intCast(21 + @divTrunc((@as(i32, state.radar_rings) - 358) * 21, 5));
        _ = try self.picture(pen, paths[@min(index, paths.len - 1)], rect, .{});
        try radarContacts(pen, point, r[2] / 350, r[3] / 221, .of(all, state.radar_range, speaker), .above);
    }

    pub fn window(self: *Renderer, held: *hud.windows.Windows, pen: hud.Pen, which: hud.windows.Window, ahead: bool, contents: hud.windows.Contents) hud.Error!void {
        if (which == .radio) {
            if (ahead) try self.commsGrid(pen);
            if (contents.radio) |radio| try hud.radio.frame(radio, held, .{ .pen = pen, .at = .{ 0, 0 }, .clip = null }, ahead);
            return;
        }
        if (!ahead) return;
        switch (which) {
            .gunnery => if (contents.gunnery) |shown| try self.gunnery(pen, shown),
            .missiles => if (contents.missiles) |shown| try self.missiles(pen, shown),
            .damage => if (contents.damage) |shown| try self.damage(pen, shown),
            .power => if (contents.power) |shown| try self.power(pen, shown),
            .objectives => if (contents.objectives) |shown| try self.objectives(pen, shown),
            .comms => if (contents.comms) |shown| try self.comms(pen, shown),
            .wing_status => if (contents.wing_status) |shown| try self.wing(pen, shown),
            .target, .big_target => if (contents.target_display) |scene| {
                const closing = held.status.get(which).phase == .closing;
                if (which == .target) {
                    if (!closing) scene.state.target_pictures.small = scene.small();
                    if (scene.state.target_pictures.small) |shown| try self.smallTarget(pen, shown);
                } else {
                    if (!closing) scene.state.target_pictures.large = scene.large();
                    if (scene.state.target_pictures.large) |shown| try self.largeTarget(pen, shown);
                }
            },
            else => {},
        }
    }

    fn gunnery(self: *Renderer, pen: hud.Pen, shown: hud.gunnery.Shown) hud.Error!void {
        try self.childImage(pen, .gunnery_display_child_floor, "wireframes/frame_120", .{ .down = true });
        try self.childImage(pen, .gunnery_display_child_grid, "wireframes/frame_123", .{});
        var key: [160]u8 = undefined;
        const ship = shipName(shown.slot.object.type);
        const rect = self.layout.child(.gunnery_display_child_ship);
        _ = try self.picture(pen, std.fmt.bufPrint(&key, "gunnery/ship_wireframes/{s}/wireframe", .{ship}) catch unreachable, rect, .{});
        var buffer: [hud.gunnery.max_items]hud.gunnery.Item = undefined;
        const items = hud.gunnery.items(shown.slot, shown.wire_frame, &buffer);
        const base = shown.wire_frame orelse return;
        for (0..@min(@as(usize, @intCast(@max(shown.slot.groupCount(), 0))), 3)) |group| {
            var on = shown.slot.object.gun_mode.all or shown.slot.object.gun_mode.group == group;
            if (shown.slot.groupCount() > 1) {
                on = false;
                for (items) |item| if (item == .shape and item.shape.index == base + group + 1) {
                    on = true;
                };
            }
            _ = try self.picture(pen, std.fmt.bufPrint(&key, "gunnery/ship_wireframes/{s}/gun_group_{d}_{s}", .{ ship, group + 1, if (on) @as([]const u8, "on") else "off" }) catch unreachable, rect, .{});
        }
        const label = self.layout.child(.gunnery_display_child_name);
        for (items) |item| switch (item) {
            .string => |entry| try inkText(pen, pen.strings.string(entry.id) orelse "", label, @floatFromInt(label.h), .centre),
            .rounds => |entry| {
                var words: [32]u8 = undefined;
                const ammo = self.layout.child(.gunnery_display_child_ammo);
                try inkText(pen, std.fmt.bufPrint(&words, "{d}", .{unsigned(entry.count)}) catch unreachable, ammo, @floatFromInt(ammo.h), .centre);
            },
            else => {},
        };
        // Both the bar and caption follow the live mode, including FULL GUNS.
        // Their rectangles follow the weapon label when the panel is moved.
        const mode = firingMode(shown.slot.object.gun_mode);
        const bar = relative(label, 0, 23, 140, 6, 230, 18);
        if (mode == .individual) {
            filled(pen, relative(bar, -37, 0, 66, 6, 140, 6), .{ 1, 0.42, 0, 1 });
            filled(pen, relative(bar, 37, 0, 66, 6, 140, 6), .{ 1, 0.42, 0, 1 });
        } else filled(pen, bar, .{ 1, 0.42, 0, 1 });
        const caption = relative(label, 0, 46, 230, 14, 230, 18);
        try inkText(pen, if (mode == .individual) "INDIVIDUAL" else "SYNCHRONISED", caption, @floatFromInt(caption.h), .centre);
    }

    fn missiles(self: *Renderer, pen: hud.Pen, shown: hud.missile_display.Shown) hud.Error!void {
        try self.childImage(pen, .missile_display_child_upper_grid, "wireframes/frame_124", .{});
        try self.childImage(pen, .missile_display_child_main_grid, "wireframes/frame_126", .{});
        const rect = self.layout.child(.missile_display_child_carousel);
        var key: [128]u8 = undefined;
        for (shown.ring.entries) |entry| {
            const count = entry.left() orelse continue;
            const name = switch (entry.type.base()) {
                .jack_hammer => "jackhammer",
                .imp => "torpedo",
                else => std.enums.tagName(@TypeOf(entry.type.base()), entry.type.base()) orelse "unmapped",
            };
            const path = missileKey(&key, name, entry.place);
            if (!try self.picture(pen, path, rect, .{})) try native(pen, @intCast(entry.shape + entry.place), rect, .{});
            if (entry.place == 0) {
                var words: [32]u8 = undefined;
                const ammo = self.layout.child(.missile_display_child_ammo);
                const label = self.layout.child(.missile_display_child_name);
                try inkText(pen, std.fmt.bufPrint(&words, "{d}", .{unsigned(count)}) catch unreachable, ammo, @floatFromInt(ammo.h), .centre);
                try inkText(pen, pen.strings.string(@intCast(entry.name)) orelse "", label, @floatFromInt(label.h), .centre);
            }
        }
    }

    fn wing(self: *Renderer, pen: hud.Pen, shown: hud.wing_status.Shown) hud.Error!void {
        try self.childImage(pen, .wing_status_child_grid, "wireframes/wing_status_grid", .{ .across = true });
        try self.string(pen, .wing_status_child_name, 0xA6, 20, .centre);
        var entries: [6]hud.wing_status.Entry = undefined;
        var key: [128]u8 = undefined;
        for (hud.wing_status.entries(shown.all, &entries)) |entry| {
            const child: Child = @enumFromInt(@intFromEnum(Child.wing_status_child_ship_1) + entry.number - 1);
            const rect = self.layout.childSized(child, .{ 76, 76 });
            const index = shown.all.wing[entry.number - 1] orelse continue;
            const kind = shown.all.slots[index].object.type;
            if (!try self.picture(pen, std.fmt.bufPrint(&key, "squadron/{s}", .{shipName(kind)}) catch unreachable, rect, .{})) {
                if (entry.icon) |icon| try native(pen, icon, rect, .{});
            }
            var label = rect;
            label.y -= @divTrunc(rect.h, 2) + @divTrunc(rect.w * 30, 76);
            label.h = @divTrunc(rect.w * 24, 76);
            try text(pen, std.fmt.bufPrint(&key, "{d}", .{entry.number}) catch unreachable, label, @floatFromInt(label.h), .centre);
            const bar: Rect = .{ .x = rect.x + @divTrunc(rect.w, 2) + @divTrunc(rect.w, 10), .y = rect.y, .w = @max(4, @divTrunc(rect.w, 16)), .h = @max(40, @divTrunc(rect.h * 3, 4)) };
            segments(pen, bar, 1 - @as(f32, @floatFromInt(entry.lost)) / 38, 10, true);
        }
    }

    fn damage(self: *Renderer, pen: hud.Pen, shown: hud.damage.Shown) hud.Error!void {
        try self.childImage(pen, .systems_damage_child_upper_grid, "wireframes/frame_120", .{ .across = true });
        try self.childImage(pen, .systems_damage_child_side_grid, "wireframes/frame_121", .{ .across = true });
        try self.string(pen, .systems_damage_child_title, 0x28D, 18, .right);
        for ([_]Child{ .systems_damage_child_weapons, .systems_damage_child_engines, .systems_damage_child_shields }, [_][]const u8{ "Guns", "Engine", "Shields" }, std.enums.values(hud.damage.System)) |child, icon, system| {
            const r = self.layout.child(child);
            var key: [64]u8 = undefined;
            _ = try self.picture(pen, std.fmt.bufPrint(&key, "indicators/{s}", .{icon}) catch unreachable, relative(r, -48, -5, 32, 32, 142, 38), .{});
            const label: []const u8 = switch (system) {
                .weapons => "WEAPONS",
                .engines => "ENGINES",
                .shields => "SHIELDS",
            };
            try text(pen, label, relative(r, 15, -10, 90, 14, 142, 38), 14 * @as(f32, @floatFromInt(r.h)) / 38, .left);
            filled(pen, relative(r, 16, 1, 90, 1, 142, 38), .{ 1, 0.55, 0.05, 1 });
            filled(pen, relative(r, -29, 7, 1, 12, 142, 38), .{ 1, 0.55, 0.05, 1 });
            filled(pen, relative(r, -45, 12, 32, 1, 142, 38), .{ 1, 0.55, 0.05, 1 });
            segments(pen, relative(r, 13, 7, 78, 6, 142, 38), system.condition(shown.object), 20, false);
        }
    }

    fn power(self: *Renderer, pen: hud.Pen, shown: hud.power.Shown) hud.Error!void {
        try self.childImage(pen, .power_distribution_child_grid, "wireframes/power_distribution_grid", .{});
        try self.childText(pen, .power_distribution_child_title, "POWER DISTRIBUTION", 18, .centre);
        const setting = input_power.point(shown.object);
        shown.ball.render(setting, shown.hit_shake, shown.random);
        var orb = self.layout.child(.power_distribution_child_orb);
        const original_width = orb.w;
        orb.w = @divTrunc(orb.w * hud.power.image_width, hud.power.size);
        orb.x += @divTrunc(orb.w - original_width, 2);
        image(pen, &shown.ball.image, orb, .{});
        const shares = hud.power.percentages(setting);
        for ([_]Child{ .power_distribution_child_weapons, .power_distribution_child_engines, .power_distribution_child_shields }, [_]input_power.System{ .guns, .engines, .shields }, [_][]const u8{ "Guns", "Engine", "Shields" }, [_][]const u8{ "WEAPONS", "ENGINES", "SHIELDS" }) |child, system, icon, label| {
            const r = self.layout.child(child);
            var key: [64]u8 = undefined;
            _ = try self.picture(pen, std.fmt.bufPrint(&key, "indicators/{s}", .{icon}) catch unreachable, relative(r, 0, -27, 64, 64, 68, 118), .{});
            try text(pen, label, relative(r, 0, 16, 68, 14, 68, 118), 14 * @as(f32, @floatFromInt(r.w)) / 68, .centre);
            try text(pen, std.fmt.bufPrint(&key, "{d}%", .{unsigned(shares.get(system))}) catch unreachable, relative(r, 0, 39, 68, 18, 68, 118), 18 * @as(f32, @floatFromInt(r.w)) / 68, .centre);
        }
    }

    fn objectives(self: *Renderer, pen: hud.Pen, shown: hud.objectives_window.Shown) hud.Error!void {
        try self.childImage(pen, .mission_objectives_child_grid, "wireframes/mission_objectives_grid", .{ .across = true });
        try self.string(pen, .mission_objectives_child_title, 0x128, 18, .right);
        const words = hud.objectives_window.words(shown.objectives);
        try self.string(pen, .mission_objectives_child_status, words.heading, 14, .right);
        const body = words.name orelse return;
        const value = switch (body) {
            .string => |id| pen.strings.string(id) orelse "",
            .missing => "No objectives available.",
        };
        const r = self.layout.child(.mission_objectives_child_body);
        var lines: hud.WrappedText = .init(&pen.font.widths, value, 140, 6);
        var row = r;
        row.h = @max(1, @divTrunc(r.h, 6));
        row.y = r.y - @divTrunc(r.h, 2) + @divTrunc(row.h, 2);
        while (lines.next()) |line| : (row.y += row.h) try text(pen, line, row, @floatFromInt(row.h), .left);
    }

    fn smallTarget(self: *Renderer, pen: hud.Pen, shown: hud.target_display.Small) hud.Error!void {
        try self.status(pen, shown.status, .target);
        var r = self.layout.child(.target_schematic_child_readout);
        const height = @max(8, @divTrunc(15 * r.h, 52));
        const pitch = @max(1, @divTrunc(r.h - height, 3));
        r.y -= @divTrunc(r.h, 2) - @divTrunc(height, 2);
        r.h = height;
        var buffer: [32]u8 = undefined;
        try text(pen, pen.strings.string(shown.facts.name orelse 0) orelse "", r, @floatFromInt(height), .left);
        r.y += pitch;
        try text(pen, pen.strings.string(shown.pilot orelse 0) orelse "", r, @floatFromInt(height), .left);
        r.y += pitch;
        try text(pen, hud.rangeText(buffer[0..16], shown.facts.range), r, @floatFromInt(height), .left);
        r.y += pitch;
        try text(pen, std.fmt.bufPrint(&buffer, "{d} kps", .{unsigned(shown.facts.speed)}) catch unreachable, r, @floatFromInt(height), .left);
    }

    fn largeTarget(self: *Renderer, pen: hud.Pen, shown: hud.target_display.Large) hud.Error!void {
        try self.childImage(pen, .large_target_display_child_side_grid, "wireframes/frame_123", .{ .across = true });
        try self.childImage(pen, .large_target_display_child_floor_grid, "wireframes/frame_125", .{});
        if (shown.picture) |schematic| {
            const set = if (schematic.art.pictures) |pictures| pictures.set else "";
            const base = std.fs.path.stem(set);
            var buffer: [128]u8 = undefined;
            const r = self.layout.child(.large_target_display_child_schematic);
            if (!try self.picture(pen, std.fmt.bufPrint(&buffer, "schems/large_target/{s}", .{base}) catch unreachable, r, .{})) try native(pen.drawing(schematic), 0, r, .{});
        }
        try self.string(pen, .large_target_display_child_name, shown.facts.name orelse 0, 15, .right);
        var buffer: [32]u8 = undefined;
        try self.childText(pen, .large_target_display_child_range, hud.rangeText(buffer[0..16], shown.facts.range), 15, .right);
        try self.number(pen, .large_target_display_child_speed, "{d} kps", .{unsigned(shown.facts.speed)}, 15, .right);
        if (shown.hull) |bar| segments(pen, self.layout.child(.large_target_display_child_target_health), 1 - @as(f32, @floatFromInt(bar.unlit)) / 98, 22, true);
        if (shown.subtarget) |part| {
            const r = self.layout.child(.large_target_display_child_subtarget);
            if (!try self.picture(pen, std.fmt.bufPrint(&buffer, "target/subtargets/frame_{d}", .{part.named.icon}) catch unreachable, r, .{})) try native(pen, part.named.icon, r, .{});
            try self.string(pen, .large_target_display_child_subtarget_label, part.named.name, 15, .left);
            if (part.unlit) |unlit| segments(pen, self.layout.child(.large_target_display_child_subtarget_health), 1 - @as(f32, @floatFromInt(unlit)) / 38, 10, true);
        }
    }

    fn commsGrid(self: *Renderer, pen: hud.Pen) hud.Error!void {
        try self.childImage(pen, .comms_child_side_grid, "wireframes/frame_121", .{});
        try self.childImage(pen, .comms_child_upper_grid, "wireframes/frame_120", .{});
    }

    pub fn radioShape(self: *Renderer, pen: hud.Pen, index: usize) hud.Error!void {
        try native(pen, index, self.layout.child(.comms_child_portrait), .{});
    }

    pub fn radioImage(self: *Renderer, pen: hud.Pen, img: *srtexture.Image, shake: ?hud.Shake) void {
        image(pen, img, self.layout.child(.comms_child_portrait), .{ .shake = shake });
    }

    pub fn radioName(self: *Renderer, pen: hud.Pen, id: u32) std.mem.Allocator.Error!void {
        try self.string(pen, .comms_child_speaker_name, id, 18, .left);
    }

    fn comms(self: *Renderer, pen: hud.Pen, shown: @import("../videoreports/menu.zig").Shown) hud.Error!void {
        try self.commsGrid(pen);
        try self.childText(pen, .comms_child_menu_text, "COMMS", 20, .left);
        var r = self.layout.child(.comms_child_command_text);
        const title = self.layout.child(.comms_child_menu_text);
        const content = self.layout.child(.comms_child_content);
        const height = @max(8, @divTrunc(r.w * 12, 222));
        // This child's defaults describe the original whole command pane. Its
        // live rows start beneath the authored title; retain any extra offsets.
        r.x = title.x - @divTrunc(title.w, 2) + @divTrunc(r.w, 2) + r.x - content.x + @divTrunc(content.w, 225);
        r.y = title.y + @divTrunc(title.h, 2) + height + r.y - content.y + @divTrunc(content.w * 2, 225);
        r.h = height;
        for (shown.menu.shown(), 0..) |item, index| {
            var label: [@import("../videoreports/menu.zig").Label.room]u8 = undefined;
            var buffer: [512]u8 = undefined;
            try text(pen, std.fmt.bufPrint(&buffer, "{d}. {s}", .{ index + 1, item.label.words(pen.strings, &label) }) catch continue, r, @floatFromInt(height), .left);
            r.y += height;
        }
    }
};

/// Several supplied HUD images have black outlines but white RGB in alpha-zero
/// pixels. Straight-alpha texture filtering includes that invisible white in
/// edge samples. Give those clear pixels the outline's black before making
/// mipmaps; leave every visible pixel and every alpha value untouched.
fn clearTransparentMatte(rgba: []u8) void {
    for (std.mem.bytesAsSlice([4]u8, rgba)) |*pixel| {
        if (pixel[3] == 0) pixel[0..3].* = .{ 0, 0, 0 };
    }
}

test "radar matte cleanup preserves visible colour and coverage" {
    var rgba = [_]u8{ 255, 255, 255, 0, 133, 4, 2, 255, 12, 3, 1, 80, 0, 0, 0, 255 };
    clearTransparentMatte(&rgba);
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0, 0, 133, 4, 2, 255, 12, 3, 1, 80, 0, 0, 0, 255 }, &rgba);
}

test "filtering a black radar edge cannot pick up a white fringe" {
    const gpa = std.testing.allocator;
    const rgba = try gpa.dupe(u8, &.{ 0, 0, 0, 255, 255, 255, 255, 0 });
    clearTransparentMatte(rgba);
    var img = try srtexture.mipmapped(gpa, .{ .width = 2, .height = 1, .rgba = rgba });
    defer img.deinit(gpa);
    const edge = img.sample(0, 0.5, 0.5);
    try std.testing.expectEqual([4]f32{ 0, 0, 0, 0.5 }, edge);
    // The reduced image is also black, with only its coverage changing.
    try std.testing.expectEqualSlices(u8, &.{ 0, 0, 0 }, img.levels[1].texels[0..3]);
}

fn relative(parent: Rect, x: i32, y: i32, w: i32, h: i32, bw: i32, bh: i32) Rect {
    return .{ .x = parent.x + @divTrunc(x * parent.w, bw), .y = parent.y + @divTrunc(y * parent.h, bh), .w = @max(1, @divTrunc(w * parent.w, bw)), .h = @max(1, @divTrunc(h * parent.h, bh)) };
}

fn segments(pen: hud.Pen, r: Rect, share: f32, count: i32, vertical: bool) void {
    var i: i32 = 0;
    while (i < count) : (i += 1) {
        const lit = if (vertical) @as(f32, @floatFromInt(count - i)) / @as(f32, @floatFromInt(count)) <= share + 0.001 else @as(f32, @floatFromInt(i)) / @as(f32, @floatFromInt(count)) < share;
        const piece = if (vertical) relative(r, 0, 2 * i + 1 - count, 1, 1, 1, 2 * count) else relative(r, 2 * i + 1 - count, 0, 1, 1, 2 * count, 1);
        filled(pen, piece, if (lit) .{ 0.9, 0.42, 0.025, 1 } else .{ 0.5, 0.03, 0.01, 1 });
    }
}

fn screenScale(pen: hud.Pen) f32 {
    return @min(@as(f32, @floatFromInt(pen.screen[0])) / 1920, @as(f32, @floatFromInt(pen.screen[1])) / 1080);
}

fn filled(pen: hud.Pen, rect: Rect, colour: [4]f32) void {
    const r = rect.onScreen(pen.screen);
    hud.drawFilled(pen.device, .{ .left = r[0] - r[2] / 2, .right = r[0] + r[2] / 2, .top = r[1] - r[3] / 2, .bottom = r[1] + r[3] / 2 }, colour);
}

fn shipName(kind: gameobj.Type) []const u8 {
    return switch (@intFromEnum(kind.untwinned())) {
        0 => "predator",
        1 => "naginata",
        2 => "grendal",
        3 => "crusader",
        4 => "coyote",
        5 => "mirage",
        6 => "tempest",
        7 => "patriot",
        8 => "wolverine",
        9 => "reaper",
        10 => "shroud",
        11 => "phoenix",
        23 => "sai",
        25 => "galahad",
        26 => "hades",
        29 => "boarding_ship",
        31 => "ripper",
        39 => "haidar",
        40 => "karac",
        41 => "salin",
        42 => "azan",
        43 => "saber",
        44 => "lagg",
        45 => "kamov",
        46 => "saracen",
        47 => "coal_gun_sat",
        48 => "scimitar",
        49 => "basilisk",
        50 => "kossac",
        65 => "loki",
        else => "unmapped",
    };
}

fn isHalo(p: []const u8) bool {
    return p[3] > 0 and p[3] < 240 and p[0] <= 4 and p[1] <= 4 and p[2] <= 4;
}

fn silhouetteBounds(level: srtexture.Level) [4]i32 {
    var halos: usize = 0;
    var i: usize = 0;
    while (i < level.texels.len) : (i += 4) if (isHalo(level.texels[i..][0..4])) {
        halos += 1;
    };
    var b: [4]i32 = .{ @intCast(level.width), @intCast(level.height), 0, 0 };
    for (0..level.height) |y| for (0..level.width) |x| {
        const pixel = level.texels[(y * level.width + x) * 4 ..][0..4];
        if (pixel[3] <= 8 or (halos >= 256 and isHalo(pixel))) continue;
        b[0] = @min(b[0], @as(i32, @intCast(x)));
        b[1] = @min(b[1], @as(i32, @intCast(y)));
        b[2] = @max(b[2], @as(i32, @intCast(x + 1)));
        b[3] = @max(b[3], @as(i32, @intCast(y + 1)));
    };
    return if (b[2] <= b[0] or b[3] <= b[1]) .{ 0, 0, @intCast(level.width), @intCast(level.height) } else b;
}

fn radarContacts(pen: hud.Pen, point: [2]f32, sx: f32, sy: f32, input: hud.Radar.Contacts, plane: hud.Radar.Plane) hud.Error!void {
    var contacts = input;
    var own = pen.sized(2.6 * @min(sx, sy));
    own.custom_hud = null;
    while (contacts.next()) |contact| {
        if (contact.plane() != plane) continue;
        const x = point[0] + @as(f32, @floatFromInt(contact.at[0])) * 2.52 * sx;
        const y = std.math.clamp(point[1] + @as(f32, @floatFromInt(contact.at[1])) * 2.30 * sy, 0, @as(f32, @floatFromInt(pen.screen[1])) - 2);
        if (contact.look == .nav_point) {
            pen.line(.{ x - 2 * sx, y }, .{ x + 2 * sx, y }, .{ 1, 1, 1, pen.colour[3] });
            pen.line(.{ x, y - 2 * sy }, .{ x, y + 2 * sy }, .{ 1, 1, 1, pen.colour[3] });
        } else {
            if (contact.height != 0) {
                const other = y - @as(f32, @floatFromInt(contact.height)) * 2.30 * sy;
                const colour = pen.art.paletteColour(contact.look.line());
                hud.drawFilled(pen.device, .{ .left = x, .right = x + @max(1, 3 * sx), .top = @min(y, other), .bottom = @max(y, other) }, colour);
            }
            try own.shape(contact.look.shape(), .{ hud.round(x + 2 * sx), hud.round(y) });
        }
    }
}

test "player ship twins choose the same custom artwork" {
    for (0..12) |number| {
        try std.testing.expectEqualStrings(shipName(@enumFromInt(number)), shipName(@enumFromInt(number + gameobj.GameType.player_twins_first)));
    }
    try std.testing.expectEqualStrings("coyote", shipName(@enumFromInt(248)));
}

test "schematic bounds ignore transparent pixels and exclude a large black halo" {
    var pixels: [32 * 32 * 4]u8 = @splat(0);
    for (0..32 * 32) |i| pixels[i * 4 + 3] = 100;
    for (8..24) |y| for (10..22) |x| {
        pixels[(y * 32 + x) * 4] = 255;
        pixels[(y * 32 + x) * 4 + 3] = 255;
    };
    try std.testing.expectEqual([4]i32{ 10, 8, 22, 24 }, silhouetteBounds(.{ .width = 32, .height = 32, .texels = &pixels }));
}

fn unsigned(value: anytype) u32 {
    return @intCast(@max(0, value));
}

fn missileKey(buffer: []u8, name: []const u8, place: i32) []const u8 {
    return std.fmt.bufPrint(buffer, "missiles/{s}/slot_{d:0>2}_{s}", .{ name, unsigned(place), if (place == 0) @as([]const u8, "gold") else "red" }) catch unreachable;
}

test "carousel filenames match the zero-padded authored assets" {
    var buffer: [128]u8 = undefined;
    try std.testing.expectEqualStrings("missiles/bandit/slot_00_gold", missileKey(&buffer, "bandit", 0));
    try std.testing.expectEqualStrings("missiles/screamer/slot_02_red", missileKey(&buffer, "screamer", 2));
    try std.testing.expectEqualStrings("missiles/havoc/slot_09_red", missileKey(&buffer, "havoc", 9));
}

const FiringMode = enum { full, synchronised, individual };

fn firingMode(mode: gameobj.GunMode) FiringMode {
    return if (mode.all) .full else if (mode.synchronised) .synchronised else .individual;
}

fn inkRows(pixels: []const u8, width: u32, height: u32) [2]u32 {
    var first = height;
    var last: u32 = 0;
    if (width > 0) for (pixels, 0..) |value, i| {
        if (value == 0) continue;
        const row: u32 = @intCast(i / width);
        first = @min(first, row);
        last = @max(last, row + 1);
    };
    return if (last > first) .{ first, last } else .{ 0, @max(1, height) };
}

test "gunnery distinguishes full, synchronised and individual firing" {
    var mode = gameobj.GunMode.created(2);
    try std.testing.expectEqual(FiringMode.full, firingMode(mode));
    mode.synchronised = false;
    try std.testing.expectEqual(FiringMode.full, firingMode(mode));
    mode.all = false;
    try std.testing.expectEqual(FiringMode.individual, firingMode(mode));
    mode.synchronised = true;
    try std.testing.expectEqual(FiringMode.synchronised, firingMode(mode));
}

test "readout cap height excludes empty rows without losing faint edges" {
    try std.testing.expectEqual([2]u32{ 1, 3 }, inkRows(&.{ 0, 0, 1, 255, 255, 2, 0, 0 }, 2, 4));
    try std.testing.expectEqual([2]u32{ 0, 4 }, inkRows(&.{ 0, 0, 0, 0 }, 1, 4));
    try std.testing.expectEqual([2]u32{ 0, 1 }, inkRows(&.{}, 0, 0));
}
