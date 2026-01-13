import { BenchmarkScenario } from '../lib/types';

export const exampleScenarios: BenchmarkScenario[] = [
  {
    id: 'llama-7b-training',
    name: 'LLaMA 7B Training',
    model: {
      name: 'LLaMA 7B',
      parameters: 7,
      architectureType: 'dense',
      contextLength: 2048,
      precision: 'bf16',
      hiddenSize: 4096,
      numLayers: 32,
      numHeads: 32,
      vocabularySize: 32000
    },
    parallelism: {
      dataParallel: 8,
      tensorParallel: 1,
      pipelineParallel: 1,
      gradientAccumulationSteps: 1,
      activationCheckpointing: false,
      sequenceParallel: false
    },
    workload: {
      type: 'training',
      batchSize: 256,
      microBatchSize: 32,
      targetMetric: 'tokens_per_second'
    },
    hardwareProfiles: ['nvidia-a100-80gb', 'nvidia-h100-80gb', 'google-tpu-v4', 'google-tpu-v5p']
  },
  {
    id: 'llama-70b-training',
    name: 'LLaMA 70B Training (3D Parallelism)',
    model: {
      name: 'LLaMA 70B',
      parameters: 70,
      architectureType: 'dense',
      contextLength: 4096,
      precision: 'bf16',
      hiddenSize: 8192,
      numLayers: 80,
      numHeads: 64,
      vocabularySize: 32000
    },
    parallelism: {
      dataParallel: 16,
      tensorParallel: 4,
      pipelineParallel: 2,
      gradientAccumulationSteps: 4,
      activationCheckpointing: true,
      sequenceParallel: true
    },
    workload: {
      type: 'training',
      batchSize: 1024,
      microBatchSize: 8,
      targetMetric: 'tokens_per_second'
    },
    hardwareProfiles: ['nvidia-h100-80gb', 'google-tpu-v5p']
  },
  {
    id: 'mixtral-8x7b-training',
    name: 'Mixtral 8x7B (MoE) Training',
    model: {
      name: 'Mixtral 8x7B',
      parameters: 46.7, // 8 experts, 2 active
      architectureType: 'moe',
      contextLength: 32768,
      precision: 'bf16',
      hiddenSize: 4096,
      numLayers: 32,
      numHeads: 32,
      vocabularySize: 32000
    },
    parallelism: {
      dataParallel: 16,
      tensorParallel: 2,
      pipelineParallel: 1,
      gradientAccumulationSteps: 2,
      activationCheckpointing: true,
      sequenceParallel: false
    },
    workload: {
      type: 'training',
      batchSize: 512,
      microBatchSize: 16,
      targetMetric: 'tokens_per_second'
    },
    hardwareProfiles: ['nvidia-h100-80gb', 'google-tpu-v5p']
  }
];
