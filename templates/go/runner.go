// Gota runner (Go) - YOUR code. This is the file you edit.
//
// It declares the operation(s) to measure and plugs them into the harness. There is
// no timing, batching, or JSON here: Run hands your closure a *gota.Bencher and the
// buffer, and you call b.Bench(name, op) once per operation.
//
//	go build -o runner . && ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]
package main

import "gotaexample/gota"

const impl = "example" // your implementation's name

func main() {
	gota.Run(impl, func(b *gota.Bencher, data []byte) {
		// Replace with your real operation(s). Each op closes over `data` and runs
		// the work to measure. Call b.Bench once per operation you want in the table.
		//
		// This example writes `data` in place, which is always observed. If your op
		// instead computes a value, consume it (e.g. `data[0] ^= byte(result)`) or the
		// compiler may delete the work and you measure nothing.
		b.Bench("example", func() {
			for i := range data {
				data[i] ^= 0x5A
			}
		})
	})
}
