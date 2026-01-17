#!/usr/bin/env python3
"""
LightOS DCIM Pro API - Enhanced
Advanced DCIM with ISA-95, ML-based peak shaving, and autonomous AI optimization
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import uvicorn
import os
from pathlib import Path

app = FastAPI(
    title="LightOS DCIM Pro API",
    description="AI-Driven Data Center Management with ISA-95 and ML-based optimization",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENHANCED DATA MODELS & SIMULATORS
# ============================================================================

class EnhancedDCIMSimulator:
    """Enhanced DCIM simulator with advanced features"""

    def __init__(self):
        self.base_power = 150000  # 150kW base load
        self.num_gpus = 128
        self.base_temp = 22.0  # Celsius
        self.time_start = datetime.now()

        # Advanced feature states
        self.predictive_cooling_active = True
        self.dynamic_power_capping_active = True
        self.carbon_aware_scheduling = True
        self.digital_twin_active = True

        # Peak shaving state
        self.peak_events_prevented = 23
        self.cost_savings_monthly = 1850.0

        # Job orchestration state
        self.low_priority_jobs = 12
        self.jobs_per_hour = 1240
        self.job_queue_depth = 3

    def get_enhanced_kpi_summary(self) -> Dict[str, Any]:
        """Get enhanced KPI summary with all new metrics"""
        # Base metrics
        clock_stability = 99.8 - random.uniform(0, 0.3)
        throttle_events = random.randint(0, 2)

        # AI-OEE calculation (more detailed)
        availability = 0.998
        performance = random.uniform(0.94, 0.98)
        quality = random.uniform(0.96, 0.99)
        ai_oee = availability * performance * quality

        # MFU (Model FLOPS Utilization)
        mfu = random.uniform(0.85, 0.92)

        # PUE with industry comparison
        pue = random.uniform(1.08, 1.12)
        industry_avg_pue = 1.58

        return {
            "timestamp": datetime.now().isoformat(),
            "clock_stability_pct": clock_stability,
            "throttle_events_count": throttle_events,
            "thermal_headroom_c": random.uniform(20, 25),
            "power_utilization_pct": random.uniform(88, 95),
            "ai_oee_pct": ai_oee * 100,
            "mfu_pct": mfu * 100,
            "pue": pue,
            "industry_avg_pue": industry_avg_pue,
            "pue_improvement_pct": ((industry_avg_pue - pue) / industry_avg_pue) * 100,
            "peak_shaving_savings_usd": random.uniform(12000, 18000),
            "uptime_hours": (datetime.now() - self.time_start).total_seconds() / 3600,
            "status": "optimal",
            "alerts": []
        }

    def get_peak_shaving_status(self) -> Dict[str, Any]:
        """Get ML-based peak shaving system status"""
        current_time = datetime.now()
        peak_time = current_time + timedelta(minutes=15)

        current_load = random.uniform(380, 420)
        predicted_peak = current_load * random.uniform(1.12, 1.18)

        return {
            "timestamp": current_time.isoformat(),
            "step1_monitoring": {
                "grid_power_kw": current_load,
                "ess_soc_pct": random.uniform(65, 85),
                "it_load_pdu_kw": current_load * 0.8,
                "it_load_workload_usages": current_load * 0.75
            },
            "step2_ml_prediction": {
                "predicted_peak_kw": predicted_peak,
                "peak_time_forecast": peak_time.isoformat(),
                "time_to_peak_minutes": 15,
                "confidence_pct": random.uniform(92, 96),
                "model_accuracy": 94.2,
                "integrated_monitoring": True,
                "machine_learning": "LSTM + Attention"
            },
            "step3_power_control": {
                "ess_dc_power_kw": random.uniform(20, 40),
                "pcs_status": random.choice(["Standby", "Charging", "Discharging"]),
                "peak_reduction_pct": random.uniform(12, 18),
                "time_to_charge_minutes": random.randint(45, 90),
                "power_conversion_system": "Bidirectional DC/AC"
            },
            "step4_job_relocation": {
                "low_priority_jobs_count": self.low_priority_jobs,
                "job_queue_depth": self.job_queue_depth,
                "power_freed_kw": random.uniform(7, 10),
                "peak_time_detected": True,
                "low_ess_battery": False,
                "high_electricity_cost": random.uniform(0.12, 0.18),
                "scheduler_decision_engine": "K8s + Slurm"
            },
            "step5_optimization": {
                "batch_size_adjustment": "256→128",
                "spikes_prevented_count": self.peak_events_prevented,
                "cost_savings_monthly_usd": self.cost_savings_monthly,
                "real_time_adjustment": True,
                "prevent_power_spikes": True,
                "large_model_optimization": "sLLM (Lightweight)",
                "reduce_gpu_power": "Reduce compute speed, throttling"
            },
            "summary": {
                "peak_shaving_active": True,
                "total_savings_today_usd": random.uniform(150, 300),
                "peaks_prevented_today": random.randint(2, 5),
                "ess_cycles_today": random.randint(1, 3),
                "carbon_reduced_kg": random.uniform(45, 75)
            }
        }

    def get_advanced_features_status(self) -> Dict[str, Any]:
        """Get status of all advanced AI-driven features"""
        return {
            "predictive_cooling": {
                "active": self.predictive_cooling_active,
                "energy_saved_pct": random.uniform(16, 20),
                "accuracy_pct": random.uniform(94, 98),
                "response_time_seconds": random.uniform(8, 12),
                "pre_cooling_enabled": True,
                "thermal_inertia_model": "Physics-based + ML",
                "scheduled_workload_impact": "15 min ahead",
                "description": "Pre-cooling based on schedule thermal inertia and workload predictions"
            },
            "workload_orchestration": {
                "active": True,
                "jobs_per_hour": self.jobs_per_hour + random.randint(-50, 50),
                "efficiency_pct": random.uniform(92, 96),
                "avg_queue_time_minutes": random.uniform(2, 3),
                "topology_aware": True,
                "power_thermal_constraints": True,
                "scheduler_type": "Topology-aware with GPU affinity",
                "description": "Topology-aware scheduling with power and thermal constraints"
            },
            "dynamic_power_capping": {
                "active": self.dynamic_power_capping_active,
                "capacity_gain_pct": random.uniform(10, 14),
                "safety_margin_pct": 5,
                "response_time_ms": random.uniform(45, 55),
                "safe_oversubscription": True,
                "real_time_control": True,
                "power_conversion_control": "Active",
                "description": "Safe oversubscription via real-time power conversion control"
            },
            "digital_twin": {
                "active": self.digital_twin_active,
                "accuracy_pct": random.uniform(97, 99),
                "scenarios_per_day": random.randint(400, 500),
                "prediction_window_minutes": 15,
                "simulation_active": True,
                "what_if_analysis": True,
                "real_time_learning": True,
                "description": "Real-time simulation and learning for what-if analysis"
            },
            "esg_carbon_tracking": {
                "active": self.carbon_aware_scheduling,
                "co2_reduced_pct": random.uniform(28, 32),
                "green_hours_pct": random.uniform(65, 70),
                "monthly_savings_usd": random.uniform(4000, 4500),
                "carbon_aware_scheduling": True,
                "low_carbon_hours_prioritized": True,
                "grid_carbon_intensity_monitoring": True,
                "description": "Carbon-aware scheduling to shift workloads to low-carbon hours"
            },
            "advanced_billing": {
                "active": True,
                "cost_per_token_usd": 0.002,
                "spot_savings_pct": random.uniform(38, 42),
                "accuracy_pct": 99.9,
                "per_token_pricing": True,
                "spot_pricing": True,
                "real_time_cost_optimization": True,
                "description": "Per-token, spot pricing with real-time cost optimization"
            },
            "sla_management": {
                "active": True,
                "sla_met_pct": random.uniform(99.93, 99.97),
                "violations_count": 0,
                "uptime_pct": random.uniform(99.96, 99.99),
                "performance_based_guarantees": True,
                "automated_tracking": True,
                "real_time_monitoring": True,
                "description": "Performance-based guarantees with automated tracking"
            },
            "capacity_planning": {
                "active": True,
                "utilization_pct": random.uniform(90, 94),
                "forecast_accuracy_pct": random.uniform(93, 97),
                "lead_time_days": 30,
                "stranded_power_prevention": True,
                "ml_demand_forecasting": True,
                "capacity_optimization": True,
                "description": "Preventing stranded power via ML-based demand forecasting"
            }
        }

    def get_isa95_detailed(self) -> Dict[str, Any]:
        """Get detailed ISA-95 5-layer architecture with features"""
        return {
            "timestamp": datetime.now().isoformat(),
            "layers": {
                "m5_ai_orchestration": {
                    "id": "M5",
                    "name": "AI Orchestration & Optimization",
                    "level": 5,
                    "description": "Cross-layer AI for autonomous datacenter optimization",
                    "features": {
                        "autonomous_optimization": {
                            "name": "Autonomous Optimization",
                            "description": "AI for AI Ops: ML-driven workload and infrastructure control",
                            "status": "active",
                            "metrics": {
                                "optimization_cycles_per_day": random.randint(800, 1200),
                                "accuracy": random.uniform(94, 98),
                                "response_time_ms": random.uniform(100, 200)
                            }
                        },
                        "predictive_cooling": {
                            "name": "Predictive Cooling",
                            "description": "Pre-cooling based on schedule thermal inertia predictions",
                            "status": "active",
                            "metrics": {
                                "energy_saved_pct": random.uniform(16, 20),
                                "prediction_accuracy": random.uniform(94, 98),
                                "lead_time_minutes": 15
                            }
                        },
                        "dynamic_power_capping": {
                            "name": "Dynamic Power Capping",
                            "description": "Safe oversubscription via power conversion real-time control",
                            "status": "active",
                            "metrics": {
                                "capacity_gain_pct": random.uniform(10, 14),
                                "safety_margin_pct": 5,
                                "response_time_ms": random.uniform(45, 55)
                            }
                        },
                        "esg_carbon_aware": {
                            "name": "ESG: Carbon-Aware Scheduling",
                            "description": "Shift workloads to low-carbon grid hours",
                            "status": "active",
                            "metrics": {
                                "co2_reduced_pct": random.uniform(28, 32),
                                "green_hours_pct": random.uniform(65, 70),
                                "cost_savings_usd": random.uniform(4000, 4500)
                            }
                        }
                    }
                },
                "m4_business_planning": {
                    "id": "M4",
                    "name": "Business Planning & Logistics",
                    "level": 4,
                    "description": "Strategic planning and financial optimization",
                    "features": {
                        "advanced_billing": {
                            "name": "Advanced Billing",
                            "description": "Per-token, spot pricing for AI workloads",
                            "status": "active",
                            "metrics": {
                                "tokens_processed_billions": random.uniform(1.2, 1.8),
                                "cost_per_token": 0.002,
                                "spot_savings_pct": random.uniform(38, 42)
                            }
                        },
                        "sla_management": {
                            "name": "SLA Management",
                            "description": "Performance-based guarantees with automated tracking",
                            "status": "active",
                            "metrics": {
                                "sla_met_pct": random.uniform(99.93, 99.97),
                                "violations_count": 0,
                                "uptime_pct": random.uniform(99.96, 99.99)
                            }
                        },
                        "capacity_planning": {
                            "name": "Capacity Planning",
                            "description": "Preventing stranded power via demand forecasting",
                            "status": "active",
                            "metrics": {
                                "utilization_pct": random.uniform(90, 94),
                                "forecast_accuracy": random.uniform(93, 97),
                                "lead_time_days": 30
                            }
                        },
                        "roi_analysis": {
                            "name": "ROI Analysis",
                            "description": "Energy procurement & cost tracking optimization",
                            "status": "active",
                            "metrics": {
                                "annual_savings_usd": random.uniform(180000, 220000),
                                "roi_pct": random.uniform(25, 35),
                                "payback_period_months": random.randint(8, 14)
                            }
                        }
                    }
                },
                "m3_manufacturing_operations": {
                    "id": "M3",
                    "name": "Manufacturing Operations Management",
                    "level": 3,
                    "description": "Operational efficiency and orchestration",
                    "features": {
                        "operational_efficiency": {
                            "name": "Operational Efficiency",
                            "description": "Workload orchestration via topology-aware scheduling",
                            "status": "active",
                            "metrics": {
                                "jobs_per_hour": random.randint(1200, 1300),
                                "efficiency_pct": random.uniform(92, 96),
                                "topology_awareness": True
                            }
                        },
                        "ai_oee_tracking": {
                            "name": "AI-OEE Tracking",
                            "description": "Maximizing MFU & ETTF ratio",
                            "status": "active",
                            "metrics": {
                                "mfu_pct": random.uniform(85, 92),
                                "ettf_pct": random.uniform(88, 94),
                                "ai_oee": random.uniform(0.92, 0.96)
                            }
                        },
                        "asset_lifecycle": {
                            "name": "Asset Lifecycle",
                            "description": "Predictive maintenance scheduling optimization",
                            "status": "active",
                            "metrics": {
                                "mtbf_hours": random.randint(8000, 12000),
                                "maintenance_windows": random.randint(2, 4),
                                "downtime_reduction_pct": random.uniform(40, 60)
                            }
                        },
                        "resource_optimization": {
                            "name": "Resource Optimization",
                            "description": "Power/thermal-aware workload placement",
                            "status": "active",
                            "metrics": {
                                "placement_efficiency": random.uniform(93, 97),
                                "power_balance_score": random.uniform(0.85, 0.95),
                                "thermal_hotspots": 0
                            }
                        }
                    }
                },
                "m2_monitoring_supervision": {
                    "id": "M2",
                    "name": "Monitoring & Supervision",
                    "level": 2,
                    "description": "Holistic visibility and IT/OT convergence",
                    "features": {
                        "holistic_visibility": {
                            "name": "Holistic Visibility",
                            "description": "Single Pane of Glass: Integrated dashboards",
                            "status": "active",
                            "metrics": {
                                "data_sources": 15,
                                "refresh_rate_hz": 1,
                                "dashboard_uptime_pct": 99.99
                            }
                        },
                        "it_ot_convergence": {
                            "name": "IT/OT Convergence",
                            "description": "Correlating physical facility data with IT workload performance",
                            "status": "active",
                            "metrics": {
                                "correlation_accuracy": random.uniform(94, 98),
                                "data_integration_points": 28,
                                "real_time_sync": True
                            }
                        },
                        "deep_telemetry": {
                            "name": "Deep Telemetry",
                            "description": "DCGM (GPU), Packet Loss, thermal impact compute",
                            "status": "active",
                            "metrics": {
                                "signals_monitored": 45,
                                "sampling_rate_hz": 1,
                                "data_retention_days": 90
                            }
                        },
                        "real_time_alerting": {
                            "name": "Real-time Alerting",
                            "description": "Anomaly detection with automated response",
                            "status": "active",
                            "metrics": {
                                "alerts_per_day": random.randint(5, 15),
                                "false_positive_rate_pct": random.uniform(2, 5),
                                "response_time_seconds": random.uniform(5, 15)
                            }
                        }
                    }
                },
                "m1_sensing_manipulation": {
                    "id": "M1",
                    "name": "Sensing & Manipulation",
                    "level": 1,
                    "description": "Real-time interface and precision control",
                    "features": {
                        "real_time_interface": {
                            "name": "Real-Time Interface",
                            "description": "High-Frequency Telemetry: ms-level power data",
                            "status": "active",
                            "metrics": {
                                "sampling_rate_khz": 1,
                                "latency_ms": random.uniform(0.5, 2),
                                "data_accuracy_pct": 99.99
                            }
                        },
                        "precision_control": {
                            "name": "Precision Control",
                            "description": "Liquid cooling (flow/temp), PTP time sync",
                            "status": "active",
                            "metrics": {
                                "flow_control_accuracy_pct": random.uniform(98, 99.5),
                                "temp_control_precision_c": 0.5,
                                "ptp_sync_accuracy_ns": random.randint(50, 150)
                            }
                        },
                        "synchronization": {
                            "name": "Synchronization",
                            "description": "IEEE 1588v2 PTP for distributed coordination",
                            "status": "active",
                            "metrics": {
                                "sync_accuracy_ns": random.randint(50, 150),
                                "nodes_synchronized": 128,
                                "sync_stability_pct": 99.99
                            }
                        },
                        "abstraction": {
                            "name": "Abstraction",
                            "description": "Redfish, Modbus for hardware interaction",
                            "status": "active",
                            "metrics": {
                                "protocols_supported": 5,
                                "api_calls_per_second": random.randint(500, 1000),
                                "compatibility_score": 100
                            }
                        }
                    }
                }
            }
        }

    # Keep existing methods
    def get_gpu_metrics(self, gpu_id: int = 0) -> Dict[str, Any]:
        """Get real-time GPU metrics"""
        clock_base = 1410  # MHz
        clock_jitter = random.uniform(-5, 5)
        temp_base = 65 + random.uniform(-3, 3)
        power_base = 350 + random.uniform(-20, 20)
        throttle_event = random.random() < 0.001

        return {
            "gpu_id": gpu_id,
            "timestamp": datetime.now().isoformat(),
            "sm_clock_mhz": clock_base + clock_jitter,
            "memory_clock_mhz": 1215,
            "temperature_c": temp_base,
            "power_draw_w": power_base,
            "power_limit_w": 400,
            "utilization_pct": random.uniform(92, 98),
            "memory_used_mb": random.randint(70000, 79000),
            "memory_total_mb": 80000,
            "throttle_reasons": {
                "sw_power_cap": throttle_event,
                "hw_slowdown": False,
                "hw_thermal_slowdown": False,
                "hw_power_brake_slowdown": False
            },
            "fan_speed_pct": random.uniform(60, 75),
            "pcie_tx_mbps": random.uniform(15000, 16000),
            "pcie_rx_mbps": random.uniform(15000, 16000)
        }

    def get_cluster_metrics(self) -> Dict[str, Any]:
        """Get cluster-wide metrics"""
        total_power = self.base_power + sum(
            random.uniform(300, 400) for _ in range(self.num_gpus)
        )

        availability = 0.998
        performance = random.uniform(0.94, 0.98)
        quality = random.uniform(0.96, 0.99)
        ai_oee = availability * performance * quality

        return {
            "timestamp": datetime.now().isoformat(),
            "total_gpus": self.num_gpus,
            "active_gpus": self.num_gpus,
            "total_power_kw": total_power / 1000,
            "pue": random.uniform(1.08, 1.12),
            "avg_gpu_temp_c": 65 + random.uniform(-2, 2),
            "avg_gpu_util_pct": random.uniform(93, 97),
            "cooling_temp_c": self.base_temp + random.uniform(0, 2),
            "cooling_flow_lpm": random.uniform(4500, 5000),
            "ai_oee": ai_oee,
            "mfu_pct": random.uniform(0.85, 0.92),
            "uptime_hours": (datetime.now() - self.time_start).total_seconds() / 3600
        }

    def get_power_metrics(self) -> Dict[str, Any]:
        """Get power distribution metrics"""
        hour = datetime.now().hour
        if 9 <= hour <= 17:
            load_factor = random.uniform(0.85, 0.95)
        else:
            load_factor = random.uniform(0.60, 0.75)

        total_capacity = 500
        current_load = total_capacity * load_factor

        return {
            "timestamp": datetime.now().isoformat(),
            "total_capacity_kw": total_capacity,
            "current_load_kw": current_load,
            "load_factor_pct": load_factor * 100,
            "power_factor": random.uniform(0.95, 0.99),
            "ess_soc_pct": random.uniform(65, 85),
            "ess_charging": random.choice([True, False]),
            "peak_predicted_kw": current_load * 1.15,
            "peak_time_forecast": (datetime.now() + timedelta(hours=2)).isoformat(),
            "grid_status": "normal",
            "voltage_v": [480, 480, 480],
            "current_a": [current_load * 1000 / 480 / 3] * 3,
            "frequency_hz": 60.0 + random.uniform(-0.1, 0.1)
        }


# Global enhanced simulator instance
simulator = EnhancedDCIMSimulator()


# ============================================================================
# UI DATA ENDPOINTS
# ============================================================================

# Mock data for UI
PROVIDERS = [
    {"id": "1", "name": "LightRail DC-SJ", "type": "On-Prem", "totalGpus": 1240, "totalTpus": 512, "utilization": 84.5, "hourlyCost": 1240.50, "sla": 99.99, "region": "US-West"},
    {"id": "2", "name": "AWS-US-West-2", "type": "Cloud", "totalGpus": 5200, "totalTpus": 0, "utilization": 62.1, "hourlyCost": 4850.20, "sla": 99.95, "region": "US-West"},
    {"id": "3", "name": "GCP-Europe-1", "type": "Cloud", "totalGpus": 800, "totalTpus": 2048, "utilization": 71.8, "hourlyCost": 2100.80, "sla": 99.9, "region": "EU-North"},
]

JOBS = [
    {"id": "J-101", "name": "LLM-Pretrain-A", "tenant": "NeuroScale AI", "status": "RUNNING", "resources": "8x H100", "provider": "LightRail DC-SJ", "startTime": "2h ago", "cost": 420.50, "progress": 45, "kwhPerJob": 120},
    {"id": "J-102", "name": "Vision-Distill-01", "tenant": "SightCorp", "status": "QUEUED", "resources": "4x TPU v5e", "provider": "GCP-Europe-1", "startTime": "-", "cost": 0, "progress": 0},
    {"id": "J-103", "name": "Inference-Fleet-X", "tenant": "AutoBot", "status": "RUNNING", "resources": "16x A100", "provider": "AWS-US-West-2", "startTime": "12h ago", "cost": 1240.80, "progress": 88, "kwhPerJob": 450},
]

SITES = [
    {"id": "S-1", "name": "SJ-Alpha-01", "region": "San Jose, CA", "pue": 1.12, "racks": 48, "utilization": 86, "totalPowerCapacity": 2.5},
    {"id": "S-2", "name": "EU-Central-02", "region": "Frankfurt, DE", "pue": 1.24, "racks": 32, "utilization": 64, "totalPowerCapacity": 1.8},
]

RACKS = [
    {"id": "R-01", "name": "Rack-01", "pue": 1.08, "nodeCount": 12, "status": "OK", "powerLimit": 40, "powerActual": 32.4, "inletTemp": 22, "outletTemp": 34},
    {"id": "R-02", "name": "Rack-02", "pue": 1.15, "nodeCount": 10, "status": "OK", "powerLimit": 40, "powerActual": 38.1, "inletTemp": 24, "outletTemp": 38},
    {"id": "R-03", "name": "Rack-03", "pue": 1.21, "nodeCount": 12, "status": "WARNING", "powerLimit": 40, "powerActual": 39.8, "inletTemp": 28, "outletTemp": 44},
]

HCI_NODES = [
    {"id": f"HCI-{i+1}", "name": f"Converged-Node-0{i+1}", "computeUtil": 60 + random.uniform(0, 30), "storageUtil": 40 + random.uniform(0, 50),
     "throughput": f"{(100 + random.uniform(0, 200)):.1f} GB/s", "latency": f"{(0.1 + random.uniform(0, 0.2)):.2f}ms",
     "redundancyStatus": "DEGRADED" if i == 7 else "ACTIVE", "tenantId": "T-01" if i < 4 else "T-02"}
    for i in range(8)
]

TENANT_ISOLATION = [
    {"id": "T-01", "name": "OpenAI-Research", "resourceShare": 45, "noisyNeighborScore": 4, "securityAlignment": "COMPLIANT"},
    {"id": "T-02", "name": "Enterprise-Core", "resourceShare": 30, "noisyNeighborScore": 12, "securityAlignment": "COMPLIANT"},
    {"id": "T-03", "name": "Edge-Inference-Labs", "resourceShare": 25, "noisyNeighborScore": 2, "securityAlignment": "COMPLIANT"},
]

MOCK_NODES = [
    {"id": f"N-{i+1}", "name": f"Rack-01-Node-{i+1}", "rackId": "R-01", "type": "NVIDIA H100" if i % 2 == 0 else "Google TPU v5e",
     "power": random.uniform(0.5, 3.0), "temp": random.uniform(40, 60), "utilization": random.uniform(0, 100),
     "health": "OK" if random.random() > 0.1 else "WARNING", "throttlingLoss": random.uniform(0, 15) if random.random() > 0.8 else 0}
    for i in range(12)
]

@app.get("/api/providers")
async def get_providers():
    """Get infrastructure providers"""
    return PROVIDERS

@app.get("/api/jobs")
async def get_jobs():
    """Get workload jobs"""
    return JOBS

@app.get("/api/sites")
async def get_sites():
    """Get datacenter sites"""
    return SITES

@app.get("/api/racks")
async def get_racks():
    """Get rack information"""
    return RACKS

@app.get("/api/nodes")
async def get_nodes():
    """Get node metrics"""
    return MOCK_NODES

@app.get("/api/hci-nodes")
async def get_hci_nodes():
    """Get HCI nodes"""
    return HCI_NODES

@app.get("/api/tenant-isolation")
async def get_tenant_isolation():
    """Get tenant isolation info"""
    return TENANT_ISOLATION


# ============================================================================
# ENHANCED API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "LightOS DCIM Pro API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "ISA-95 5-Layer Architecture",
            "ML-Based Peak Shaving",
            "Predictive Cooling",
            "Dynamic Power Capping",
            "Carbon-Aware Scheduling",
            "Digital Twin",
            "Advanced Billing",
            "SLA Management"
        ],
        "endpoints": {
            "kpi": "/api/dcim/kpi",
            "gpu": "/api/dcim/gpu/{gpu_id}",
            "cluster": "/api/dcim/cluster",
            "power": "/api/dcim/power",
            "peak_shaving": "/api/dcim/peak-shaving",
            "advanced_features": "/api/dcim/advanced-features",
            "isa95": "/api/dcim/isa95",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime_seconds": (datetime.now() - simulator.time_start).total_seconds()
    }


@app.get("/api/dcim/kpi")
async def get_kpi():
    """Get enhanced KPI summary"""
    return simulator.get_enhanced_kpi_summary()


@app.get("/api/dcim/gpu/{gpu_id}")
async def get_gpu_metrics(gpu_id: int):
    """Get GPU-specific metrics"""
    if gpu_id < 0 or gpu_id >= simulator.num_gpus:
        return JSONResponse(
            status_code=400,
            content={"error": f"GPU ID must be between 0 and {simulator.num_gpus - 1}"}
        )
    return simulator.get_gpu_metrics(gpu_id)


@app.get("/api/dcim/cluster")
async def get_cluster_metrics():
    """Get cluster-wide metrics"""
    return simulator.get_cluster_metrics()


@app.get("/api/dcim/power")
async def get_power_metrics():
    """Get power distribution metrics"""
    return simulator.get_power_metrics()


@app.get("/api/dcim/peak-shaving")
async def get_peak_shaving_status():
    """Get ML-based peak shaving system status"""
    return simulator.get_peak_shaving_status()


@app.get("/api/dcim/advanced-features")
async def get_advanced_features():
    """Get status of all advanced AI-driven features"""
    return simulator.get_advanced_features_status()


@app.get("/api/dcim/isa95")
async def get_isa95_details():
    """Get detailed ISA-95 5-layer architecture"""
    return simulator.get_isa95_detailed()


# WebSocket for real-time streaming
@app.websocket("/ws/dcim")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry"""
    await websocket.accept()
    try:
        while True:
            data = {
                "timestamp": datetime.now().isoformat(),
                "kpi": simulator.get_enhanced_kpi_summary(),
                "power": simulator.get_power_metrics(),
                "peak_shaving": simulator.get_peak_shaving_status()
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)  # 1 Hz
    except WebSocketDisconnect:
        pass


# ============================================================================
# STATIC FILE SERVING
# ============================================================================

# Mount static files if the build directory exists
STATIC_DIR = Path(__file__).parent.parent / "web-ui" / "dist"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SPA for all non-API routes"""
        # Skip API routes
        if full_path.startswith("api/") or full_path.startswith("ws/") or full_path == "health" or full_path == "docs" or full_path == "openapi.json":
            return JSONResponse({"error": "Not found"}, status_code=404)

        # Serve index.html for SPA routes
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return JSONResponse({"error": "Frontend not built. Run: cd web-ui && npm run build"}, status_code=404)


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
