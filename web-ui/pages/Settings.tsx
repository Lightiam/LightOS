
import React, { useState } from 'react';
import { User, Bell, Shield, Globe, Database, Cpu, Power, Trash2, Key, Download } from 'lucide-react';

const Settings: React.FC = () => {
  const [debugLogging, setDebugLogging] = useState(false);
  const [autoOptimize, setAutoOptimize] = useState(true);

  const sections = [
    { id: 'profile', icon: User, title: 'Profile & Identity', desc: 'Manage your personal details and avatar', action: () => alert("Identity Management: Syncing with LightRail Auth Service...") },
    { id: 'notifications', icon: Bell, title: 'Alerts & Notifications', desc: 'Configure system health and job status emails', action: () => alert("Notification Hub: Configuring SMTP and Webhook listeners...") },
    { id: 'security', icon: Shield, title: 'Security & Access', desc: 'Manage API keys and multi-factor authentication', action: () => alert("Security Vault: Rotate keys or manage MFA...") },
    { id: 'network', icon: Globe, title: 'Global Fabric Config', desc: 'Manage region endpoints and VPN tunnels', action: () => alert("Fabric Routing: Updating global endpoint topology...") },
    { id: 'data', icon: Database, title: 'Data Retention', desc: 'Configure logging and historical metrics storage', action: () => alert("Data Policy: Setting retention window to 365 days...") },
    { id: 'compute', icon: Cpu, title: 'Compute Policies', desc: 'Set default resource limits and priority rules', action: () => alert("Compute Governance: Tuning priority weights for H100 shards...") },
  ];

  const handleSave = () => {
    alert(`Settings Synchronized Successfully:\n- Debug Logging: ${debugLogging ? 'ON' : 'OFF'}\n- Auto-Optimization: ${autoOptimize ? 'ON' : 'OFF'}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12">
      <div className="glass-panel rounded-2xl p-8 border border-slate-800">
        <h2 className="text-2xl font-bold text-white mb-2">System Configuration</h2>
        <p className="text-slate-400 text-sm">Fine-tune the Aurora mission control parameters and account settings.</p>
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          {sections.map(section => (
            <button 
              key={section.id} 
              onClick={section.action}
              className="p-6 text-left rounded-2xl bg-slate-800/30 border border-slate-700/50 hover:border-[#00FF41]/50 transition-all group"
            >
              <div className="flex items-center gap-4 mb-3">
                <div className="p-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-500 group-hover:text-[#00FF41] group-hover:border-[#00FF41]/20 transition-all">
                  <section.icon className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-white text-sm tracking-tight">{section.title}</h3>
              </div>
              <p className="text-xs text-slate-500 font-medium leading-relaxed">{section.desc}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="glass-panel rounded-2xl p-8 border border-slate-800">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-bold text-white">Advanced Telemetry</h3>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold text-slate-500 uppercase">Status</span>
            <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]"></span>
          </div>
        </div>
        
        <div className="space-y-4">
          <div 
            className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl border border-slate-700/50 cursor-pointer"
            onClick={() => setDebugLogging(!debugLogging)}
          >
            <div>
              <p className="text-sm font-bold text-white">Debug Logging</p>
              <p className="text-xs text-slate-500">Enable verbose job orchestration logs</p>
            </div>
            <div className={`w-10 h-5 rounded-full relative transition-all ${debugLogging ? 'bg-[#00FF41]' : 'bg-slate-700'}`}>
              <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${debugLogging ? 'right-1' : 'left-1'}`}></div>
            </div>
          </div>
          <div 
            className="flex items-center justify-between p-4 bg-slate-800/30 rounded-xl border border-slate-700/50 cursor-pointer"
            onClick={() => setAutoOptimize(!autoOptimize)}
          >
            <div>
              <p className="text-sm font-bold text-white">Auto-Optimization</p>
              <p className="text-xs text-slate-500">Automatically migrate idle spot workloads</p>
            </div>
            <div className={`w-10 h-5 rounded-full relative transition-all ${autoOptimize ? 'bg-[#00FF41]' : 'bg-slate-700'}`}>
              <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${autoOptimize ? 'right-1' : 'left-1'}`}></div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-end gap-4">
          <button 
            onClick={() => { setDebugLogging(false); setAutoOptimize(true); }}
            className="px-6 py-2 text-sm font-bold text-slate-400 hover:text-white transition-colors"
          >
            Discard
          </button>
          <button 
            onClick={handleSave}
            className="px-8 py-2.5 aurora-gradient text-black font-bold rounded-xl text-sm shadow-lg shadow-green-500/10 hover:scale-[1.02] transition-all"
          >
            Save Global Config
          </button>
        </div>
      </div>
      
      <div className="p-8 rounded-2xl bg-red-500/5 border border-red-500/10 flex justify-between items-center">
         <div>
           <h3 className="text-sm font-bold text-red-400">Hazard Zone</h3>
           <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-0.5">Sensitive Infrastructure Actions</p>
         </div>
         <div className="flex gap-4">
           <button onClick={() => alert("Purging stale fabric caches...")} className="px-4 py-2 rounded-xl border border-slate-800 text-[10px] font-bold text-slate-400 hover:bg-slate-800 transition-all uppercase">Purge Cache</button>
           <button onClick={() => alert("DANGER: Wiping telemetry database is disabled in production.")} className="px-4 py-2 rounded-xl bg-red-500/10 text-red-500 text-[10px] font-bold hover:bg-red-500/20 transition-all uppercase">Factory Reset</button>
         </div>
      </div>
    </div>
  );
};

export default Settings;
