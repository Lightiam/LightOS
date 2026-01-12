#!/usr/bin/env python3
"""
LightRail AI DCIM Demo
Demonstrates AI-driven datacenter management functions
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
import numpy as np


class LightRailAI:
    """
    LightRail AI - Autonomous Datacenter Management

    Capabilities:
    1. Peak Power Prediction (ML-based forecasting)
    2. Thermal Anomaly Detection
    3. Workload Optimization & Relocation
    4. Predictive Maintenance
    5. Energy Cost Optimization
    """

    def __init__(self):
        self.model_loaded = True
        self.training_data_points = 10000
        self.prediction_accuracy = 0.94

    async def predict_peak_power(
        self,
        current_load_kw: float,
        time_of_day: int,
        job_queue_depth: int,
        historical_pattern: List[float]
    ) -> Dict[str, Any]:
        """
        Predict power demand peak using ML model

        Args:
            current_load_kw: Current power load in kW
            time_of_day: Hour of day (0-23)
            job_queue_depth: Number of queued jobs
            historical_pattern: Historical load pattern

        Returns:
            Prediction with confidence interval
        """
        print(f"\n🤖 LightRail AI: Analyzing power demand patterns...")
        await asyncio.sleep(0.5)  # Simulate ML inference

        # Simulate ML model prediction
        # In production, this would use trained LSTM/Transformer model

        # Base prediction on time of day pattern
        if 9 <= time_of_day <= 17:  # Peak hours
            base_multiplier = 1.2
        elif 18 <= time_of_day <= 22:
            base_multiplier = 1.1
        else:
            base_multiplier = 0.9

        # Factor in job queue
        queue_factor = 1 + (job_queue_depth * 0.02)

        # Predicted peak
        predicted_peak = current_load_kw * base_multiplier * queue_factor

        # Add noise to simulate real ML uncertainty
        prediction_std = predicted_peak * 0.05
        confidence_interval = {
            "lower": predicted_peak - 1.96 * prediction_std,
            "upper": predicted_peak + 1.96 * prediction_std
        }

        # Estimate time to peak
        if time_of_day < 14:
            hours_to_peak = 14 - time_of_day
        else:
            hours_to_peak = 24 - time_of_day + 14

        peak_time = datetime.now() + timedelta(hours=hours_to_peak)

        result = {
            "predicted_peak_kw": round(predicted_peak, 2),
            "confidence_interval": confidence_interval,
            "peak_time_forecast": peak_time.isoformat(),
            "hours_to_peak": hours_to_peak,
            "model_confidence": self.prediction_accuracy,
            "recommendation": self._generate_peak_recommendation(predicted_peak, current_load_kw)
        }

        print(f"✓ Predicted peak: {result['predicted_peak_kw']:.1f} kW")
        print(f"✓ Time to peak: {hours_to_peak} hours")
        print(f"✓ Model confidence: {self.prediction_accuracy*100:.1f}%")

        return result

    def _generate_peak_recommendation(self, predicted_peak: float, current_load: float) -> str:
        """Generate recommendation based on prediction"""
        increase_pct = ((predicted_peak - current_load) / current_load) * 100

        if increase_pct > 20:
            return "HIGH ALERT: Activate ESS discharge + relocate non-critical jobs"
        elif increase_pct > 10:
            return "MODERATE: Prepare ESS for peak shaving"
        else:
            return "NORMAL: Continue monitoring"

    async def detect_thermal_anomaly(
        self,
        gpu_temps: List[float],
        ambient_temp: float,
        coolant_flow: float
    ) -> Dict[str, Any]:
        """
        Detect thermal anomalies using AI

        Args:
            gpu_temps: List of GPU temperatures
            ambient_temp: Ambient temperature
            coolant_flow: Coolant flow rate

        Returns:
            Anomaly detection results
        """
        print(f"\n🌡️ LightRail AI: Running thermal anomaly detection...")
        await asyncio.sleep(0.3)

        # Calculate thermal metrics
        avg_temp = np.mean(gpu_temps)
        max_temp = np.max(gpu_temps)
        temp_std = np.std(gpu_temps)

        # Anomaly detection logic
        anomalies = []

        # Check for hot spots
        if max_temp > 80:
            anomalies.append({
                "type": "hot_spot",
                "severity": "high",
                "gpu_id": int(np.argmax(gpu_temps)),
                "temperature": max_temp,
                "action": "Increase cooling to affected zone"
            })

        # Check for temperature variance
        if temp_std > 5:
            anomalies.append({
                "type": "uneven_cooling",
                "severity": "medium",
                "std_dev": temp_std,
                "action": "Balance airflow distribution"
            })

        # Check coolant flow
        if coolant_flow < 4000:  # LPM
            anomalies.append({
                "type": "low_coolant_flow",
                "severity": "high",
                "flow_rate": coolant_flow,
                "action": "Check pump operation and valve positions"
            })

        result = {
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "avg_gpu_temp": round(avg_temp, 2),
            "max_gpu_temp": round(max_temp, 2),
            "temp_std_dev": round(temp_std, 2),
            "status": "anomaly_detected" if anomalies else "normal"
        }

        if anomalies:
            print(f"⚠️  Detected {len(anomalies)} thermal anomalies")
            for anomaly in anomalies:
                print(f"   - {anomaly['type']}: {anomaly['severity']} severity")
        else:
            print(f"✓ No thermal anomalies detected")

        return result

    async def optimize_workload_placement(
        self,
        job_requirements: Dict[str, Any],
        cluster_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize job placement using AI

        Args:
            job_requirements: Job resource requirements
            cluster_state: Current cluster state

        Returns:
            Optimal placement recommendation
        """
        print(f"\n🎯 LightRail AI: Optimizing workload placement...")
        await asyncio.sleep(0.4)

        # Simulate AI-driven placement optimization
        # In production, this would use reinforcement learning model

        num_gpus = job_requirements.get("num_gpus", 1)
        memory_gb = job_requirements.get("memory_gb", 40)
        priority = job_requirements.get("priority", "normal")

        # Score each node
        available_nodes = cluster_state.get("nodes", [])
        scored_nodes = []

        for node in available_nodes:
            score = 0

            # Prefer nodes with lower utilization
            score += (100 - node["gpu_util_pct"]) * 0.4

            # Prefer nodes with lower temperature
            score += (100 - node["avg_temp_c"]) * 0.3

            # Prefer nodes with sufficient memory
            if node["free_memory_gb"] >= memory_gb:
                score += 20

            # Locality bonus (same rack)
            if node.get("rack_id") == cluster_state.get("preferred_rack"):
                score += 10

            scored_nodes.append({
                "node_id": node["node_id"],
                "score": score,
                "gpu_util": node["gpu_util_pct"],
                "temp": node["avg_temp_c"],
                "free_memory": node["free_memory_gb"]
            })

        # Sort by score
        scored_nodes.sort(key=lambda x: x["score"], reverse=True)
        best_nodes = scored_nodes[:num_gpus]

        result = {
            "recommended_nodes": [n["node_id"] for n in best_nodes],
            "placement_score": sum(n["score"] for n in best_nodes) / len(best_nodes),
            "expected_performance": "optimal",
            "power_impact_kw": num_gpus * 0.4,  # 400W per GPU
            "thermal_impact": "minimal",
            "reasoning": [
                f"Node {n['node_id']}: score={n['score']:.1f}, util={n['gpu_util']:.1f}%, temp={n['temp']:.1f}°C"
                for n in best_nodes
            ]
        }

        print(f"✓ Recommended placement: {result['recommended_nodes']}")
        print(f"✓ Placement score: {result['placement_score']:.1f}/100")
        print(f"✓ Expected power impact: +{result['power_impact_kw']:.1f} kW")

        return result

    async def predict_maintenance_needs(
        self,
        component_metrics: Dict[str, Any],
        operating_hours: float
    ) -> Dict[str, Any]:
        """
        Predict maintenance needs using AI

        Args:
            component_metrics: Component health metrics
            operating_hours: Total operating hours

        Returns:
            Maintenance predictions
        """
        print(f"\n🔧 LightRail AI: Analyzing predictive maintenance...")
        await asyncio.sleep(0.3)

        predictions = []

        # Battery health prediction
        ess_soh = component_metrics.get("ess_soh_pct", 100)
        if ess_soh < 85:
            predictions.append({
                "component": "Energy Storage System",
                "issue": "Battery degradation",
                "severity": "medium",
                "estimated_time_to_failure": "6-12 months",
                "recommended_action": "Schedule battery replacement",
                "confidence": 0.87
            })

        # Cooling system prediction
        pump_vibration = component_metrics.get("pump_vibration_mm_s", 2.5)
        if pump_vibration > 4.5:
            predictions.append({
                "component": "Coolant Pump",
                "issue": "Bearing wear detected",
                "severity": "high",
                "estimated_time_to_failure": "2-4 weeks",
                "recommended_action": "Replace pump bearings immediately",
                "confidence": 0.92
            })

        # PDU health
        if operating_hours > 30000:
            predictions.append({
                "component": "PDU Contactors",
                "issue": "Normal wear from operating hours",
                "severity": "low",
                "estimated_time_to_failure": "12-18 months",
                "recommended_action": "Schedule preventive maintenance",
                "confidence": 0.78
            })

        result = {
            "predictions_count": len(predictions),
            "predictions": predictions,
            "overall_health_score": 95 - (len(predictions) * 5),
            "recommended_maintenance_window": self._find_maintenance_window()
        }

        if predictions:
            print(f"⚠️  {len(predictions)} maintenance needs predicted")
            for pred in predictions:
                print(f"   - {pred['component']}: {pred['severity']} severity")
        else:
            print(f"✓ All systems healthy, no immediate maintenance needed")

        return result

    def _find_maintenance_window(self) -> Dict[str, str]:
        """Find optimal maintenance window"""
        # Suggest low-utilization period
        now = datetime.now()
        if now.weekday() < 5:  # Weekday
            window_start = now.replace(hour=2, minute=0, second=0) + timedelta(days=1)
        else:  # Weekend
            window_start = now.replace(hour=2, minute=0, second=0)

        window_end = window_start + timedelta(hours=4)

        return {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "expected_impact": "minimal"
        }

    async def optimize_energy_cost(
        self,
        current_tariff: float,
        load_forecast: List[float],
        ess_soc: float
    ) -> Dict[str, Any]:
        """
        Optimize energy cost using AI

        Args:
            current_tariff: Current electricity rate ($/kWh)
            load_forecast: Forecasted load for next 24 hours
            ess_soc: Battery state of charge (%)

        Returns:
            Energy optimization strategy
        """
        print(f"\n💰 LightRail AI: Optimizing energy costs...")
        await asyncio.sleep(0.4)

        # Simulate AI-driven energy optimization
        # In production, this would use dynamic programming/RL model

        strategy = []

        # Analyze tariff periods
        peak_tariff = current_tariff * 2.5
        offpeak_tariff = current_tariff * 0.6

        # Generate charging/discharging schedule
        for hour in range(24):
            forecasted_load = load_forecast[hour] if hour < len(load_forecast) else 150

            if hour >= 22 or hour < 6:  # Off-peak hours
                action = "charge"
                tariff = offpeak_tariff
                reasoning = "Low tariff period - charge ESS"
            elif 9 <= hour <= 17:  # Peak hours
                action = "discharge"
                tariff = peak_tariff
                reasoning = "High tariff period - discharge ESS to reduce grid draw"
            else:
                action = "standby"
                tariff = current_tariff
                reasoning = "Normal tariff - standby mode"

            strategy.append({
                "hour": hour,
                "action": action,
                "forecasted_load_kw": forecasted_load,
                "tariff_usd_per_kwh": tariff,
                "reasoning": reasoning
            })

        # Calculate savings
        baseline_cost = sum(s["forecasted_load_kw"] * s["tariff_usd_per_kwh"] for s in strategy)
        optimized_cost = baseline_cost * 0.78  # 22% savings with ESS
        savings = baseline_cost - optimized_cost

        result = {
            "strategy": strategy,
            "baseline_cost_daily_usd": round(baseline_cost, 2),
            "optimized_cost_daily_usd": round(optimized_cost, 2),
            "daily_savings_usd": round(savings, 2),
            "monthly_savings_usd": round(savings * 30, 2),
            "annual_savings_usd": round(savings * 365, 2),
            "savings_percentage": 22
        }

        print(f"✓ Daily cost: ${optimized_cost:.2f} (vs ${baseline_cost:.2f} baseline)")
        print(f"✓ Daily savings: ${savings:.2f} (22%)")
        print(f"✓ Annual savings: ${result['annual_savings_usd']:,.2f}")

        return result


async def demo():
    """Run comprehensive AI demo"""
    print("="*70)
    print("LightRail AI DCIM Demo")
    print("Autonomous Datacenter Management")
    print("="*70)

    ai = LightRailAI()

    # Demo 1: Peak Power Prediction
    print("\n" + "="*70)
    print("DEMO 1: Peak Power Prediction")
    print("="*70)

    peak_prediction = await ai.predict_peak_power(
        current_load_kw=175,
        time_of_day=10,
        job_queue_depth=25,
        historical_pattern=[150, 160, 170, 180, 175]
    )
    print(f"\nResult: {json.dumps(peak_prediction, indent=2)}")

    # Demo 2: Thermal Anomaly Detection
    print("\n" + "="*70)
    print("DEMO 2: Thermal Anomaly Detection")
    print("="*70)

    gpu_temps = [65, 67, 64, 83, 66, 68, 65, 67]  # Note: GPU 3 is hot
    thermal_result = await ai.detect_thermal_anomaly(
        gpu_temps=gpu_temps,
        ambient_temp=25,
        coolant_flow=4800
    )
    print(f"\nResult: {json.dumps(thermal_result, indent=2)}")

    # Demo 3: Workload Optimization
    print("\n" + "="*70)
    print("DEMO 3: Workload Placement Optimization")
    print("="*70)

    job_req = {
        "num_gpus": 4,
        "memory_gb": 320,
        "priority": "high"
    }

    cluster = {
        "nodes": [
            {"node_id": "node-01", "gpu_util_pct": 45, "avg_temp_c": 62, "free_memory_gb": 400, "rack_id": "A"},
            {"node_id": "node-02", "gpu_util_pct": 78, "avg_temp_c": 70, "free_memory_gb": 200, "rack_id": "A"},
            {"node_id": "node-03", "gpu_util_pct": 32, "avg_temp_c": 58, "free_memory_gb": 450, "rack_id": "B"},
            {"node_id": "node-04", "gpu_util_pct": 65, "avg_temp_c": 68, "free_memory_gb": 350, "rack_id": "B"},
        ],
        "preferred_rack": "A"
    }

    placement = await ai.optimize_workload_placement(job_req, cluster)
    print(f"\nResult: {json.dumps(placement, indent=2)}")

    # Demo 4: Predictive Maintenance
    print("\n" + "="*70)
    print("DEMO 4: Predictive Maintenance")
    print("="*70)

    components = {
        "ess_soh_pct": 82,
        "pump_vibration_mm_s": 5.2,
        "fan_speed_rpm": 3500
    }

    maintenance = await ai.predict_maintenance_needs(components, operating_hours=32000)
    print(f"\nResult: {json.dumps(maintenance, indent=2)}")

    # Demo 5: Energy Cost Optimization
    print("\n" + "="*70)
    print("DEMO 5: Energy Cost Optimization")
    print("="*70)

    load_forecast = [140, 135, 130, 125, 130, 140, 160, 180, 190, 200, 205, 210,
                     205, 200, 195, 190, 185, 180, 170, 160, 150, 145, 140, 135]

    energy_opt = await ai.optimize_energy_cost(
        current_tariff=0.12,
        load_forecast=load_forecast,
        ess_soc=75
    )
    print(f"\n✓ Annual savings: ${energy_opt['annual_savings_usd']:,.2f}")

    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    print("\nLightRail AI successfully demonstrated:")
    print("  ✓ Peak power prediction with ML")
    print("  ✓ Thermal anomaly detection")
    print("  ✓ Intelligent workload placement")
    print("  ✓ Predictive maintenance")
    print("  ✓ Energy cost optimization")
    print("\nIntegrate these AI capabilities into your DCIM system!")


if __name__ == "__main__":
    asyncio.run(demo())
