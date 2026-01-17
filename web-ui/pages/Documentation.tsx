
import React from 'react';
import { useParams, NavLink, Navigate } from 'react-router-dom';
import { 
  Book, Terminal, Shield, Globe, Zap, Copy, Code, Box, 
  Cpu as CpuIcon, ChevronRight, HardDrive, Network,
  Info, Cpu, Rocket, Server, Key, ShieldAlert, Thermometer,
  FileBarChart, Layers, History, ClipboardCheck,
  Share2, Database, Lock, Layout, Binary, Radio, Users,
  ShieldCheck
} from 'lucide-react';

const CodeBlock = ({ code, lang = "bash" }: { code: string; lang?: string }) => (
  <div className="relative group mt-4 mb-6">
    <div className="absolute -top-3 right-4 px-2 py-0.5 bg-slate-800 rounded border border-slate-700 text-[9px] font-bold text-slate-400 uppercase tracking-widest z-10">
      {lang}
    </div>
    <pre className="p-5 rounded-2xl bg-slate-950/90 border border-slate-800 text-sm font-mono text-slate-300 overflow-x-auto leading-relaxed border-l-4 border-l-[#00FF41]">
      <code>{code}</code>
    </pre>
    <button onClick={() => navigator.clipboard.writeText(code)} className="absolute bottom-4 right-4 p-2 bg-slate-800/50 hover:bg-slate-700 rounded-lg text-slate-400 opacity-0 group-hover:opacity-100 transition-all">
      <Copy className="w-4 h-4" />
    </button>
  </div>
);

// --- Content Page Factory ---
const DocPage = ({ icon: Icon, title, desc, children }: any) => (
  <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500">
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-xl bg-slate-800 border border-slate-700">
          <Icon className="w-6 h-6 text-[#00FF41]" />
        </div>
        <h2 className="text-3xl font-bold text-white tracking-tight">{title}</h2>
      </div>
      <p className="text-lg text-slate-400 leading-relaxed max-w-4xl">{desc}</p>
    </div>
    {children}
  </div>
);

// --- Component Map ---
const components: Record<string, React.FC> = {
  introduction: () => (
    <DocPage icon={Zap} title="Introduction" desc="LightOS Aurora acts as the global control plane for hybrid compute fabrics.">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800">
          <h4 className="text-white font-bold mb-2">Platform Goal</h4>
          <p className="text-sm text-slate-500">Eliminate the abstraction gap between facility physics and AI workload scheduling.</p>
        </div>
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 border-t-4 border-t-[#00FF41]">
          <h4 className="text-white font-bold mb-2">HCI Convergence</h4>
          <p className="text-sm text-slate-500">A unified management plane for compute, storage, and networking.</p>
        </div>
      </div>
    </DocPage>
  ),
  'compute-management': () => (
    <DocPage icon={Cpu} title="Compute Management" desc="Balancing compute resources across AI, analytics, and enterprise workloads.">
      <div className="space-y-6">
        <p className="text-slate-400">Aurora HCI manages resource allocation by dynamically weighting GPU-accelerated nodes for training versus inference.</p>
        <div className="p-6 rounded-2xl bg-slate-800 border border-slate-700">
          <h5 className="text-white font-bold text-sm mb-3">Core Functions:</h5>
          <ul className="list-disc list-inside text-xs text-slate-500 space-y-2">
            <li>CPU & Memory Allocation: Precision balancing across multi-tenant shards.</li>
            <li>GPU Enablement: Full-stack acceleration for large-scale training.</li>
            <li>Workload Placement: Dynamic node selection based on real-time performance needs.</li>
          </ul>
        </div>
        <CodeBlock code={`lightrail compute rebalance --strategy performance`} />
      </div>
    </DocPage>
  ),
  'storage-locality': () => (
    <DocPage icon={Database} title="Storage & Data Locality" desc="Ensuring training data remains close to compute nodes to minimize I/O overhead.">
      <p className="text-slate-400">Hyper-converged storage optimizes throughput for high-frequency AI pipelines by pinning datasets directly to local node storage.</p>
      <CodeBlock code={`lightrail storage pin --dataset "imagenet-v2" --node-id HCI-01`} />
    </DocPage>
  ),
  'scalability-control': () => (
    <DocPage icon={Layers} title="Scalability & Capacity" desc="Predictable scaling as clusters grow from 1 to 1,000+ nodes.">
      <p className="text-slate-400">Supports node-based scaling and capacity planning through advanced GPU/CPU forecasting models.</p>
      <CodeBlock code={`lightrail cluster expand --nodes 4 --type h100-converged`} />
    </DocPage>
  ),
  'workload-isolation': () => (
    <DocPage icon={Lock} title="AI Workload Isolation" desc="Separating critical AI training from general enterprise workloads.">
      <p className="text-slate-400">Uses Noisy Neighbor Prevention and Multi-Tenant Support to ensure stable performance under mixed loads.</p>
      <CodeBlock code={`lightrail security isolation-shield --tenant "Research-Alpha" --enable`} />
    </DocPage>
  ),
  'reliability-ha': () => (
    <DocPage icon={ShieldCheck} title="Reliability & High Availability" desc="Automated recovery and redundant paths for resilient inference.">
      <p className="text-slate-400">Protects workloads from node or disk failures through built-in failover handling and state syncing.</p>
      <CodeBlock code={`lightrail ha status --cluster "SJ-ALPHA"`} />
    </DocPage>
  ),
  'operational-simplicity': () => (
    <DocPage icon={Layout} title="Operational Simplicity" desc="Unified management of compute, storage, and network from one interface.">
      <p className="text-slate-400">Enables rolling updates and reduced infrastructure complexity through software-defined HCI logic.</p>
      <CodeBlock code={`lightrail cluster update --rolling --strategy zero-downtime`} />
    </DocPage>
  ),
  'hybrid-edge': () => (
    <DocPage icon={Radio} title="Hybrid & Edge AI Enablement" desc="Deploying inference close to data sources with seamless cloud integration.">
      <p className="text-slate-400">Supports on-prem AI workloads where cloud residency is not feasible or compliant, and manages edge site life-cycles.</p>
      <CodeBlock code={`lightrail edge deploy --site "Site-London-01" --job "Edge-Vision-v2"`} />
    </DocPage>
  ),
  'cost-predictability': () => (
    <DocPage icon={FileBarChart} title="Cost & Governance" desc="Usage visibility and CapEx-based cost modeling for infrastructure ROI.">
      <p className="text-slate-400">Supports enterprise compliance, security alignment, and predictive infrastructure spend tracking through detailed usage reporting.</p>
      <CodeBlock code={`lightrail report generate --type governance --format pdf`} />
    </DocPage>
  ),
  authentication: () => (
    <DocPage icon={Shield} title="Authentication" desc="Secure your control plane with Bearer tokens and ED25519 signing.">
      <p className="text-slate-400">Access tokens can be generated in the System Settings panel and must be passed in the Authorization header.</p>
      <CodeBlock code={`curl -H "Authorization: Bearer LR_XXXX" https://lightrail.ink/v1/auth`} />
    </DocPage>
  )
};

const Documentation: React.FC = () => {
  const { section } = useParams();

  const navigation = [
    { group: 'Getting Started', items: [
      { id: 'introduction', name: 'Introduction', icon: Zap },
      { id: 'authentication', name: 'Authentication', icon: Shield },
    ]},
    { group: 'HCI Domain Functions', items: [
      { id: 'compute-management', name: 'Compute Management', icon: Cpu },
      { id: 'storage-locality', name: 'Storage Locality', icon: Database },
      { id: 'scalability-control', name: 'Scalability & Capacity', icon: Layers },
      { id: 'workload-isolation', name: 'AI Workload Isolation', icon: Lock },
      { id: 'reliability-ha', name: 'Reliability & HA', icon: ShieldCheck },
      { id: 'operational-simplicity', name: 'Operational Simplicity', icon: Layout },
      { id: 'hybrid-edge', name: 'Hybrid & Edge AI', icon: Radio },
      { id: 'cost-predictability', name: 'Cost & Governance', icon: FileBarChart },
    ]}
  ];

  const CurrentPage = section && components[section] ? components[section] : components['introduction'];

  return (
    <div className="max-w-7xl mx-auto flex flex-col xl:flex-row gap-12 pb-24">
      {/* Sidebar */}
      <aside className="w-full xl:w-80 shrink-0 space-y-10">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
            <Book className="w-8 h-8 text-[#00FF41]" />
            Docs
          </h1>
          <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-2 pl-1">V1.4.2 Technical Ref</p>
        </div>

        <nav className="space-y-8">
          {navigation.map(group => (
            <div key={group.group}>
              <h3 className="text-[10px] font-bold text-slate-600 uppercase tracking-widest mb-3 pl-4">{group.group}</h3>
              <div className="space-y-1">
                {group.items.map(item => (
                  <NavLink
                    key={item.id}
                    to={`/docs/${item.id}`}
                    className={({ isActive }) => `
                      flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all
                      ${isActive ? 'bg-slate-800 text-[#00FF41] border border-slate-700 shadow-lg' : 'text-slate-400 hover:text-white'}
                    `}
                  >
                    <item.icon className="w-4 h-4" />
                    {item.name}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>
      </aside>

      {/* Content */}
      <div className="flex-1 bg-slate-900/30 rounded-[2.5rem] border border-slate-800 p-8 md:p-14 shadow-2xl relative overflow-hidden min-h-[600px]">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#00FF41]/5 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="relative z-10">
          <CurrentPage />
        </div>
      </div>
    </div>
  );
};

export default Documentation;
