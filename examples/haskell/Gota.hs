{-# LANGUAGE BangPatterns #-}

-- | Gota harness (Haskell). Copy this file into your project as-is and do not edit it.
--
-- It owns the measurement: argument parsing, the buffer, the peak-of-batches timing
-- loop, and the JSON output. Your code plugs in through @run@ / @bench@: the harness
-- hands your register a 'Bencher' and a read-only 'BS.ByteString' buffer, and you call
-- @bench b name op@ for each operation. See ../../PROTOCOL.md.
--
-- The op type is the language-forced variation here: @op :: Word64 -> Word64@ takes the
-- running accumulator and returns its result. In a lazy language a computed value is a
-- thunk that is never evaluated unless forced, and a result that does not vary can be
-- shared (computed once). So the harness threads each op's result into the next call and
-- forces it: that makes the work real every iteration (it cannot be deferred or shared)
-- — Haskell's laziness is the dead-code-elimination/sink hazard in another guise.
--
-- Build with plain ghc (it picks up this module from runner.hs):
--     ghc -O2 runner.hs -o runner
module Gota (Bencher, run, bench) where

import Control.Exception (evaluate)
import Data.List (sort)
import Data.Word (Word64)
import GHC.Clock (getMonotonicTimeNSec)
import System.Environment (getArgs)
import System.IO (BufferMode (LineBuffering), hSetBuffering, stdout)
import Text.Printf (printf)
import qualified Data.ByteString as BS

data Bencher = Bencher
  { bImpl     :: String
  , bBufBytes :: Int
  , bWarmup   :: Double
  , bMeasure  :: Double
  }

-- Monotonic clock in seconds (read only at batch boundaries).
nowS :: IO Double
nowS = do
  ns <- getMonotonicTimeNSec
  pure (fromIntegral ns / 1e9)

-- Fold @op@ over a threaded accumulator @n@ times, strictly. Threading each result into
-- the next call (and forcing it with @!acc@) is what makes the work real: the input
-- varies per call, so GHC can neither leave it a thunk nor share one computation.
runBatch :: Int -> (Word64 -> Word64) -> Word64 -> Word64
runBatch n op = go n
  where
    go 0 !acc = acc
    go k !acc = go (k - 1) (op acc)

-- | Report peak throughput across many batches (the max MB/s is the reproducible rate;
-- jitter only ever slows a batch) plus the median of the per-batch rates as a stability
-- signal. The batch grows until one clears ~100ms; the clock is read at batch boundaries.
bench :: Bencher -> String -> (Word64 -> Word64) -> IO ()
bench b name op = do
  -- warm up
  wStart <- nowS
  let warmLoop !acc = do
        t <- nowS
        if t - wStart < bWarmup b then warmLoop (op acc) else pure acc
  acc0 <- warmLoop 0
  -- size a batch until one clears ~100ms
  let grow !batch !acc = do
        s <- nowS
        let !acc' = runBatch batch op acc
        e <- nowS
        if e - s >= 0.1 then pure (batch, acc') else grow (batch * 2) acc'
  (batch, acc1) <- grow 1 acc0
  -- measure: collect each batch's MB/s, report peak + median
  let bytes = fromIntegral (bBufBytes b) :: Double
      mbpsOf dt = bytes * fromIntegral batch / 1e6 / dt
  t0 <- nowS
  let loop !best !total samples !acc = do
        s <- nowS
        let !acc' = runBatch batch op acc
        e <- nowS
        let !m = mbpsOf (e - s)
        if e - t0 < bMeasure b
          then loop (max best m) (total + batch) (m : samples) acc'
          else pure (max best m, total + batch, m : samples, acc')
  (best, total, samples, accFinal) <- loop 0 0 [] acc1
  _ <- evaluate accFinal -- so the last result is not dead-code-eliminated
  let sorted = sort samples
      n = length sorted
      median
        | n == 0    = 0
        | odd n     = sorted !! (n `div` 2)
        | otherwise = (sorted !! (n `div` 2 - 1) + sorted !! (n `div` 2)) / 2
  printf
    "{\"impl\":\"%s\",\"bench\":\"%s\",\"mbps\":%.2f,\"mbps_median\":%.2f,\"iters\":%d,\"protocol\":\"1.2.0\"}\n"
    (bImpl b) name (best :: Double) (median :: Double) (total :: Int)

-- | Parse argv (buffer_bytes, warmup_s, measure_s), allocate a zeroed buffer, and call
-- @register b buf@.
run :: String -> (Bencher -> BS.ByteString -> IO ()) -> IO ()
run implName register = do
  hSetBuffering stdout LineBuffering
  args <- getArgs
  let argAt i d = if length args > i then read (args !! i) else d
      n  = argAt 0 1048576 :: Int
      wu = argAt 1 0.5 :: Double
      ms = argAt 2 2.0 :: Double
  register (Bencher implName n wu ms) (BS.replicate n 0)
