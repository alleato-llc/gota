{-# LANGUAGE BangPatterns #-}

-- | Example Gota runner (Haskell): FNV-1a over the buffer. See ../README.md.
--     ghc -O2 runner.hs -o runner && ./runner [buffer_bytes] [warmup_s] [measure_s]
--
-- The op is @Word64 -> Word64@: it folds the buffer with FNV-1a, seeded by the running
-- accumulator. The harness forces and re-feeds that result, so laziness can neither
-- defer the work (a thunk) nor share one computation across calls.
import Data.Bits (xor)
import Data.Word (Word64)
import Gota (bench, run)
import qualified Data.ByteString as BS

main :: IO ()
main = run "haskell" $ \b buf ->
  bench b "fnv1a-64" $ \seed ->
    BS.foldl' (\acc x -> (acc `xor` fromIntegral x) * 0x100000001b3) seed buf
