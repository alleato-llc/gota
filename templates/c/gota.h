/* Gota harness (C, C17) - public interface. Copy gota.h + gota.c into your project
 * as-is and do not edit them. Your code (runner.c) plugs in through gota_run: the
 * harness parses args, allocates the buffer, and calls your register function, which
 * calls gota_bench(b, name, op, ctx) for each operation. See ../../PROTOCOL.md. */
#ifndef GOTA_H
#define GOTA_H

#include <stddef.h>

typedef struct {
    const char *impl;
    size_t buf_bytes;
    double warmup;
    double measure;
} gota_bencher;

/* Time `op(ctx)` under the peak-of-batches protocol and print one JSON line. */
void gota_bench(const gota_bencher *b, const char *name, void (*op)(void *), void *ctx);

/* Parse argv (buffer_bytes, warmup_s, measure_s), allocate a zeroed buffer, and call
 * `reg(b, data, n)`. Returns a process exit code. */
int gota_run(const char *impl, int argc, char **argv,
             void (*reg)(const gota_bencher *b, unsigned char *data, size_t n));

#endif /* GOTA_H */
