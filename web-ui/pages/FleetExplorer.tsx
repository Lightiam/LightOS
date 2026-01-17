
import React, { useState, useMemo } from 'react';
import { 
  MapPin, Thermometer, Wind, Zap, AlertCircle, 
  CheckCircle2, Activity, Filter, Layers, 
  TrendingUp, TrendingDown, RefreshCw, Plus, Minus,
  BarChart3, Info, X, Terminal, RotateCcw, ShieldCheck,
  Search
} from 'lucide-react';
import { INITIAL_SITES, INITIAL_RACKS, MOCK_NODES } from '../services/mockData';
import { NodeMetrics } from '../types';

type HardwareFilter = 'ALL' | 'H100' | 'TPU';

const FleetExplorer: React.FC = () => {
  const [selectedSite, setSelectedSite] = useState(INITIAL_SITES[0]);
  const [selectedRack, setSelectedRack] = useState(INITIAL_RACKS[0]);
  const [hwFilter, setHwFilter] = useState<HardwareFilter>('ALL');
  const [activeNode, setActiveNode] = useState<NodeMetrics | null>(null);
  
  // Capacity Planning State
  const [isSimulating, setIsSimulating] = useState(false);
  const [h100Delta, setH100Delta] = useState(0);
  const [tpuDelta, setTpuDelta] = useState(0);

  const filteredNodes = MOCK_NODES.filter(node => {
    if (hwFilter === 'ALL') return true;
    if (hwFilter === 'H100') return node.type.includes('H100');
    if (hwFilter === 'TPU') return node.type.includes('TPU');
    return true;
  });

  // Simulation Logic
  const simulationMetrics = useMemo(() => {
    const baseGpus = 1240;
    const baseTpus = 512;
    const baseUtil = 84.5;

    const newGpus = baseGpus + h100Delta;
    const newTpus = baseTpus + tpuDelta;
    const totalNew = newGpus + newTpus;
    const totalBase = baseGpus + baseTpus;

    const projectedUtil = (baseUtil * totalBase) / totalNew;
    const hourlyDelta = (h100Delta * 3.20) + (tpuDelta * 2.80);
    const monthlyDelta = hourlyDelta * 24 * 30;

    return {
      projectedUtil: Math.min(100, Math.max(0, projectedUtil)),
      hourlyDelta,
      monthlyDelta,
      totalNew
    };
  }, [h100Delta, tpuDelta]);

  const getPueColor = (pue: number) => {
    if (pue < 1.12) return 'text-green-400';
    if (pue < 1.20) return 'text-yellow-400';
    return 'text-red-400';
  };

  const handleExpansionSubmission = () => {
    alert(`Expansion Request Submitted:\n- GPUs: ${h100Delta}\n- TPUs: ${tpuDelta}\n- Est. Monthly Budget Impact: $${simulationMetrics.monthlyDelta.toFixed(2)}`);
    setIsSimulating(false);
  };

  return (
    <div className={`space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12 transition-all ${isSimulating ? 'ring-1 ring-green-500/20 rounded-3xl p-2' : ''}`}>
      {/* Site & Simulation Toggle */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide max-w-full lg:max-w-[70%]">
          {INITIAL_SITES.map(site => (
            <button 
              key={site.id}
              onClick={() => setSelectedSite(site)}
              className={`flex-shrink-0 flex items-center gap-4 p-4 rounded-2xl border transition-all ${
                selectedSite.id === site.id 
                  ? 'bg-slate-800 border-[#00FF41]/50 shadow-lg shadow-green-500/5' 
                  : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center">
                <MapPin className={`w-6 h-6 ${selectedSite.id === site.id ? 'text-[#00FF41]' : 'text-slate-500'}`} />
              </div>
              <div className="text-left pr-4">
                <h3 className="font-bold text-white text-sm">{site.name}</h3>
                <p className="text-[10px] text-slate-500 uppercase tracking-tighter">{site.region}</p>
              </div>
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsSimulating(!isSimulating)}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm transition-all border ${
              isSimulating 
                ? 'bg-green-500/10 border-green-500 text-white shadow-[0_0_20px_rgba(0,255,65,0.2)]' 
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600 hover:bg-slate-700/50'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${isSimulating ? 'animate-spin' : ''}`} />
            {isSimulating ? 'Exit Capacity Planner' : 'Capacity Planner'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
        {/* Sidebar: Analytics or Simulator */}
        <div className="space-y-6">
          {isSimulating ? (
            <div className="glass-panel rounded-2xl p-6 border-green-500/30 bg-green-500/5 space-y-6 animate-in slide-in-from-left duration-300">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-500/20">
                  <BarChart3 className="w-5 h-5 text-green-400" />
                </div>
                <h2 className="text-lg font-bold text-white tracking-tight">Expansion Simulator</h2>
              </div>

              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-xs font-bold text-slate-400 mb-2 uppercase">
                    <span>H100 Delta</span>
                    <span className={h100Delta >= 0 ? 'text-green-400' : 'text-red-400'}>{h100Delta > 0 ? '+' : ''}{h100Delta}</span>
                  </div>
                  <input type="range" min="-128" max="1024" step="8" value={h100Delta} onChange={e => setH100Delta(parseInt(e.target.value))} className="w-full h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer accent-green-500" />
                </div>
                <div>
                  <div className="flex justify-between text-xs font-bold text-slate-400 mb-2 uppercase">
                    <span>TPU Delta</span>
                    <span className={tpuDelta >= 0 ? 'text-blue-400' : 'text-red-400'}>{tpuDelta > 0 ? '+' : ''}{tpuDelta}</span>
                  </div>
                  <input type="range" min="-128" max="1024" step="8" value={tpuDelta} onChange={e => setTpuDelta(parseInt(e.target.value))} className="w-full h-1.5 bg-slate-700 rounded-full appearance-none cursor-pointer accent-blue-500" />
                </div>
              </div>

              <div className="pt-6 border-t border-green-500/20 space-y-4">
                <div className="bg-slate-900/50 p-4 rounded-xl border border-green-500/10">
                  <p className="text-[10px] font-bold text-slate-500 uppercase">Util Projection</p>
                  <p className="text-2xl font-bold text-white">{simulationMetrics.projectedUtil.toFixed(1)}%</p>
                </div>
                <button 
                  onClick={handleExpansionSubmission}
                  className="w-full py-3 aurora-gradient text-black font-bold text-xs rounded-xl shadow-lg shadow-green-500/20 hover:scale-[1.02] transition-all"
                >
                  Confirm Infrastructure Growth
                </button>
              </div>
            </div>
          ) : (
            <div className="glass-panel rounded-2xl p-6 flex flex-col justify-between space-y-6">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Activity className="w-5 h-5 text-[#00FF41]" />
                Site Telemetry
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/50 text-center">
                  <p className="text-[10px] font-bold text-slate-500 uppercase">Load</p>
                  <p className="text-lg font-bold text-white">1,240 <span className="text-xs text-slate-500">kW</span></p>
                </div>
                <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/50 text-center">
                  <p className="text-[10px] font-bold text-slate-500 uppercase">Temp</p>
                  <p className="text-lg font-bold text-white">24.5 <span className="text-xs text-slate-500">°C</span></p>
                </div>
              </div>
              <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-[10px] font-bold text-slate-500 uppercase">Site PUE</span>
                  <span className={`text-sm font-bold ${getPueColor(selectedSite.pue)}`}>{selectedSite.pue}</span>
                </div>
                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden flex">
                  <div className="h-full bg-green-500" style={{width: '60%'}}></div>
                  <div className="h-full bg-yellow-500" style={{width: '20%'}}></div>
                </div>
              </div>
            </div>
          )}

          {/* Racks List */}
          <div className="glass-panel rounded-2xl p-6 border-slate-800/50">
            <h3 className="text-xs font-bold text-slate-500 uppercase mb-4 tracking-widest">Site Racks</h3>
            <div className="space-y-2">
              {INITIAL_RACKS.map(rack => (
                <button
                  key={rack.id}
                  onClick={() => setSelectedRack(rack)}
                  className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all ${
                    selectedRack.id === rack.id 
                      ? 'bg-slate-800 border-[#00FF41]/30' 
                      : 'border-transparent hover:bg-slate-800/20'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${rack.status === 'OK' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                    <span className="text-xs font-bold text-white">{rack.name}</span>
                  </div>
                  <span className={`text-xs font-mono font-bold ${getPueColor(rack.pue)}`}>{rack.pue}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Node View */}
        <div className="xl:col-span-3 space-y-6">
          <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="flex items-center gap-6">
                <div>
                  <h2 className="text-xl font-bold text-white tracking-tight">{selectedRack.name} View</h2>
                  <p className="text-[10px] font-bold text-slate-500 mt-1 uppercase tracking-widest">{filteredNodes.length} Total Nodes</p>
                </div>
                <div className="hidden md:flex items-center gap-4 border-l border-slate-800 pl-6">
                  <div>
                    <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Rack PUE Gauge</p>
                    <div className="flex items-end gap-1 h-4">
                      {[1,2,3,4,5,6].map(i => (
                        <div key={i} className={`w-1.5 rounded-sm transition-all duration-300 ${selectedRack.pue > 1.0 + (i*0.04) ? 'bg-green-500 shadow-[0_0_5px_#22c55e]' : 'bg-slate-800'}`} style={{height: `${i*16}%`}}></div>
                      ))}
                      <span className={`ml-2 text-sm font-mono font-bold ${getPueColor(selectedRack.pue)}`}>{selectedRack.pue}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Hardware Filter */}
              <div className="flex items-center bg-slate-900/50 p-1 rounded-xl border border-slate-800">
                {(['ALL', 'H100', 'TPU'] as const).map(type => (
                  <button
                    key={type}
                    onClick={() => setHwFilter(type)}
                    className={`px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all ${
                      hwFilter === type ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    {type === 'ALL' ? 'All' : type === 'H100' ? 'GPU' : 'TPU'}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
              {filteredNodes.map(node => (
                <button 
                  key={node.id} 
                  onClick={() => setActiveNode(node)}
                  className="bg-slate-900/40 border border-slate-800/50 rounded-2xl p-5 hover:border-[#00FF41]/40 transition-all hover:bg-slate-800/40 text-left group relative"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-sm font-bold text-white group-hover:text-[#00FF41] transition-colors">{node.name}</h4>
                      <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-0.5">{node.type}</p>
                    </div>
                    {node.health === 'OK' ? (
                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-yellow-500" />
                    )}
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-[10px] font-bold text-slate-500 mb-1.5">
                        <span>Utilization</span>
                        <span className="text-slate-300">{node.utilization.toFixed(0)}%</span>
                      </div>
                      <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-700 ${node.utilization > 90 ? 'bg-red-500' : 'bg-[#00FF41]'}`} 
                          style={{ width: `${node.utilization}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 mt-2">
                      <span className="flex items-center gap-1"><Zap className="w-3 h-3 text-yellow-500" /> {node.power.toFixed(1)}kW</span>
                      <span className="flex items-center gap-1"><Thermometer className="w-3 h-3 text-blue-400" /> {node.temp.toFixed(0)}°C</span>
                    </div>
                  </div>
                  <div className="absolute inset-0 bg-[#00FF41]/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl pointer-events-none"></div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Node Detail Modal */}
      {activeNode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
          <div className="glass-panel w-full max-w-2xl rounded-3xl overflow-hidden shadow-2xl border-slate-700 animate-in zoom-in-95 duration-200">
            {/* Header */}
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-2xl bg-slate-800 flex items-center justify-center border ${activeNode.health === 'OK' ? 'border-green-500/30' : 'border-yellow-500/30'}`}>
                  <Activity className={`w-6 h-6 ${activeNode.health === 'OK' ? 'text-[#00FF41]' : 'text-yellow-500'}`} />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-white tracking-tight">{activeNode.name}</h2>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="px-2 py-0.5 bg-slate-800 rounded text-[9px] font-bold text-slate-400 uppercase tracking-widest">{activeNode.type}</span>
                    <span className={`w-1.5 h-1.5 rounded-full ${activeNode.health === 'OK' ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`}></span>
                    <span className="text-[10px] font-bold text-slate-500">Live Telemetry</span>
                  </div>
                </div>
              </div>
              <button onClick={() => setActiveNode(null)} className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-full transition-all">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Body */}
            <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Core Telemetry</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50">
                      <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Power Draw</p>
                      <p className="text-xl font-bold text-white font-mono">{activeNode.power.toFixed(2)} <span className="text-xs text-slate-500">kW</span></p>
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-800/50 border border-slate-700/50">
                      <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Die Temp</p>
                      <p className="text-xl font-bold text-white font-mono">{activeNode.temp.toFixed(1)} <span className="text-xs text-slate-500">°C</span></p>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Load Saturation</h3>
                    <span className="text-sm font-bold text-[#00FF41] font-mono">{activeNode.utilization.toFixed(1)}%</span>
                  </div>
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex gap-0.5">
                    <div className="h-full bg-[#00FF41] shadow-[0_0_10px_#00FF41]" style={{width: `${activeNode.utilization}%`}}></div>
                  </div>
                  <div className="flex justify-between mt-2 text-[9px] font-bold text-slate-600 uppercase">
                    <span>Idle</span>
                    <span>Saturated</span>
                  </div>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Network & IO</h3>
                  <div className="p-5 rounded-2xl bg-slate-900/50 border border-slate-800 space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">Fabric Latency</span>
                      <span className="text-xs font-bold text-white font-mono">1.2ms</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">Memory Util</span>
                      <span className="text-xs font-bold text-white font-mono">64.2 GB</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-400">Throughput</span>
                      <span className="text-xs font-bold text-white font-mono">4.2 GB/s</span>
                    </div>
                  </div>
                </div>

                <div className="pt-2">
                   <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Node Operations</h3>
                   <div className="grid grid-cols-2 gap-3">
                      <button 
                        onClick={() => alert(`Shell access granted to ${activeNode.name}.`)}
                        className="flex items-center justify-center gap-2 py-3 rounded-xl border border-slate-700 hover:bg-slate-800 hover:text-[#00FF41] transition-all text-xs font-bold text-slate-300"
                      >
                        <Terminal className="w-4 h-4" /> Shell
                      </button>
                      <button 
                        onClick={() => alert(`Node ${activeNode.name} scheduled for soft reboot.`)}
                        className="flex items-center justify-center gap-2 py-3 rounded-xl border border-slate-700 hover:bg-slate-800 hover:text-orange-400 transition-all text-xs font-bold text-slate-300"
                      >
                        <RotateCcw className="w-4 h-4" /> Reset
                      </button>
                   </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-6 bg-slate-950/50 border-t border-slate-800 flex justify-between items-center">
              <div className="flex items-center gap-2 text-green-500/80">
                <ShieldCheck className="w-4 h-4" />
                <span className="text-[10px] font-bold uppercase tracking-widest">ECC Enabled • Verified Hardware</span>
              </div>
              <p className="text-[10px] font-mono text-slate-600">UUID: {activeNode.id}-AURORA-99x1</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetExplorer;
