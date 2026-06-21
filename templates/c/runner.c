/* Gota runner (C) - YOUR code. This is the file you edit.
 *
 * It declares the operation(s) to measure and plugs them into the harness. There is
 * no timing, batching, or JSON here: `reg` receives the bencher and buffer and calls
 * gota_bench once per operation. The op gets its data through a small context struct.
 *
 *     cc -std=c17 -O2 runner.c gota.c -o runner
 *     ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]
 */
#include "gota.h"

#include <stddef.h>

#define IMPL "example"

typedef struct {
    unsigned char *data;
    size_t n;
} ctx_t;

/* Replace with your real operation. It receives the context you passed to gota_bench.
 * This example writes the buffer in place, which is always observed. If your op instead
 * computes a value, consume it (e.g. `c->data[0] ^= (unsigned char)result`) or -O2 may
 * delete the work and you measure nothing. */
static void example_op(void *vctx) {
    ctx_t *c = (ctx_t *)vctx;
    for (size_t i = 0; i < c->n; i++) {
        c->data[i] ^= 0x5A;
    }
}

static void reg(const gota_bencher *b, unsigned char *data, size_t n) {
    ctx_t c = {data, n};
    gota_bench(b, "example", example_op, &c);
}

int main(int argc, char **argv) {
    return gota_run(IMPL, argc, argv, reg);
}
