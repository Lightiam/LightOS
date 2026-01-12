#!/usr/bin/env python3
"""
LightOS DCIM API
Data Center Infrastructure Management API with real-time telemetry
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uvicorn

app = FastAPI(
    title="LightOS DCIM API",
    description="Data Center Infrastructure Management with AI-driven telemetry",
    version="1.0.0"
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
# DATA MODELS & SIMULATORS
# ============================================================================

class DCIMSimulator:
    """Simulates realistic datacenter metrics"""

    def __init__(self):
        self.base_power = 150000  # 150kW base load
        self.num_gpus = 128
        self.base_temp = 22.0  # Celsius
        self.time_start = datetime.now()

    def get_gpu_metrics(self, gpu_id: int = 0) -> Dict[str, Any]:
        """Get real-time GPU metrics"""
        # Simulate realistic GPU behavior
        clock_base = 1410  # MHz
        clock_jitter = random.uniform(-5, 5)

        temp_base = 65 + random.uniform(-3, 3)
        power_base = 350 + random.uniform(-20, 20)  # Watts

        # Simulate occasional throttling (rare)
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

        avg_temp = self.base_temp + random.uniform(0, 2)

        # Calculate AI-OEE (Overall Equipment Effectiveness)
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
            "cooling_temp_c": avg_temp,
            "cooling_flow_lpm": random.uniform(4500, 5000),
            "ai_oee": ai_oee,
            "mfu_pct": random.uniform(0.85, 0.92),  # Model FLOPS Utilization
            "uptime_hours": (datetime.now() - self.time_start).total_seconds() / 3600
        }

    def get_power_metrics(self) -> Dict[str, Any]:
        """Get power distribution metrics"""
        hour = datetime.now().hour

        # Simulate daily power pattern
        if 9 <= hour <= 17:  # Peak hours
            load_factor = random.uniform(0.85, 0.95)
        else:
            load_factor = random.uniform(0.60, 0.75)

        total_capacity = 500  # kW
        current_load = total_capacity * load_factor

        return {
            "timestamp": datetime.now().isoformat(),
            "total_capacity_kw": total_capacity,
            "current_load_kw": current_load,
            "load_factor_pct": load_factor * 100,
            "power_factor": random.uniform(0.95, 0.99),
            "ess_soc_pct": random.uniform(65, 85),  # Energy Storage State of Charge
            "ess_charging": random.choice([True, False]),
            "peak_predicted_kw": current_load * 1.15,
            "peak_time_forecast": (datetime.now() + timedelta(hours=2)).isoformat(),
            "grid_status": "normal",
            "voltage_v": [480, 480, 480],
            "current_a": [current_load * 1000 / 480 / 3] * 3,
            "frequency_hz": 60.0 + random.uniform(-0.1, 0.1)
        }

    def get_thermal_metrics(self) -> Dict[str, Any]:
        """Get cooling system metrics"""
        supply_temp = self.base_temp + random.uniform(-1, 1)
        return_temp = supply_temp + random.uniform(8, 12)

        return {
            "timestamp": datetime.now().isoformat(),
            "supply_temp_c": supply_temp,
            "return_temp_c": return_temp,
            "delta_t_c": return_temp - supply_temp,
            "flow_rate_lpm": random.uniform(4500, 5000),
            "pressure_kpa": random.uniform(200, 250),
            "chiller_load_pct": random.uniform(65, 80),
            "cooling_capacity_kw": 600,
            "cooling_load_kw": random.uniform(380, 480),
            "wet_bulb_temp_c": 18 + random.uniform(-2, 2),
            "ambient_temp_c": 28 + random.uniform(-3, 3),
            "humidity_pct": random.uniform(40, 60)
        }

    def get_kpi_summary(self) -> Dict[str, Any]:
        """Get KPI summary for dashboard"""
        gpu_metrics = self.get_gpu_metrics()
        cluster = self.get_cluster_metrics()
        power = self.get_power_metrics()
        thermal = self.get_thermal_metrics()

        # Calculate key KPIs
        clock_stability = 99.8 - random.uniform(0, 0.3)
        throttle_events = random.randint(0, 2)
        thermal_headroom = 90 - gpu_metrics["temperature_c"]
        power_utilization = (gpu_metrics["power_draw_w"] / gpu_metrics["power_limit_w"]) * 100

        # Peak shaving savings
        peak_shaving_savings_monthly = random.uniform(12000, 18000)

        return {
            "timestamp": datetime.now().isoformat(),
            "clock_stability_pct": clock_stability,
            "throttle_events_count": throttle_events,
            "thermal_headroom_c": thermal_headroom,
            "power_utilization_pct": power_utilization,
            "ai_oee_pct": cluster["ai_oee"] * 100,
            "mfu_pct": cluster["mfu_pct"] * 100,
            "peak_shaving_savings_usd": peak_shaving_savings_monthly,
            "pue": cluster["pue"],
            "uptime_hours": cluster["uptime_hours"],
            "status": "optimal",
            "alerts": []
        }

    def get_telemetry_signals(self) -> List[Dict[str, Any]]:
        """Get telemetry signal definitions"""
        return [
            {
                "signal": "GPU SM Clock",
                "source": "DCGM",
                "frequency": "1 Hz",
                "primary_use": "Clock stability verification",
                "unit": "MHz"
            },
            {
                "signal": "GPU Temperature",
                "source": "DCGM",
                "frequency": "1 Hz",
                "primary_use": "Thermal headroom monitoring",
                "unit": "°C"
            },
            {
                "signal": "GPU Power Draw",
                "source": "DCGM",
                "frequency": "1 Hz",
                "primary_use": "Power utilization tracking",
                "unit": "W"
            },
            {
                "signal": "PDU Load",
                "source": "Raritan PDU",
                "frequency": "1 Hz",
                "primary_use": "Peak prediction & shaving",
                "unit": "kW"
            },
            {
                "signal": "PDU Power Factor",
                "source": "Raritan PDU",
                "frequency": "1 Hz",
                "primary_use": "Power quality monitoring",
                "unit": "ratio"
            },
            {
                "signal": "Cooling Supply Temp",
                "source": "BMS",
                "frequency": "0.1 Hz",
                "primary_use": "Thermal control",
                "unit": "°C"
            },
            {
                "signal": "Cooling Flow Rate",
                "source": "BMS",
                "frequency": "0.1 Hz",
                "primary_use": "Cooling capacity verification",
                "unit": "LPM"
            },
            {
                "signal": "ESS State of Charge",
                "source": "Battery BMS",
                "frequency": "0.1 Hz",
                "primary_use": "Peak shaving readiness",
                "unit": "%"
            },
            {
                "signal": "ESS State of Health",
                "source": "Battery BMS",
                "frequency": "0.01 Hz",
                "primary_use": "Battery lifecycle management",
                "unit": "%"
            },
            {
                "signal": "Job Queue Depth",
                "source": "Slurm",
                "frequency": "0.1 Hz",
                "primary_use": "Workload relocation decisions",
                "unit": "count"
            }
        ]


# Global simulator instance
simulator = DCIMSimulator()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "LightOS DCIM API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "kpi": "/api/dcim/kpi",
            "gpu": "/api/dcim/gpu/{gpu_id}",
            "cluster": "/api/dcim/cluster",
            "power": "/api/dcim/power",
            "thermal": "/api/dcim/thermal",
            "telemetry": "/api/dcim/telemetry",
            "websocket": "/ws/dcim"
        }
    }


@app.get("/api/dcim/kpi")
async def get_kpi():
    """Get KPI summary"""
    return simulator.get_kpi_summary()


@app.get("/api/dcim/gpu/{gpu_id}")
async def get_gpu_metrics(gpu_id: int):
    """Get metrics for specific GPU"""
    if gpu_id < 0 or gpu_id >= simulator.num_gpus:
        return JSONResponse(
            status_code=404,
            content={"error": f"GPU {gpu_id} not found"}
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


@app.get("/api/dcim/thermal")
async def get_thermal_metrics():
    """Get cooling system metrics"""
    return simulator.get_thermal_metrics()


@app.get("/api/dcim/telemetry")
async def get_telemetry_signals():
    """Get telemetry signal definitions"""
    return {
        "signals": simulator.get_telemetry_signals()
    }


@app.get("/api/dcim/isa95")
async def get_isa95_layers():
    """Get ISA-95 layer breakdown"""
    return {
        "layers": [
            {
                "layer": "M1",
                "name": "Sensing & Manipulation",
                "isa95_level": "L0-L1",
                "description": "Hardware sensors, actuators, and basic control",
                "components": ["DCGM", "PDU sensors", "BMS", "Temperature probes"],
                "data_frequency": "1-10 Hz"
            },
            {
                "layer": "M2",
                "name": "Monitoring & Supervision",
                "isa95_level": "L2",
                "description": "Real-time data aggregation and visualization",
                "components": ["Prometheus", "Grafana", "Alert Manager"],
                "data_frequency": "0.1-1 Hz"
            },
            {
                "layer": "M3",
                "name": "Manufacturing Operations Management",
                "isa95_level": "L3",
                "description": "Workload orchestration and resource management",
                "components": ["Kubernetes", "Slurm", "Job Scheduler"],
                "data_frequency": "0.01-0.1 Hz"
            },
            {
                "layer": "M4",
                "name": "Business Planning & Logistics",
                "isa95_level": "L4",
                "description": "Capacity planning, SLA management, billing",
                "components": ["ERP", "CRM", "Billing System"],
                "data_frequency": "Hourly to Daily"
            },
            {
                "layer": "M5",
                "name": "AI Orchestration & Optimization",
                "isa95_level": "Cross-layer",
                "description": "ML-driven predictive control and optimization",
                "components": ["LightRail AI", "Peak Predictor", "Thermal Optimizer"],
                "data_frequency": "Variable (event-driven)"
            }
        ]
    }


@app.get("/api/dcim/peak-shaving")
async def get_peak_shaving_strategy():
    """Get peak shaving strategy steps"""
    return {
        "strategy": [
            {
                "step": 1,
                "name": "IT Load & ESS SoC Monitoring",
                "description": "Continuous monitoring of IT power load and battery state",
                "inputs": ["PDU load (kW)", "ESS SoC (%)", "ESS SoH (%)"],
                "outputs": ["Real-time power profile"],
                "frequency": "1 Hz"
            },
            {
                "step": 2,
                "name": "ML-based Peak Prediction",
                "description": "Forecast power demand peaks 1-4 hours ahead",
                "inputs": ["Historical load", "Job queue", "Time of day", "Weather"],
                "outputs": ["Peak forecast (kW, time)"],
                "frequency": "Every 5 minutes"
            },
            {
                "step": 3,
                "name": "Peak Shaving via PCS",
                "description": "Charge/discharge battery to flatten peak",
                "inputs": ["Peak forecast", "ESS SoC", "Tariff rates"],
                "outputs": ["ESS charge/discharge commands"],
                "frequency": "Real-time"
            },
            {
                "step": 4,
                "name": "Job Relocation",
                "description": "Move non-critical jobs to off-peak hours",
                "inputs": ["Job priority", "Deadline", "Peak forecast"],
                "outputs": ["Rescheduled jobs"],
                "frequency": "Event-driven"
            },
            {
                "step": 5,
                "name": "Parameter & Model Optimization",
                "description": "Reduce power via smaller models or batch sizes",
                "inputs": ["Training config", "Power budget", "Performance requirements"],
                "outputs": ["Optimized hyperparameters"],
                "frequency": "Per-job"
            }
        ],
        "current_status": {
            "active_strategies": ["PCS", "Job Relocation"],
            "ess_mode": "standby",
            "predicted_peak_kw": simulator.get_power_metrics()["peak_predicted_kw"],
            "peak_time": simulator.get_power_metrics()["peak_time_forecast"],
            "savings_today_usd": random.uniform(400, 600)
        }
    }


@app.websocket("/ws/dcim")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time telemetry streaming"""
    await websocket.accept()

    try:
        while True:
            # Send real-time data every second
            data = {
                "type": "telemetry_update",
                "timestamp": datetime.now().isoformat(),
                "kpi": simulator.get_kpi_summary(),
                "cluster": simulator.get_cluster_metrics(),
                "power": simulator.get_power_metrics(),
                "thermal": simulator.get_thermal_metrics()
            }

            await websocket.send_json(data)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("Client disconnected")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "simulator": "running",
        "datacenter": "operational"
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LightOS DCIM API Server")
    print("=" * 70)
    print("Starting server on http://0.0.0.0:8001")
    print()
    print("Endpoints:")
    print("  - Dashboard KPIs:    http://localhost:8001/api/dcim/kpi")
    print("  - Cluster Metrics:   http://localhost:8001/api/dcim/cluster")
    print("  - Power Metrics:     http://localhost:8001/api/dcim/power")
    print("  - Thermal Metrics:   http://localhost:8001/api/dcim/thermal")
    print("  - ISA-95 Layers:     http://localhost:8001/api/dcim/isa95")
    print("  - Peak Shaving:      http://localhost:8001/api/dcim/peak-shaving")
    print("  - WebSocket:         ws://localhost:8001/ws/dcim")
    print("=" * 70)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
