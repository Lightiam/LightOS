import React, { useState } from 'react';
import { 
  Zap, Thermometer, Network, ShieldCheck, 
  Activity, AlertTriangle, FileBarChart, RefreshCw,
  Server, HardDrive, Cpu, Gauge, ShieldAlert
} from 'lucide-react';
import { INITIAL_RACKS, DCIM_ALERTS } from '../services/mockData';
import StatsCard from '../components/StatsCard';

const DCIMControl: React.FC = () => {
  const [isCalibrating, setIsCalibrating] = useState(false);

  const handleRecalibrate = () => {
    setIsCalibrating(true);
    setTimeout(() => {
      setIsCalibrating(false);
      alert("Breaker thresholds recalibrated successfully.");
    }, 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">DCIM Intelligence</h1>
          <p className="text-slate-400 text-sm mt-1">AI-Optimized Power, Thermals & Fabric Control Plane</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={handleRecalibrate}
            disabled={isCalibrating}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-xl text-xs font-bold text-slate-300 hover:bg-slate-800 transition-all disabled:opacity-50"
          >
            {isCalibrating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            {isCalibrating ? 'Calibrating...' : 'Recalibrate Breakers'}
          </button>
          <button className="flex items-center gap-2 px-6 py-2 aurora-gradient text-black font-bold rounded-xl text-xs hover:scale-[1.02] transition-all">
            <ShieldCheck className="w-4 h-4" /> Compliance: 100%
          </button>
        </div>
      </div>

      {/* Primary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
          title="Deliverable Power" 
          value="2.42 MW" 
          subValue="/ 2.50 MW Cap"
          icon={Zap} 
          trend={{ value: 2.4, isPositive: true }} 
        />
        <StatsCard 
          title="Thermal Delta (Avg)" 
          value="12.4°C" 
          subValue="Inlet: 22°C"
          icon={Thermometer} 
        />
        <StatsCard 
          title="Fabric Congestion" 
          value="14.2%" 
          subValue="NCCL Delay: 0.2ms"
          icon={Network} 
          trend={{ value: 1.2, isPositive: false }} 
        />
        <StatsCard 
          title="Asset Health Index" 
          value="98.2" 
          subValue="MTBF: 12,400h"
          icon={ShieldCheck} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Power & Thermal Grid */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel rounded-3xl p-8">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <HardDrive className="w-5 h-5 text-[#00FF41]" />
              Rack Physics Explorer
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {INITIAL_RACKS.map(rack => (
                <div key={rack.id} className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all space-y-4">
                  <div className="flex justify-between items-center">
                    <h4 className="text-white font-bold">{rack.name}</h4>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${rack.status === 'OK' ? 'bg-green-500/10 text-green-500' : 'bg-yellow-500/10 text-yellow-500'}`}>
                      {rack.status}
                    </span>
                  </div>
                  
                  {/* Power Gauge */}
                  <div>
                    <div className="flex justify-between text-[10px] font-bold text-slate-500 uppercase mb-2">
                      <span>Breaker Load</span>
                      <span className={rack.powerActual > rack.powerLimit * 0.9 ? 'text-red-400' : 'text-slate-300'}>
                        {rack.powerActual}kW / {rack.powerLimit}kW
                      </span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex gap-0.5">
                      <div 
                        className={`h-full transition-all duration-700 ${rack.powerActual > rack.powerLimit * 0.9 ? 'bg-red-500 shadow-[0_0_10px_red]' : 'bg-[#00FF41] shadow-[0_0_10px_#00FF41]'}`} 
                        style={{ width: `${(rack.powerActual / rack.powerLimit) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Thermal Delta */}
                  <div className="flex gap-4 pt-2">
                    <div className="flex-1">
                      <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Inlet Temp</p>
                      <p className="text-lg font-bold text-white">{rack.inletTemp}°C</p>
                    </div>
                    <div className="flex-1">
                      <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Outlet Temp</p>
                      <p className="text-lg font-bold text-white text-orange-400">{rack.outletTemp}°C</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Workload Impact Report */}
          <div className="glass-panel rounded-3xl p-8">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <FileBarChart className="w-5 h-5 text-blue-400" />
                Impact Analysis
              </h2>
              <button onClick={() => alert("Report Exported.")} className="text-xs font-bold text-slate-500 hover:text-[#00FF41] transition-colors">Export Compliance PDF</button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-[10px] text-slate-500 uppercase font-bold tracking-widest border-b border-slate-800">
                    <th className="pb-4">Job ID</th>
                    <th className="pb-4">Energy (kWh)</th>
                    <th className="pb-4">Carbon / Token</th>
                    <th className="pb-4">Util Efficiency</th>
                    <th className="pb-4 text-right">ROI Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {[
                    { id: 'J-101', kwh: 1240, carbon: '0.002g', eff: '94.2%', roi: '+12.4%' },
                    { id: 'J-103', kwh: 4850, carbon: '0.005g', eff: '88.1%', roi: '+8.2%' },
                    { id: 'J-105', kwh: 820, carbon: '0.001g', eff: '98.5%', roi: '+15.1%' },
                  ].map(row => (
                    <tr key={row.id} className="text-sm">
                      <td className="py-4 font-bold text-white">{row.id}</td>
                      <td className="py-4 text-slate-400">{row.kwh.toLocaleString()}</td>
                      <td className="py-4 text-slate-400">{row.carbon}</td>
                      <td className="py-4 font-mono text-[#00FF41]">{row.eff}</td>
                      <td className="py-4 text-right text-[#0ea5e9] font-bold">{row.roi}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Action Center & Logs */}
        <div className="space-y-6">
          <div className="glass-panel rounded-3xl p-8 bg-slate-900/50">
            <h3 className="text-xs font-bold text-slate-500 uppercase mb-6 tracking-widest">Autonomous Remediation</h3>
            <div className="space-y-4">
              {/* Renamed loop variable 'alert' to 'alertItem' to avoid shadowing global alert() */}
              {DCIM_ALERTS.map(alertItem => (
                <div key={alertItem.id} className="p-4 rounded-xl border border-slate-800 bg-black/30 flex gap-4">
                  <div className={`p-2 rounded-lg h-fit ${
                    alertItem.type === 'THERMAL' ? 'bg-orange-500/10 text-orange-500' :
                    alertItem.type === 'POWER' ? 'bg-red-500/10 text-red-500' :
                    'bg-blue-500/10 text-blue-500'
                  }`}>
                    {alertItem.type === 'THERMAL' ? <Thermometer className="w-4 h-4" /> : 
                     alertItem.type === 'POWER' ? <Zap className="w-4 h-4" /> : 
                     <Network className="w-4 h-4" />}
                  </div>
                  <div className="flex-1">
                    <p className="text-xs font-bold text-white leading-tight">{alertItem.message}</p>
                    <p className="text-[10px] text-slate-500 mt-1 uppercase font-bold">{alertItem.time}</p>
                    <button 
                      onClick={() => alert(`Remediation for ${alertItem.type} approved.`)}
                      className="mt-3 w-full py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-[10px] font-bold text-slate-300 hover:bg-slate-700 transition-all uppercase"
                    >
                      Approve Fix
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-8 rounded-3xl bg-green-500/5 border border-green-500/20 space-y-4 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/5 blur-3xl rounded-full"></div>
            <div className="flex items-center gap-3">
              <Gauge className="w-6 h-6 text-[#00FF41]" />
              <h3 className="text-lg font-bold text-white">Asset Lifecycle</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Tracking MTBF for cluster. Projected failure drift: <span className="text-white font-bold">-0.02%</span> this quarter.
            </p>
            <div className="flex justify-between items-end pt-4">
              <div>
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Fleet Health Score</p>
                <p className="text-2xl font-bold text-[#00FF41] shadow-[#00FF41]">AA+</p>
              </div>
              <button onClick={() => alert("RMA Dashboard Coming Soon.")} className="text-xs font-bold text-[#0ea5e9] hover:underline">View RMAs</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DCIMControl;