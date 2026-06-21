// Example Gota runner (Java): FNV-1a over the buffer. See ../README.md.
//   javac Gota.java Runner.java && java Runner [buffer_bytes] [warmup_s] [measure_s]
public final class Runner {
    public static void main(String[] args) {
        Gota.run("java", args, (b, data) -> {
            b.bench("fnv1a-64", () -> {
                long h = 0xcbf29ce484222325L;
                for (byte x : data) {
                    h = (h ^ (x & 0xffL)) * 0x100000001b3L;
                }
                data[0] ^= (byte) h; // sink: consume h
            });
        });
    }
}
