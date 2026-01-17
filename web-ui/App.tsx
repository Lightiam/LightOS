
import React, { useState, useEffect } from 'react';
import { HashRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import AuroraBackground from './components/AuroraBackground';
import Dashboard from './pages/Dashboard';
import FleetExplorer from './pages/FleetExplorer';
import Workloads from './pages/Workloads';
import CostControl from './pages/CostControl';
import DCIMControl from './pages/DCIMControl';
import HCIOrchestrator from './pages/HCIOrchestrator';
import Settings from './pages/Settings';
import Documentation from './pages/Documentation';
import Header from './components/Header';
import AIAssistant from './components/AIAssistant';
import { INITIAL_PROVIDERS, INITIAL_JOBS } from './services/mockData';
import { Provider, Job } from './types';

const App: React.FC = () => {
  const [providers, setProviders] = useState<Provider[]>(INITIAL_PROVIDERS);
  const [jobs, setJobs] = useState<Job[]>(INITIAL_JOBS);
  const [persona, setPersona] = useState<'TENANT' | 'PROVIDER'>('TENANT');

  useEffect(() => {
    const interval = setInterval(() => {
      setProviders(prev => prev.map(p => ({
        ...p,
        utilization: Math.min(100, Math.max(0, p.utilization + (Math.random() - 0.5) * 2))
      })));
      setJobs(prev => prev.map(j => {
        if (j.status === 'RUNNING') {
          const nextProgress = j.progress + Math.random() * 2;
          if (nextProgress >= 100) return { ...j, progress: 100, status: 'SUCCEEDED' };
          return { ...j, progress: nextProgress, cost: j.cost + Math.random() * 0.5 };
        }
        return j;
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <HashRouter>
      <div className="flex min-h-screen bg-[#010409]">
        <Sidebar />
        <main className="flex-1 relative">
          <AuroraBackground />
          <div className="relative z-10 p-8 pt-6">
            <Header persona={persona} setPersona={setPersona} />
            <Routes>
              <Route path="/" element={<Dashboard providers={providers} jobs={jobs} />} />
              <Route path="/fleet" element={<FleetExplorer />} />
              <Route path="/dcim" element={<DCIMControl />} />
              <Route path="/hci" element={<HCIOrchestrator />} />
              <Route path="/workloads" element={<Workloads jobs={jobs} setJobs={setJobs} providers={providers} />} />
              <Route path="/costs" element={<CostControl />} />
              <Route path="/docs" element={<Documentation />} />
              <Route path="/docs/:section" element={<Documentation />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
          <AIAssistant />
        </main>
      </div>
    </HashRouter>
  );
};

export default App;
