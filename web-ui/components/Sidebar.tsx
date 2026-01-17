
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Cpu, Activity, CreditCard, Settings, Layers, BookOpen, ShieldAlert, Share2 } from 'lucide-react';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Overview', icon: LayoutDashboard, path: '/' },
    { name: 'Fleet Explorer', icon: Layers, path: '/fleet' },
    { name: 'DCIM Control', icon: ShieldAlert, path: '/dcim' },
    { name: 'HCI Orchestrator', icon: Share2, path: '/hci' },
    { name: 'Workloads', icon: Activity, path: '/workloads' },
    { name: 'Cost Control', icon: CreditCard, path: '/costs' },
    { name: 'Documentation', icon: BookOpen, path: '/docs' },
    { name: 'System Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <aside className="w-64 border-r border-slate-800 h-screen sticky top-0 bg-[#0d1117]/80 backdrop-blur-xl flex flex-col z-20">
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 aurora-gradient rounded-md flex items-center justify-center shadow-lg shadow-green-500/20">
            <Cpu className="w-5 h-5 text-black" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">Aurora<span className="text-[#00FF41]">.</span></span>
        </div>
        <p className="text-[10px] text-slate-500 mt-1 uppercase font-semibold tracking-widest">Powered by LightRail AI</p>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto scrollbar-hide">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200
              ${isActive 
                ? 'bg-slate-800/50 text-[#00FF41] border border-slate-700/50' 
                : 'text-slate-400 hover:text-white hover:bg-slate-800/30'}
            `}
          >
            <item.icon className="w-5 h-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className="bg-slate-800/30 p-4 rounded-xl border border-slate-700/30">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-slate-400 font-medium">Power Headroom</span>
            <span className="text-xs text-[#00FF41] font-bold">12% Avail</span>
          </div>
          <div className="h-1.5 w-full bg-slate-700 rounded-full overflow-hidden">
            <div className="h-full bg-[#00FF41] w-[88%] rounded-full shadow-[0_0_8px_rgba(0,255,65,0.4)]"></div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
