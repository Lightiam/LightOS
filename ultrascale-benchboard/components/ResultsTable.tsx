'use client';

import { useState } from 'react';
import { BenchmarkResult, HardwareProfile } from '../lib/types';
import { BarChart3, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface Props {
  results: BenchmarkResult[];
  hardwareProfiles: HardwareProfile[];
}

type SortField = 'tokensPerSecond' | 'mfu' | 'costPerMillionTokens' | 'totalMemoryGB';
type SortDirection = 'asc' | 'desc';

export default function ResultsTable({ results, hardwareProfiles }: Props) {
  const [sortField, setSortField] = useState<SortField>('tokensPerSecond');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedResults = [...results].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    const multiplier = sortDirection === 'asc' ? 1 : -1;
    return (aVal - bVal) * multiplier;
  });

  const getHardwareName = (hardwareId: string) => {
    return hardwareProfiles.find(h => h.id === hardwareId)?.name || hardwareId;
  };

  const getBottleneckIcon = (bottleneck: string) => {
    switch (bottleneck) {
      case 'compute':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
      case 'memory_bandwidth':
        return <AlertTriangle className="w-4 h-4 text-orange-400" />;
      case 'network':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default:
        return <TrendingUp className="w-4 h-4 text-green-400" />;
    }
  };

  const getBottleneckText = (bottleneck: string) => {
    switch (bottleneck) {
      case 'compute':
        return 'Compute Bound';
      case 'memory_bandwidth':
        return 'Memory BW Bound';
      case 'network':
        return 'Network Bound';
      default:
        return 'Balanced';
    }
  };

  const getMfuColor = (mfu: number) => {
    if (mfu >= 0.5) return 'text-green-400';
    if (mfu >= 0.4) return 'text-yellow-400';
    return 'text-orange-400';
  };

  if (results.length === 0) {
    return (
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-12 text-center">
        <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-slate-400 text-sm">
          Select hardware profiles from the left panel to see benchmark results
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">Benchmark Results</h2>
        </div>

        <div className="text-xs text-slate-400">
          {results.length} configuration{results.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">
                Hardware
              </th>
              <th
                className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide cursor-pointer hover:text-blue-400 transition-colors"
                onClick={() => handleSort('tokensPerSecond')}
              >
                <div className="flex items-center justify-end space-x-1">
                  <span>Tokens/Sec</span>
                  {sortField === 'tokensPerSecond' && (
                    sortDirection === 'desc' ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />
                  )}
                </div>
              </th>
              <th
                className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide cursor-pointer hover:text-blue-400 transition-colors"
                onClick={() => handleSort('mfu')}
              >
                <div className="flex items-center justify-end space-x-1">
                  <span>MFU</span>
                  {sortField === 'mfu' && (
                    sortDirection === 'desc' ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />
                  )}
                </div>
              </th>
              <th
                className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide cursor-pointer hover:text-blue-400 transition-colors"
                onClick={() => handleSort('costPerMillionTokens')}
              >
                <div className="flex items-center justify-end space-x-1">
                  <span>Cost/M Tokens</span>
                  {sortField === 'costPerMillionTokens' && (
                    sortDirection === 'desc' ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />
                  )}
                </div>
              </th>
              <th
                className="text-right py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide cursor-pointer hover:text-blue-400 transition-colors"
                onClick={() => handleSort('totalMemoryGB')}
              >
                <div className="flex items-center justify-end space-x-1">
                  <span>Memory (GB)</span>
                  {sortField === 'totalMemoryGB' && (
                    sortDirection === 'desc' ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />
                  )}
                </div>
              </th>
              <th className="text-left py-3 px-4 text-xs font-semibold text-slate-400 uppercase tracking-wide">
                Bottleneck
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedResults.map((result, idx) => (
              <tr
                key={result.hardwareId}
                className={`border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors ${
                  idx === 0 ? 'bg-blue-500/5' : ''
                }`}
              >
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    {idx === 0 && <TrendingUp className="w-4 h-4 text-green-400" />}
                    <span className="text-sm font-medium text-slate-200">
                      {getHardwareName(result.hardwareId)}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className="text-sm font-semibold text-slate-200">
                    {result.tokensPerSecond.toLocaleString()}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className={`text-sm font-semibold ${getMfuColor(result.mfu)}`}>
                    {(result.mfu * 100).toFixed(1)}%
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className="text-sm text-slate-300">
                    ${result.costPerMillionTokens.toFixed(2)}
                  </span>
                </td>
                <td className="py-3 px-4 text-right">
                  <span className="text-sm text-slate-300">
                    {result.totalMemoryGB.toFixed(1)}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center space-x-2">
                    {getBottleneckIcon(result.bottleneck)}
                    <span className="text-xs text-slate-400">
                      {getBottleneckText(result.bottleneck)}
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="p-3 bg-slate-700/30 rounded-lg">
          <div className="text-xs text-slate-400 mb-1">Best Throughput</div>
          <div className="text-lg font-semibold text-blue-400">
            {Math.max(...results.map(r => r.tokensPerSecond)).toLocaleString()} tok/s
          </div>
        </div>

        <div className="p-3 bg-slate-700/30 rounded-lg">
          <div className="text-xs text-slate-400 mb-1">Best MFU</div>
          <div className="text-lg font-semibold text-green-400">
            {(Math.max(...results.map(r => r.mfu)) * 100).toFixed(1)}%
          </div>
        </div>

        <div className="p-3 bg-slate-700/30 rounded-lg">
          <div className="text-xs text-slate-400 mb-1">Lowest Cost</div>
          <div className="text-lg font-semibold text-purple-400">
            ${Math.min(...results.map(r => r.costPerMillionTokens)).toFixed(2)}/M
          </div>
        </div>
      </div>

      {/* Performance Tips */}
      <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <div className="flex items-start space-x-2">
          <TrendingUp className="w-4 h-4 text-blue-400 mt-0.5" />
          <div className="flex-1">
            <div className="text-xs font-semibold text-blue-300 mb-1">Optimization Tips</div>
            <div className="text-xs text-blue-200/80">
              {results.some(r => r.mfu < 0.4) && (
                <div>• MFU below 40%: Try increasing batch size or enabling activation checkpointing</div>
              )}
              {results.some(r => r.bottleneck === 'network') && (
                <div>• Network bottleneck detected: Reduce tensor parallelism or increase data parallelism</div>
              )}
              {results.some(r => r.bottleneck === 'memory_bandwidth') && (
                <div>• Memory bandwidth bound: Consider mixed precision (fp16/bf16) or reduce batch size</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
