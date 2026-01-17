/**
 * LightOS Electron Main Process
 *
 * This file creates the Electron window and handles native integration
 * with the C++ LightOS backend via Node.js addons or REST API.
 *
 * @file main.js
 * @author LightRail AI
 * @version 1.0.0
 */

const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const url = require('url');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1600,
        height: 900,
        minWidth: 1200,
        minHeight: 700,
        backgroundColor: '#0f172a',
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            enableRemoteModule: true,
            preload: path.join(__dirname, 'preload.js')
        },
        frame: true,
        titleBarStyle: 'default',
        icon: path.join(__dirname, '../assets/icon.png')
    });

    // Load React app
    const startUrl = process.env.ELECTRON_START_URL || url.format({
        pathname: path.join(__dirname, '../build/index.html'),
        protocol: 'file:',
        slashes: true
    });

    mainWindow.loadURL(startUrl);

    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// IPC Handlers for native integration
ipcMain.handle('enumerate-devices', async () => {
    // Call native C++ function via Node.js addon
    // For now, return mock data
    return [
        {
            name: 'NVIDIA H100 PCIe',
            type: 'NvidiaGPU',
            temperature: 72.5,
            powerDraw: 650,
            tdpWatts: 700,
            memoryTotal: 80 * 1024 * 1024 * 1024,
            utilization: 0.89
        },
        {
            name: 'NVIDIA A100 80GB',
            type: 'NvidiaGPU',
            temperature: 68.2,
            powerDraw: 380,
            tdpWatts: 400,
            memoryTotal: 80 * 1024 * 1024 * 1024,
            utilization: 0.95
        }
    ];
});

ipcMain.handle('get-statistics', async () => {
    return {
        totalJobsCompleted: 1247,
        thermalThrottleEvents: 3,
        predictiveCoolingTriggers: 42,
        jobMigrations: 8,
        avgTemperatureC: 70.3,
        avgPowerWatts: 1030,
        avgUtilization: 0.92,
        avgQueueTimeMs: 145
    };
});

ipcMain.handle('set-power-limit', async (event, deviceId, watts) => {
    console.log(`Setting power limit for device ${deviceId}: ${watts}W`);
    return { success: true };
});

ipcMain.handle('submit-job', async (event, jobConfig) => {
    console.log('Submitting job:', jobConfig);
    return { jobId: Date.now(), status: 'queued' };
});

console.log('LightOS Electron main process started');
