# Gota runner: Rust

Files:

- `gota.rs` — the harness. Copy as-is; do not edit.
- `runner.rs` — your code. Replace the `example` op in the `run` closure.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
rustc -O runner.rs -o runner
./runner 65536 0.5 2.0
```

The seam: `gota::run(IMPL, |b, data| { ... })` parses args, allocates the buffer, and
hands your closure a `&Bencher` and `&mut Vec<u8>`; you call `b.bench(name, op)` once
per operation.

Notes:

- `mod gota;` picks up `gota.rs` sitting beside `runner.rs`, so plain `rustc` is
  enough; no Cargo project is required for the template.
- In a real consumer you would instead make this a Cargo binary that depends on your
  crate, keeping `gota.rs` as a module (or a small internal crate).
- Each `bench` call borrows `data` mutably for the duration of that call, which is why
  the seam is one imperative `b.bench(...)` per op rather than a returned list of ops.
