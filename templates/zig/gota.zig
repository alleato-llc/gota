//! Gota harness (Zig 0.16). Copy this file into your project as-is and do not edit it.
//!
//! It owns the measurement: argument parsing, the buffer, the peak-of-batches timing
//! loop, and the JSON output. Your code plugs in through `run(init, impl, register)`:
//! the harness hands your register a `*Bencher`, and you call `b.bench(name, op)` for
//! each operation, where `op` is `fn([]u8) void` over the shared buffer. See
//! ../../PROTOCOL.md.
//!
//! Zig 0.16 notes (see the dorado port's DEVELOPMENT.md): `std.process.argsAlloc` and
//! `std.time.Timer` are gone; args arrive via `std.process.Init`, the clock is
//! `std.Io.Clock`, and the buffered stdout writer must be flushed before exit.

const std = @import("std");

pub const Bencher = struct {
    io: std.Io,
    impl: []const u8,
    buf_bytes: usize,
    warmup: f64,
    measure: f64,
    data: []u8,
    w: *std.Io.Writer,

    fn nowS(self: *Bencher) f64 {
        const ns: i96 = std.Io.Clock.now(.awake, self.io).toNanoseconds();
        return @as(f64, @floatFromInt(ns)) / 1e9;
    }

    // Report peak throughput across many batches (max MB/s is the reproducible rate;
    // jitter only ever slows a batch). The clock is read only at batch boundaries,
    // which matters since Zig's Io clock is costlier than a raw monotonic read.
    pub fn bench(self: *Bencher, name: []const u8, op: *const fn ([]u8) void) !void {
        const wstart = self.nowS();
        while (self.nowS() - wstart < self.warmup) op(self.data);

        var batch: u64 = 1;
        while (true) {
            const start = self.nowS();
            var i: u64 = 0;
            while (i < batch) : (i += 1) op(self.data);
            if (self.nowS() - start >= 0.1) break;
            batch *= 2;
        }

        var best: f64 = 0;
        var total: u64 = 0;
        const t0 = self.nowS();
        while (self.nowS() - t0 < self.measure) {
            const start = self.nowS();
            var i: u64 = 0;
            while (i < batch) : (i += 1) op(self.data);
            const mbps = @as(f64, @floatFromInt(self.buf_bytes)) * @as(f64, @floatFromInt(batch)) / 1e6 / (self.nowS() - start);
            if (mbps > best) best = mbps;
            total += batch;
        }
        try self.w.print("{{\"impl\":\"{s}\",\"bench\":\"{s}\",\"mbps\":{d:.2},\"iters\":{d}}}\n", .{ self.impl, name, best, total });
    }
};

pub fn run(init: std.process.Init, impl: []const u8, comptime register: fn (*Bencher) anyerror!void) !void {
    const a = init.gpa;
    const io = init.io;

    var args: std.ArrayList([]const u8) = .empty;
    defer args.deinit(a);
    var it = std.process.Args.Iterator.init(init.minimal.args);
    while (it.next()) |arg| try args.append(a, arg);

    const buf_bytes: usize = if (args.items.len > 1) try std.fmt.parseInt(usize, args.items[1], 10) else 1048576;
    const warmup: f64 = if (args.items.len > 2) try std.fmt.parseFloat(f64, args.items[2]) else 0.5;
    const measure: f64 = if (args.items.len > 3) try std.fmt.parseFloat(f64, args.items[3]) else 2.0;

    const data = try a.alloc(u8, buf_bytes);
    defer a.free(data);
    @memset(data, 0);

    var stdout = std.Io.File.stdout();
    var wbuf: [4096]u8 = undefined;
    var fw = stdout.writer(io, &wbuf);

    var b = Bencher{
        .io = io,
        .impl = impl,
        .buf_bytes = buf_bytes,
        .warmup = warmup,
        .measure = measure,
        .data = data,
        .w = &fw.interface,
    };
    try register(&b);
    try fw.interface.flush();
}
