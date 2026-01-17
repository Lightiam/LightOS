
import React, { useState } from 'react';
/* Added MoreHorizontal to imports, removed unused MoreVertical */
import { Plus, Search, Filter, Play, Clock, CheckCircle, XCircle, MoreHorizontal } from 'lucide-react';
import { Job, Provider } from '../types';

interface WorkloadsProps {
  jobs: Job[];
  setJobs: React.Dispatch<React.SetStateAction<Job[]>>;
  providers: Provider[];
}

const Workloads: React.FC<WorkloadsProps> = ({ jobs, setJobs, providers }) => {
  const [showModal, setShowModal] = useState(false);
  const [newJob, setNewJob] = useState({
    name: '',
    resources: '8x H100',
    provider: 'LightRail DC-SJ',
    priority: 'Normal'
  });

  const handleCreateJob = (e: React.FormEvent) => {
    e.preventDefault();
    const job: Job = {
      id: `J-${Math.floor(Math.random() * 900) + 100}`,
      name: newJob.name,
      tenant: 'LightRail Admin',
      status: 'QUEUED',
      resources: newJob.resources,
      provider: newJob.provider,
      startTime: '-',
      cost: 0,
      progress: 0
    };
    setJobs([job, ...jobs]);
    setShowModal(false);
    setNewJob({ name: '', resources: '8x H100', provider: 'LightRail DC-SJ', priority: 'Normal' });
  };

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'RUNNING': return 'text-blue-400 bg-blue-400/10 border-blue-400/20';
      case 'QUEUED': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      case 'SUCCEEDED': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'FAILED': return 'text-red-400 bg-red-400/10 border-red-400/20';
    }
  };

  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'RUNNING': return Play;
      case 'QUEUED': return Clock;
      case 'SUCCEEDED': return CheckCircle;
      case 'FAILED': return XCircle;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search jobs..." 
              className="w-full bg-slate-800/50 border border-slate-700 rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-[#00FF41]/50 text-white"
            />
          </div>
          <button className="p-2 border border-slate-700 rounded-xl text-slate-400 hover:bg-slate-800 transition-all">
            <Filter className="w-5 h-5" />
          </button>
        </div>
        
        <button 
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-6 py-2.5 aurora-gradient text-black font-bold rounded-xl shadow-lg shadow-green-500/20 hover:scale-[1.02] transition-all w-full md:w-auto justify-center"
        >
          <Plus className="w-5 h-5" />
          Submit Job
        </button>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-slate-800/30 text-slate-500 text-[10px] uppercase font-bold tracking-widest border-b border-slate-800">
              <th className="px-6 py-4">Job Details</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Provider / Region</th>
              <th className="px-6 py-4">Resources</th>
              <th className="px-6 py-4 text-right">Cost (Est.)</th>
              <th className="px-6 py-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {jobs.map((job) => {
              const StatusIcon = getStatusIcon(job.status);
              return (
                <tr key={job.id} className="hover:bg-slate-800/20 transition-all group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center border border-slate-700 font-mono text-xs text-[#00FF41]">
                        {job.id.split('-')[1]}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-white">{job.name}</p>
                        <p className="text-[10px] text-slate-500 font-medium">Tenant: {job.tenant}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-bold ${getStatusColor(job.status)}`}>
                      <StatusIcon className="w-3 h-3" />
                      {job.status}
                    </div>
                    {job.status === 'RUNNING' && (
                      <div className="mt-2 w-24 h-1 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-400 rounded-full transition-all duration-1000" style={{ width: `${job.progress}%` }}></div>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-xs text-white font-medium">{job.provider}</p>
                    <p className="text-[10px] text-slate-500">Global Fabric</p>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-xs font-mono text-slate-300">{job.resources}</p>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <p className="text-sm font-bold text-white">${job.cost.toFixed(2)}</p>
                    <p className="text-[10px] text-slate-500">{job.startTime}</p>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-1.5 text-slate-500 hover:text-white rounded-lg hover:bg-slate-700 transition-all">
                      <MoreHorizontal className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Modal - Simple Implementation */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#0d1117] border border-slate-800 rounded-2xl w-full max-w-md p-8 shadow-2xl animate-in zoom-in duration-200">
            <h2 className="text-2xl font-bold text-white mb-6">Orchestrate New Job</h2>
            <form onSubmit={handleCreateJob} className="space-y-5">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Workload Name</label>
                <input 
                  required
                  value={newJob.name}
                  onChange={(e) => setNewJob({...newJob, name: e.target.value})}
                  type="text" 
                  placeholder="e.g. Llama-3-Tune-v1" 
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#00FF41]/50 text-white"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Resource Profile</label>
                <select 
                  value={newJob.resources}
                  onChange={(e) => setNewJob({...newJob, resources: e.target.value})}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm focus:outline-none text-white"
                >
                  <option>8x H100</option>
                  <option>16x A100</option>
                  <option>4x TPU v5e</option>
                  <option>2x L40S</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Placement Strategy</label>
                <select className="w-full bg-slate-800 border border-slate-700 rounded-xl p-3 text-sm focus:outline-none text-white">
                  <option>Lowest Cost (Recommended)</option>
                  <option>Lowest Latency</option>
                  <option>Green Power Priority</option>
                </select>
              </div>
              <div className="flex gap-4 pt-4">
                <button 
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-3 border border-slate-700 rounded-xl text-slate-400 font-bold hover:bg-slate-800 transition-all"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="flex-1 py-3 aurora-gradient text-black font-bold rounded-xl hover:scale-[1.02] transition-all"
                >
                  Launch Job
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Workloads;
