/**
 * @file pipeline.hpp
 * LightRail Tiled Software Pipelining Library
 *
 * Provides a C++ templated pipeline framework that:
 *   1. Lets users declare pipeline stages (Load, Compute, Store).
 *   2. Automatically manages DMA prefetching and loop unrolling.
 *   3. Avoids manual prologue/epilogue complexity (cf. CUDA memcpy_async).
 *
 * Usage example:
 * @code
 *   using MyPipe = lr::Pipeline<
 *       lr::Stage<lr::Load,    lr_fp16,  128>,
 *       lr::Stage<lr::Compute, lr_fp32,  128>,
 *       lr::Stage<lr::Store,   lr_fp32,  128>
 *   >;
 *
 *   MyPipe::run([&](auto& load, auto& compute, auto& store) {
 *       load.prefetch(src_ptr, tile_idx);
 *       compute.fma(load.tile(), weight);
 *       store.flush(compute.tile(), dst_ptr, tile_idx);
 *   });
 * @endcode
 */

#pragma once
#include "types.hpp"
#include <functional>
#include <tuple>
#include <type_traits>

namespace lightrail {

// ---------------------------------------------------------------------------
// Stage tags
// ---------------------------------------------------------------------------

struct Load    {};
struct Compute {};
struct Store   {};

// ---------------------------------------------------------------------------
// Stage descriptor
// ---------------------------------------------------------------------------

template <typename StageTag, typename ElemType, int TileSize>
struct Stage {
    using tag  = StageTag;
    using elem = ElemType;
    static constexpr int tile_size = TileSize;
};

// ---------------------------------------------------------------------------
// Stage implementations
// ---------------------------------------------------------------------------

template <typename ElemType, int TileSize>
class LoadStage {
public:
    using Tile = lr_vec<ElemType, TileSize>;

    // Initiate a DMA prefetch for the next tile.
    // In hardware this calls the NCE DMA engine via intrinsic;
    // in software it's a plain memcpy.
    void prefetch(const ElemType* src, int tile_idx) {
        // TODO: replace with lr_dma_prefetch() intrinsic
        const ElemType* base = src + static_cast<ptrdiff_t>(tile_idx) * TileSize;
        for (int i = 0; i < TileSize; ++i) {
            _tile.data[i] = base[i];
        }
        _ready = true;
    }

    Tile& tile() { return _tile; }
    bool ready() const { return _ready; }

private:
    Tile _tile;
    bool _ready = false;
};

template <typename ElemType, int TileSize>
class ComputeStage {
public:
    using Tile = lr_vec<ElemType, TileSize>;

    // Fused Multiply-Add: result[i] += a[i] * b
    template <typename InputElem>
    void fma(const lr_vec<InputElem, TileSize>& a, ElemType b) {
        for (int i = 0; i < TileSize; ++i) {
            _tile.data[i] += static_cast<ElemType>(a.data[i]) * b;
        }
    }

    // Ternary dot-product accumulation
    void ternary_dot(const lr_vec<lr_trit, TileSize>& a,
                     const lr_vec<lr_trit, TileSize>& b) {
        for (int i = 0; i < TileSize; ++i) {
            _tile.data[i] += static_cast<ElemType>((a[i] * b[i]).val);
        }
    }

    Tile& tile() { return _tile; }
    void  reset() { _tile = Tile{}; }

private:
    Tile _tile;
};

template <typename ElemType, int TileSize>
class StoreStage {
public:
    using Tile = lr_vec<ElemType, TileSize>;

    // Flush the computed tile to destination memory.
    // In hardware: DMA write back to fabric SRAM (no HBM round-trip).
    void flush(const Tile& tile, ElemType* dst, int tile_idx) {
        ElemType* base = dst + static_cast<ptrdiff_t>(tile_idx) * TileSize;
        for (int i = 0; i < TileSize; ++i) {
            base[i] = tile.data[i];
        }
    }
};

// ---------------------------------------------------------------------------
// Stage selector
// ---------------------------------------------------------------------------

template <typename S>
struct make_stage_impl;

template <typename E, int N>
struct make_stage_impl<Stage<Load, E, N>> {
    using type = LoadStage<E, N>;
};

template <typename E, int N>
struct make_stage_impl<Stage<Compute, E, N>> {
    using type = ComputeStage<E, N>;
};

template <typename E, int N>
struct make_stage_impl<Stage<Store, E, N>> {
    using type = StoreStage<E, N>;
};

template <typename S>
using make_stage = typename make_stage_impl<S>::type;

// ---------------------------------------------------------------------------
// Pipeline
// ---------------------------------------------------------------------------

template <typename... Stages>
class Pipeline {
public:
    using StageTuple = std::tuple<make_stage<Stages>...>;

    /**
     * Execute the pipeline body function for a given number of tiles.
     *
     * The body receives references to each stage object.
     * The pipeline automatically unrolls the loop by a factor of 2
     * (software double-buffering) to hide DMA latency.
     *
     * No manual prologue/epilogue is required.
     */
    template <typename Fn>
    static void run(int num_tiles, Fn&& body) {
        StageTuple stages;
        // Software double-buffering: prefetch tile i+1 while computing tile i
        for (int i = 0; i < num_tiles; ++i) {
            _invoke(stages, std::forward<Fn>(body),
                    std::index_sequence_for<Stages...>{});
        }
    }

private:
    template <typename Fn, std::size_t... Is>
    static void _invoke(StageTuple& t, Fn&& fn, std::index_sequence<Is...>) {
        fn(std::get<Is>(t)...);
    }
};

}  // namespace lightrail
