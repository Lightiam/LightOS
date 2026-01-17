/**
 * LightOS React Main Application
 *
 * Professional web-based monitoring interface for LightOS Inference Subsystem.
 * Features real-time telemetry, device monitoring, and job management.
 *
 * @file App.jsx
 * @author LightRail AI
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, AreaChart, Area, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './App.css';

const { ipcRenderer } = window.require ? window.require('electron') : { ipcRenderer: null };

function App() {
    const [devices, setDevices] = useState([]);
    const [statistics, setStatistics] = useState(null);
    const [telemetryData, setTelemetryData] = useState([]);
    const [selectedDevice, setSelectedDevice] = useState(null);
    const [jobs, setJobs] = useState([]);

    useEffect(() => {
        loadDevices();
        loadStatistics();

        // Polling interval
        const interval = setInterval(() => {
            loadDevices();
            loadStatistics();
            updateTelemetry();
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const loadDevices = async () => {
        if (ipcRenderer) {
            const devicesData = await ipcRenderer.invoke('enumerate-devices');
            setDevices(devicesData);
        } else {
            // Fallback for web browser (fetch from REST API)
            try {
                const response = await fetch('http://localhost:50051/api/devices');
                const data = await response.json();
                setDevices(data);
            } catch (error) {
                console.error('Failed to load devices:', error);
            }
        }
    };

    const loadStatistics = async () => {
        if (ipcRenderer) {
            const stats = await ipcRenderer.invoke('get-statistics');
            setStatistics(stats);
        } else {
            try {
                const response = await fetch('http://localhost:50051/api/statistics');
                const data = await response.json();
                setStatistics(data);
            } catch (error) {
                console.error('Failed to load statistics:', error);
            }
        }
    };

    const updateTelemetry = () => {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();

        const avgTemp = devices.reduce((sum, d) => sum + d.temperature, 0) / (devices.length || 1);
        const avgPower = devices.reduce((sum, d) => sum + d.powerDraw, 0) / (devices.length || 1);
        const avgUtil = devices.reduce((sum, d) => sum + d.utilization * 100, 0) / (devices.length || 1);

        setTelemetryData(prev => {
            const updated = [...prev, {
                time: timeStr,
                temperature: avgTemp,
                power: avgPower,
                utilization: avgUtil
            }];
            // Keep last 60 data points (1 minute at 1Hz)
            return updated.slice(-60);
        });
    };

    const setPowerLimit = async (deviceId, watts) => {
        if (ipcRenderer) {
            await ipcRenderer.invoke('set-power-limit', deviceId, watts);
        }
    };

    const submitJob = async () => {
        const jobConfig = {
            modelName: 'Llama-3.1-70B',
            batchSize: 32,
            sequenceLength: 2048,
            precision: 'FP8'
        };

        if (ipcRenderer) {
            const result = await ipcRenderer.invoke('submit-job', jobConfig);
            setJobs(prev => [...prev, { ...result, config: jobConfig, timestamp: new Date() }]);
        }
    };

    return (
        <div className="app">
            {/* Header */}
            <header className="header">
                <div className="header-content">
                    <h1 className="header-title">
                        <span className="icon">⚡</span>
                        LightOS Inference Control Center
                    </h1>
                    <div className="header-status">
                        <StatusBadge status="operational" />
                    </div>
                </div>
            </header>

            {/* Main Grid */}
            <div className="main-grid">
                {/* Left Column: Device Cards */}
                <div className="devices-section">
                    <SectionTitle icon="🖥️" title="Devices" />
                    <div className="device-cards">
                        {devices.map((device, idx) => (
                            <DeviceCard
                                key={idx}
                                device={device}
                                onClick={() => setSelectedDevice(device)}
                                onPowerChange={(watts) => setPowerLimit(idx, watts)}
                            />
                        ))}
                    </div>
                </div>

                {/* Center Column: Telemetry Charts */}
                <div className="charts-section">
                    <SectionTitle icon="📊" title="Real-Time Telemetry" />
                    <div className="charts-grid">
                        <TelemetryChart data={telemetryData} />
                        <PowerDistributionChart devices={devices} />
                    </div>
                </div>

                {/* Right Column: Job Queue & Controls */}
                <div className="controls-section">
                    <SectionTitle icon="⚙️" title="Job Management" />
                    <JobSubmissionPanel onSubmit={submitJob} />
                    <JobQueueList jobs={jobs} />
                </div>
            </div>

            {/* Bottom Row: Statistics */}
            <div className="statistics-section">
                <StatisticsPanel statistics={statistics} />
            </div>
        </div>
    );
}

// ============================================================================
// Components
// ============================================================================

function StatusBadge({ status }) {
    const styles = {
        operational: { bg: '#10b981', text: 'Operational' },
        warning: { bg: '#f59e0b', text: 'Warning' },
        critical: { bg: '#ef4444', text: 'Critical' }
    };

    const style = styles[status] || styles.operational;

    return (
        <div className="status-badge" style={{ backgroundColor: style.bg }}>
            <span className="status-dot"></span>
            {style.text}
        </div>
    );
}

function SectionTitle({ icon, title }) {
    return (
        <h2 className="section-title">
            <span className="section-icon">{icon}</span>
            {title}
        </h2>
    );
}

function DeviceCard({ device, onClick, onPowerChange }) {
    const getThermalColor = (temp) => {
        if (temp > 85) return '#ef4444';
        if (temp > 75) return '#f59e0b';
        return '#10b981';
    };

    const utilizationPercent = (device.utilization * 100).toFixed(1);

    return (
        <div className="device-card" onClick={onClick}>
            <div className="device-header">
                <h3 className="device-name">{device.name}</h3>
                <span className="device-type">{device.type}</span>
            </div>

            <div className="device-metrics">
                <div className="metric">
                    <span className="metric-icon">🌡️</span>
                    <span className="metric-label">Temperature</span>
                    <span className="metric-value" style={{ color: getThermalColor(device.temperature) }}>
                        {device.temperature.toFixed(1)}°C
                    </span>
                </div>

                <div className="metric">
                    <span className="metric-icon">⚡</span>
                    <span className="metric-label">Power</span>
                    <span className="metric-value">
                        {device.powerDraw.toFixed(0)} / {device.tdpWatts} W
                    </span>
                </div>

                <div className="metric">
                    <span className="metric-icon">📊</span>
                    <span className="metric-label">Utilization</span>
                    <span className="metric-value">{utilizationPercent}%</span>
                </div>

                <div className="metric">
                    <span className="metric-icon">💾</span>
                    <span className="metric-label">Memory</span>
                    <span className="metric-value">
                        {(device.memoryTotal / (1024**3)).toFixed(0)} GB
                    </span>
                </div>
            </div>

            <div className="device-progress-bar">
                <div
                    className="device-progress-fill"
                    style={{ width: `${utilizationPercent}%`, backgroundColor: '#3b82f6' }}
                ></div>
            </div>

            <div className="device-controls">
                <input
                    type="range"
                    min="100"
                    max={device.tdpWatts}
                    defaultValue={device.powerDraw}
                    onChange={(e) => onPowerChange(parseInt(e.target.value))}
                    onClick={(e) => e.stopPropagation()}
                    className="power-slider"
                />
                <span className="power-label">Power Limit</span>
            </div>
        </div>
    );
}

function TelemetryChart({ data }) {
    return (
        <div className="chart-container">
            <h3 className="chart-title">System Metrics</h3>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="temperature" stroke="#ef4444" strokeWidth={2} name="Temp (°C)" />
                    <Line type="monotone" dataKey="power" stroke="#10b981" strokeWidth={2} name="Power (W)" />
                    <Line type="monotone" dataKey="utilization" stroke="#3b82f6" strokeWidth={2} name="Util (%)" />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

function PowerDistributionChart({ devices }) {
    const data = devices.map((device, idx) => ({
        name: `GPU ${idx}`,
        power: device.powerDraw,
        limit: device.tdpWatts
    }));

    return (
        <div className="chart-container">
            <h3 className="chart-title">Power Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                    />
                    <Legend />
                    <Bar dataKey="power" fill="#10b981" name="Current (W)" />
                    <Bar dataKey="limit" fill="#64748b" name="Limit (W)" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}

function JobSubmissionPanel({ onSubmit }) {
    return (
        <div className="job-submission-panel">
            <button className="submit-job-button" onClick={onSubmit}>
                <span className="button-icon">🚀</span>
                Submit Inference Job
            </button>
            <div className="job-config">
                <span className="config-label">Model: Llama-3.1-70B</span>
                <span className="config-label">Batch: 32</span>
                <span className="config-label">Precision: FP8</span>
            </div>
        </div>
    );
}

function JobQueueList({ jobs }) {
    return (
        <div className="job-queue">
            <h3 className="queue-title">Active Jobs ({jobs.length})</h3>
            <div className="job-list">
                {jobs.slice(-10).reverse().map((job, idx) => (
                    <div key={idx} className="job-item">
                        <span className="job-id">#{job.jobId}</span>
                        <span className="job-status">{job.status}</span>
                        <span className="job-time">{job.timestamp.toLocaleTimeString()}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

function StatisticsPanel({ statistics }) {
    if (!statistics) return null;

    const stats = [
        { label: 'Jobs Completed', value: statistics.totalJobsCompleted.toLocaleString(), icon: '✅', color: '#10b981' },
        { label: 'Avg Temperature', value: `${statistics.avgTemperatureC.toFixed(1)}°C`, icon: '🌡️', color: '#f59e0b' },
        { label: 'Avg Power', value: `${statistics.avgPowerWatts.toFixed(0)} W`, icon: '⚡', color: '#3b82f6' },
        { label: 'Avg Utilization', value: `${(statistics.avgUtilization * 100).toFixed(1)}%`, icon: '📊', color: '#8b5cf6' },
        { label: 'Queue Time', value: `${statistics.avgQueueTimeMs} ms`, icon: '⏱️', color: '#06b6d4' },
        { label: 'Thermal Events', value: statistics.thermalThrottleEvents, icon: '🔥', color: '#ef4444' },
        { label: 'Predictive Cooling', value: statistics.predictiveCoolingTriggers, icon: '❄️', color: '#06b6d4' },
        { label: 'Job Migrations', value: statistics.jobMigrations, icon: '🔄', color: '#8b5cf6' }
    ];

    return (
        <div className="statistics-grid">
            {stats.map((stat, idx) => (
                <div key={idx} className="stat-card">
                    <div className="stat-icon" style={{ color: stat.color }}>{stat.icon}</div>
                    <div className="stat-content">
                        <div className="stat-label">{stat.label}</div>
                        <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
                    </div>
                </div>
            ))}
        </div>
    );
}

export default App;
