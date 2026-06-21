// Example Gota runner (Zig): FNV-1a over the buffer. See ../README.md.
//   zig build-exe runner.zig -O ReleaseFast && ./runner [buffer_bytes] [warmup_s] [measure_s]
const std = @import("std");
const gota = @import("gota.zig");

fn fnv1a(data: []u8) void {
    var h: u64 = 0xcbf29ce484222325;
    for (data) |x| h = (h ^ @as(u64, x)) *% 0x100000001b3;
    data[0] ^= @truncate(h); // sink: consume h
}

fn register(b: *gota.Bencher) !void {
    try b.bench("fnv1a-64", fnv1a);
}

pub fn main(init: std.process.Init) !void {
    try gota.run(init, "zig", register);
}
