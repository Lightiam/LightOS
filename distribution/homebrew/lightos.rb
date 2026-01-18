# Homebrew Formula for LightOS Accelerated Inference
# Install with: brew install lightos

class Lightos < Formula
  desc "High-performance AI inference with thermal-aware scheduling"
  homepage "https://github.com/lightiam/lightos"
  url "https://github.com/lightiam/lightos/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "Apache-2.0"
  head "https://github.com/lightiam/lightos.git", branch: "main"

  # Dependencies
  depends_on "cmake" => :build
  depends_on "ninja" => :build
  depends_on "python@3.11"
  depends_on "numpy"
  depends_on "protobuf"

  # Optional dependencies for GPU support
  option "with-cuda", "Build with NVIDIA CUDA support"
  option "with-rocm", "Build with AMD ROCm support"

  # Platform-specific dependencies
  on_macos do
    depends_on "libomp"
  end

  on_linux do
    depends_on "gcc" => :build
  end

  def install
    # Set Python path
    python3 = Formula["python@3.11"].opt_bin/"python3.11"

    # CMake args
    args = %W[
      -DCMAKE_INSTALL_PREFIX=#{prefix}
      -DCMAKE_BUILD_TYPE=Release
      -DPYTHON_EXECUTABLE=#{python3}
      -DBUILD_PYTHON_BINDINGS=ON
      -DBUILD_TESTING=OFF
      -DBUILD_EXAMPLES=OFF
    ]

    # Add CUDA support if requested
    if build.with? "cuda"
      args << "-DENABLE_CUDA=ON"
      args << "-DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda"
    end

    # Add ROCm support if requested
    if build.with? "rocm"
      args << "-DENABLE_ROCM=ON"
      args << "-DROCM_PATH=/opt/rocm"
    end

    # Platform-specific optimizations
    if Hardware::CPU.arm?
      # Apple Silicon optimizations
      args << "-DCMAKE_OSX_ARCHITECTURES=arm64"
      args << "-DENABLE_NEON=ON"
    elsif Hardware::CPU.intel?
      # Intel optimizations
      args << "-DENABLE_AVX512=ON"
    end

    # Build C++ core
    system "cmake", "-S", "inference-subsystem/core",
                    "-B", "build",
                    "-G", "Ninja",
                    *args
    system "cmake", "--build", "build", "--parallel"
    system "cmake", "--install", "build"

    # Install Python bindings
    cd "inference-subsystem/python-bindings" do
      system python3, "-m", "pip", "install", "--prefix=#{prefix}",
                                               "--no-deps",
                                               "--ignore-installed",
                                               "."
    end

    # Install deployment scripts
    bin.install "inference-subsystem/deployment/grpc_server.py" => "lightos-server"

    # Install documentation
    doc.install "README.md"
    doc.install "inference-subsystem/docs/MODERN_FEATURES.md"
    doc.install "inference-subsystem/docs/ARCHITECTURE.md"

    # Install example notebooks
    (share/"lightos/notebooks").install Dir["inference-subsystem/notebooks/*.ipynb"]
  end

  def caveats
    <<~EOS
      LightOS has been installed!

      Quick start:
        # Python API
        python3 -c "from lightos_accelerated import LightDevice; print('✅ LightOS ready')"

        # Start inference server
        lightos-server --port=50051 --devices=auto

        # View documentation
        open #{HOMEBREW_PREFIX}/share/doc/lightos/MODERN_FEATURES.md

      Examples and notebooks:
        #{HOMEBREW_PREFIX}/share/lightos/notebooks/

      GPU Support:
        - NVIDIA: Requires CUDA Toolkit (install separately)
        - AMD: Requires ROCm (install separately)
        - CPU: Works out of the box

      For more information: https://github.com/lightiam/lightos
    EOS
  end

  test do
    # Test C++ library
    (testpath/"test.cpp").write <<~EOS
      #include <light_accelerator.hpp>
      int main() {
        using namespace lightos;
        auto device = LightAccelerator::create(DeviceType::CPU, 0);
        return device.has_value() ? 0 : 1;
      }
    EOS

    system ENV.cxx, "test.cpp",
           "-I#{include}/lightos",
           "-L#{lib}",
           "-llightos_core",
           "-o", "test"
    system "./test"

    # Test Python bindings
    system Formula["python@3.11"].opt_bin/"python3.11", "-c", <<~EOS
      from lightos_accelerated import LightDevice, DeviceType
      device = LightDevice(DeviceType.CPU, 0)
      assert device is not None
      print("✅ LightOS tests passed")
    EOS
  end
end
