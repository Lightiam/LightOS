/**
 * @file wdm.hpp
 * WDM Channel Abstraction Layer
 *
 * Provides typed, RAII wrappers around the raw lr_wdm_* intrinsics.
 * Replaces the CUDA thread/block/grid hierarchy with compile-time
 * channel binding.
 *
 * Core concept:
 *   WDMChannel<ID, T> — represents wavelength channel ID carrying type T.
 *   Each channel is a deterministic, single-stream virtual processor.
 *   No scheduling, no idle waiting, no warp divergence.
 *
 * Example:
 * @code
 *   // Bind computation to channel 3 at compile time
 *   constexpr auto ch = lr::WDMChannel<3, lr_fp32>{};
 *   ch.send(42.0f);
 *   lr_fp32 val = WDMChannel<3, lr_fp32>::recv();
 * @endcode
 */

#pragma once
#include "intrinsics.hpp"
#include "types.hpp"

namespace lightrail {

// ---------------------------------------------------------------------------
// WDM Channel ID — compile-time constant
// ---------------------------------------------------------------------------

template <int ChannelID>
struct channel_tag {
    static constexpr int id = ChannelID;
    static_assert(ChannelID >= 0 && ChannelID < 64,
                  "LightRail supports 0..63 WDM channels");
};

// ---------------------------------------------------------------------------
// Typed channel wrapper
// ---------------------------------------------------------------------------

template <int ChannelID, typename T>
struct WDMChannel {
    using value_type = T;
    static constexpr int id = ChannelID;

    /** Send a value on this channel (non-blocking). */
    static void send(T value);

    /** Receive from this channel (blocks until data arrives). */
    static T recv();

    /** Broadcast from this channel to all other channels. */
    static void broadcast(T value);
};

// Specialisations for supported types

template <int ID>
struct WDMChannel<ID, lr_fp32> {
    static constexpr int id = ID;
    static void   send(lr_fp32 v)  { lr_wdm_send_f32(ID, v); }
    static lr_fp32 recv()          { return lr_wdm_recv_f32(ID); }
    static void   broadcast(lr_fp32 v) { lr_wdm_broadcast_f32(v); }
};

template <int ID>
struct WDMChannel<ID, lr_int32> {
    static constexpr int id = ID;
    static void    send(lr_int32 v)  { lr_wdm_send_i32(ID, v); }
    static lr_int32 recv()           { return lr_wdm_recv_i32(ID); }
};

template <int ID>
struct WDMChannel<ID, lr_trit> {
    static constexpr int id = ID;
    static void   send(lr_trit v)  { lr_wdm_send_trit(ID, v); }
    static lr_trit recv()          { return lr_wdm_recv_trit(ID); }
};

// ---------------------------------------------------------------------------
// Channel ring: static list of channels
// ---------------------------------------------------------------------------

template <int... IDs>
struct ChannelRing {
    static constexpr int count = sizeof...(IDs);
    static constexpr int ids[sizeof...(IDs)] = { IDs... };

    /** Send value to all channels in the ring (broadcast). */
    template <typename T>
    static void broadcast(T value) {
        (WDMChannel<IDs, T>::send(value), ...);
    }
};

// Predefined rings matching the 20-layer topology
using AllChannels = ChannelRing<
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
    16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,
    32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,
    48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
>;

// Heavy-compute channels (upper half, pinned to layers 8-12)
using HeavyChannels = ChannelRing<
    32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47
>;

// Light-data channels (lower half, layers 1-7)
using LightChannels = ChannelRing<
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
>;

// ---------------------------------------------------------------------------
// Helper: current channel ID (set by compiler at kernel launch time)
// ---------------------------------------------------------------------------

/**
 * Returns the compile-time channel ID for the current execution stream.
 * Analogous to threadIdx.x in CUDA but determined statically — no dynamic
 * scheduling overhead.
 *
 * Usage: constexpr int my_ch = lr_channel_id();
 */
#define lr_channel_id() (lightrail::_current_channel_id)

// Set by the Fabric OS before dispatch; read-only for user code.
extern thread_local int _current_channel_id;

}  // namespace lightrail
