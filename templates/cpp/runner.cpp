// Gota runner (C++) - YOUR code. This is the file you edit.
//
// It declares the operation(s) to measure and plugs them into the harness. There is
// no timing, batching, or JSON here: run hands your lambda a gota::Bencher and the
// buffer, and you call b.bench(name, op) once per operation.
//
//     c++ -std=c++20 -O2 runner.cpp -o runner
//     ./runner [buffer_bytes] [warmup_seconds] [measure_seconds]
#include "gota.hpp"

#include <cstdint>
#include <span>
#include <string_view>

namespace {
constexpr std::string_view IMPL = "example";  // your implementation's name
}

int main(int argc, char** argv) {
    return gota::run(IMPL, argc, argv,
                     [](gota::Bencher& b, std::span<std::uint8_t> data) {
        // Replace with your real operation(s). Each op captures `data` and runs the
        // work to measure. Call b.bench once per operation for the table.
        //
        // This example writes `data` in place, which is always observed. If your op
        // instead computes a value, consume it (e.g. `data[0] ^= (std::uint8_t)result`)
        // or -O2 may delete the work and you measure nothing.
        b.bench("example", [&] {
            for (auto& byte : data) {
                byte ^= 0x5A;
            }
        });
    });
}
