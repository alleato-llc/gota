# Gota runner: C++

Files:

- `gota.hpp` — the harness. Copy as-is; do not edit.
- `runner.cpp` — your code. Replace the `example` op.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
c++ -std=c++20 -O2 runner.cpp -o runner
./runner 65536 0.5 2.0
```

The seam: `gota::run(IMPL, argc, argv, [](gota::Bencher& b, std::span<std::uint8_t> data)
{ ... })` parses args, allocates the buffer, and hands your lambda a bencher and the
buffer; you call `b.bench(name, op)` once per operation.

Notes:

- **Header-only, unlike the C template.** C++ has lambdas, so `bench` is a template and
  your op is inlined into the timing loop — the same seam Rust's `impl FnMut()` gives.
  C's function pointer + `void* ctx` is a workaround for a language without closures;
  C++ does not need it, so there is no `gota.cpp`.
- C++20 is required for `std::span`. If you are stuck on C++17, replace the span
  parameter with `std::uint8_t* data, std::size_t n` — nothing else in the harness needs
  it.
- Only the standard library is used (`std::chrono::steady_clock` for timing —
  monotonic, so it never jumps).
- Editors may flag `std::span` if they default to an older standard; the build is what
  matters. Point your tooling at `-std=c++20` (a one-line `.clangd` or
  `compile_commands.json`) if the squiggles bother you.
- The committed example op is deliberately trivial and its throughput is **not**
  comparable to the other templates' example ops — each is just a placeholder to keep
  its template runnable. For a cross-language comparison see [`examples/`](../../examples/),
  where every language runs the same FNV-1a.

History: [`CHANGELOG.md`](CHANGELOG.md) tracks changes to this template; [`VERSIONS.md`](../../VERSIONS.md) lists every component's version.
