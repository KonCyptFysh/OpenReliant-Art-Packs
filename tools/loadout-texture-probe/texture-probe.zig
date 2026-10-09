const std = @import("std");
const sr = @import("openreliant").engine.surrender.surrenderlib.srtexture;
const Context = struct {
    io: std.Io,
    folder: []const u8,
    fn read(raw: *const anyopaque, gpa: std.mem.Allocator, name: []const u8) std.mem.Allocator.Error!?[]u8 {
        const ctx: *const Context = @ptrCast(@alignCast(raw));
        const path = try std.fs.path.join(gpa, &.{ctx.folder, name});
        defer gpa.free(path);
        return std.Io.Dir.cwd().readFileAlloc(ctx.io, path, gpa, .limited(512 * 1024 * 1024)) catch |err| switch (err) {
            error.OutOfMemory => return error.OutOfMemory,
            else => return null,
        };
    }
};
pub fn main(init: std.process.Init) !void {
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    if (args.len != 3) return error.Arguments;
    const ctx: Context = .{ .io = init.io, .folder = args[1] };
    const files: sr.Files = .{ .context = &ctx, .readFn = Context.read };
    const gpa = std.heap.page_allocator;
    var original = (try sr.mod_pictures.load(gpa, files, args[2], 256, null, null)) orelse return error.MissingBase;
    defer original.deinit(gpa);
    if (original.maps.normal == null or original.maps.orm == null) return error.MissingMaps;
    for ([_]sr.Copy{ .green, .red }) |copy| {
        var variant = (try sr.mod_pictures.load(gpa, files, args[2], 256, null, copy)) orelse return error.MissingVariant;
        defer variant.deinit(gpa);
        if (variant.maps.normal == null or variant.maps.orm == null) return error.MissingInheritedMaps;
        for (original.maps.normal.?, variant.maps.normal.?) |a, b| if (!std.mem.eql(u8, a.texels, b.texels)) return error.NormalChanged;
        for (original.maps.orm.?, variant.maps.orm.?) |a, b| if (!std.mem.eql(u8, a.texels, b.texels)) return error.MaterialChanged;
        if (std.mem.eql(u8, original.levels[0].texels, variant.levels[0].texels)) return error.ColourUnchanged;
        const pixels = variant.levels[0].texels;
        var i: usize = 0;
        while (i < pixels.len) : (i += 4) {
            if (copy == .green and (pixels[i+1] < pixels[i] or pixels[i+1] < pixels[i+2])) return error.NotGreen;
            if (copy == .red and (pixels[i+1] != 0 or pixels[i+2] != 0)) return error.NotRed;
        }
    }
    std.debug.print("PASS {s}: base, green, red; normal and ORM inherited byte-for-byte; generated colour channels verified\n", .{args[2]});
}
