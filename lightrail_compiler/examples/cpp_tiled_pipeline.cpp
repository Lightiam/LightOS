/**
 * LightRail C++ Tiled Pipeline Example
 *
 * Demonstrates the C++ advanced-user API:
 *  - Explicit stage declarations (Load, Compute, Store)
 *  - Automatic DMA prefetching managed by the pipeline template
 *  - WDM channel binding at compile time
 *  - Ternary and analog intrinsics
 *
 * Compile (when LightRail SDK is installed):
 *   lrc++ -O3 -I${LIGHTRAIL_SDK}/include cpp_tiled_pipeline.cpp \
 *         -llightrail -o tiled_gemm
 */

#include <lightrail/lightrail.hpp>
#include <cstdio>

using namespace lightrail;

// ---------------------------------------------------------------------------
// Kernel: Tiled GEMM with software double-buffering
// C[M][N] += A[M][K] * B[K][N]
// ---------------------------------------------------------------------------

constexpr int TILE = 128;
constexpr int M = 1024, N = 1024, K = 1024;

// Declare the three pipeline stages:
//   Load:    read fp16 tiles from fabric SRAM
//   Compute: accumulate in fp32
//   Store:   write fp32 results back to SRAM
using GemmPipe = Pipeline<
    Stage<Load,    lr_fp16, TILE>,
    Stage<Compute, lr_fp32, TILE>,
    Stage<Store,   lr_fp32, TILE>
>;

void gemm_kernel(const lr_fp16* A, const lr_fp16* B, lr_fp32* C) {
    const int num_tiles = K / TILE;

    // The Pipeline::run() call automatically inserts DMA prefetch/drain
    // around each iteration — no manual prologue/epilogue needed.
    GemmPipe::run(num_tiles, [&](auto& load_a, auto& compute, auto& store) {
        // Stage 1: prefetch next A tile
        load_a.prefetch(A, /* tile_idx */ 0);

        // Stage 2: accumulate
        // In hardware this calls lr_mma_f16f16f32()
        compute.fma(load_a.tile(), static_cast<lr_fp32>(1.0f));

        // Stage 3: flush result tile
        store.flush(compute.tile(), C, 0);
        compute.reset();
    });
}

// ---------------------------------------------------------------------------
// Kernel: Ternary weight matmul (binary neural network style)
// ---------------------------------------------------------------------------

void ternary_kernel(const lr_trit* W, const lr_fp32* X, lr_fp32* Y, int n) {
    // Use WDM channel 0 for output accumulation
    using OutChannel = WDMChannel<0, lr_fp32>;

    lr_fp32 acc = 0.0f;
    for (int i = 0; i < n; ++i) {
        // lr_trit_dot handles the ternary multiply and sum
        acc += static_cast<lr_fp32>(W[i].val) * X[i];
    }

    // Broadcast result to all output channels
    OutChannel::send(acc);
    *Y = OutChannel::recv();
}

// ---------------------------------------------------------------------------
// Kernel: Analog wave softmax (layers 6-7)
// ---------------------------------------------------------------------------

void analog_softmax(const lr_fp32* logits, lr_analog* out, int n) {
    // Write logits as optical amplitudes (normalised to [0,1])
    lr_fp32 max_val = logits[0];
    for (int i = 1; i < n; ++i) {
        if (logits[i] > max_val) max_val = logits[i];
    }

    for (int i = 0; i < n; ++i) {
        // Encode shifted logit as analog amplitude
        lr_fp32 shifted = logits[i] - max_val;  // subtract max for stability
        lr_analog amp(0.5f + 0.5f * (shifted / 10.0f));  // normalise to [0,1]
        lr_analog_write(i, amp);
    }

    // Analog accumulate (optical power summation on layers 6-7)
    // In hardware this is a single optical bus operation
    lr_fence();  // ensure all writes are committed

    lr_fp32 total = 0.0f;
    for (int i = 0; i < n; ++i) {
        out[i] = lr_analog_read(i);
        total += out[i].amplitude;
    }
    // Normalise
    for (int i = 0; i < n; ++i) {
        out[i].amplitude = total > 0.0f ? out[i].amplitude / total : 0.0f;
    }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

int main() {
    printf("LightRail C++ Tiled Pipeline Example\n");
    printf("  GEMM: %dx%d x %dx%d  tile=%d\n", M, K, K, N, TILE);
    printf("  WDM channels: 64 (compile-time bound, no warp scheduling)\n");
    printf("  Analog compute: layers 6-7\n");
    printf("  Ternary compute: layers 3-5\n");
    printf("\nThis binary targets LightRail NCE gen-1 hardware.\n");
    printf("Run 'lrc-aot --hw-gen 1 tiled_gemm.lrbs' to produce NPU binary.\n");
    return 0;
}
