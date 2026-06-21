// Gota runner (Java) - YOUR code. This is the file you edit.
//
// It declares the operation(s) to measure and plugs them into the harness. There is
// no timing, batching, or JSON here: run hands your lambda a Gota bencher and the
// buffer, and you call b.bench(name, op) once per operation.
//
//   javac Gota.java Runner.java
//   java Runner [buffer_bytes] [warmup_seconds] [measure_seconds]

public final class Runner {
    static final String IMPL = "example"; // your implementation's name

    public static void main(String[] args) {
        Gota.run(IMPL, args, (b, data) -> {
            // Replace with your real operation(s). Each op closes over `data` and runs
            // the work to measure. Call b.bench once per operation for the table.
            //
            // This example writes `data` in place, which is always observed. If your op
            // instead computes a value, consume it (e.g. `data[0] ^= (byte) result`) so
            // the JIT can't delete the work and you measure nothing.
            b.bench("example", () -> {
                for (int i = 0; i < data.length; i++) {
                    data[i] ^= 0x5A;
                }
            });
        });
    }
}
