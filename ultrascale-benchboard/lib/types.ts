// Hardware profile types
export type AcceleratorType = 'gpu' | 'tpu' | 'other';

export interface HardwareProfile {
  id: string;
  name: string;
  type: AcceleratorType;
  vendor: string;

  // Compute specs
  smCount?: number; // For GPUs
  fp16Tflops: number;
  fp32Tflops?: number;
  int8Tops?: number;

  // Memory specs
  hbmBandwidthGBps: number;
  vramSizeGB: number;

  // Network
  interconnect: string;
  interconnectBandwidthGBps: number;

  // TPU specific
  podSize?: number;

  // Cost
  costPerHour: number;

  // Framework support
  frameworks: string[];
  notes?: string;
}

// Model configuration
export interface ModelConfig {
  name: string;
  parameters: number; // in billions
  architectureType: 'dense' | 'moe';
  contextLength: number;
  precision: 'fp32' | 'fp16' | 'bf16' | 'int8';
  hiddenSize?: number;
  numLayers?: number;
  numHeads?: number;
  vocabularySize?: number;
}

// Parallelism configuration
export interface ParallelismConfig {
  dataParallel: number;
  tensorParallel: number;
  pipelineParallel: number;
  gradientAccumulationSteps: number;
  activationCheckpointing: boolean;
  sequenceParallel: boolean;
}

// Workload configuration
export interface WorkloadConfig {
  type: 'training' | 'inference';
  batchSize: number;
  microBatchSize?: number;
  targetMetric: 'tokens_per_second' | 'samples_per_second' | 'latency';
}

// Benchmark scenario
export interface BenchmarkScenario {
  id: string;
  name: string;
  model: ModelConfig;
  parallelism: ParallelismConfig;
  workload: WorkloadConfig;
  hardwareProfiles: string[]; // IDs of hardware profiles to compare
}

// Benchmark results
export interface BenchmarkResult {
  scenarioId: string;
  hardwareId: string;

  // Performance metrics
  theoreticalFlopsPerStep: number;
  estimatedStepTimeMs: number;
  tokensPerSecond: number;
  mfu: number; // Model FLOPs Utilization (0-1)

  // Memory estimates
  modelMemoryGB: number;
  activationMemoryGB: number;
  optimizerMemoryGB: number;
  totalMemoryGB: number;
  memoryUtilization: number; // % of VRAM used

  // Cost
  costPerMillionTokens: number;
  costPerHour: number;

  // Communication
  allReduceTimeMs?: number;
  communicationOverhead?: number; // % of step time

  // Bottleneck analysis
  bottleneck: 'compute' | 'memory_bandwidth' | 'network' | 'balanced';
  warnings: string[];
}

// Real benchmark run (for future integration)
export interface BenchmarkRun {
  id: string;
  scenario: BenchmarkScenario;
  hardwareId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;

  // Real metrics (when available)
  actualTokensPerSecond?: number;
  actualMfu?: number;
  actualMemoryUsageGB?: number;

  // Logs and traces
  logs?: string[];
  traces?: any;
}

// Playbook guidance
export interface PlaybookGuidance {
  title: string;
  category: 'parallelism' | 'memory' | 'communication' | 'hardware' | 'optimization';
  content: string;
  applicableFor: {
    acceleratorTypes?: AcceleratorType[];
    modelSizes?: string; // e.g., "7B-70B"
    parallelismStrategies?: string[];
  };
  priority: 'high' | 'medium' | 'low';
}
