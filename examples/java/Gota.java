// Gota harness (Java). Copy this file into your project as-is and do not edit it.
//
// It owns the measurement: argument parsing, the buffer, the peak-of-batches timing
// loop, and the JSON output. Your code plugs in through Gota.run(impl, args,
// register): the harness hands your Register a Gota bencher and the buffer, and you
// call b.bench(name, op) for each operation. See ../../PROTOCOL.md.

import java.util.ArrayList;
import java.util.Collections;

public final class Gota {

    public interface Op {
        void run();
    }

    public interface Register {
        void register(Gota b, byte[] data);
    }

    private final String impl;
    private final int bufBytes;
    private final double warmup;
    private final double measure;

    private Gota(String impl, int bufBytes, double warmup, double measure) {
        this.impl = impl;
        this.bufBytes = bufBytes;
        this.warmup = warmup;
        this.measure = measure;
    }

    // Report peak throughput across many batches (max MB/s is the reproducible rate;
    // jitter only ever slows a batch). The clock is read only at batch boundaries.
    public void bench(String name, Op op) {
        long start = System.nanoTime();
        while ((System.nanoTime() - start) / 1e9 < warmup) {
            op.run();
        }
        long batch = 1;
        while (true) {
            start = System.nanoTime();
            for (long i = 0; i < batch; i++) {
                op.run();
            }
            if ((System.nanoTime() - start) / 1e9 >= 0.1) {
                break;
            }
            batch *= 2;
        }
        double best = 0.0;
        long total = 0;
        ArrayList<Double> samples = new ArrayList<>(); // per-batch MB/s; median vs peak shows stability
        long t0 = System.nanoTime();
        while ((System.nanoTime() - t0) / 1e9 < measure) {
            start = System.nanoTime();
            for (long i = 0; i < batch; i++) {
                op.run();
            }
            double mbps = (double) bufBytes * batch / 1e6 / ((System.nanoTime() - start) / 1e9);
            if (mbps > best) {
                best = mbps;
            }
            samples.add(mbps);
            total += batch;
        }
        Collections.sort(samples);
        int n = samples.size();
        double median = n == 0 ? 0.0
                : (n % 2 == 1 ? samples.get(n / 2) : (samples.get(n / 2 - 1) + samples.get(n / 2)) / 2);
        System.out.printf("{\"impl\":\"%s\",\"bench\":\"%s\",\"mbps\":%.2f,\"mbps_median\":%.2f,\"iters\":%d,\"protocol\":\"1.2.0\"}%n", impl, name, best, median, total);
    }

    public static void run(String impl, String[] args, Register reg) {
        int bufBytes = args.length > 0 ? Integer.parseInt(args[0]) : 1048576;
        double warmup = args.length > 1 ? Double.parseDouble(args[1]) : 0.5;
        double measure = args.length > 2 ? Double.parseDouble(args[2]) : 2.0;
        Gota b = new Gota(impl, bufBytes, warmup, measure);
        reg.register(b, new byte[bufBytes]);
    }
}
