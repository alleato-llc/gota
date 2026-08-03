// Package gota is the Gota harness (Go). Copy this package into your project as-is
// and do not edit it. It owns the measurement: argument parsing, the buffer, the
// peak-of-batches timing loop, and the JSON output. Your code plugs in through
// Run(impl, register): the harness hands your register a *Bencher and the buffer, and
// you call b.Bench(name, op) for each operation. See ../../../PROTOCOL.md.
package gota

import (
	"fmt"
	"os"
	"sort"
	"strconv"
	"time"
)

type Bencher struct {
	Impl     string
	BufBytes int
	Warmup   time.Duration
	Measure  time.Duration
}

// Bench reports peak throughput across many batches (max MB/s is the reproducible
// rate; jitter only ever slows a batch). The clock is read only at batch boundaries.
func (b *Bencher) Bench(name string, op func()) {
	start := time.Now()
	for time.Since(start) < b.Warmup {
		op()
	}
	var batch uint64 = 1
	for {
		start = time.Now()
		for i := uint64(0); i < batch; i++ {
			op()
		}
		if time.Since(start) >= 100*time.Millisecond {
			break
		}
		batch *= 2
	}
	best := 0.0
	var total uint64
	var samples []float64 // per-batch MB/s; median vs peak shows run stability
	t0 := time.Now()
	for time.Since(t0) < b.Measure {
		start = time.Now()
		for i := uint64(0); i < batch; i++ {
			op()
		}
		mbps := float64(b.BufBytes) * float64(batch) / 1e6 / time.Since(start).Seconds()
		if mbps > best {
			best = mbps
		}
		samples = append(samples, mbps)
		total += batch
	}
	sort.Float64s(samples)
	median := 0.0
	if n := len(samples); n > 0 {
		if n%2 == 1 {
			median = samples[n/2]
		} else {
			median = (samples[n/2-1] + samples[n/2]) / 2
		}
	}
	fmt.Printf("{\"impl\":\"%s\",\"bench\":\"%s\",\"mbps\":%.2f,\"mbps_median\":%.2f,\"iters\":%d,\"protocol\":\"1.2.0\"}\n", b.Impl, name, best, median, total)
}

// Run parses argv (buffer_bytes, warmup_s, measure_s), allocates a buffer, and calls
// register with a Bencher and that buffer.
func Run(impl string, register func(b *Bencher, data []byte)) {
	bufBytes := 1048576
	warmup := 0.5
	measure := 2.0
	if len(os.Args) > 1 {
		bufBytes, _ = strconv.Atoi(os.Args[1])
	}
	if len(os.Args) > 2 {
		warmup, _ = strconv.ParseFloat(os.Args[2], 64)
	}
	if len(os.Args) > 3 {
		measure, _ = strconv.ParseFloat(os.Args[3], 64)
	}
	b := &Bencher{
		Impl:     impl,
		BufBytes: bufBytes,
		Warmup:   time.Duration(warmup * float64(time.Second)),
		Measure:  time.Duration(measure * float64(time.Second)),
	}
	register(b, make([]byte, bufBytes))
}
