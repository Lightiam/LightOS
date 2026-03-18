"""
LightRail Photonic Compiler — Matrix Multiplication Example

Demonstrates @lightrail.jit on a matrix multiply kernel.
Runs in CPU emulation mode when no NCE hardware is present.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import python as lightrail


@lightrail.jit(num_wavelengths=64, enable_ternary=False, enable_analog=False)
def matmul(A, B):
    """Dense matrix multiply: C = A @ B"""
    return A @ B


@lightrail.jit(num_wavelengths=32, enable_ternary=True)
def ternary_matmul(A, B):
    """
    Ternary-quantised matrix multiply.
    Weights are encoded in {-1,0,+1} and mapped to layers 3-5.
    """
    return A @ B


@lightrail.jit(num_wavelengths=64, enable_analog=True)
def analog_matmul(A, B):
    """
    Analog wave matmul — uses optical amplitude for accumulation.
    Dispatched to layers 6-7 of the photonic fabric.
    """
    return A @ B


def run():
    import math

    # Simulate inputs (Python lists as stand-ins for NCE tensors)
    M, K, N = 128, 256, 128
    A = [[1.0 / K] * K for _ in range(M)]
    B = [[1.0 / K] * N for _ in range(K)]

    print("=== LightRail Matmul Example ===")
    print(f"A: {M}x{K}  B: {K}x{N}")

    # Standard FP32 matmul
    result = matmul(A, B)
    print(f"Standard matmul kernel: {matmul._lightrail_kernel}")

    # Ternary matmul
    result_ternary = ternary_matmul(A, B)
    print(f"Ternary matmul kernel:  {ternary_matmul._lightrail_kernel}")

    # Analog matmul
    result_analog = analog_matmul(A, B)
    print(f"Analog matmul kernel:   {analog_matmul._lightrail_kernel}")

    print("\nAll kernels compiled and dispatched successfully.")
    print("(Running in CPU emulation — connect NCE hardware for photonic dispatch)")


if __name__ == "__main__":
    run()
