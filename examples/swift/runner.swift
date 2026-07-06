// Example Gota runner (Swift): FNV-1a over the buffer. See ../README.md.
//   swiftc -O Gota.swift runner.swift -o runner && ./runner [buffer_bytes] [warmup_s] [measure_s]

@main
struct Runner {
    static func main() {
        Gota.run("swift") { b, data in
            b.bench("fnv1a-64") {
                var h: UInt64 = 0xcbf2_9ce4_8422_2325
                for x in data {
                    h = (h ^ UInt64(x)) &* 0x0000_0100_0000_01b3
                }
                data[0] ^= UInt8(truncatingIfNeeded: h)  // sink: consume h
            }
        }
    }
}
