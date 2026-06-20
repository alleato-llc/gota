//! Gota runner (Zig 0.16) - YOUR code. This is the file you edit.
//!
//! It declares the operation(s) to measure and plugs them into the harness. There is
//! no timing, batching, or JSON here: `register` receives a `*gota.Bencher` and calls
//! `b.bench(name, op)` once per operation. Each op is `fn([]u8) void` over the buffer.
//!
//!     zig build-exe runner.zig -O ReleaseFast
//!     ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]

const std = @import("std");
const gota = @import("gota.zig");

const IMPL = "example"; // your implementation's name

// Replace with your real operation. It receives the shared buffer.
fn exampleOp(data: []u8) void {
    for (data) |*x| x.* ^= 0x5A;
}

fn register(b: *gota.Bencher) !void {
    try b.bench("example", exampleOp);
}

pub fn main(init: std.process.Init) !void {
    try gota.run(init, IMPL, register);
}
