'use client';

import { HardwareProfile } from '../lib/types';
import { Cpu, Plus, Check } from 'lucide-react';

interface Props {
  profiles: HardwareProfile[];
  selectedIds: string[];
  onSelectProfile: (id: string) => void;
  onAddProfile: (profile: HardwareProfile) => void;
}

export default function HardwarePanel({ profiles, selectedIds, onSelectProfile, onAddProfile }: Props) {
  const gpus = profiles.filter(p => p.type === 'gpu');
  const tpus = profiles.filter(p => p.type === 'tpu');
  const others = profiles.filter(p => p.type === 'other');

  const renderProfile = (profile: HardwareProfile) => {
    const isSelected = selectedIds.includes(profile.id);

    return (
      <button
        key={profile.id}
        onClick={() => onSelectProfile(profile.id)}
        className={`w-full text-left p-3 rounded-lg border transition-all ${
          isSelected
            ? 'bg-blue-500/20 border-blue-500/50'
            : 'bg-slate-800/30 border-slate-700/50 hover:border-blue-500/30'
        }`}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold text-slate-200">{profile.name}</span>
              {isSelected && <Check className="w-4 h-4 text-blue-400" />}
            </div>
            <div className="mt-1 space-y-0.5">
              <div className="text-xs text-slate-400">
                {profile.fp16Tflops} TFLOPS (FP16)
              </div>
              <div className="text-xs text-slate-400">
                {profile.vramSizeGB} GB VRAM
              </div>
              <div className="text-xs text-blue-400 font-medium">
                ${profile.costPerHour}/hr
              </div>
            </div>
          </div>
        </div>
      </button>
    );
  };

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Cpu className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">Hardware Catalog</h2>
        </div>
      </div>

      <div className="space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto scrollbar-hide">
        {/* NVIDIA GPUs */}
        <div>
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
            NVIDIA GPUs
          </div>
          <div className="space-y-2">
            {gpus.map(renderProfile)}
          </div>
        </div>

        {/* Google TPUs */}
        <div>
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
            Google TPUs
          </div>
          <div className="space-y-2">
            {tpus.map(renderProfile)}
          </div>
        </div>

        {/* Other Accelerators */}
        {others.length > 0 && (
          <div>
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
              Other Accelerators
            </div>
            <div className="space-y-2">
              {others.map(renderProfile)}
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-700/50">
        <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-slate-700/50 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm text-slate-300 transition-colors">
          <Plus className="w-4 h-4" />
          <span>Add Custom Profile</span>
        </button>
      </div>
    </div>
  );
}
