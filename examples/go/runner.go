// Example Gota runner (Go): FNV-1a over the buffer. See ../README.md.
package main

import "gotaexample/gota"

const impl = "go"

func main() {
	gota.Run(impl, func(b *gota.Bencher, data []byte) {
		b.Bench("fnv1a-64", func() {
			var h uint64 = 0xcbf29ce484222325
			for _, x := range data {
				h = (h ^ uint64(x)) * 0x100000001b3
			}
			data[0] ^= byte(h) // sink: consume h
		})
	})
}
