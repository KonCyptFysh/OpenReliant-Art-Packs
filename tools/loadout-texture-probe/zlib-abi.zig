pub const uLong = c_ulong;
pub const uLongf = c_ulong;
pub const Z_OK: c_int = 0;
pub extern "z" fn uncompress2(dest: [*]u8, dest_len: *uLongf, source: [*]const u8, source_len: *uLong) c_int;
