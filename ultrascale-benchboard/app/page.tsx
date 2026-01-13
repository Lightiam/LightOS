'use client';

import { useState, useEffect } from 'react';
import HardwarePanel from '../components/HardwarePanel';
import BenchmarkBuilder from '../components/BenchmarkBuilder';
import ResultsTable from '../components/ResultsTable';
import PlaybookPanel from '../components/PlaybookPanel';
import AIAssistant from '../components/AIAssistant';
import { defaultHardwareProfiles } from '../data/hardware';
import { exampleScenarios } from '../data/examples';
import { playbookGuidance } from '../data/playbook';
import { HardwareProfile, BenchmarkScenario, BenchmarkResult } from '../lib/types';
import { estimateBenchmark } from '../lib/estimator';
import { Cpu, Zap, BarChart3, BookOpen, MessageSquare } from 'lucide-react';

export default function Home() {
  const [hardwareProfiles, setHardwareProfiles] = useState<HardwareProfile[]>(defaultHardwareProfiles);
  const [currentScenario, setCurrentScenario] = useState<BenchmarkScenario>(exampleScenarios[0]);
  const [results, setResults] = useState<BenchmarkResult[]>([]);
  const [showAI, setShowAI] = useState(false);

  // Run benchmark estimation whenever scenario changes
  useEffect(() => {
    const newResults: BenchmarkResult[] = [];

    for (const hwId of currentScenario.hardwareProfiles) {
      const hardware = hardwareProfiles.find(h => h.id === hwId);
      if (!hardware) continue;

      const result = estimateBenchmark(
        currentScenario.id,
        currentScenario.model,
        currentScenario.parallelism,
        currentScenario.workload,
        hardware
      );

      newResults.push(result);
    }

    setResults(newResults);
  }, [currentScenario, hardwareProfiles]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur-sm bg-slate-900/80 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  UltraScale Benchboard
                </h1>
                <p className="text-xs text-slate-400">LLM Benchmark Comparison Tool</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-400 font-medium">Ready</span>
              </div>

              <button
                onClick={() => setShowAI(!showAI)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  showAI
                    ? 'bg-purple-500/20 border border-purple-500/50 text-purple-300'
                    : 'bg-slate-800/50 border border-slate-700 text-slate-300 hover:border-purple-500/50'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span className="text-sm font-medium">AI Assistant</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Panel - Hardware Catalog */}
          <div className="col-span-3">
            <HardwarePanel
              profiles={hardwareProfiles}
              selectedIds={currentScenario.hardwareProfiles}
              onSelectProfile={(id) => {
                setCurrentScenario(prev => ({
                  ...prev,
                  hardwareProfiles: prev.hardwareProfiles.includes(id)
                    ? prev.hardwareProfiles.filter(hid => hid !== id)
                    : [...prev.hardwareProfiles, id]
                }));
              }}
              onAddProfile={(profile) => setHardwareProfiles(prev => [...prev, profile])}
            />
          </div>

          {/* Center Panel - Benchmark Builder & Results */}
          <div className="col-span-6 space-y-6">
            <BenchmarkBuilder
              scenario={currentScenario}
              examples={exampleScenarios}
              onUpdate={setCurrentScenario}
              onLoadExample={(example) => setCurrentScenario(example)}
            />

            <ResultsTable
              results={results}
              hardwareProfiles={hardwareProfiles}
            />
          </div>

          {/* Right Panel - Playbook Guidance */}
          <div className="col-span-3">
            <PlaybookPanel
              guidance={playbookGuidance}
              currentScenario={currentScenario}
            />
          </div>
        </div>
      </div>

      {/* AI Assistant Overlay */}
      {showAI && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="w-full max-w-2xl">
            <AIAssistant
              scenario={currentScenario}
              results={results}
              onClose={() => setShowAI(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
