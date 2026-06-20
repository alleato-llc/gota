//! Gota runner (Rust) - YOUR code. This is the file you edit.
//!
//! It declares the operation(s) to measure and plugs them into the harness. There is
//! no timing, batching, or JSON here: `run` hands you a `&Bencher` and the buffer,
//! and you call `b.bench(name, op)` once per operation.
//!
//! Build with plain rustc (gota.rs is picked up by `mod gota;`), then run:
//!     rustc -O runner.rs -o runner
//!     ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]

mod gota;

const IMPL: &str = "example"; // your implementation's name

fn main() {
    gota::run(IMPL, |b, data| {
        // Replace with your real operation(s). Each op closes over `data` and runs
        // the work to measure. Call b.bench once per operation you want in the table.
        b.bench("example", || {
            for x in data.iter_mut() {
                *x ^= 0x5A;
            }
        });
    });
}
