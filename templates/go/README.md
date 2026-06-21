# Gota runner: Go

Files:

- `go.mod` + `gota/gota.go` — the harness (its own package). Copy as-is; do not edit
  `gota.go`. Rename the module in `go.mod` if you vendor it elsewhere.
- `runner.go` — your code (package `main`). Replace the `example` op.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
go build -o runner .
./runner 65536 0.5 2.0
```

The seam: `gota.Run(impl, func(b *gota.Bencher, data []byte) { ... })` parses args,
allocates the buffer, and hands your closure the bencher and buffer; you call
`b.Bench(name, op)` once per operation.

Notes:

- The harness is a separate package (`gota`) precisely so your `main` imports it
  rather than sharing a file with it; that is the decoupling. A `go.mod` is the
  lightest way to make that import resolve.
- Only the standard library is used (`time` for the clock).

History: [`CHANGELOG.md`](CHANGELOG.md) tracks changes to this template; [`VERSIONS.md`](../../VERSIONS.md) lists every component's version.
