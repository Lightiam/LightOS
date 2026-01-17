
import React from 'react';
import { Cpu, Server, Activity, DollarSign } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import StatsCard from '../components/StatsCard';
import { Provider, Job } from '../types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { UTILIZATION_HISTORY } from '../services/mockData';

interface DashboardProps {
  providers: Provider[];
  jobs: Job[];
}

const Dashboard: React.FC<DashboardProps> = ({ providers, jobs }) => {
  const navigate = useNavigate();
  const totalGpus = providers.reduce((acc, p) => acc + p.totalGpus, 0);
  const totalTpus = providers.reduce((acc, p) => acc + p.totalTpus, 0);
  const avgUtilization = providers.reduce((acc, p) => acc + p.utilization, 0) / providers.length;
  const currentHourlyBurn = providers.reduce((acc, p) => acc + p.hourlyCost, 0);
  const activeJobs = jobs.filter(j => j.status === 'RUNNING').length;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard 
          title="Global Compute Fleet" 
          value={`${(totalGpus + totalTpus).toLocaleString()}`} 
          subValue={`${totalGpus}G / ${totalTpus}T`}
          icon={Server} 
          trend={{ value: 12, isPositive: true }} 
        />
        <StatsCard 
          title="Fleet Utilization" 
          value={`${avgUtilization.toFixed(1)}%`} 
          icon={Activity} 
          trend={{ value: 4, isPositive: false }} 
        />
        <StatsCard 
          title="Active Workloads" 
          value={activeJobs} 
          subValue={`/ ${jobs.length} Total`}
          icon={Cpu} 
        />
        <StatsCard 
          title="Run-Rate Burn" 
          value={`$${currentHourlyBurn.toLocaleString()}`} 
          subValue="/hr"
          icon={DollarSign} 
          trend={{ value: 8, isPositive: true }} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Utilization Chart */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#00FF41]" />
              Utilization Over Time
            </h2>
            <select className="bg-slate-800 border-none rounded-lg text-xs font-semibold px-3 py-1.5 text-slate-300 ring-1 ring-slate-700">
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={UTILIZATION_HISTORY}>
                <defs>
                  <linearGradient id="colorUtil" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00FF41" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00FF41" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" vertical={false} />
                <XAxis dataKey="time" stroke="#8b949e" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#8b949e" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0d1117', border: '1px solid #30363d', borderRadius: '8px' }}
                  itemStyle={{ color: '#00FF41' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="utilization" 
                  stroke="#00FF41" 
                  fillOpacity={1} 
                  fill="url(#colorUtil)" 
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Providers Table */}
        <div className="glass-panel rounded-2xl p-6">
          <h2 className="text-xl font-bold text-white mb-6">Top Providers</h2>
          <div className="space-y-4">
            {providers.sort((a,b) => b.utilization - a.utilization).map((p) => (
              <div key={p.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/30 border border-slate-700/50 hover:border-[#00FF41]/30 transition-all cursor-pointer group" onClick={() => navigate('/fleet')}>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center font-bold text-xs text-slate-400 border border-slate-800 group-hover:text-[#00FF41]">
                    {p.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white leading-tight">{p.name}</h4>
                    <p className="text-[10px] text-slate-500 font-medium tracking-wide">{p.region} • {p.type}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold text-[#00FF41]">{p.utilization.toFixed(1)}%</p>
                  <p className="text-[10px] text-slate-500 uppercase font-bold">Util</p>
                </div>
              </div>
            ))}
          </div>
          <button 
            onClick={() => navigate('/fleet')}
            className="w-full mt-6 py-2.5 rounded-xl border border-slate-700 text-slate-400 text-xs font-bold hover:bg-slate-800 hover:text-[#00FF41] transition-all"
          >
            Explore Fleet Map
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
