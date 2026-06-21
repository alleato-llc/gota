# Gota runner: Haskell

Files:

- `Gota.hs` — the harness. Copy as-is; do not edit. (Capitalised because GHC requires the
  filename to match the module name `Gota`.)
- `runner.hs` — your code. Replace the `example` op in the `run` closure.

Build and run (args: `[buffer_bytes] [warmup_s] [measure_s]`, defaults `1048576 0.5 2.0`):

```
ghc -O2 runner.hs -o runner
./runner 65536 0.5 2.0
```

`ghc -O2 runner.hs` picks up `Gota.hs` sitting beside `runner.hs` (it chases the import),
so plain `ghc` is enough — no Cabal or Stack project. Everything it uses ships with GHC
(`base` for the clock/args/printf, the `bytestring` boot library for the buffer); there
are no extra dependencies.

The seam: `run "impl" (\b buf -> ...)` parses args, allocates a zeroed `ByteString`, and
hands your callback a `Bencher` and that buffer; you call `bench b name op` once per op.

The op type is the language-forced variation: **`op :: Word64 -> Word64`**. It takes the
running accumulator and returns a result; the harness forces that result and feeds it
into the next call.

Notes:

- **Why the accumulator.** Haskell is lazy: a computed value is a thunk that is never
  evaluated unless something forces it, and a result that does not vary can be computed
  once and shared. Either way you would measure *nothing*. Threading each op's result
  into the next call (and forcing it) makes the input vary per call, so the work can be
  neither deferred nor shared — this is the dead-code-elimination/sink hazard from
  `PROTOCOL.md` in lazy clothing. The example seeds its FNV-1a fold with the accumulator
  for exactly this reason.
- **Read-only buffer.** The buffer is an immutable `ByteString`, which suits gota's usual
  ops (hashes, checksums, reductions via strict folds like `BS.foldl'`). An in-place
  transform would use a mutable buffer (e.g. `Data.Array.IO` / a `Ptr`) instead.
- Building leaves `*.hi`/`*.o` files beside the sources; they are ignored by `.gitignore`.

History: [`CHANGELOG.md`](CHANGELOG.md) tracks changes to this template; [`VERSIONS.md`](../../VERSIONS.md) lists every component's version.
