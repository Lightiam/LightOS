/**
 * @file types.hpp
 * LightRail Native Types
 *
 * Defines the scalar and vector types used by the LightRail C++ tiled
 * pipelining library.  Mirrors the IR ScalarKind enumeration.
 *
 * Supported types:
 *   lr_fp32, lr_fp16, lr_bf16, lr_abfp16, lr_fp8
 *   lr_int32, lr_int16, lr_int8
 *   lr_trit   — balanced ternary element {-1, 0, +1}
 *   lr_analog — analog wave amplitude [0.0, 1.0]
 */

#pragma once
#include <cstdint>
#include <array>
#include <type_traits>

namespace lightrail {

// ---------------------------------------------------------------------------
// Scalar types
// ---------------------------------------------------------------------------

using lr_int8    = int8_t;
using lr_int16   = int16_t;
using lr_int32   = int32_t;
using lr_int64   = int64_t;
using lr_fp32    = float;
using lr_fp64    = double;

// 16-bit floats  (compiler must support __fp16 / __bf16 or fallback to uint16)
#if defined(__ARM_FP16_FORMAT_IEEE) || defined(__FLT16_MAX__)
using lr_fp16 = _Float16;
#else
struct lr_fp16 { uint16_t bits; };
#endif

struct lr_bf16  { uint16_t bits; };   // BFloat16 (truncated fp32)
struct lr_abfp16{ uint16_t bits; };   // LightRail Adaptive BFP16

// FP8 — E4M3 format used on NCE
struct lr_fp8 { uint8_t bits; };

// Balanced ternary trit
struct lr_trit {
    int8_t val;  // must be -1, 0, or +1
    explicit lr_trit(int8_t v = 0) : val(v) {
        // assert(v >= -1 && v <= 1);
    }
    lr_trit operator~()  const { return lr_trit(-val); }
    lr_trit operator+(const lr_trit& o) const {
        int8_t s = val + o.val;
        return lr_trit(s > 1 ? 1 : (s < -1 ? -1 : s));
    }
    lr_trit operator*(const lr_trit& o) const { return lr_trit(val * o.val); }
    bool operator==(const lr_trit& o) const { return val == o.val; }
};

// Analog amplitude [0, 1] mapped to optical power
struct lr_analog {
    float amplitude;  // [0.0, 1.0]
    explicit lr_analog(float a = 0.5f) : amplitude(a) {}
};

// ---------------------------------------------------------------------------
// Vector types (SIMD-width matches WDM channel count)
// ---------------------------------------------------------------------------

template <typename T, int N>
struct alignas(64) lr_vec {
    std::array<T, N> data;

    lr_vec() { data.fill(T{}); }
    explicit lr_vec(T fill_val) { data.fill(fill_val); }

    T&       operator[](int i)       { return data[i]; }
    const T& operator[](int i) const { return data[i]; }

    static constexpr int size() { return N; }
};

// Convenience aliases matching the 64-wavelength WDM width
using lr_vec64_fp32  = lr_vec<lr_fp32,  64>;
using lr_vec64_fp16  = lr_vec<lr_fp16,  64>;
using lr_vec64_bf16  = lr_vec<lr_bf16,  64>;
using lr_vec64_int32 = lr_vec<lr_int32, 64>;
using lr_vec64_trit  = lr_vec<lr_trit,  64>;

// 32-wavelength half-width variants
using lr_vec32_fp32  = lr_vec<lr_fp32,  32>;
using lr_vec32_trit  = lr_vec<lr_trit,  32>;

}  // namespace lightrail
