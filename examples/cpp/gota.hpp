// Gota harness (C++20). Copy this file into your project as-is and do not edit it.
//
// It owns the measurement: argument parsing, the buffer, the peak-of-batches timing
// loop, and the JSON output. Your code plugs in through gota::run(impl, argc, argv,
// reg): the harness hands your callable a gota::Bencher and the buffer, and you call
// b.bench(name, op) for each operation. See ../../PROTOCOL.md.
//
// Header-only on purpose. C++ has lambdas, so `bench` is a template and the op is
// inlined into the timing loop — the same seam Rust's `impl FnMut()` gives. The C
// template's function pointer + void* ctx is a workaround for a language without
// closures, and C++ does not need it.
#ifndef GOTA_HPP
#define GOTA_HPP

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <span>
#include <string_view>
#include <vector>

namespace gota {

class Bencher {
public:
    Bencher(std::string_view impl, std::size_t buf_bytes, double warmup, double measure)
        : impl_(impl), buf_bytes_(buf_bytes), warmup_(warmup), measure_(measure) {}

    // Report peak throughput across many batches (the max MB/s is the reproducible
    // rate; jitter only ever slows a batch). The clock is read only at batch
    // boundaries.
    template <typename Op>
    void bench(std::string_view name, Op&& op) {
        auto start = Clock::now();
        while (secs_since(start) < warmup_) {
            op();
        }

        std::uint64_t batch = 1;
        for (;;) {
            start = Clock::now();
            for (std::uint64_t i = 0; i < batch; ++i) {
                op();
            }
            if (secs_since(start) >= 0.1) {
                break;
            }
            batch *= 2;
        }

        double best = 0.0;
        std::uint64_t total = 0;
        std::vector<double> samples;  // per-batch MB/s; median vs peak shows stability
        const auto t0 = Clock::now();
        while (secs_since(t0) < measure_) {
            start = Clock::now();
            for (std::uint64_t i = 0; i < batch; ++i) {
                op();
            }
            const double mbps = static_cast<double>(buf_bytes_) *
                                static_cast<double>(batch) / 1e6 / secs_since(start);
            best = std::max(best, mbps);
            samples.push_back(mbps);
            total += batch;
        }

        std::sort(samples.begin(), samples.end());
        const std::size_t n = samples.size();
        double median = 0.0;
        if (n > 0) {
            median = n % 2 ? samples[n / 2] : (samples[n / 2 - 1] + samples[n / 2]) / 2;
        }

        // %.*s so a string_view needs no null terminator (and no allocation).
        std::printf(
            "{\"impl\":\"%.*s\",\"bench\":\"%.*s\",\"mbps\":%.2f,\"mbps_median\":%.2f,\"iters\":%llu}\n",
            static_cast<int>(impl_.size()), impl_.data(),
            static_cast<int>(name.size()), name.data(),
            best, median, static_cast<unsigned long long>(total));
    }

private:
    using Clock = std::chrono::steady_clock;  // monotonic; never jumps

    static double secs_since(Clock::time_point t) {
        return std::chrono::duration<double>(Clock::now() - t).count();
    }

    std::string_view impl_;
    std::size_t buf_bytes_;
    double warmup_;
    double measure_;
};

// Parse argv (buffer_bytes, warmup_s, measure_s), allocate a zeroed buffer, and call
// reg(bencher, data). Returns a process exit code.
template <typename Reg>
int run(std::string_view impl, int argc, char** argv, Reg&& reg) {
    const std::size_t n =
        argc > 1 ? static_cast<std::size_t>(std::strtoull(argv[1], nullptr, 10)) : 1048576;
    const double warmup = argc > 2 ? std::atof(argv[2]) : 0.5;
    const double measure = argc > 3 ? std::atof(argv[3]) : 2.0;

    std::vector<std::uint8_t> data(n, 0);
    Bencher b(impl, n, warmup, measure);
    reg(b, std::span<std::uint8_t>(data));
    return 0;
}

}  // namespace gota

#endif  // GOTA_HPP
