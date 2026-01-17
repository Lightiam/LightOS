
import React from 'react';
import { Search, Bell, User, ChevronDown, UserCircle2, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  persona: 'TENANT' | 'PROVIDER';
  setPersona: (p: 'TENANT' | 'PROVIDER') => void;
}

const Header: React.FC<HeaderProps> = ({ persona, setPersona }) => {
  const handleSearch = () => {
    alert("Universal Search: Scanning global compute fabric, jobs, and DCIM telemetry...");
  };

  const handleNotifications = () => {
    alert("Recent System Events:\n- PUE optimization triggered in SJ-Alpha-01\n- Job J-101 completed successfully\n- Breaker threshold recalibrated in Rack-03");
  };

  const handleUserMenu = () => {
    alert("User Profile: Alex Rivera\nRole: Site Admin\nPermissions: FULL_ORCHESTRATION_RW");
  };

  return (
    <header className="flex justify-between items-center mb-8">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Mission Control</h1>
        <p className="text-slate-400 text-sm flex items-center gap-2 mt-1">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          System Online • US-West Fabric Operational
        </p>
      </div>

      <div className="flex items-center gap-6">
        {/* Persona Toggle */}
        <div className="flex bg-slate-800/50 p-1 rounded-xl border border-slate-700/50">
          <button
            onClick={() => setPersona('TENANT')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              persona === 'TENANT' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <UserCircle2 className="w-4 h-4" />
            Tenant
          </button>
          <button
            onClick={() => setPersona('PROVIDER')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              persona === 'PROVIDER' ? 'bg-slate-700 text-[#00FF41] shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            Provider
          </button>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={handleSearch}
            className="p-2 text-slate-400 hover:text-[#00FF41] hover:bg-slate-800/50 rounded-lg transition-colors"
          >
            <Search className="w-5 h-5" />
          </button>
          <button 
            onClick={handleNotifications}
            className="p-2 text-slate-400 hover:text-yellow-400 hover:bg-slate-800/50 rounded-lg transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-[#010409]"></span>
          </button>
        </div>

        <div className="h-8 w-[1px] bg-slate-800"></div>

        <button 
          onClick={handleUserMenu}
          className="flex items-center gap-3 p-1 pr-3 hover:bg-slate-800/50 rounded-full transition-all group"
        >
          <div className="w-9 h-9 rounded-full bg-slate-700 flex items-center justify-center border border-slate-600 group-hover:border-[#00FF41]">
            <User className="w-5 h-5 text-slate-300" />
          </div>
          <div className="text-left hidden sm:block">
            <p className="text-sm font-bold text-white leading-none">Alex Rivera</p>
            <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Site Admin</p>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-500 group-hover:text-white" />
        </button>
      </div>
    </header>
  );
};

export default Header;
