//! Mission 0, OpenReliant's own: the sandbox, a standard mission file that the build writes into
//! `mission0.dte` (`write`) and `openreliant` plays where no other mission is chosen. It holds only
//! what the game's own missions hold, laid out as they are, so that the original plays it too.
//!
//! Its scene: the Reliant at the origin, facing along Z, from whose first four tubes the player's
//! ship and three wingmen, a Grendel, a Wolverine and a Reaper, listed in the player's wing, launch.
//! Ahead, a wing of four Sabres facing the Reliant; beyond them the Badanov, the smallest of the
//! Coalition's capital ships, turned across the way; and past the Badanov, outside the action's
//! sphere, a field of twelve rocks, the seven asteroids in turn, placed and turned from a fixed
//! seed.
//!
//! Its script's start part makes the Reliant's flight group, then every other, so that the wing
//! finds the Reliant to launch from as it is made, has an ejected pilot fare each way as likely and
//! the rocks tumble slowly (Random Spin Slow), and plays the launch's music. It starts the wing's
//! launch and waits until the wing is out (`WaitForJumpOrLaunch`), as mission 1 does, the capital
//! ships holding their fire meanwhile (`DisableGuns`). Then the Reliant and the Badanov fly on at a
//! tenth of their speed, free to fire, the Sabres fight the player and each wingman a Sabre, the
//! mission's music follows the launch's, and the player may land: the script clears it
//! (`vm.Variables.landing_cleared`), as mission 1's does once the Reliant jumps in, so that
//! PERMISSION TO LAND lands the player's ship on the Reliant, which ends the mission. The Sabres' pilot is record 42 of
//! `pilotstats.bin`, one of its weakest, where the game gives a Sabre the sharp pilot of record 66,
//! so the player's missiles mostly get past their countermeasures.

const std = @import("std");
const Allocator = std.mem.Allocator;
const Io = std.Io;

const openreliant = @import("openreliant");
const dte = openreliant.dte;
const game = openreliant.engine.game;
const Type = game.gameobj.GameType;
const Order = game.ai.orders.Order;
const Routine = dte.assemble.Routine;

/// The name OpenReliant keeps in the file (`dte.OpenReliantName`).
pub const name = "HUD 1.8 shared-frame overlap QA";

/// The mission's number, which `openreliant` plays by default.
pub const number = 0;

/// The mission's flight groups, in the order of their records.
const Group = enum(u8) {
    alpha,
    reliant,
    badanov,
    sabres,
    rocks,

    /// The name the group's record carries.
    fn label(group: Group) []const u8 {
        return switch (group) {
            .alpha => "(FG)Alpha",
            .reliant => "(FG)Reliant",
            .badanov => "(FG)Badanov",
            .sabres => "(FG)Sabres",
            .rocks => "(FG)Rocks",
        };
    }

    /// The wing the group is listed in: the player's for the player's own.
    fn wing(group: Group) dte.FlightGroup.Wing {
        return if (group == .alpha) .player else .none;
    }
};

/// A ship the mission places: its name, its kind, its flight group, its pilot, where it stands and
/// how it is turned, in whole degrees, and the Reliant's tube it launches through, where it
/// launches.
const Placed = struct {
    name: []const u8,
    kind: Type,
    group: Group,
    pilot: u8 = dte.Ship.no_pilot,
    at: [3]f32,
    yaw: i16 = 0,
    pitch: i16 = 0,
    roll: i16 = 0,
    gate: ?u8 = null,
};

/// The Badanov's heading: across the wing's way.
const across_yaw = 63;
/// The speed the capital ships fly at once the wing is out: a tenth of the 100 the Reliant's type
/// cruises at.
const crawl_speed = 10;

/// The capital ships, which hold their fire until the wing is out and then fly on at a crawl.
/// Their Huge Guns lead a target a quarter of their shots' life away, 600000 at 1200 a tick for
/// 2000 ticks (`gunstats.bin`), which the Badanov stands well within, so they would fire over the
/// launch, beside the player's hangar.
const capital_ships = [_]Group{ .reliant, .badanov };

/// The music the launch plays to, and the mission's after it, from the game's music folder.
const launch_music = "new_launch.wav";
const mission_music = "New_Mission01.wav";

/// The Sabres: `wing_size` of them, `wing_ahead` in front of the player and `wing_spacing` apart,
/// turned to face the player, flown by `wing_pilot`.
pub const wing_size = 4;
pub const wing_ahead: f32 = 150000;
pub const wing_spacing: f32 = 3000;
pub const wing_pilot = 42;

/// The field of rocks: `field_rows` rows of `field_columns`, `field_spacing` apart about
/// `field_centre`, each strayed up to `field_stray` along and across and `field_height` up or down
/// from the grid, from the random numbers of `field_seed`. Each rock is the asteroid `field_step` on
/// from the last, so neighbours differ.
const field_centre: [3]f32 = .{ 6000, -9000, 250000 };
const field_rows = 3;
const field_columns = 4;
const field_spacing: f32 = 26000;
const field_stray: f32 = 7000;
const field_height: f32 = 12000;
const field_step = 3;
const field_seed = 0x5A4D;
const field_size = field_rows * field_columns;

/// The ships before the rocks: the player's ship first, whose slot is the player's. The wing is
/// placed at the Reliant, whose tubes the launch puts it in.
const ships = [_]Placed{
    .{ .name = "Player", .kind = .predator, .group = .alpha, .at = .{ 0, 0, 80000 } },
    .{ .name = "(A2)Grendel", .kind = .grendel, .group = .alpha, .at = .{ 1000, 0, 80000 } },
    .{ .name = "(A3)Wolverine", .kind = .wolverine, .group = .alpha, .at = .{ -1000, 0, 80000 } },
    .{ .name = "(A4)Reaper", .kind = .reaper, .group = .alpha, .at = .{ 2000, 0, 80000 } },
    .{ .name = "The Reliant", .kind = .reliant, .group = .reliant, .at = @splat(0) },
    .{ .name = "The Badanov", .kind = .badanov, .group = .badanov, .at = .{ 6000, -9000, 190000 }, .yaw = across_yaw },
} ++ sabres;

const sabres = sabres: {
    var placed: [wing_size]Placed = undefined;
    for (&placed, 0..) |*sabre, n| {
        const across = (@as(f32, @floatFromInt(n)) - @as(f32, wing_size - 1) / 2) * wing_spacing;
        sabre.* = .{ .name = std.fmt.comptimePrint("Sabre {d}", .{n + 1}), .kind = .sabre, .group = .sabres, .pilot = wing_pilot, .at = .{ across, 0, wing_ahead }, .yaw = 180 };
    }
    break :sabres placed;
};

/// Where each ship stands in the list, by what it is.
const player = 0;
const wingmen = [_]u16{ 1, 2, 3 };
const first_sabre = 6;
const first_rock = ships.len;

/// The rocks, placed and turned from `field_seed`.
fn rocks() [field_size]Placed {
    var prng: std.Random.DefaultPrng = .init(field_seed);
    const random = prng.random();
    var placed: [field_size]Placed = undefined;
    for (&placed, 0..) |*rock, n| {
        const column: f32 = @floatFromInt(n % field_columns);
        const row: f32 = @floatFromInt(n / field_columns);
        const middle: [2]f32 = .{ @as(f32, field_columns - 1) / 2, @as(f32, field_rows - 1) / 2 };
        rock.* = .{
            .name = rock_names[n],
            .kind = .asteroid(n * field_step),
            .group = .rocks,
            .at = .{
                field_centre[0] + (column - middle[0]) * field_spacing + (random.float(f32) * 2 - 1) * field_stray,
                field_centre[1] + (random.float(f32) * 2 - 1) * field_height,
                field_centre[2] + (row - middle[1]) * field_spacing + (random.float(f32) * 2 - 1) * field_stray,
            },
            .yaw = random.intRangeLessThan(i16, 0, 360),
            .pitch = random.intRangeLessThan(i16, 0, 360),
            .roll = random.intRangeLessThan(i16, 0, 360),
        };
    }
    return placed;
}

const rock_names = names: {
    var all: [field_size][]const u8 = undefined;
    for (&all, 1..) |*rock, n| rock.* = std.fmt.comptimePrint("Rock {d}", .{n});
    break :names all;
};

/// Mission 0's file, made in `gpa`.
pub fn write(gpa: Allocator) ![]u8 {
    var arena_state: std.heap.ArenaAllocator = .init(gpa);
    defer arena_state.deinit();
    const arena = arena_state.allocator();
    const placed = ships ++ rocks();

    var strings: std.ArrayList(u8) = .empty;
    const part_name = try addString(arena, &strings, "(F)Start");

    const records = try arena.alloc(dte.Ship, placed.len);
    for (records, placed, 0..) |*record, ship, index| record.* = shipRecord(ship, @intCast(index), try addString(arena, &strings, ship.name));

    const groups = std.enums.values(Group);
    const group_records = try arena.alloc(dte.FlightGroup, groups.len);
    var listed: u32 = 0;
    for (group_records, groups) |*record, group| {
        var count: u8 = 0;
        for (placed) |ship| {
            if (ship.group == group) count += 1;
        }
        record.* = .{
            .object_id = @intCast(placed.len + @backingInt(group)),
            ._unknown_02 = 0,
            .name = try addString(arena, &strings, group.label()),
            ._unknown_06 = 0,
            .wing = group.wing(),
            .ship_count = count,
            ._unknown_0a = 0,
            .first_ship = listed,
            ._unknown_10 = group_tail,
        };
        listed += count;
    }

    // The object table: the ships' IDs, then the flight groups', none with triggers.
    const objects = try arena.alloc(dte.Object, placed.len + groups.len);
    for (objects, 0..) |*object, id| object.* = .{
        .kind = if (id < placed.len) .ship else .flight_group,
        .count = 0,
        .first = no_triggers,
        ._unknown_04 = 0,
    };

    const code = try script(arena);
    var part = std.mem.zeroes(dte.Part);
    part.name = part_name;
    part.offset = 0;
    part.flags.start = true;
    part.length = @intCast(code.len / @sizeOf(u16));

    var sections: dte.write.Sections = @splat(.{});
    const section = dte.write.set;
    section(&sections, .strings, strings.items.len, strings.items);
    section(&sections, .ships, records.len, std.mem.sliceAsBytes(records));
    section(&sections, .flight_groups, group_records.len, std.mem.sliceAsBytes(group_records));
    section(&sections, .script, code.len / @sizeOf(u16), code);
    section(&sections, .objects, objects.len, std.mem.sliceAsBytes(objects));
    section(&sections, .parts, 1, std.mem.asBytes(&part));
    section(&sections, .script_flags, code.len, try arena.alloc(u8, code.len));
    @memset(@constCast(sections[@backingInt(dte.Section.script_flags)].bytes), 0);
    const flags = dte.write.template.command_flags;
    section(&sections, .command_flags, flags.len, std.mem.sliceAsBytes(&flags));
    return dte.write.write(gpa, &sections, .{ .name = name });
}

/// The object table's `first` for an object with no triggers, as the game's missions give it.
const no_triggers = 0xFFFF;

/// A flight group's last word, as every flight group of the game's missions has it.
/// **Unknown:** what it means.
const group_tail = 0xFF19FFFF;

/// The bytes after a ship's pitch (`_unknown_3c`, `tier`, `_unknown_3e`, the marker's curve and its
/// place on it), as most of the ships of the game's missions have them: tier 255, which asks for
/// the campaign's, and no curve.
const ship_tail = [_]u8{ 0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00 };

/// Ship `ship`'s record, as the game's missions have their ships': object ID `id`, named at
/// `name_at`, launching through its tube of the first Reliant, or from none, in no formation, every
/// component intact, standing where it is placed.
fn shipRecord(ship: Placed, id: u32, name_at: u16) dte.Ship {
    var record = std.mem.zeroes(dte.Ship);
    record.object_id = id;
    record.name = name_at;
    record.runtime_position = ship.at;
    record.position = ship.at;
    record.flight_group = @backingInt(ship.group);
    record.pilot = ship.pilot;
    record.kind = @intCast(ship.kind.number());
    record.launch_from = if (ship.gate != null) @intCast(Type.reliant.number()) else std.math.maxInt(u16);
    record._unknown_2a = 0xFF;
    record.launch_gate = ship.gate orelse dte.Ship.no_launch;
    record.runtime_yaw = ship.yaw;
    record.yaw = ship.yaw;
    record.intact_components = dte.Ship.all_intact;
    record.formation_point = dte.Ship.no_formation_point;
    record._unknown_36 = 0xFFFF;
    record.runtime_pitch = ship.pitch;
    record.pitch = ship.pitch;
    const tail = std.mem.asBytes(&record)[@offsetOf(dte.Ship, "_unknown_3c")..][0..ship_tail.len];
    tail.* = ship_tail;
    record.runtime_roll = ship.roll;
    record.roll = ship.roll;
    return record;
}

/// Adds `text` to the string pool, NUL-terminated, and gives the byte offset it starts at.
fn addString(gpa: Allocator, strings: *std.ArrayList(u8), text: []const u8) !u16 {
    const at: u16 = @intCast(strings.items.len);
    try strings.appendSlice(gpa, text);
    try strings.append(gpa, 0);
    return at;
}

/// The order the start part makes the flight groups in: the Reliant's first, which the wing
/// launches from as it is made.
const made = [_]Group{ .reliant, .alpha, .badanov, .sabres, .rocks };

comptime {
    for (std.enums.values(Group)) |group| std.debug.assert(std.mem.indexOfScalar(Group, &made, group) != null);
}

/// The start part: every flight group made, the ejected pilot's odds each as likely, the rocks
/// tumbling, the capital ships' guns held, the launch's music, and the wing's launch. Once the wing
/// is out, the capital ships fly at a crawl, their guns free, the Sabres fight the player and each
/// wingman a Sabre, the mission's music plays, and the landing is cleared.
fn script(gpa: Allocator) ![]u8 {
    var routine: Routine = .init(gpa);
    defer routine.deinit();
    for (made) |group| {
        try routine.op(.push_flight_group, &.{@backingInt(group)});
        try routine.command("CreateFlightGroup");
    }
    // A quiet inspection scene: no weapon fire from any flight group.
    for (made) |group| try disableGuns(&routine, .{ .group = group }, true);
    try routine.op(.push_ship, &.{0});
    try routine.pushConstant(2);
    try routine.command("SetInvulnerability");
    try routine.pushConstant(1);
    try routine.command("OpenInstrument");
    try routine.pushConstant(2);
    try routine.command("OpenInstrument");
    try routine.pushConstant(4);
    try routine.command("OpenInstrument");
    try routine.pushConstant(7);
    try routine.command("OpenInstrument");
    try routine.op(.push_ship, &.{0});
    try routine.op(.push_ship, &.{6});
    try routine.command("SetPlayerTarget");
    try routine.pushConstant(11);
    try routine.command("OpenInstrument");
    // Native mission branches only go forwards. Emit 36 timed transmissions:
    // fifteen minutes of review, then leave the mission running normally.
    for (0..36) |_| {
        try routine.pushString("Rel_Brdge_Off.fm8");
        try routine.pushString("rc_review.ut");
        try routine.pushConstant(0x44); // Matching Bridge Officer name.
        try routine.command("PlayCommsMovie");
        try routine.pushConstant(12);
        try routine.command("Wait");
        try routine.pushConstant(11);
        try routine.command("OpenInstrument");
        try routine.pushConstant(13);
        try routine.command("Wait");
    }
    try routine.op(.push_byte, &.{1});
    try routine.op(.@"return", &.{});

    return routine.finish();
}

/// The game's variable that clears the player's ship to land (`vm.Variables.landing_cleared`).
const landing_cleared = openreliant.engine.vm.Variables.number("landing_cleared");

/// `PlayMusic` of the piece `piece`, once the music playing has faded out.
fn playMusic(routine: *Routine, piece: []const u8) !void {
    try routine.pushString(piece);
    try routine.pushConstant(0);
    try routine.command("PlayMusic");
}

/// What a command names: a ship or a flight group.
const Entity = union(enum) {
    ship: u16,
    group: Group,
};

/// Pushes the ship or the flight group `entity` names, for a command that takes an entity.
fn pushEntity(routine: *Routine, entity: Entity) !void {
    switch (entity) {
        .ship => |ship| try routine.op(.push_ship, &.{@intCast(ship)}),
        .group => |group| try routine.op(.push_flight_group, &.{@backingInt(group)}),
    }
}

/// `SetAI` of `order` on `entity`, aimed at the ship `target`, or at nothing, starting at once.
fn setAI(routine: *Routine, entity: Entity, order: Order, target: ?usize) !void {
    try pushEntity(routine, entity);
    try routine.pushConstant(@intCast(@backingInt(order)));
    try routine.pushConstant(1);
    if (target) |ship| try routine.op(.push_ship, &.{@intCast(ship)}) else try routine.op(.push_null, &.{});
    try routine.command("SetAI");
}

/// `DisableGuns` on `entity`: its guns and turrets held, or free again, as the game's missions give
/// it, the entity and then 1 or 0.
fn disableGuns(routine: *Routine, entity: Entity, disabled: bool) !void {
    try pushEntity(routine, entity);
    try routine.pushConstant(@intFromBool(disabled));
    try routine.command("DisableGuns");
}

/// Writes mission 0's file to the path its argument gives, for the build.
pub fn main(init: std.process.Init) !u8 {
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    if (args.len != 2) {
        std.debug.print("usage: mission0 <output>\n", .{});
        return 2;
    }
    const bytes = try write(init.gpa);
    defer init.gpa.free(bytes);
    try Io.Dir.cwd().writeFile(init.io, .{ .sub_path = args[1], .data = bytes });
    return 0;
}
