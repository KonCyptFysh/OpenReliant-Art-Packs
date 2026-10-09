//! Standalone layout validation helper; not part of the game executable.
const std = @import("std");
const layout = @import("engine/game/hud/recommissioned_layout.zig");
const defs = @import("engine/game/hud/recommissioned_layout_defs.zig");
pub fn main(init: std.process.Init) !void {
    const gpa = init.arena.allocator();
    const args = try init.minimal.args.toSlice(gpa);
    const bytes = try std.Io.Dir.cwd().readFileAlloc(init.io, args[1], gpa, .limited(128 * 1024));
    const found = try layout.Layout.parse(bytes);
    for (std.enums.values(layout.Root)) |id| {
        const r = found.root(id);
        std.debug.print("{s} {d} {d} {d} {d}\n", .{ @tagName(id), r.x, r.y, r.w, r.h });
    }
    for (std.enums.values(layout.Child), defs.children) |id, spec| {
        const r = found.child(id);
        std.debug.print("{s} {d} {d} {d} {d}\n", .{ spec.name, r.x, r.y, r.w, r.h });
    }
}
