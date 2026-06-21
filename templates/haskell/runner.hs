{-# LANGUAGE BangPatterns #-}

-- | Gota runner (Haskell) - YOUR code. This is the file you edit.
--
-- It declares the operation(s) to measure and plugs them into the harness. There is no
-- timing, batching, or JSON here: @run@ hands you a 'Bencher' and the buffer, and you
-- call @bench b name op@ once per operation.
--
-- The op is @Word64 -> Word64@: it takes the running accumulator and returns a result.
-- The harness forces and re-feeds that result, so the work can be neither deferred (left
-- a thunk) nor shared (computed once) — in Haskell, laziness is the sink hazard, and
-- seeding the op with the accumulator is how you defeat it. Read-only ops (hashes,
-- checksums, reductions) fit a 'BS.ByteString' buffer naturally; an in-place transform
-- would use a mutable buffer instead.
--
--     ghc -O2 runner.hs -o runner
--     ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]
import Data.Bits (xor)
import Data.Word (Word64)
import Gota (bench, run)
import qualified Data.ByteString as BS

main :: IO ()
main = run "example" $ \b buf ->
  -- Replace with your real operation(s). This example folds the buffer with FNV-1a,
  -- seeded by the accumulator so each call does the full work over `buf`.
  bench b "example" $ \seed ->
    BS.foldl' (\acc x -> (acc `xor` fromIntegral x) * 0x100000001b3) seed buf
