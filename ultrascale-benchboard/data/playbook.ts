import { PlaybookGuidance } from '../lib/types';

export const playbookGuidance: PlaybookGuidance[] = [
  // Parallelism strategies
  {
    title: 'Data Parallelism (DP)',
    category: 'parallelism',
    content: `Data parallelism replicates the model across devices and splits the batch. Each device computes gradients independently, then synchronizes via AllReduce.

**Best for:**
- Small to medium models (< 7B params)
- Strong interconnect (NVLink, ICI)
- High batch sizes

**Memory:** O(model_size)
**Communication:** AllReduce of gradients after each step
**MFU impact:** Minimal if interconnect is fast`,
    applicableFor: {
      acceleratorTypes: ['gpu', 'tpu'],
      modelSizes: '<70B'
    },
    priority: 'high'
  },
  {
    title: 'Tensor Parallelism (TP)',
    category: 'parallelism',
    content: `Tensor parallelism shards individual layers across devices. Each device computes a portion of each matrix multiplication.

**Best for:**
- Large models (7B-70B params)
- GPUs with fast NVLink
- When model doesn't fit in single GPU

**Memory:** O(model_size / TP)
**Communication:** AllReduce after each layer
**MFU impact:** Moderate (5-10% overhead)

**Recommendation:** Use TP=2,4,8 for GPUs. Avoid TP>8.`,
    applicableFor: {
      acceleratorTypes: ['gpu'],
      modelSizes: '7B-70B',
      parallelismStrategies: ['tensor_parallel']
    },
    priority: 'high'
  },
  {
    title: 'Pipeline Parallelism (PP)',
    category: 'parallelism',
    content: `Pipeline parallelism splits the model vertically (by layers) across devices. Micro-batches flow through the pipeline stages.

**Best for:**
- Very large models (70B+ params)
- When TP alone isn't enough
- Minimizing communication

**Memory:** O(model_size / PP)
**Communication:** Minimal (only activations between stages)
**MFU impact:** Moderate (pipeline bubbles reduce efficiency)

**Recommendation:** Use PP=2,4,8. Requires careful micro-batch tuning.`,
    applicableFor: {
      acceleratorTypes: ['gpu', 'tpu'],
      modelSizes: '>70B',
      parallelismStrategies: ['pipeline_parallel']
    },
    priority: 'medium'
  },

  // Memory optimization
  {
    title: 'Activation Checkpointing',
    category: 'memory',
    content: `Activation checkpointing (gradient checkpointing) trades compute for memory by recomputing activations during backward pass instead of storing them.

**Memory savings:** ~√N where N = number of layers
**Compute overhead:** ~33% additional FLOPs
**MFU impact:** -5 to -10%

**When to use:**
- Model doesn't fit in memory
- Want to increase batch size
- Memory-bound workloads

**Nanotron insight:** Checkpoint every ~√layers transformer blocks for optimal trade-off.`,
    applicableFor: {
      acceleratorTypes: ['gpu', 'tpu'],
      modelSizes: '>7B'
    },
    priority: 'high'
  },
  {
    title: 'Mixed Precision Training',
    category: 'memory',
    content: `Use fp16/bf16 for most computations, fp32 for critical operations (loss scaling, optimizer states).

**Memory savings:** 2x for model weights and activations
**Compute speedup:** 2-3x on modern GPUs with Tensor Cores
**MFU impact:** +20 to +50%

**Recommendation:**
- **H100/A100:** Use bf16 (better numerical stability)
- **V100:** Use fp16 with loss scaling
- **TPUs:** Use bf16 (native support)`,
    applicableFor: {
      acceleratorTypes: ['gpu', 'tpu']
    },
    priority: 'high'
  },

  // Hardware-specific
  {
    title: 'GPU-Specific: Maximize NVLink Usage',
    category: 'hardware',
    content: `For NVIDIA GPUs, NVLink provides high-bandwidth inter-GPU communication (600 GB/s for A100, 900 GB/s for H100).

**Best practices:**
- Use tensor parallelism within a node (TP=2,4,8)
- Use data parallelism across nodes
- Ensure GPUs are NVLink-connected (check topology)

**Avoid:** TP across nodes (uses slower InfiniBand)`,
    applicableFor: {
      acceleratorTypes: ['gpu']
    },
    priority: 'medium'
  },
  {
    title: 'TPU-Specific: Leverage ICI and XLA',
    category: 'hardware',
    content: `TPUs excel with high data parallelism and XLA-optimized models.

**Best practices:**
- Use high DP (16, 32, 64+) to leverage pod interconnect
- Ensure batch shapes are powers of 2 and multiples of 128
- Use JAX or PyTorch/XLA for best MFU
- v5p: Use for ultra-large models with 4.8 TB/s ICI bandwidth

**MFU:** TPUs can achieve 55-65% MFU with proper XLA fusion.`,
    applicableFor: {
      acceleratorTypes: ['tpu']
    },
    priority: 'high'
  },

  // Communication optimization
  {
    title: 'Communication-Compute Overlap',
    category: 'communication',
    content: `Modern frameworks overlap gradient AllReduce with backward computation to hide communication latency.

**Techniques:**
- Gradient bucketing (FSDP, DDP)
- Asynchronous communication
- Pipelined micro-batches (PP)

**Expected overhead:**
- **Good:** <10% comm overhead
- **Acceptable:** 10-20%
- **Poor:** >20% (investigate parallelism strategy)

**Tool:** Use `torch.profiler` or `jax.profiler` to measure overlap.`,
    applicableFor: {
      parallelismStrategies: ['data_parallel', 'tensor_parallel']
    },
    priority: 'medium'
  },

  // General optimization
  {
    title: 'Achieving High MFU',
    category: 'optimization',
    content: `Model FLOPs Utilization (MFU) measures how efficiently you're using hardware compute.

**Target MFU:**
- **H100:** 50-60%
- **A100:** 40-50%
- **TPU v5p:** 55-65%

**Strategies to increase MFU:**
1. Increase batch size (until memory limit)
2. Use mixed precision (fp16/bf16)
3. Enable activation checkpointing if memory-bound
4. Use flash attention for long sequences
5. Reduce tensor parallelism if comm-bound
6. Profile and remove CPU bottlenecks

**Nanotron benchmark:** 7B model on 8xH100 achieves ~52% MFU.`,
    applicableFor: {
      acceleratorTypes: ['gpu', 'tpu']
    },
    priority: 'high'
  },
  {
    title: '3D Parallelism for 100B+ Models',
    category: 'parallelism',
    content: `For models >100B params, combine Data + Tensor + Pipeline parallelism (3D parallelism).

**Example: 175B model on 128 GPUs**
- DP=16 (across nodes)
- TP=4 (within node, 4 GPUs per node)
- PP=2 (split model vertically)

**Memory per GPU:** Model/TP/PP + Activations/PP
**Communication:** TP (high freq), PP (low freq), DP (per step)

**Recommendation:** Start with Megatron-LM or Nanotron configs for your model size.`,
    applicableFor: {
      acceleratorTypes: ['gpu'],
      modelSizes: '>100B'
    },
    priority: 'medium'
  }
];
