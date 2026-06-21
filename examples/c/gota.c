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

static int cmp_double(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
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
    /* Per-batch MB/s samples; median vs peak shows run stability. Each measure-phase
     * batch clears ~100ms, so the count is bounded by measure/0.1; size generously. */
    size_t cap = (size_t)(b->measure / 0.05) + 64;
    double *samples = malloc(cap * sizeof(double));
    size_t nsamp = 0;
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
        if (samples && nsamp < cap) {
            samples[nsamp++] = mbps;
        }
        total += batch;
    }
    double median = 0.0;
    if (samples && nsamp > 0) {
        qsort(samples, nsamp, sizeof(double), cmp_double);
        median = nsamp % 2 ? samples[nsamp / 2] : (samples[nsamp / 2 - 1] + samples[nsamp / 2]) / 2;
    }
    free(samples);
    printf("{\"impl\":\"%s\",\"bench\":\"%s\",\"mbps\":%.2f,\"mbps_median\":%.2f,\"iters\":%llu}\n", b->impl, name, best, median, total);
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
