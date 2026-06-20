# Gota runner: Java

Files:

- `Gota.java` — the harness. Copy as-is; do not edit.
- `Runner.java` — your code. Replace the `example` op.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
javac Gota.java Runner.java
java Runner 65536 0.5 2.0
```

The seam: `Gota.run(IMPL, args, (b, data) -> { ... })` parses args, allocates the
buffer, and hands your lambda a `Gota` bencher and the buffer; you call
`b.bench(name, op)` once per operation.

Notes:

- `main` receives `args`, so the harness can't read them globally; `Gota.run` takes
  `args` as a parameter. The op is the `Gota.Op` functional interface (`void run()`).
- The JVM is warmed up before measuring (the protocol's warmup phase), so the numbers
  reflect JIT-compiled steady state, not interpretation.
- Only the JDK is used (`System.nanoTime()` for timing).
