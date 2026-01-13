'use client';

import { useState } from 'react';
import { PlaybookGuidance, BenchmarkScenario } from '../lib/types';
import { BookOpen, ChevronDown, ChevronRight, Cpu, MemoryStick, Network, Zap } from 'lucide-react';

interface Props {
  guidance: PlaybookGuidance[];
  currentScenario: BenchmarkScenario;
}

export default function PlaybookPanel({ guidance, currentScenario }: Props) {
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set([0]));
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedIds(newExpanded);
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'parallelism':
        return <Cpu className="w-4 h-4" />;
      case 'memory':
        return <MemoryStick className="w-4 h-4" />;
      case 'hardware':
        return <Zap className="w-4 h-4" />;
      case 'communication':
        return <Network className="w-4 h-4" />;
      default:
        return <BookOpen className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-green-500/50 bg-green-500/10';
      case 'medium':
        return 'border-blue-500/50 bg-blue-500/10';
      case 'low':
        return 'border-slate-500/50 bg-slate-500/10';
      default:
        return 'border-slate-500/50 bg-slate-500/10';
    }
  };

  // Filter guidance based on current scenario
  const filteredGuidance = guidance.filter(item => {
    if (selectedCategory !== 'all' && item.category !== selectedCategory) {
      return false;
    }

    // Check if guidance is applicable
    if (item.applicableFor) {
      const { acceleratorTypes, modelSizes, parallelismStrategies } = item.applicableFor;

      // For now, show all items - in a real app, you'd filter based on scenario
      // This is a placeholder for more sophisticated filtering
    }

    return true;
  });

  const categories = [
    { id: 'all', name: 'All' },
    { id: 'parallelism', name: 'Parallelism' },
    { id: 'memory', name: 'Memory' },
    { id: 'hardware', name: 'Hardware' },
    { id: 'communication', name: 'Communication' },
    { id: 'optimization', name: 'Optimization' }
  ];

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">Playbook</h2>
        </div>
      </div>

      {/* Category Filter */}
      <div className="mb-4">
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="w-full px-3 py-2 bg-slate-700/50 border border-slate-600 rounded-lg text-sm text-slate-300 focus:outline-none focus:border-blue-500"
        >
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>
      </div>

      {/* Guidance Items */}
      <div className="flex-1 overflow-y-auto space-y-3 scrollbar-hide">
        {filteredGuidance.map((item, index) => {
          const isExpanded = expandedIds.has(index);

          return (
            <div
              key={index}
              className={`border rounded-lg overflow-hidden transition-all ${getPriorityColor(item.priority)}`}
            >
              <button
                onClick={() => toggleExpanded(index)}
                className="w-full flex items-start justify-between p-3 hover:bg-slate-700/30 transition-colors"
              >
                <div className="flex items-start space-x-2 flex-1">
                  <div className="mt-0.5 text-slate-400">
                    {getCategoryIcon(item.category)}
                  </div>
                  <div className="text-left flex-1">
                    <div className="text-sm font-semibold text-slate-200">
                      {item.title}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5 capitalize">
                      {item.category}
                      {item.priority === 'high' && (
                        <span className="ml-2 px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded text-xs">
                          High Priority
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="ml-2">
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </button>

              {isExpanded && (
                <div className="px-3 pb-3">
                  <div className="pt-2 border-t border-slate-700/50">
                    <div className="text-xs text-slate-300 whitespace-pre-line leading-relaxed">
                      {item.content}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Context Info */}
      <div className="mt-4 pt-4 border-t border-slate-700/50">
        <div className="text-xs text-slate-400 mb-2">Current Configuration</div>
        <div className="space-y-1 text-xs text-slate-300">
          <div className="flex justify-between">
            <span className="text-slate-400">Model:</span>
            <span className="font-medium">{currentScenario.model.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Parallelism:</span>
            <span className="font-medium">
              DP={currentScenario.parallelism.dataParallel}
              TP={currentScenario.parallelism.tensorParallel}
              PP={currentScenario.parallelism.pipelineParallel}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Batch Size:</span>
            <span className="font-medium">{currentScenario.workload.batchSize}</span>
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="mt-3 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <div className="text-xs font-semibold text-blue-300 mb-1">Quick Tips</div>
        <ul className="text-xs text-blue-200/80 space-y-1">
          {currentScenario.parallelism.tensorParallel > 1 && (
            <li>• TP={currentScenario.parallelism.tensorParallel}: Use NVLink-connected GPUs within node</li>
          )}
          {currentScenario.parallelism.pipelineParallel > 1 && (
            <li>• PP={currentScenario.parallelism.pipelineParallel}: Tune micro-batch size to minimize bubbles</li>
          )}
          {currentScenario.model.parameters > 70 && (
            <li>• 70B+ model: Enable activation checkpointing for memory</li>
          )}
          {!currentScenario.parallelism.activationCheckpointing && currentScenario.model.parameters > 7 && (
            <li>• Consider activation checkpointing to fit larger batches</li>
          )}
        </ul>
      </div>
    </div>
  );
}
