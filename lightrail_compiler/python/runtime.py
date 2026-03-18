"""
LightRail Python Runtime - device management and tensor utilities.
"""

from __future__ import annotations
import os
from typing import Optional


class LightRailDevice:
    """Represents a physical LightRail NCE device."""

    def __init__(self, device_id: int = 0, num_layers: int = 20, num_wavelengths: int = 64):
        self.device_id = device_id
        self.num_layers = num_layers
        self.num_wavelengths = num_wavelengths
        self._available = self._probe_hardware()

    def _probe_hardware(self) -> bool:
        """Check whether actual LightRail hardware is present."""
        driver_path = f"/dev/lightrail{self.device_id}"
        return os.path.exists(driver_path)

    @property
    def is_available(self) -> bool:
        return self._available

    def __repr__(self):
        status = "online" if self._available else "emulated"
        return f"<LightRailDevice id={self.device_id} layers={self.num_layers} status={status}>"


class LightRailRuntime:
    """
    Manages one or more LightRail NCE devices and provides tensor
    allocation/transfer primitives.
    """

    def __init__(self):
        self._devices: list[LightRailDevice] = []
        self._default_device: Optional[LightRailDevice] = None
        self._scan_devices()

    def _scan_devices(self):
        for i in range(8):  # Scan up to 8 devices
            dev = LightRailDevice(i)
            self._devices.append(dev)
            if self._default_device is None and dev.is_available:
                self._default_device = dev

        if self._default_device is None:
            # Emulation mode
            self._default_device = LightRailDevice(0)

    @property
    def default_device(self) -> LightRailDevice:
        return self._default_device

    @property
    def device_count(self) -> int:
        return sum(1 for d in self._devices if d.is_available)

    def allocate_sram(self, size_bytes: int, device: Optional[LightRailDevice] = None) -> int:
        """
        Allocate SRAM on the photonic fabric.
        Because optical interconnects flatten the datacenter, SRAM from
        different chips is directly addressable — no HBM indirection.
        Returns a virtual fabric address.
        """
        dev = device or self._default_device
        # Stub: in production this calls the kernel driver ioctl
        return id(dev) ^ (size_bytes & 0xFFFFFFFF)

    def dma_transfer(self, src_addr: int, dst_addr: int, size_bytes: int):
        """Direct DMA between fabric SRAM nodes — bypasses HBM entirely."""
        pass  # Kernel driver call in production


_default_runtime: Optional[LightRailRuntime] = None


def get_default_runtime() -> LightRailRuntime:
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = LightRailRuntime()
    return _default_runtime
