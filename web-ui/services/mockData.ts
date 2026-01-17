
import { Provider, Job, Site, NodeMetrics, Rack, HCINode, TenantIsolation } from '../types';

export const INITIAL_PROVIDERS: Provider[] = [
  { id: '1', name: 'LightRail DC-SJ', type: 'On-Prem', totalGpus: 1240, totalTpus: 512, utilization: 84.5, hourlyCost: 1240.50, sla: 99.99, region: 'US-West' },
  { id: '2', name: 'AWS-US-West-2', type: 'Cloud', totalGpus: 5200, totalTpus: 0, utilization: 62.1, hourlyCost: 4850.20, sla: 99.95, region: 'US-West' },
  { id: '3', name: 'GCP-Europe-1', type: 'Cloud', totalGpus: 800, totalTpus: 2048, utilization: 71.8, hourlyCost: 2100.80, sla: 99.9, region: 'EU-North' },
];

export const INITIAL_JOBS: Job[] = [
  { id: 'J-101', name: 'LLM-Pretrain-A', tenant: 'NeuroScale AI', status: 'RUNNING', resources: '8x H100', provider: 'LightRail DC-SJ', startTime: '2h ago', cost: 420.50, progress: 45, kwhPerJob: 120 },
  { id: 'J-102', name: 'Vision-Distill-01', tenant: 'SightCorp', status: 'QUEUED', resources: '4x TPU v5e', provider: 'GCP-Europe-1', startTime: '-', cost: 0, progress: 0 },
  { id: 'J-103', name: 'Inference-Fleet-X', tenant: 'AutoBot', status: 'RUNNING', resources: '16x A100', provider: 'AWS-US-West-2', startTime: '12h ago', cost: 1240.80, progress: 88, kwhPerJob: 450 },
];

export const HCI_NODES: HCINode[] = Array.from({ length: 8 }, (_, i) => ({
  id: `HCI-${i + 1}`,
  name: `Converged-Node-0${i + 1}`,
  computeUtil: 60 + Math.random() * 30,
  storageUtil: 40 + Math.random() * 50,
  throughput: `${(100 + Math.random() * 200).toFixed(1)} GB/s`,
  latency: `${(0.1 + Math.random() * 0.2).toFixed(2)}ms`,
  redundancyStatus: i === 7 ? 'DEGRADED' : 'ACTIVE',
  tenantId: i < 4 ? 'T-01' : 'T-02'
}));

export const TENANT_ISOLATION: TenantIsolation[] = [
  { id: 'T-01', name: 'OpenAI-Research', resourceShare: 45, noisyNeighborScore: 4, securityAlignment: 'COMPLIANT' },
  { id: 'T-02', name: 'Enterprise-Core', resourceShare: 30, noisyNeighborScore: 12, securityAlignment: 'COMPLIANT' },
  { id: 'T-03', name: 'Edge-Inference-Labs', resourceShare: 25, noisyNeighborScore: 2, securityAlignment: 'COMPLIANT' },
];

export const INITIAL_SITES: Site[] = [
  { id: 'S-1', name: 'SJ-Alpha-01', region: 'San Jose, CA', pue: 1.12, racks: 48, utilization: 86, totalPowerCapacity: 2.5 },
  { id: 'S-2', name: 'EU-Central-02', region: 'Frankfurt, DE', pue: 1.24, racks: 32, utilization: 64, totalPowerCapacity: 1.8 },
];

export const INITIAL_RACKS: Rack[] = [
  { id: 'R-01', name: 'Rack-01', pue: 1.08, nodeCount: 12, status: 'OK', powerLimit: 40, powerActual: 32.4, inletTemp: 22, outletTemp: 34 },
  { id: 'R-02', name: 'Rack-02', pue: 1.15, nodeCount: 10, status: 'OK', powerLimit: 40, powerActual: 38.1, inletTemp: 24, outletTemp: 38 },
  { id: 'R-03', name: 'Rack-03', pue: 1.21, nodeCount: 12, status: 'WARNING', powerLimit: 40, powerActual: 39.8, inletTemp: 28, outletTemp: 44 },
];

export const MOCK_NODES: NodeMetrics[] = Array.from({ length: 12 }, (_, i) => ({
  id: `N-${i + 1}`,
  name: `Rack-01-Node-${i + 1}`,
  rackId: 'R-01',
  type: i % 2 === 0 ? 'NVIDIA H100' : 'Google TPU v5e',
  power: Math.random() * 2.5 + 0.5,
  temp: Math.random() * 20 + 40,
  utilization: Math.random() * 100,
  health: Math.random() > 0.1 ? 'OK' : 'WARNING',
  throttlingLoss: Math.random() > 0.8 ? Math.random() * 15 : 0,
}));

export const DCIM_ALERTS = [
  { id: 1, type: 'THERMAL', message: 'Rack-03 inlet delta exceeds policy (28°C). Throttling risk.', time: '2m ago' },
  { id: 2, type: 'POWER', message: 'Circuit A-14 approaching breaker limit (94%). Auto-rebalancing initiated.', time: '5m ago' },
  { id: 3, type: 'FABRIC', message: 'East-West congestion on SJ-Leaf-04 blocking collective NCCL operations.', time: '12m ago' },
];

export const UTILIZATION_HISTORY = [
  { time: '00:00', utilization: 65 },
  { time: '04:00', utilization: 42 },
  { time: '08:00', utilization: 78 },
  { time: '12:00', utilization: 92 },
  { time: '16:00', utilization: 85 },
  { time: '20:00', utilization: 74 },
  { time: '23:59', utilization: 68 },
];

export const COST_BREAKDOWN = [
  { name: 'GPU Compute (H100/A100)', value: 142000 },
  { name: 'TPU Clusters (v5e)', value: 38500 },
  { name: 'PUE/Facility Overhead', value: 12400 },
  { name: 'Fabric Transit', value: 8900 },
];
