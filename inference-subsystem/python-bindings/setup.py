#!/usr/bin/env python3
"""
LightOS Accelerated Inference - Python Package Setup
High-performance AI inference with thermal-aware scheduling
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """Extension built with CMake instead of setuptools default compiler"""

    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Custom build command that uses CMake"""

    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            self.build_cmake(ext)
        else:
            super().build_extension(ext)

    def build_cmake(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # CMake build configuration
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            '-DCMAKE_BUILD_TYPE=Release',
            '-DBUILD_PYTHON_BINDINGS=ON',
        ]

        # Platform-specific configuration
        if sys.platform == 'darwin':
            # macOS: Support both Intel and Apple Silicon
            cmake_args += [
                '-DCMAKE_OSX_ARCHITECTURES=x86_64;arm64',  # Universal binary
            ]

        if sys.platform == 'win32':
            # Windows: Use Visual Studio generator
            cmake_args += [
                '-G', 'Visual Studio 17 2022',
                '-A', 'x64',
            ]

        # Build configuration
        build_args = ['--config', 'Release']

        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            # Use all available cores
            import multiprocessing
            build_args += ['--', f'-j{multiprocessing.cpu_count()}']

        # Create build directory
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        # Run CMake configure
        subprocess.check_call(
            ['cmake', ext.sourcedir] + cmake_args,
            cwd=self.build_temp
        )

        # Run CMake build
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=self.build_temp
        )


# Read long description from README
def read_long_description():
    readme_path = Path(__file__).parent.parent / 'README.md'
    if readme_path.exists():
        return readme_path.read_text(encoding='utf-8')
    return "LightOS Accelerated Inference - High-performance AI inference with thermal-aware scheduling"


# Read version from version file
def read_version():
    version_file = Path(__file__).parent / 'lightos_accelerated' / '__version__.py'
    if version_file.exists():
        version_dict = {}
        exec(version_file.read_text(), version_dict)
        return version_dict['__version__']
    return '1.0.0'


setup(
    # Package metadata
    name='lightos-accelerated',
    version=read_version(),
    author='LightOS Team',
    author_email='info@lightos.ai',
    description='High-performance AI inference with thermal-aware scheduling and hardware-agnostic execution',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/lightiam/lightos',
    license='Apache 2.0',

    # Package discovery
    packages=find_packages(where='.'),
    package_dir={'': '.'},
    py_modules=['lightos_accelerated'],

    # C++ extension (built with CMake)
    ext_modules=[
        CMakeExtension('lightos_core', sourcedir='../core')
    ],
    cmdclass={
        'build_ext': CMakeBuild,
    },

    # Python version requirement
    python_requires='>=3.8',

    # Dependencies
    install_requires=[
        'numpy>=1.20.0,<2.0.0',
        'onnx>=1.12.0',
        'protobuf>=3.20.0,<5.0.0',
    ],

    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'server': [
            'grpcio>=1.50.0',
            'grpcio-tools>=1.50.0',
        ],
        'jupyter': [
            'jupyter>=1.0.0',
            'matplotlib>=3.5.0',
            'ipywidgets>=8.0.0',
        ],
        'torch': [
            'torch>=2.0.0',
        ],
        'all': [
            'grpcio>=1.50.0',
            'grpcio-tools>=1.50.0',
            'jupyter>=1.0.0',
            'matplotlib>=3.5.0',
            'ipywidgets>=8.0.0',
            'torch>=2.0.0',
        ],
    },

    # Entry points (CLI commands)
    entry_points={
        'console_scripts': [
            'lightos=lightos_accelerated.cli:main',
            'lightos-server=lightos_accelerated.server:main',
        ],
    },

    # Package data
    package_data={
        'lightos_accelerated': [
            '*.so',
            '*.dll',
            '*.dylib',
            'kernels/*.ptx',
            'kernels/*.cubin',
        ],
    },

    # Include additional files
    include_package_data=True,

    # PyPI classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware',
    ],

    # Keywords for PyPI search
    keywords=[
        'AI', 'inference', 'GPU', 'CUDA', 'ROCm', 'ONNX', 'TorchScript',
        'thermal-aware', 'high-performance', 'machine-learning', 'deep-learning',
        'neural-networks', 'model-optimization', 'graph-optimization',
    ],

    # Project URLs
    project_urls={
        'Documentation': 'https://docs.lightos.ai',
        'Source': 'https://github.com/lightiam/lightos',
        'Bug Reports': 'https://github.com/lightiam/lightos/issues',
        'Discussions': 'https://github.com/lightiam/lightos/discussions',
    },

    # Zip safe
    zip_safe=False,
)
