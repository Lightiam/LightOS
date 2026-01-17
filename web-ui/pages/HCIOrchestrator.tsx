
import React, { useState, useEffect } from 'react';
import { 
  Share2, ShieldCheck, Box, Cpu, HardDrive, Network, Zap, 
  RefreshCw, Plus, ArrowRight, Lock, Users, Activity, 
  BarChart, Layers, Globe, Database, Settings, ShieldAlert,
  Server, Layout, Binary, Radio, Cloud, Download, Trash2, 
  Eye, Save, Power, CheckCircle
} from 'lucide-react';
import StatsCard from '../components/StatsCard';
import { HCI_NODES, TENANT_ISOLATION } from '../services/mockData';

const HCIOrchestrator: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'MANAGEMENT' | 'RELIABILITY' | 'SCALABILITY'>('MANAGEMENT');
  const [isSimulatingFailover, setIsSimulatingFailover] = useState(false);
  const [nodes, setNodes] = useState(HCI_NODES);
  const [isScaling, setIsScaling] = useState(false);
  const [actionLog, setActionLog] = useState<string[]>(["Cluster initialization complete.", "Fabric status: HEALTHY"]);

  const logAction = (msg: string) => {
    setActionLog(prev => [`[${new Date().toLocaleTimeString()}] ${msg}`, ...prev].slice(0, 5));
  };

  const handleFailoverTest = () => {
    setIsSimulatingFailover(true);
    logAction("Initiating failover readiness test...");
    setTimeout(() => {
      setIsSimulatingFailover(false);
      logAction("Failover test PASSED. Redundancy confirmed.");
    }, 2500);
  };

  const handleAddNode = () => {
    setIsScaling(true);
    logAction("Provisioning new HCI Converged Node...");
    setTimeout(() => {
      const newNode = {
        id: `HCI-${nodes.length + 1}`,
        name: `Converged-Node-0${nodes.length + 1}`,
        computeUtil: 0,
        storageUtil: 0,
        throughput: "0.0 GB/s",
        latency: "0.1ms",
        redundancyStatus: 'ACTIVE' as const,
        tenantId: 'T-01'
      };
      setNodes([...nodes, newNode]);
      setIsScaling(false);
      logAction(`Node ${newNode.name} added to cluster.`);
    }, 2000);
  };

  const handleRollingUpgrade = () => {
    logAction("Starting rolling firmware update...");
    // Mock simulation of rolling update across nodes
    nodes.forEach((_, i) => {
      setTimeout(() => logAction(`Updating Node 0${i+1}...`), (i + 1) * 600);
    });
    setTimeout(() => logAction("All nodes updated to v1.4.2."), nodes.length * 700);
  };

  const handleDownloadReport = () => {
    logAction("Generating Cost & Governance PDF report...");
    setTimeout(() => alert("HCI Governance Report generated successfully."), 500);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-20">
      {/* HCI Mission Control Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-green-500/10 border border-green-500/20">
              <Share2 className="w-8 h-8 text-[#00FF41]" />
            </div>
            <h1 className="text-3xl font-bold text-white tracking-tight">HCI Orchestrator</h1>
          </div>
          <p className="text-slate-400 text-sm pl-1 uppercase font-bold tracking-widest opacity-70">Hyper-Converged Infrastructure Fabric</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleFailoverTest}
            disabled={isSimulatingFailover}
            className="flex items-center gap-2 px-4 py-2.5 bg-slate-800/50 border border-slate-700 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-800 transition-all disabled:opacity-50"
          >
            {isSimulatingFailover ? <RefreshCw className="w-4 h-4 animate-spin" /> : <ShieldAlert className="w-4 h-4 text-yellow-500" />}
            {isSimulatingFailover ? 'Rebalancing...' : 'Resiliency Test'}
          </button>
          <button 
            onClick={handleAddNode}
            disabled={isScaling}
            className="flex items-center gap-2 px-6 py-2.5 aurora-gradient text-black font-bold rounded-xl text-xs hover:scale-[1.02] transition-all shadow-lg shadow-green-500/10 disabled:opacity-50"
          >
            {isScaling ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Add HCI Node
          </button>
        </div>
      </div>

      {/* Main HCI Domain Grid - 4 Primary Stats cards using neon green/blue */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
          title="Compute Balance" 
          value="8.2 PF" 
          subValue="HCI Shard 01"
          icon={Cpu} 
          trend={{ value: 12.4, isPositive: true }} 
        />
        <StatsCard 
          title="Storage Locality" 
          value="98.1%" 
          subValue="Low Latency"
          icon={Database} 
        />
        <StatsCard 
          title="Fabric Capacity" 
          value={nodes.length} 
          subValue="Nodes Online"
          icon={Layers} 
          trend={{ value: 4.2, isPositive: true }} 
        />
        <StatsCard 
          title="Isolation Shield" 
          value="Active" 
          subValue="Multi-Tenant"
          icon={Lock} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Management & Core Fabric */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Section 1: Unified Management Plane */}
          <div className="glass-panel rounded-[2.5rem] p-8 border-slate-800/50 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#00FF41]/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
            
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-10">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Box className="w-5 h-5 text-[#00FF41]" />
                  Unified Management Plane
                </h2>
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">Converged Compute, Storage & Networking</p>
              </div>
              <div className="flex bg-slate-900/50 p-1 rounded-xl border border-slate-800">
                <button onClick={() => setActiveTab('MANAGEMENT')} className={`px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all ${activeTab === 'MANAGEMENT' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500'}`}>Locality</button>
                <button onClick={() => setActiveTab('RELIABILITY')} className={`px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all ${activeTab === 'RELIABILITY' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500'}`}>Failover</button>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {nodes.map(node => (
                <div key={node.id} className="p-5 rounded-2xl bg-slate-900/40 border border-slate-800 hover:border-[#00FF41]/30 transition-all group cursor-default">
                   <div className="flex justify-between mb-4">
                      <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center">
                        <Binary className={`w-4 h-4 ${node.redundancyStatus === 'ACTIVE' ? 'text-[#0ea5e9]' : 'text-yellow-500'}`} />
                      </div>
                      {isSimulatingFailover && node.id === `HCI-${nodes.length}` && (
                        <span className="flex h-2 w-2 rounded-full bg-red-500 animate-ping"></span>
                      )}
                   </div>
                   <h4 className="text-[11px] font-bold text-white mb-1">{node.name}</h4>
                   <p className="text-[9px] text-slate-500 font-mono mb-4">{node.throughput} / {node.latency}</p>
                   
                   <div className="space-y-2">
                      <div className="flex justify-between text-[8px] font-bold text-slate-500 uppercase">
                        <span>Data Affinity</span>
                        <span className="text-white">{node.storageUtil.toFixed(0)}%</span>
                      </div>
                      <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-[#00FF41] shadow-[0_0_8px_#00FF41]" style={{ width: `${node.storageUtil}%` }}></div>
                      </div>
                   </div>
                </div>
              ))}
            </div>

            {/* HCI Details Overlay / Additional Controls */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 border-t border-slate-800">
               <button 
                 onClick={() => logAction("Re-pinning high-priority datasets for locality...")}
                 className="flex gap-3 hover:bg-slate-800/30 p-2 rounded-xl transition-all text-left"
               >
                 <div className="p-2 rounded-lg bg-blue-500/10 h-fit">
                   <HardDrive className="w-4 h-4 text-blue-400" />
                 </div>
                 <div>
                   <h5 className="text-xs font-bold text-white">Optimize Locality</h5>
                   <p className="text-[10px] text-slate-500 mt-0.5">Auto-pin datasets to GPUs.</p>
                 </div>
               </button>
               <button 
                 onClick={() => logAction("Initiating cluster I/O benchmark...")}
                 className="flex gap-3 hover:bg-slate-800/30 p-2 rounded-xl transition-all text-left"
               >
                 <div className="p-2 rounded-lg bg-green-500/10 h-fit">
                   <Zap className="w-4 h-4 text-green-400" />
                 </div>
                 <div>
                   <h5 className="text-xs font-bold text-white">Throughput Test</h5>
                   <p className="text-[10px] text-slate-500 mt-0.5">Benchmark fabric I/O.</p>
                 </div>
               </button>
               <button 
                 onClick={() => logAction("Verifying node configuration hashes...")}
                 className="flex gap-3 hover:bg-slate-800/30 p-2 rounded-xl transition-all text-left"
               >
                 <div className="p-2 rounded-lg bg-green-500/10 h-fit">
                   <CheckCircle className="w-4 h-4 text-green-400" />
                 </div>
                 <div>
                   <h5 className="text-xs font-bold text-white">Verify Health</h5>
                   <p className="text-[10px] text-slate-500 mt-0.5">Global sync check.</p>
                 </div>
               </button>
            </div>
          </div>

          {/* Section 2: Isolation & Noisy Neighbor Monitor */}
          <div className="glass-panel rounded-[2.5rem] p-8 border-slate-800/50">
             <div className="flex justify-between items-center mb-8">
               <h2 className="text-xl font-bold text-white flex items-center gap-2">
                 <Lock className="w-5 h-5 text-[#00FF41]" />
                 AI Workload Isolation
               </h2>
               <button 
                 onClick={() => logAction("Hardening security alignment for all tenants...")}
                 className="flex items-center gap-2 px-3 py-1 bg-green-500/10 rounded-lg border border-green-500/20 hover:bg-green-500/20 transition-all"
               >
                 <ShieldCheck className="w-3.5 h-3.5 text-green-400" />
                 <span className="text-[9px] font-bold text-green-400 uppercase tracking-widest">Enforce Policy</span>
               </button>
             </div>

             <div className="space-y-4">
                {TENANT_ISOLATION.map(tenant => (
                  <div key={tenant.id} className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-6 group hover:border-[#00FF41]/30 transition-all">
                    <div className="flex items-center gap-4 w-full md:w-auto">
                      <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center">
                        <Users className="w-6 h-6 text-[#00FF41]" />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-white">{tenant.name}</h4>
                        <div className="flex gap-2 mt-1">
                          <span className="px-1.5 py-0.5 bg-blue-500/10 text-blue-400 text-[8px] font-bold uppercase rounded">Isolated</span>
                          <span className="px-1.5 py-0.5 bg-green-500/10 text-green-400 text-[8px] font-bold uppercase rounded">Compliant</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex-1 w-full max-w-xs space-y-1.5">
                       <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase">
                         <span>Isolation Integrity</span>
                         <span className="text-[#00FF41]">Optimal</span>
                       </div>
                       <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-[#00FF41]" style={{ width: `${100 - tenant.noisyNeighborScore}%` }}></div>
                       </div>
                    </div>

                    <div className="flex gap-3">
                      <button 
                        onClick={() => logAction(`Viewing resource telemetry for ${tenant.name}...`)}
                        className="p-2 bg-slate-800 rounded-lg hover:text-white hover:bg-slate-700 transition-all"
                      >
                        <Eye className="w-4 h-4 text-slate-400" />
                      </button>
                      <button 
                         onClick={() => logAction(`Modifying isolation gates for ${tenant.name}...`)}
                         className="p-2 bg-slate-800 rounded-lg hover:text-white hover:bg-slate-700 transition-all"
                      >
                        <Settings className="w-4 h-4 text-slate-400" />
                      </button>
                    </div>
                  </div>
                ))}
             </div>
          </div>
        </div>

        {/* Right Column: Operational Logs & Global Controls */}
        <div className="space-y-8">
          
          {/* Action Hub / Logs */}
          <div className="glass-panel rounded-[2.5rem] p-8 space-y-6">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
              <Activity className="w-4 h-4" /> Operational Logs
            </h3>
            <div className="space-y-3 font-mono">
              {actionLog.map((log, i) => (
                <div key={i} className={`text-[10px] p-2 rounded-lg bg-black/30 border border-slate-800 ${i === 0 ? 'text-[#00FF41]' : 'text-slate-500'}`}>
                  {log}
                </div>
              ))}
            </div>
            <button 
              onClick={() => setActionLog([])}
              className="w-full py-2 text-[10px] font-bold text-slate-600 hover:text-white uppercase transition-all"
            >
              Clear Logs
            </button>
          </div>

          {/* Operational Simplicity - Functional Buttons */}
          <div className="glass-panel rounded-[2.5rem] p-8 space-y-6">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
              <Layout className="w-4 h-4" /> Operational Control
            </h3>
            <div className="space-y-3">
               <button 
                 onClick={handleRollingUpgrade}
                 className="w-full flex items-center justify-between p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-[#00FF41]/30 transition-all text-left"
               >
                  <div className="flex items-center gap-3">
                    <RefreshCw className="w-4 h-4 text-green-400" />
                    <div>
                      <h5 className="text-[11px] font-bold text-white">Rolling Upgrade</h5>
                      <p className="text-[9px] text-slate-500">Zero-disruption firmware.</p>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-700" />
               </button>
               <button 
                 onClick={() => logAction("Scanning for orphaned HCI volumes...")}
                 className="w-full flex items-center justify-between p-4 rounded-xl bg-slate-900 border border-slate-800 hover:border-[#00FF41]/30 transition-all text-left"
               >
                  <div className="flex items-center gap-3">
                    <Trash2 className="w-4 h-4 text-red-400" />
                    <div>
                      <h5 className="text-[11px] font-bold text-white">Prune Storage</h5>
                      <p className="text-[9px] text-slate-500">Cleanup unused segments.</p>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-700" />
               </button>
            </div>
          </div>

          {/* Hybrid & Edge Deployment */}
          <div className="glass-panel rounded-[2.5rem] p-8 space-y-6 bg-green-500/5 border-green-500/20">
             <h3 className="text-xs font-bold text-green-400 uppercase tracking-widest flex items-center gap-2">
               <Radio className="w-4 h-4" /> Hybrid & Edge AI
             </h3>
             <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Site-London-01</span>
                  <span className="text-[10px] font-bold text-green-400 px-2 py-0.5 bg-green-500/10 rounded">Deploying...</span>
                </div>
                <button 
                  onClick={() => logAction("Syncing Edge-Vision workload to London Site...")}
                  className="w-full py-3 bg-slate-800 border border-slate-700 rounded-xl text-[10px] font-bold text-white hover:bg-slate-700 transition-all uppercase"
                >
                  Manage Edge Sites
                </button>
             </div>
          </div>

          {/* Cost Predictability - Actionable */}
          <div className="p-8 rounded-[2.5rem] aurora-gradient shadow-2xl shadow-green-500/10 group cursor-pointer overflow-hidden relative" onClick={handleDownloadReport}>
            <div className="absolute inset-0 bg-black/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex items-center justify-between relative z-10 mb-2">
              <div className="flex items-center gap-3">
                <BarChart className="w-5 h-5 text-black" />
                <h4 className="text-black font-bold text-sm uppercase tracking-widest">HCI Governance</h4>
              </div>
              <Download className="w-5 h-5 text-black" />
            </div>
            <p className="text-black/80 text-[10px] font-semibold relative z-10 leading-relaxed uppercase tracking-tight">
              Export CapEx Visibility & ROI Analytics
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};

export default HCIOrchestrator;
