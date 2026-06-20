# Gota runner: Python

Files:

- `gota.py` — the harness. Copy as-is; do not edit.
- `runner.py` — your code. Replace the `example` op in `register`.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
python3 runner.py 65536 0.5 2.0
```

The seam: `gota.run(IMPL, register)` parses args, allocates the buffer, and calls your
`register(b, data)`; you call `b.bench(name, op)` once per operation. The op closes
over `data` and never touches the clock or output.

Notes:

- Pure-Python loops are slow by a large factor; that is expected and is exactly the
  kind of thing the comparison is meant to show. If your real op delegates to a C
  extension, you are measuring that extension, not Python.
- No third-party packages are needed.
