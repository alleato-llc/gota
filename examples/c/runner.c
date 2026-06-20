/* Example Gota runner (C): FNV-1a over the buffer. See ../README.md. */
#include "gota.h"

#include <stddef.h>
#include <stdint.h>

#define IMPL "c"

typedef struct {
    unsigned char *data;
    size_t n;
} ctx_t;

static void fnv1a(void *vctx) {
    ctx_t *c = (ctx_t *)vctx;
    uint64_t h = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < c->n; i++) {
        h = (h ^ c->data[i]) * 0x100000001b3ULL;
    }
    c->data[0] ^= (unsigned char)h; /* sink: consume h */
}

static void reg(const gota_bencher *b, unsigned char *data, size_t n) {
    ctx_t c = {data, n};
    gota_bench(b, "fnv1a-64", fnv1a, &c);
}

int main(int argc, char **argv) {
    return gota_run(IMPL, argc, argv, reg);
}
