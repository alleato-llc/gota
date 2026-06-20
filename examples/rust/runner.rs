//! Example Gota runner (Rust): FNV-1a over the buffer. See ../README.md.
//!     rustc -O runner.rs -o runner

mod gota;

const IMPL: &str = "rust";

fn main() {
    gota::run(IMPL, |b, data| {
        b.bench("fnv1a-64", || {
            let mut h: u64 = 0xcbf2_9ce4_8422_2325;
            for &x in data.iter() {
                h = (h ^ x as u64).wrapping_mul(0x0000_0100_0000_01b3);
            }
            data[0] ^= h as u8; // sink: consume h
        });
    });
}
