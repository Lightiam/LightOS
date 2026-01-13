import { ModelConfig, ParallelismConfig, WorkloadConfig, HardwareProfile, BenchmarkResult } from './types';

/**
 * Estimate theoretical FLOPs per training step for a transformer model
 * Based on: FLOPs ≈ 6 * params * tokens + 12 * layers * hidden_size^2 * tokens
 * This is the Nanotron/Megatron-LM formula
 */
export function estimateTheoreticalFlops(
  model: ModelConfig,
  batchSize: number,
  sequenceLength: number
): number {
  const params = model.parameters * 1e9; // Convert to actual number
  const tokens = batchSize * sequenceLength;

  // Forward + backward pass FLOPs
  // Forward: 2 * params * tokens (matrix multiplies)
  // Backward: 4 * params * tokens (gradients for weights and activations)
  const forwardBackwardFlops = 6 * params * tokens;

  // Additional attention FLOPs (if we have layer info)
  let attentionFlops = 0;
  if (model.numLayers && model.hiddenSize) {
    // Self-attention: Q, K, V projections + attention scores + output projection
    attentionFlops = 12 * model.numLayers * (model.hiddenSize ** 2) * tokens;
  }

  return forwardBackwardFlops + attentionFlops;
}

/**
 * Estimate memory requirements for model training
 * Based on Nanotron's memory model:
 * - Model parameters: params * bytes_per_param
 * - Gradients: params * bytes_per_param
 * - Optimizer states: params * bytes_per_param * 2 (Adam has 2 states)
 * - Activations: depends on batch size, sequence length, hidden size
 */
export function estimateMemoryRequirements(
  model: ModelConfig,
  workload: WorkloadConfig,
  parallelism: ParallelismConfig
): {
  modelMemoryGB: number;
  activationMemoryGB: number;
  optimizerMemoryGB: number;
  totalMemoryGB: number;
} {
  const params = model.parameters * 1e9;

  // Bytes per parameter based on precision
  const bytesPerParam = {
    fp32: 4,
    fp16: 2,
    bf16: 2,
    int8: 1
  }[model.precision];

  // Model weights
  let modelMemoryGB = (params * bytesPerParam) / (1024 ** 3);

  // Gradients (same size as model)
  let gradientMemoryGB = modelMemoryGB;

  // Optimizer states (for Adam: 2x model size for momentum and variance)
  let optimizerMemoryGB = modelMemoryGB * 2;

  // Apply tensor parallelism reduction
  if (parallelism.tensorParallel > 1) {
    modelMemoryGB /= parallelism.tensorParallel;
    gradientMemoryGB /= parallelism.tensorParallel;
    optimizerMemoryGB /= parallelism.tensorParallel;
  }

  // Activations (depends on batch size and sequence length)
  const microBatchSize = workload.microBatchSize || workload.batchSize;
  const hiddenSize = model.hiddenSize || (model.parameters * 1e9 / (model.numLayers || 32) / 4) ** 0.5;
  const numLayers = model.numLayers || 32;

  // Activation memory per layer: batch * seq * hidden * bytes * 12 (various activations)
  let activationMemoryGB = (microBatchSize * model.contextLength * hiddenSize * numLayers * bytesPerParam * 12) / (1024 ** 3);

  // Reduce with activation checkpointing
  if (parallelism.activationCheckpointing) {
    activationMemoryGB = activationMemoryGB / Math.sqrt(numLayers);
  }

  // Reduce with pipeline parallelism
  if (parallelism.pipelineParallel > 1) {
    activationMemoryGB /= parallelism.pipelineParallel;
  }

  const totalMemoryGB = modelMemoryGB + gradientMemoryGB + optimizerMemoryGB + activationMemoryGB;

  return {
    modelMemoryGB: modelMemoryGB + gradientMemoryGB, // Combined for display
    activationMemoryGB,
    optimizerMemoryGB,
    totalMemoryGB
  };
}

/**
 * Estimate communication overhead for data parallelism (allreduce)
 * Based on: time = (2 * model_size * (DP - 1) / DP) / bandwidth
 */
export function estimateCommunicationTime(
  modelSizeGB: number,
  parallelism: ParallelismConfig,
  interconnectBandwidthGBps: number
): number {
  // AllReduce for data parallelism
  if (parallelism.dataParallel <= 1) {
    return 0;
  }

  const dp = parallelism.dataParallel;
  const dataToTransferGB = (2 * modelSizeGB * (dp - 1)) / dp;

  // Ring allreduce time in milliseconds
  const allReduceTimeMs = (dataToTransferGB / interconnectBandwidthGBps) * 1000;

  return allReduceTimeMs;
}

/**
 * Main benchmark estimation function
 * Estimates performance metrics for a given model + hardware + parallelism config
 */
export function estimateBenchmark(
  scenarioId: string,
  model: ModelConfig,
  parallelism: ParallelismConfig,
  workload: WorkloadConfig,
  hardware: HardwareProfile
): BenchmarkResult {
  // Calculate batch parameters
  const globalBatchSize = workload.batchSize;
  const microBatchSize = workload.microBatchSize || globalBatchSize;
  const seqLength = model.contextLength;

  // Total devices
  const totalDevices = parallelism.dataParallel * parallelism.tensorParallel * parallelism.pipelineParallel;

  // Theoretical FLOPs per step
  const theoreticalFlopsPerStep = estimateTheoreticalFlops(model, microBatchSize, seqLength);

  // Memory estimation
  const memory = estimateMemoryRequirements(model, workload, parallelism);

  // MFU (Model FLOPs Utilization) - realistic estimates based on hardware type
  // GPUs typically achieve 30-50% MFU, TPUs can achieve 50-65% with XLA
  let estimatedMfu = 0.35; // Default for GPUs
  if (hardware.type === 'tpu') {
    estimatedMfu = 0.55; // TPUs with XLA
  }

  // Adjust MFU based on configuration
  if (parallelism.activationCheckpointing) {
    estimatedMfu *= 0.95; // Slight overhead
  }
  if (parallelism.tensorParallel > 1) {
    estimatedMfu *= 0.93; // Communication overhead
  }
  if (memory.totalMemoryGB > hardware.vramSizeGB * 0.95) {
    estimatedMfu *= 0.7; // Severe memory pressure
  }

  // Compute time per step
  const achievedTflops = hardware.fp16Tflops * estimatedMfu;
  const computeTimeMs = (theoreticalFlopsPerStep / (achievedTflops * 1e12)) * 1000;

  // Communication time
  const commTimeMs = estimateCommunicationTime(
    memory.modelMemoryGB,
    parallelism,
    hardware.interconnectBandwidthGBps
  );

  // Total step time
  const totalStepTimeMs = computeTimeMs + commTimeMs;

  // Throughput
  const tokensPerSecond = (globalBatchSize * seqLength) / (totalStepTimeMs / 1000);

  // Cost calculation
  const stepsPerHour = (3600 * 1000) / totalStepTimeMs;
  const tokensPerHour = tokensPerSecond * 3600;
  const costPerMillionTokens = (hardware.costPerHour * totalDevices * 1e6) / tokensPerHour;

  // Memory utilization
  const memoryUtilization = (memory.totalMemoryGB / hardware.vramSizeGB) * 100;

  // Bottleneck analysis
  let bottleneck: 'compute' | 'memory_bandwidth' | 'network' | 'balanced' = 'balanced';
  if (memoryUtilization > 95) {
    bottleneck = 'memory_bandwidth';
  } else if (commTimeMs > computeTimeMs) {
    bottleneck = 'network';
  } else if (computeTimeMs > commTimeMs * 3) {
    bottleneck = 'compute';
  }

  // Warnings
  const warnings: string[] = [];
  if (memoryUtilization > 100) {
    warnings.push('⚠️ Out of memory! Reduce batch size or enable activation checkpointing.');
  } else if (memoryUtilization > 95) {
    warnings.push('⚠️ Very high memory usage. Consider reducing batch size.');
  }

  if (parallelism.tensorParallel > 8 && hardware.type === 'gpu') {
    warnings.push('⚠️ High tensor parallelism may cause communication overhead.');
  }

  if (parallelism.dataParallel > 512) {
    warnings.push('⚠️ Very large data parallelism. Ensure sufficient interconnect bandwidth.');
  }

  if (estimatedMfu < 0.25) {
    warnings.push('⚠️ Low MFU detected. Check memory pressure and parallelism strategy.');
  }

  return {
    scenarioId,
    hardwareId: hardware.id,
    theoreticalFlopsPerStep,
    estimatedStepTimeMs: totalStepTimeMs,
    tokensPerSecond,
    mfu: estimatedMfu,
    ...memory,
    memoryUtilization,
    costPerMillionTokens,
    costPerHour: hardware.costPerHour * totalDevices,
    allReduceTimeMs: commTimeMs,
    communicationOverhead: (commTimeMs / totalStepTimeMs) * 100,
    bottleneck,
    warnings
  };
}
