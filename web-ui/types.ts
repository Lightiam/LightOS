
export type HealthStatus = 'OK' | 'WARNING' | 'CRITICAL';

export interface Provider {
  id: string;
  name: string;
  type: 'Cloud' | 'On-Prem' | 'Edge';
  totalGpus: number;
  totalTpus: number;
  utilization: number;
  hourlyCost: number;
  sla: number;
  region: string;
}

export interface Job {
  id: string;
  name: string;
  tenant: string;
  status: 'QUEUED' | 'RUNNING' | 'SUCCEEDED' | 'FAILED';
  resources: string;
  provider: string;
  startTime: string;
  cost: number;
  progress: number;
  kwhPerJob?: number;
}

export interface HCINode {
  id: string;
  name: string;
  computeUtil: number;
  storageUtil: number;
  throughput: string; // e.g. "80 GB/s"
  latency: string; // e.g. "0.2ms"
  redundancyStatus: 'ACTIVE' | 'STANDBY' | 'DEGRADED';
  tenantId: string;
}

export interface TenantIsolation {
  id: string;
  name: string;
  resourceShare: number; // % of cluster
  noisyNeighborScore: number; // 0-100, lower is better
  securityAlignment: 'COMPLIANT' | 'NON_COMPLIANT';
}

export interface Rack {
  id: string;
  name: string;
  pue: number;
  nodeCount: number;
  status: HealthStatus;
  powerLimit: number; // kW
  powerActual: number; // kW
  inletTemp: number; // C
  outletTemp: number; // C
}

export interface NodeMetrics {
  id: string;
  name: string;
  rackId: string;
  type: string;
  power: number; // kW
  temp: number; // Celsius
  utilization: number;
  health: HealthStatus;
  throttlingLoss: number; // % performance lost to thermals
}

export interface Site {
  id: string;
  name: string;
  region: string;
  pue: number;
  racks: number;
  utilization: number;
  totalPowerCapacity: number; // MW
}
