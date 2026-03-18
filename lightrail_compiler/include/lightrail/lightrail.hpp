/**
 * @file lightrail.hpp
 * LightRail C++ Unified Include
 *
 * Single-header convenience include for the LightRail tiled pipelining
 * library.  Advanced users can include individual headers directly.
 */

#pragma once

#include "types.hpp"
#include "intrinsics.hpp"
#include "pipeline.hpp"
#include "wdm.hpp"

/**
 * @mainpage LightRail Photonic Compiler C++ Library
 *
 * The LightRail C++ library provides a CUDA-like developer experience
 * without the complexity of thread scheduling, warp divergence, or HBM
 * bottlenecks.
 *
 * Key concepts:
 *
 * 1. **WDM Channels** replace CUDA threads.
 *    64 optical wavelengths run in true parallel, bound at compile time.
 *    @code
 *    WDMChannel<MY_CH, lr_fp32>::send(result);
 *    @endcode
 *
 * 2. **Tiled Pipeline** replaces manual CUDA async-copy boilerplate.
 *    @code
 *    using Pipe = Pipeline<
 *        Stage<Load, lr_fp16, 128>,
 *        Stage<Compute, lr_fp32, 128>,
 *        Stage<Store, lr_fp32, 128>
 *    >;
 *    Pipe::run(num_tiles, [&](auto& ld, auto& cp, auto& st) { ... });
 *    @endcode
 *
 * 3. **Ternary & Analog** compute layers.
 *    Native ternary types (lr_trit) and analog amplitudes (lr_analog)
 *    map to LightRail's unique optical physics — no emulation overhead.
 *
 * 4. **Direct DMA** between any two SRAM nodes on the photonic mesh.
 *    Because optical interconnects flatten latency, cross-chip memory
 *    access is as fast as local SRAM — bypassing HBM entirely.
 *    @code
 *    lr_dma_sync(dst_fabric_addr, src_fabric_addr, bytes);
 *    @endcode
 */
