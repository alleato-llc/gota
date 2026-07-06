// Gota runner (Swift) - YOUR code. This is the file you edit.
//
// It declares the operation(s) to measure and plugs them into the harness. There is
// no timing, batching, or JSON here: run hands your closure a Gota bencher and the
// buffer, and you call b.bench(name, op) once per operation.
//
//   swiftc -O Gota.swift runner.swift -o runner
//   ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]

@main
struct Runner {
    static let impl = "example"  // your implementation's name

    static func main() {
        Gota.run(impl) { b, data in
            // Replace with your real operation(s). Each op closes over `data` and runs
            // the work to measure. Call b.bench once per operation for the table.
            //
            // This example writes `data` in place, which is always observed. If your op
            // instead computes a value, consume it (e.g. `data[0] ^= UInt8(
            // truncatingIfNeeded: result)`) so `swiftc -O` can't delete the work and
            // you measure nothing.
            b.bench("example") {
                for i in data.indices {
                    data[i] ^= 0x5A
                }
            }
        }
    }
}
