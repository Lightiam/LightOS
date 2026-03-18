"""
LightRail Photonic Compiler — Python package setup.
"""

from setuptools import setup, find_packages

setup(
    name="lightrail-compiler",
    version="0.1.0",
    description="CUDA-like compiler and OS for the LightRail Neural Compute Engine",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    author="LightRail AI",
    packages=find_packages(exclude=["tests*", "examples*"]),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-cov"],
        "torch": ["torch>=2.0"],
        "jax": ["jax>=0.4"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
    ],
)
