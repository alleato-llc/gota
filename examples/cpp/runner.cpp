// Example Gota runner (C++): FNV-1a over the buffer. See ../README.md.
#include "gota.hpp"

#include <cstdint>
#include <span>
#include <string_view>

namespace {
constexpr std::string_view IMPL = "cpp";
}

int main(int argc, char** argv) {
    return gota::run(IMPL, argc, argv,
                     [](gota::Bencher& b, std::span<std::uint8_t> data) {
        b.bench("fnv1a-64", [&] {
            std::uint64_t h = 0xcbf29ce484222325ULL;
            for (const std::uint8_t x : data) {
                h = (h ^ x) * 0x100000001b3ULL;
            }
            data[0] ^= static_cast<std::uint8_t>(h);  // sink: consume h
        });
    });
}
