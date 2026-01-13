'use client';

import { BenchmarkScenario } from '../lib/types';
import { Settings, Play, RotateCcw } from 'lucide-react';

interface Props {
  scenario: BenchmarkScenario;
  examples: BenchmarkScenario[];
  onUpdate: (scenario: BenchmarkScenario) => void;
  onLoadExample: (example: BenchmarkScenario) => void;
}

export default function BenchmarkBuilder({ scenario, examples, onUpdate, onLoadExample }: Props) {
  const updateModel = (updates: Partial<typeof scenario.model>) => {
    onUpdate({
      ...scenario,
      model: { ...scenario.model, ...updates }
    });
  };

  const updateParallelism = (updates: Partial<typeof scenario.parallelism>) => {
    onUpdate({
      ...scenario,
      parallelism: { ...scenario.parallelism, ...updates }
    });
  };

  const updateWorkload = (updates: Partial<typeof scenario.workload>) => {
    onUpdate({
      ...scenario,
      workload: { ...scenario.workload, ...updates }
    });
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">Benchmark Builder</h2>
        </div>

        <div className="flex items-center space-x-2">
          <select
            className="px-3 py-1.5 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-300"
            value={scenario.id}
            onChange={(e) => {
              const example = examples.find(ex => ex.id === e.target.value);
              if (example) onLoadExample(example);
            }}
          >
            {examples.map(ex => (
              <option key={ex.id} value={ex.id}>{ex.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-6">
        {/* Model Configuration */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
            Model Configuration
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Model Name</label>
              <input
                type="text"
                value={scenario.model.name}
                onChange={(e) => updateModel({ name: e.target.value })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Parameters (Billions)</label>
              <input
                type="number"
                value={scenario.model.parameters}
                onChange={(e) => updateModel({ parameters: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Architecture</label>
              <select
                value={scenario.model.architectureType}
                onChange={(e) => updateModel({ architectureType: e.target.value as 'dense' | 'moe' })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="dense">Dense</option>
                <option value="moe">Mixture of Experts (MoE)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Precision</label>
              <select
                value={scenario.model.precision}
                onChange={(e) => updateModel({ precision: e.target.value as any })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="fp32">FP32</option>
                <option value="fp16">FP16</option>
                <option value="bf16">BF16</option>
                <option value="int8">INT8</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Context Length</label>
              <input
                type="number"
                value={scenario.model.contextLength}
                onChange={(e) => updateModel({ contextLength: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Hidden Size</label>
              <input
                type="number"
                value={scenario.model.hiddenSize}
                onChange={(e) => updateModel({ hiddenSize: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Parallelism Configuration */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
            Parallelism Strategy
          </h3>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Data Parallel (DP)</label>
              <input
                type="number"
                value={scenario.parallelism.dataParallel}
                onChange={(e) => updateParallelism({ dataParallel: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Tensor Parallel (TP)</label>
              <input
                type="number"
                value={scenario.parallelism.tensorParallel}
                onChange={(e) => updateParallelism({ tensorParallel: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Pipeline Parallel (PP)</label>
              <input
                type="number"
                value={scenario.parallelism.pipelineParallel}
                onChange={(e) => updateParallelism({ pipelineParallel: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Gradient Accum. Steps</label>
              <input
                type="number"
                value={scenario.parallelism.gradientAccumulationSteps}
                onChange={(e) => updateParallelism({ gradientAccumulationSteps: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="col-span-2 flex items-center space-x-4 pt-5">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={scenario.parallelism.activationCheckpointing}
                  onChange={(e) => updateParallelism({ activationCheckpointing: e.target.checked })}
                  className="w-4 h-4 bg-slate-700 border-slate-600 rounded"
                />
                <span className="text-sm text-slate-300">Activation Checkpointing</span>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={scenario.parallelism.sequenceParallel}
                  onChange={(e) => updateParallelism({ sequenceParallel: e.target.checked })}
                  className="w-4 h-4 bg-slate-700 border-slate-600 rounded"
                />
                <span className="text-sm text-slate-300">Sequence Parallel</span>
              </label>
            </div>
          </div>

          <div className="mt-3 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <div className="text-xs text-blue-300">
              <strong>Total GPUs/TPUs:</strong> {scenario.parallelism.dataParallel * scenario.parallelism.tensorParallel * scenario.parallelism.pipelineParallel}
            </div>
          </div>
        </div>

        {/* Workload Configuration */}
        <div>
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Workload Configuration
          </h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Workload Type</label>
              <select
                value={scenario.workload.type}
                onChange={(e) => updateWorkload({ type: e.target.value as 'training' | 'inference' })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="training">Training</option>
                <option value="inference">Inference</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Global Batch Size</label>
              <input
                type="number"
                value={scenario.workload.batchSize}
                onChange={(e) => updateWorkload({ batchSize: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Micro Batch Size</label>
              <input
                type="number"
                value={scenario.workload.microBatchSize}
                onChange={(e) => updateWorkload({ microBatchSize: parseInt(e.target.value) })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs text-slate-400 mb-1">Target Metric</label>
              <select
                value={scenario.workload.targetMetric}
                onChange={(e) => updateWorkload({ targetMetric: e.target.value as any })}
                className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="tokens_per_second">Tokens/Second</option>
                <option value="mfu">Model FLOPs Utilization</option>
                <option value="cost_per_token">Cost per Token</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
