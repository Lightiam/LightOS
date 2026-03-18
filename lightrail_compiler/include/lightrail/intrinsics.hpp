/**
 * @file intrinsics.hpp
 * LightRail Hardware Intrinsics
 *
 * Low-level intrinsic functions that map directly to NCE instructions.
 * These are declared as extern "C" stubs; the real implementations are
 * provided by the LightRail runtime library (liblightrail.a).
 *
 * Categories:
 *   - DMA intrinsics       (lr_dma_*)
 *   - WDM channel ops      (lr_wdm_*)
 *   - Ternary compute      (lr_trit_*)
 *   - Analog wave compute  (lr_analog_*)
 *   - Synchronisation      (lr_fence, lr_barrier)
 */

#pragma once
#include "types.hpp"
#include <cstddef>

namespace lightrail {

// ---------------------------------------------------------------------------
// DMA intrinsics — direct SRAM-to-SRAM transfers (no HBM)
// ---------------------------------------------------------------------------

/**
 * Asynchronously copy `bytes` from src_fabric_addr to dst_fabric_addr.
 * Both addresses are virtual fabric addresses (flat across the datacenter).
 * Returns a completion token; use lr_dma_wait() to synchronize.
 */
extern "C" uint64_t lr_dma_async(uint64_t dst_fabric_addr,
                                  uint64_t src_fabric_addr,
                                  size_t   bytes);

/** Block until the DMA operation identified by `token` completes. */
extern "C" void lr_dma_wait(uint64_t token);

/** Synchronous DMA (blocks caller until transfer is done). */
inline void lr_dma_sync(uint64_t dst, uint64_t src, size_t bytes) {
    lr_dma_wait(lr_dma_async(dst, src, bytes));
}

// ---------------------------------------------------------------------------
// WDM channel intrinsics — photonic wavelength send/receive
// ---------------------------------------------------------------------------

/** Send value on wavelength channel `ch`. Non-blocking. */
extern "C" void lr_wdm_send_f32(int ch, lr_fp32 value);
extern "C" void lr_wdm_send_i32(int ch, lr_int32 value);
extern "C" void lr_wdm_send_trit(int ch, lr_trit value);

/** Receive value from wavelength channel `ch`. Blocks until data arrives. */
extern "C" lr_fp32   lr_wdm_recv_f32(int ch);
extern "C" lr_int32  lr_wdm_recv_i32(int ch);
extern "C" lr_trit   lr_wdm_recv_trit(int ch);

/** Broadcast value to all active wavelength channels (collective). */
extern "C" void lr_wdm_broadcast_f32(lr_fp32 value);

/** All-reduce across all wavelength channels using summation. */
extern "C" lr_fp32 lr_wdm_allreduce_sum_f32(lr_fp32 local_value);

// ---------------------------------------------------------------------------
// Ternary compute intrinsics (layers 3-5)
// ---------------------------------------------------------------------------

/** Element-wise ternary multiply-add: result = a * b + c (saturated). */
extern "C" lr_trit lr_trit_fma(lr_trit a, lr_trit b, lr_trit c);

/** Ternary dot-product over vectors of length N. */
extern "C" lr_fp32 lr_trit_dot(const lr_trit* a, const lr_trit* b, int n);

/** Encode a float into the nearest ternary value. */
inline lr_trit lr_float_to_trit(lr_fp32 f) {
    if (f >  0.333f) return lr_trit( 1);
    if (f < -0.333f) return lr_trit(-1);
    return lr_trit(0);
}

// ---------------------------------------------------------------------------
// Analog wave compute intrinsics (layers 6-7)
// ---------------------------------------------------------------------------

/** Write amplitude to the analog compute lane. Range [0, 1]. */
extern "C" void lr_analog_write(int lane, lr_analog amplitude);

/** Read amplitude from the analog compute lane. */
extern "C" lr_analog lr_analog_read(int lane);

/** Analog multiply: modulates the optical carrier amplitude. */
extern "C" lr_analog lr_analog_mul(lr_analog a, lr_analog b);

/** Analog accumulate (sum of optical powers). */
extern "C" lr_analog lr_analog_sum(const lr_analog* values, int n);

// ---------------------------------------------------------------------------
// Synchronisation primitives
// ---------------------------------------------------------------------------

/**
 * Full memory/fabric fence.
 * Ensures all prior DMA and WDM operations are visible before continuing.
 * Replaces CUDA's __threadfence() — but operates on the optical fabric
 * without warp-level complications.
 */
extern "C" void lr_fence();

/**
 * Channel barrier — block until all wavelength channels reach this point.
 * Equivalent to CUDA's __syncthreads() but deterministic (no straggler wait).
 */
extern "C" void lr_barrier();

// ---------------------------------------------------------------------------
// Matrix / tensor intrinsics
// ---------------------------------------------------------------------------

/**
 * Photonic matrix-multiply accumulate:
 *   C[M][N] += A[M][K] * B[K][N]
 *
 * Dispatched to the photonic dot-product engine on the fabric.
 * Types may be mixed (e.g., fp16 inputs, fp32 accumulator).
 */
extern "C" void lr_mma_f16f16f32(int M, int N, int K,
                                   const lr_fp16* A,
                                   const lr_fp16* B,
                                   lr_fp32*       C);

extern "C" void lr_mma_trit(int M, int N, int K,
                              const lr_trit* A,
                              const lr_trit* B,
                              lr_fp32*       C);

}  // namespace lightrail
