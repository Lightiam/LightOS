
import React, { useState } from 'react';
import { CreditCard, TrendingDown, Info, ShieldAlert, Download, RefreshCw } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { COST_BREAKDOWN } from '../services/mockData';

const COLORS = ['#00FF41', '#0ea5e9', '#34d399', '#64748b'];

const CostControl: React.FC = () => {
  const [shiftPercentage, setShiftPercentage] = useState(20);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const currentTotal = COST_BREAKDOWN.reduce((acc, curr) => acc + curr.value, 0);
  const projectedSaving = (currentTotal * (shiftPercentage / 100) * 0.28).toFixed(2);

  const handleApplyStrategy = () => {
    setIsOptimizing(true);
    setTimeout(() => {
      setIsOptimizing(false);
      alert(`Optimization strategy applied. Projected monthly savings: $${projectedSaving}`);
    }, 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Cost Breakdown */}
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-8 flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-[#00FF41]" />
            Spend Breakdown
          </h2>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="h-[250px] w-full md:w-1/2">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={COST_BREAKDOWN}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {COST_BREAKDOWN.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0d1117', border: '1px solid #30363d', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="w-full md:w-1/2 space-y-4">
              {COST_BREAKDOWN.map((item, index) => (
                <div key={item.name} className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index] }}></div>
                    <span className="text-sm text-slate-400">{item.name}</span>
                  </div>
                  <span className="text-sm font-bold text-white">${item.value.toLocaleString()}</span>
                </div>
              ))}
              <div className="pt-4 border-t border-slate-800">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-slate-500 uppercase">Monthly Total</span>
                  <span className="text-lg font-bold text-[#00FF41]">${currentTotal.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Optimizer Simulation */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[#00FF41]/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl"></div>
          
          <h2 className="text-xl font-bold text-white mb-4">Aurora Cost Optimizer</h2>
          <p className="text-sm text-slate-400 mb-8">Shift workloads to LightRail Native Fabric to capture performance-per-watt savings.</p>
          
          <div className="space-y-8">
            <div>
              <div className="flex justify-between mb-3">
                <label className="text-sm font-bold text-slate-300">Shift to Native Fabric</label>
                <span className="text-sm font-bold text-[#00FF41]">{shiftPercentage}%</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="100" 
                value={shiftPercentage}
                onChange={(e) => setShiftPercentage(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-[#00FF41]"
              />
              <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-widest">
                <span>Conservative</span>
                <span>Optimized</span>
              </div>
            </div>

            <div className="p-6 bg-[#00FF41]/5 border border-[#00FF41]/20 rounded-2xl">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-[#00FF41]/10 flex items-center justify-center">
                  <TrendingDown className="w-6 h-6 text-[#00FF41]" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Projected Monthly Savings</h3>
                  <p className="text-[10px] text-slate-400 font-medium uppercase tracking-tighter">ROI Forecast</p>
                </div>
              </div>
              <p className="text-3xl font-bold text-[#00FF41]">${projectedSaving} <span className="text-sm text-slate-500 font-normal">/ month</span></p>
            </div>
            
            <button 
              onClick={handleApplyStrategy}
              disabled={isOptimizing}
              className="w-full py-4 aurora-gradient text-black font-bold rounded-xl hover:scale-[1.01] transition-all shadow-xl shadow-green-500/10 disabled:opacity-50"
            >
              {isOptimizing ? <RefreshCw className="w-5 h-5 animate-spin mx-auto" /> : 'Apply Optimization Strategy'}
            </button>
          </div>
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="glass-panel rounded-2xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">Optimization Insights</h2>
          <button className="flex items-center gap-2 text-xs font-bold text-[#00FF41] hover:underline">
            <Download className="w-4 h-4" /> Export Report
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-slate-800/30 border border-slate-700/50 rounded-xl flex items-start gap-4">
            <div className="p-2 bg-yellow-400/10 text-yellow-400 rounded-lg">
              <Info className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">AWS Capacity Leak</h4>
              <p className="text-xs text-slate-400 mt-1">Found 12 H100s idle for &gt;48h. Estimated leak: $820/day.</p>
              <button onClick={() => alert("AWS instances shutdown successfully.")} className="mt-3 text-xs font-bold text-[#00FF41] hover:underline">Execute Cleanup</button>
            </div>
          </div>
          <div className="p-4 bg-slate-800/30 border border-slate-700/50 rounded-xl flex items-start gap-4">
            <div className="p-2 bg-blue-400/10 text-blue-400 rounded-lg">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">Regional Arbitrage</h4>
              <p className="text-xs text-slate-400 mt-1">LightRail Native Fabric rates in US-West just dropped. Shift inference fleet now.</p>
              <button onClick={() => alert("Fleet migration scheduled.")} className="mt-3 text-xs font-bold text-blue-400 hover:underline">Migrate Workload</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CostControl;
