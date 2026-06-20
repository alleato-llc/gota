/* Gota harness (C, C17) - implementation. Copy as-is and do not edit. */
#include "gota.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static double now_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

/* Report peak throughput across many batches (the max MB/s is the reproducible rate;
 * jitter only ever slows a batch). The clock is read only at batch boundaries. */
void gota_bench(const gota_bencher *b, const char *name, void (*op)(void *), void *ctx) {
    double start = now_s();
    while (now_s() - start < b->warmup) {
        op(ctx);
    }
    unsigned long long batch = 1;
    for (;;) {
        start = now_s();
        for (unsigned long long i = 0; i < batch; i++) {
            op(ctx);
        }
        if (now_s() - start >= 0.1) {
            break;
        }
        batch *= 2;
    }
    double best = 0.0;
    unsigned long long total = 0;
    double t0 = now_s();
    while (now_s() - t0 < b->measure) {
        start = now_s();
        for (unsigned long long i = 0; i < batch; i++) {
            op(ctx);
        }
        double mbps = (double)b->buf_bytes * (double)batch / 1e6 / (now_s() - start);
        if (mbps > best) {
            best = mbps;
        }
        total += batch;
    }
    printf("{\"impl\":\"%s\",\"bench\":\"%s\",\"mbps\":%.2f,\"iters\":%llu}\n", b->impl, name, best, total);
}

int gota_run(const char *impl, int argc, char **argv,
             void (*reg)(const gota_bencher *b, unsigned char *data, size_t n)) {
    size_t n = argc > 1 ? (size_t)strtoull(argv[1], NULL, 10) : 1048576;
    double warmup = argc > 2 ? atof(argv[2]) : 0.5;
    double measure = argc > 3 ? atof(argv[3]) : 2.0;

    unsigned char *data = calloc(n, 1);
    if (!data) {
        return 1;
    }
    gota_bencher b = {impl, n, warmup, measure};
    reg(&b, data, n);
    free(data);
    return 0;
}
