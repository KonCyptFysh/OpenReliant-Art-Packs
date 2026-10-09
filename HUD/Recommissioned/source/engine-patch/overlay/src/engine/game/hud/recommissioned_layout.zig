//! **Improvement:** geometry for the Recommissioned HUD editor's layout file.
//! Coordinates are centres on a 1920 by 1080 canvas. The SL editor truncates each
//! integer operation toward zero, including negative offsets and nested comms.
//! Used by the live mod renderer; absent layouts leave the native HUD active.

const std = @import("std");
const profile = @import("../../profile.zig");
const bigfile = @import("../bigfile.zig");
const defs = @import("recommissioned_layout_defs.zig");

pub const Root = defs.Root;
pub const Child = defs.Child;
pub const file_name = "hud_layout.ini";
pub const reference_size: [2]u32 = .{ 1920, 1080 };
const maximum_file_size = 128 * 1024;
const coordinate_limit = 100000;
const minimum_root_size = 16;
const maximum_root_size = 1024;
const minimum_child_scale = 25;
const maximum_child_scale = 400;

pub const Error = error{ MissingRoot, InvalidInteger, OutOfRange, FileTooLarge };

pub const Placement = struct { x: i32, y: i32, size: i32 };
pub const Adjustment = struct { x: i32, y: i32, percent: i32 };

/// The full art canvas, including its transparent margins, centred on x and y.
/// This is not the editor's hit box, or a native sprite's anchor rectangle.
pub const Rect = struct {
    x: i32,
    y: i32,
    w: i32,
    h: i32,

    pub fn array(rect: Rect) [4]i32 {
        return .{ rect.x, rect.y, rect.w, rect.h };
    }

    /// Centre, width and height in framebuffer pixels. Fit the authored canvas
    /// uniformly and centre it, including on displays that are not 16:9.
    pub fn onScreen(rect: Rect, screen: [2]u32) [4]f32 {
        const sw: f32 = @floatFromInt(screen[0]);
        const sh: f32 = @floatFromInt(screen[1]);
        const rw: f32 = @floatFromInt(reference_size[0]);
        const rh: f32 = @floatFromInt(reference_size[1]);
        const scale = @min(sw / rw, sh / rh);
        return .{
            (sw - rw * scale) / 2 + @as(f32, @floatFromInt(rect.x)) * scale,
            (sh - rh * scale) / 2 + @as(f32, @floatFromInt(rect.y)) * scale,
            @as(f32, @floatFromInt(rect.w)) * scale,
            @as(f32, @floatFromInt(rect.h)) * scale,
        };
    }
};

pub const Layout = struct {
    roots: [defs.root_sizes.len]Placement,
    children: [defs.children.len]Adjustment,

    /// Parse a complete editor export atomically. Unknown keys are ignored, so
    /// synthetic frame labels never become native SPR shape indices. Missing
    /// children keep the original editor's offsets and 100 percent scale.
    pub fn parse(bytes: []const u8) Error!Layout {
        if (bytes.len > maximum_file_size) return error.FileTooLarge;
        const bom = "\xef\xbb\xbf";
        const text = if (std.mem.startsWith(u8, bytes, bom)) bytes[bom.len..] else bytes;
        const ini: profile.Profile = .{ .text = text };
        var layout: Layout = undefined;
        inline for (std.meta.fields(Root), 0..) |field, index| {
            const x = ini.value(field.name, "x") orelse return error.MissingRoot;
            const y = ini.value(field.name, "y") orelse return error.MissingRoot;
            const size = ini.value(field.name, "size") orelse return error.MissingRoot;
            layout.roots[index] = .{
                .x = try number(x, -coordinate_limit, coordinate_limit),
                .y = try number(y, -coordinate_limit, coordinate_limit),
                .size = try number(size, minimum_root_size, maximum_root_size),
            };
        }
        for (defs.children, 0..) |spec, index| {
            layout.children[index] = .{
                .x = try optionalNumber(ini, spec.name, "offset_x", spec.offset[0], -coordinate_limit, coordinate_limit),
                .y = try optionalNumber(ini, spec.name, "offset_y", spec.offset[1], -coordinate_limit, coordinate_limit),
                .percent = try optionalNumber(ini, spec.name, "scale_percent", 100, minimum_child_scale, maximum_child_scale),
            };
        }
        return layout;
    }

    pub fn root(layout: *const Layout, id: Root) Rect {
        const at = @intFromEnum(id);
        const saved = layout.roots[at];
        const base = defs.root_sizes[at];
        const denominator = @max(base[0], base[1]);
        return .{
            .x = saved.x,
            .y = saved.y,
            .w = @max(1, scaled(base[0], saved.size, denominator)),
            .h = @max(1, scaled(base[1], saved.size, denominator)),
        };
    }

    pub fn child(layout: *const Layout, id: Child) Rect {
        return layout.childSized(id, defs.children[@intFromEnum(id)].size);
    }

    /// Some draw recipes use a smaller canvas than the child's selection box:
    /// for example, wing icons are 76 by 76 inside a 96 by 92 editor handle.
    pub fn childSized(layout: *const Layout, id: Child, piece: [2]i32) Rect {
        const spec = defs.children[@intFromEnum(id)];
        const saved = layout.children[@intFromEnum(id)];
        var parent = layout.root(spec.parent);
        var numerator = parent.w;
        var denominator = defs.root_sizes[@intFromEnum(spec.parent)][0];
        if (spec.parent == .missile_display) {
            numerator = parent.h;
            denominator = defs.root_sizes[@intFromEnum(spec.parent)][1];
        }
        if (spec.nested_comms) {
            parent = layout.child(.comms_child_content);
            numerator = parent.w;
            denominator = defs.root_sizes[@intFromEnum(Root.comms)][0];
        }
        return .{
            .x = parent.x + scaled(saved.x, numerator, denominator),
            .y = parent.y + scaled(saved.y, numerator, denominator),
            .w = @max(1, scaled(scaled(piece[0], numerator, denominator), saved.percent, 100)),
            .h = @max(1, scaled(scaled(piece[1], numerator, denominator), saved.percent, 100)),
        };
    }
};

/// Use the same resolver as other mod files: the last enabled mod wins, file
/// names are case insensitive, and --no-mods yields null. No absolute game path.
/// The caller must catch a malformed layout and retain the native HUD as a whole.
pub fn load(gpa: std.mem.Allocator, mods: *const bigfile.Mods) (bigfile.ReadError || Error)!?Layout {
    const bytes = try mods.readFile(gpa, file_name) orelse return null;
    defer gpa.free(bytes);
    return try Layout.parse(bytes);
}

fn number(text: []const u8, minimum: i32, maximum: i32) Error!i32 {
    // Match the editor's decimal integers, including signed child offsets.
    if (text.len == 0) return error.InvalidInteger;
    const digits = if (text[0] == '-') text[1..] else text;
    if (digits.len == 0) return error.InvalidInteger;
    for (digits) |digit| if (!std.ascii.isDigit(digit)) return error.InvalidInteger;
    const value = std.fmt.parseInt(i32, text, 10) catch return error.InvalidInteger;
    if (value < minimum or value > maximum) return error.OutOfRange;
    return value;
}

fn optionalNumber(ini: profile.Profile, section: []const u8, key: []const u8, default: i32, minimum: i32, maximum: i32) Error!i32 {
    return number(ini.value(section, key) orelse return default, minimum, maximum);
}

fn scaled(value: i32, numerator: i32, denominator: i32) i32 {
    return @intCast(@divTrunc(@as(i64, value) * numerator, denominator));
}

const fixtures = @import("recommissioned_layout_fixtures.zig");

test "every saved root and child agrees with the browser editor" {
    const layout = try Layout.parse(fixtures.ini);
    for (fixtures.roots, 0..) |expected, index| {
        try std.testing.expectEqual(expected, layout.root(@enumFromInt(index)).array());
    }
    for (fixtures.children, 0..) |expected, index| {
        try std.testing.expectEqual(expected, layout.child(@enumFromInt(index)).array());
    }
}

test "integer truncation, missile height scaling and nested comms at unusual sizes" {
    for (fixtures.cases) |case| {
        var layout = try Layout.parse(fixtures.ini);
        for (&layout.roots) |*saved| saved.size = case.size;
        for (&layout.children) |*saved| saved.* = .{ .x = -37, .y = 59, .percent = 137 };
        for (case.roots, 0..) |expected, index| {
            try std.testing.expectEqual(expected, layout.root(@enumFromInt(index)).array());
        }
        for (case.children, 0..) |expected, index| {
            try std.testing.expectEqual(expected, layout.child(@enumFromInt(index)).array());
        }
    }
}

test "bad input rejects the complete layout" {
    try std.testing.expectError(error.MissingRoot, Layout.parse("[eject]\nx=960\ny=434\nsize=64\n"));
    try std.testing.expectError(error.InvalidInteger, number("1.5", -coordinate_limit, coordinate_limit));
    try std.testing.expectError(error.InvalidInteger, number("1_000", -coordinate_limit, coordinate_limit));
    try std.testing.expectError(error.InvalidInteger, number("2147483648", -coordinate_limit, coordinate_limit));
    try std.testing.expectError(error.OutOfRange, number("0", minimum_root_size, maximum_root_size));
    try std.testing.expectError(error.OutOfRange, number("401", minimum_child_scale, maximum_child_scale));
    const bom = try Layout.parse("\xef\xbb\xbf" ++ fixtures.ini);
    try std.testing.expectEqual(fixtures.roots[0], bom.root(.eject).array());
}

test "projection preserves the authored aspect ratio" {
    const centre: Rect = .{ .x = 960, .y = 540, .w = 350, .h = 221 };
    try std.testing.expectEqual([4]f32{ 960, 540, 350, 221 }, centre.onScreen(.{ 1920, 1080 }));
    try std.testing.expectEqual([4]f32{ 1920, 1080, 700, 442 }, centre.onScreen(.{ 3840, 2160 }));
    const narrow = centre.onScreen(.{ 1280, 1024 });
    try std.testing.expectApproxEqAbs(@as(f32, 640), narrow[0], 0.001);
    try std.testing.expectApproxEqAbs(@as(f32, 512), narrow[1], 0.001);
    try std.testing.expectApproxEqAbs(@as(f32, 350.0 / 221.0), narrow[2] / narrow[3], 0.001);
}

test "no mod means no custom layout" {
    try std.testing.expectEqual(@as(?Layout, null), try load(std.testing.allocator, &bigfile.Mods.none));
}
