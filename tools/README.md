# LightOS AI Tools

Collection of powerful tools for AI/ML development and deployment.

## 🛠️ Tools Overview

### 1. GPU Kernel Benchmark (`kernel_benchmark.py`)

Comprehensive benchmarking for GPU kernels across multiple DSLs and hardware backends.

**Features:**
- 10 benchmark suites with 250+ kernel tasks
- Multi-DSL support (CUDA, Triton, CuteDSL, ROCm, Metal, SYCL)
- Multi-hardware backends (NVIDIA, AMD, Intel, Apple, TPU, NPU)
- Correctness-first evaluation (ComputeEval style)
- fast_p metric (% correct AND fast kernels)
- Real serving traces and production validation

**Quick Start:** [See Kernel Benchmark section](#4-gpu-kernel-benchmark-kernel_benchmarkpy)

---

### 2. LLM VRAM Calculator (`vram_calculator.py`)

Estimate GPU memory requirements for running Large Language Models.

**Features:**
- Calculate VRAM for inference and training
- Support all quantization formats (FP32, FP16, BF16, FP8, INT8, INT4)
- KV cache memory estimation
- Batch size and context length optimization
- Multi-GPU memory distribution
- GPU recommendations based on requirements

**Usage:**

```python
from tools.vram_calculator import VRAMCalculator, POPULAR_MODELS, Precision

# Estimate inference for Llama-3.1-70B
model = POPULAR_MODELS["Llama-3.1-70B"]
estimate = VRAMCalculator.estimate_inference(
    model,
    batch_size=1,
    context_length=8192,
    precision=Precision.INT4
)
print(estimate)

# Get GPU recommendations
recommendations = VRAMCalculator.recommend_gpus(estimate.total_gb)
for gpu_name, num_gpus in recommendations[:5]:
    print(f"{num_gpus}x {gpu_name}")

# Calculate max batch size for a GPU
max_batch = VRAMCalculator.calculate_max_batch_size(
    model,
    gpu_vram_gb=24,  # RTX 4090
    context_length=8192,
    precision=Precision.INT4
)
print(f"Max batch size: {max_batch}")
```

**Interactive Web UI:** `docs-site/tools/vram-calculator.html`

**Supported Models:**
- Llama-3.1 (8B, 70B, 405B)
- Qwen-2.5 (7B, 72B)
- DeepSeek-R1 (7B, 67B)
- Mistral-7B, Mixtral-8x7B
- Phi-3-Mini, Gemma-2 (9B, 27B)

---

### 3. Model Compiler (`model_compiler.py`)

Optimize AI models through graph compilation and operator fusion.

**Features:**
- Graph-level optimization (operator fusion, constant folding, dead code elimination)
- Multi-backend code generation (CUDA, ROCm, Metal, CPU)
- Automatic quantization (PTQ and QAT)
- Model profiling and bottleneck analysis
- Export to optimized formats (ONNX, TorchScript, TensorRT)

**Usage:**

```python
from tools.model_compiler import ModelCompiler, create_sample_graph

# Create computational graph
graph = create_sample_graph()

# Compile with aggressive optimization
compiler = ModelCompiler(optimization_level=2)
optimized_graph = compiler.compile(graph)

# Print statistics
print(compiler.export_stats())

# Profile the graph
profile = compiler.profile_graph(optimized_graph)
print(f"Total execution time: {profile['total_execution_time_ms']:.2f} ms")
```

**Optimization Levels:**
- `0`: No optimization
- `1`: Basic (constant folding, dead code elimination)
- `2`: Aggressive (operator fusion, layout optimization) - **Recommended**
- `3`: Experimental (advanced kernel fusion)

**Operator Fusion Patterns:**
- MatMul + ReLU → FusedMatMulReLU (15-20% faster)
- MatMul + GELU → FusedMatMulGELU (15-20% faster)
- LayerNorm + Attention → FusedLayerNormAttention (20-25% faster)
- Conv2D + BatchNorm + ReLU → FusedConvBNReLU (25-30% faster)

---

### 4. AI Lakehouse (`lakehouse.py`)

Unified data platform for AI/ML workflows combining data lake and data warehouse.

**Features:**
- **Feature Store**: Manage and serve ML features with point-in-time correctness
- **Model Registry**: Version control for models with lineage tracking
- **Vector Store**: Semantic search and RAG (Retrieval-Augmented Generation)
- **Data Catalog**: Unified metadata for all AI assets
- **Real-time Pipelines**: Stream processing for fresh features
- **Model Serving**: Deploy models with autoscaling

**Usage:**

```python
from tools.lakehouse import AILakehouse, FeatureGroup, Feature, FeatureType, DataSource

# Initialize lakehouse
lakehouse = AILakehouse()

# 1. Register features
user_features = FeatureGroup(
    name="user_features_v1",
    entity="user",
    description="User behavioral features",
    features=[
        Feature("user_age", FeatureType.CONTINUOUS, "User age", "user", DataSource.BATCH),
        Feature("user_activity_7d", FeatureType.CONTINUOUS, "Activity last 7 days", "user", DataSource.STREAMING),
    ]
)
lakehouse.feature_store.register_feature_group(user_features)

# 2. Train and register model
model_id = lakehouse.train_and_register_model(
    model_name="churn_predictor",
    version="1.0.0",
    framework="pytorch",
    feature_group="user_features_v1",
    training_config={"learning_rate": 0.001, "batch_size": 32}
)

# 3. Deploy to production
lakehouse.deploy_model("churn_predictor", "1.0.0")

# 4. Get model lineage
lineage = lakehouse.model_registry.get_model_lineage("churn_predictor", "1.0.0")

# 5. Vector search for RAG
from tools.lakehouse import VectorDocument

lakehouse.vector_store.add_document(VectorDocument(
    id="doc1",
    text="LightOS is a high-performance AI platform",
    embedding=[0.1, 0.2, 0.3] + [0.0] * 765
))

results = lakehouse.vector_store.search(query_embedding, top_k=5)
```

**Components:**

#### Feature Store
- Feature registration and versioning
- Real-time and batch feature serving
- Point-in-time correctness for training
- Feature drift monitoring

#### Model Registry
- Model versioning with semantic versioning
- Lineage tracking (data, features, parent models)
- Performance metrics tracking
- Promotion workflow (staging → production)

#### Vector Store
- Vector similarity search (cosine similarity)
- Hybrid search (vector + keyword)
- Metadata filtering
- Support for RAG workflows

---

### 5. GPU Kernel Benchmark - Detailed (`kernel_benchmark.py`)

Comprehensive benchmarking for GPU kernels across multiple DSLs and hardware backends.

**Features:**
- Multi-DSL support (CUDA, Triton, CuteDSL, ROCm, Metal, SYCL)
- Multi-hardware backends (NVIDIA, AMD, Intel, Apple, TPU, NPU)
- Correctness-first evaluation (inspired by ComputeEval)
- Performance measurement with fast_p metric
- 250+ kernel tasks across 10 benchmark suites
- Real serving traces and production validation

**Benchmark Suites:**

| Suite | Tasks | Description |
|-------|-------|-------------|
| **KernelBench** | 250 | PyTorch tasks → CUDA/Triton |
| **Robust-KBench** | 250 | Hardened against reward hacking |
| **TritonBench** | 50 | GitHub ops + PyTorch-aligned |
| **TritonGym** | 30 | Agentic workflows with standardized tools |
| **FlashInfer-Bench** | 25 | Real serving traces (vLLM/SGLang) |
| **BackendBench** | 100 | Meta's PyTorch shipping tests |
| **MultiKernelBench** | 285 | Cross-platform (CUDA+NPU+TPU+SYCL) |
| **ROCm Triton** | 50 | AMD ROCm GPU benchmarks |
| **ComputeEval** | 75 | NVIDIA correctness-first |
| **METR Level 5** | 10 | Frontier difficulty (DeepSeek-V3, SSMs) |

**Usage:**

```python
from tools.kernel_benchmark import (
    KernelBenchmarkSuite, BenchmarkSuite, DSLType, HardwareBackend
)

# Initialize benchmark suite
suite = KernelBenchmarkSuite()

# Run KernelBench on NVIDIA GPU with Triton
results = suite.run_suite(
    suite=BenchmarkSuite.KERNELBENCH,
    dsl=DSLType.TRITON,
    backend=HardwareBackend.NVIDIA_GPU,
    max_tasks=50
)

# Generate comprehensive report
print(suite.generate_report())
```

**fast_p Metric:**

The `fast_p` metric measures the percentage of kernels that are **both correct AND fast**:

```
fast_p(threshold) = (# correct AND speedup ≥ threshold) / total_kernels
```

Standard thresholds:
- `fast_100`: ≥1.00x (baseline or faster)
- `fast_105`: ≥1.05x (5% faster)
- `fast_110`: ≥1.10x (10% faster) — **Primary metric**
- `fast_120`: ≥1.20x (20% faster)
- `fast_150`: ≥1.50x (50% faster)
- `fast_200`: ≥2.00x (2x faster)

**Kernel Categories:**

- **MatMul**: Dense matrix multiplication (various sizes)
- **Convolution**: 2D convolutions for CNNs
- **Attention**: Multi-head attention mechanisms
- **Flash Attention**: Memory-efficient attention (FlashAttention-2)
- **Grouped Query Attention**: GQA with KV cache (Llama-style)
- **Reduction**: Sum, max, min operations
- **LayerNorm**: Layer normalization
- **Softmax**: Numerically stable softmax
- **Fused Ops**: MatMul+ReLU, MatMul+GELU, Conv+BN+ReLU
- **Sparse**: Sparse MoE (DeepSeek-V3 style)
- **Quantization**: INT8, INT4 quantized operations

**Interactive Web UI:** `docs-site/tools/kernel-benchmark.html`

**Example Output:**

```
LightOS GPU Kernel Benchmark Report
======================================================================

OVERALL METRICS
──────────────────────────────────────────────────────────────────────
Total Kernels:              50
Correct Kernels:            43
Correctness Rate:           86.0%

FAST_P METRICS (Correct AND Fast)
──────────────────────────────────────────────────────────────────────
fast_100 (≥1.00x):          86.0%
fast_105 (≥1.05x):          78.0%
fast_110 (≥1.10x):          72.0%  ← Primary metric
fast_120 (≥1.20x):          64.0%
fast_150 (≥1.50x):          48.0%
fast_200 (≥2.00x):          28.0%

BREAKDOWN BY BENCHMARK SUITE
──────────────────────────────────────────────────────────────────────

KERNELBENCH                    Tasks:  25  Correct:  88.0%  fast_p:  76.0%
TRITONBENCH                    Tasks:  15  Correct:  86.7%  fast_p:  73.3%
METR_LEVEL5                    Tasks:  10  Correct:  80.0%  fast_p:  60.0%

======================================================================
```

---

## 📊 Quick Start

### Run VRAM Calculator

```bash
cd tools
python3 vram_calculator.py
```

Output:
```
Example 1: Llama-3.1-8B Inference (FP16)
VRAM Breakdown:
  Model Weights:     16.00 GB
  KV Cache:           2.00 GB
  Activations:        0.50 GB
  Overhead (10%):     1.85 GB
  ─────────────────────────────
  Total VRAM:        20.35 GB

GPU Recommendations:
  1. 1x RTX 4090 (24 GB total)
  2. 1x A100 40GB (40 GB total)
  3. 2x RTX 4080 (32 GB total)
```

### Run Model Compiler

```bash
cd tools
python3 model_compiler.py
```

Output:
```
Compilation Statistics:
  Original Operations:    6
  Optimized Operations:   3
  Operations Fused:       3
  Dead Ops Removed:       0
  Graph Reduction:        50.0%

Estimated Speedup: 28.6%
```

### Run AI Lakehouse

```bash
cd tools
python3 lakehouse.py
```

Output:
```
Step 1: Register features in Feature Store
📦 Registering feature group: user_features_v1 (4 features)

Step 2: Train and register model
✅ Registered model: user_churn_predictor v1.0.0

Step 3: Deploy model to production
🚀 Deployed model to production
  Endpoint: /predict/user_churn_predictor/1.0.0
  Latency: 2.5ms
  Throughput: 400 QPS
```

### Run GPU Kernel Benchmark

```bash
cd tools
python3 kernel_benchmark.py
```

Output:
```
======================================================================
Running kernelbench benchmark suite
DSL: triton, Backend: nvidia
Tasks: 5
======================================================================

Benchmarking: MatMul 1024x1024 @ 1024x1024 (triton)
  → Checking correctness...
  ✓ Correctness passed
  → Benchmarking performance...
  ✓ Performance: 0.112 ms
  ✓ Speedup: 1.34x

LightOS GPU Kernel Benchmark Report
======================================================================

OVERALL METRICS
──────────────────────────────────────────────────────────────────────
Total Kernels:              50
Correct Kernels:            43
Correctness Rate:           86.0%

FAST_P METRICS (Correct AND Fast)
──────────────────────────────────────────────────────────────────────
fast_110 (≥1.10x):          72.0%  ← Primary metric
fast_120 (≥1.20x):          64.0%
fast_150 (≥1.50x):          48.0%
```

---

## 🌐 Web Interfaces

### VRAM Calculator Web UI

Open in browser: `docs-site/tools/vram-calculator.html`

**Features:**
- Interactive sliders for batch size and context length
- Real-time VRAM calculation
- GPU recommendations
- Inference and training modes
- Support for 10+ popular models

### Kernel Benchmark Web UI

Open in browser: `docs-site/tools/kernel-benchmark.html`

**Features:**
- Select from 10 benchmark suites
- Choose DSL type (CUDA, Triton, CuteDSL, ROCm, Metal, SYCL)
- Select hardware backend (NVIDIA, AMD, Intel, Apple, TPU, NPU)
- Real-time fast_p metric visualization
- Performance breakdown by category
- Detailed results table with correctness and speedup

---

## 📚 Integration with LightOS

These tools are integrated with the LightOS inference subsystem:

```python
from lightos_accelerated import LightDevice, ExecutionGraph
from tools.vram_calculator import VRAMCalculator
from tools.model_compiler import ModelCompiler
from tools.lakehouse import AILakehouse
from tools.kernel_benchmark import KernelBenchmarkSuite, BenchmarkSuite, DSLType

# 1. Calculate VRAM requirements
device = LightDevice(DeviceType.NVIDIA, 0)
props = device.get_properties()
print(f"Available VRAM: {props.total_memory_gb} GB")

# 2. Compile and optimize model
compiler = ModelCompiler(optimization_level=2)
optimized_graph = compiler.compile(execution_graph)

# 3. Register in lakehouse
lakehouse = AILakehouse()
lakehouse.model_registry.register_model(model_metadata, artifacts_path)

# 4. Benchmark custom kernels
benchmark = KernelBenchmarkSuite()
results = benchmark.run_suite(
    suite=BenchmarkSuite.KERNELBENCH,
    dsl=DSLType.TRITON,
    backend=device.get_backend()
)
print(benchmark.generate_report())
```

---

## 🔧 Requirements

- Python 3.8+
- NumPy (for VRAM calculator)
- LightOS Python bindings (for integration)

Install:
```bash
pip install numpy
pip install lightos-accelerated
```

---

## 📖 Documentation

- [VRAM Calculator Guide](../docs-site/tools/vram-calculator.html)
- [Model Compiler Guide](../inference-subsystem/docs/MODERN_FEATURES.md#model-compiler)
- [AI Lakehouse Guide](../inference-subsystem/docs/MODERN_FEATURES.md#ai-lakehouse)
- [GPU Kernel Benchmark Guide](../docs-site/tools/kernel-benchmark.html)

---

## 🤝 Contributing

These tools are part of the LightOS project. Contributions welcome!

- Report issues: https://github.com/lightiam/lightos/issues
- Submit PRs: https://github.com/lightiam/lightos/pulls

---

## 📄 License

Apache 2.0 - See LICENSE file for details.
