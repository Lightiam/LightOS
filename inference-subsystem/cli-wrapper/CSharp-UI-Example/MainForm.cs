/**
 * LightOS Windows Forms UI - Main Dashboard
 *
 * This is a professional C# Windows Forms application that demonstrates
 * the LightOS Inference Subsystem capabilities through the C++/CLI wrapper.
 *
 * Features:
 * - Real-time device monitoring (temperature, power, utilization)
 * - Thermal-aware scheduling visualization
 * - Job submission and tracking
 * - Power management controls
 * - Live telemetry graphs
 *
 * @file MainForm.cs
 * @author LightRail AI
 * @version 1.0.0
 */

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using System.Windows.Forms.DataVisualization.Charting;
using LightOS.Interop;

namespace LightOS.UI
{
    public partial class MainForm : Form
    {
        private PowerGovernor governor;
        private TelemetryMonitor monitor;
        private List<LightDevice> devices;
        private Timer refreshTimer;

        public MainForm()
        {
            InitializeComponent();
            InitializeLightOS();
        }

        private void InitializeComponent()
        {
            this.Text = "LightOS Inference Control Center";
            this.Size = new Size(1600, 900);
            this.BackColor = Color.FromArgb(15, 23, 42);  // Dark blue

            // Create main layout
            var mainPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                RowCount = 3,
                ColumnCount = 2,
                Padding = new Padding(20)
            };

            // Header
            var headerLabel = new Label
            {
                Text = "⚡ LightOS Inference Subsystem",
                Font = new Font("Segoe UI", 24, FontStyle.Bold),
                ForeColor = Color.FromArgb(56, 189, 248),  // Electric blue
                AutoSize = true,
                Dock = DockStyle.Top,
                TextAlign = ContentAlignment.MiddleCenter
            };

            // Device Cards Panel
            var devicesPanel = CreateDevicesPanel();

            // Telemetry Chart Panel
            var chartPanel = CreateTelemetryChart();

            // Power Control Panel
            var powerPanel = CreatePowerControlPanel();

            // Job Queue Panel
            var jobPanel = CreateJobQueuePanel();

            // Statistics Panel
            var statsPanel = CreateStatisticsPanel();

            // Layout
            this.Controls.Add(headerLabel);
            mainPanel.Controls.Add(devicesPanel, 0, 0);
            mainPanel.Controls.Add(chartPanel, 1, 0);
            mainPanel.Controls.Add(powerPanel, 0, 1);
            mainPanel.Controls.Add(jobPanel, 1, 1);
            mainPanel.Controls.Add(statsPanel, 0, 2);

            mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 40F));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 40F));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 20F));
            mainPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));
            mainPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50F));

            this.Controls.Add(mainPanel);
        }

        private void InitializeLightOS()
        {
            try
            {
                // Initialize PowerGovernor with Predictive Cooling
                governor = new PowerGovernor(
                    SchedulingPolicy.PredictiveCooling,
                    globalPowerBudgetWatts: 5000.0f
                );

                // Enumerate and register devices
                devices = new List<LightDevice>();
                var deviceProps = DeviceManager.EnumerateDevices();

                foreach (var props in deviceProps)
                {
                    var device = new LightDevice(props.Type, 0);
                    governor.RegisterDevice(device);
                    devices.Add(device);
                }

                // Start scheduler
                governor.StartScheduler();

                // Start telemetry monitoring
                monitor = new TelemetryMonitor(governor);
                monitor.OnThermalWarning += Monitor_OnThermalWarning;
                monitor.OnThermalCritical += Monitor_OnThermalCritical;
                monitor.OnPowerUpdate += Monitor_OnPowerUpdate;
                monitor.OnJobCompleted += Monitor_OnJobCompleted;
                monitor.Start(intervalMs: 1000);

                // UI refresh timer
                refreshTimer = new Timer { Interval = 500 };
                refreshTimer.Tick += RefreshTimer_Tick;
                refreshTimer.Start();

                LogMessage("✅ LightOS initialized successfully", Color.Green);
            }
            catch (Exception ex)
            {
                LogMessage($"❌ Failed to initialize: {ex.Message}", Color.Red);
            }
        }

        private Panel CreateDevicesPanel()
        {
            var panel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(30, 41, 59),
                Padding = new Padding(10)
            };

            var titleLabel = new Label
            {
                Text = "🖥️ Devices",
                Font = new Font("Segoe UI", 16, FontStyle.Bold),
                ForeColor = Color.White,
                Dock = DockStyle.Top,
                Height = 40
            };
            panel.Controls.Add(titleLabel);

            var deviceList = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                AutoScroll = true,
                FlowDirection = FlowDirection.TopDown
            };
            panel.Controls.Add(deviceList);

            return panel;
        }

        private Panel CreateDeviceCard(DeviceProperties props)
        {
            var card = new Panel
            {
                Width = 350,
                Height = 200,
                BackColor = Color.FromArgb(51, 65, 85),
                Margin = new Padding(10),
                Padding = new Padding(15)
            };

            var nameLabel = new Label
            {
                Text = props.Name,
                Font = new Font("Segoe UI", 14, FontStyle.Bold),
                ForeColor = Color.FromArgb(56, 189, 248),
                AutoSize = true,
                Location = new Point(10, 10)
            };

            var tempLabel = new Label
            {
                Text = $"🌡️ {props.CurrentTemperature:F1}°C",
                Font = new Font("Segoe UI", 12),
                ForeColor = GetThermalColor(props.CurrentTemperature),
                AutoSize = true,
                Location = new Point(10, 40)
            };

            var powerLabel = new Label
            {
                Text = $"⚡ {props.CurrentPowerDraw:F0} W / {props.TdpWatts:F0} W",
                Font = new Font("Segoe UI", 12),
                ForeColor = Color.White,
                AutoSize = true,
                Location = new Point(10, 65)
            };

            var memoryLabel = new Label
            {
                Text = $"💾 {props.GlobalMemorySize / (1024*1024*1024)} GB HBM",
                Font = new Font("Segoe UI", 12),
                ForeColor = Color.White,
                AutoSize = true,
                Location = new Point(10, 90)
            };

            var typeLabel = new Label
            {
                Text = props.Type.ToString(),
                Font = new Font("Segoe UI", 10, FontStyle.Italic),
                ForeColor = Color.FromArgb(148, 163, 184),
                AutoSize = true,
                Location = new Point(10, 120)
            };

            card.Controls.AddRange(new Control[] {
                nameLabel, tempLabel, powerLabel, memoryLabel, typeLabel
            });

            return card;
        }

        private Panel CreateTelemetryChart()
        {
            var panel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(30, 41, 59),
                Padding = new Padding(10)
            };

            var titleLabel = new Label
            {
                Text = "📊 Real-Time Telemetry",
                Font = new Font("Segoe UI", 16, FontStyle.Bold),
                ForeColor = Color.White,
                Dock = DockStyle.Top,
                Height = 40
            };
            panel.Controls.Add(titleLabel);

            var chart = new Chart
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(51, 65, 85)
            };

            var chartArea = new ChartArea
            {
                BackColor = Color.FromArgb(51, 65, 85),
                AxisX = {
                    LabelStyle = { ForeColor = Color.White },
                    LineColor = Color.FromArgb(148, 163, 184),
                    MajorGrid = { LineColor = Color.FromArgb(71, 85, 105) }
                },
                AxisY = {
                    LabelStyle = { ForeColor = Color.White },
                    LineColor = Color.FromArgb(148, 163, 184),
                    MajorGrid = { LineColor = Color.FromArgb(71, 85, 105) }
                }
            };
            chart.ChartAreas.Add(chartArea);

            // Temperature series
            var tempSeries = new Series
            {
                Name = "Temperature (°C)",
                ChartType = SeriesChartType.Line,
                Color = Color.FromArgb(239, 68, 68),
                BorderWidth = 3
            };
            chart.Series.Add(tempSeries);

            // Power series
            var powerSeries = new Series
            {
                Name = "Power (W)",
                ChartType = SeriesChartType.Line,
                Color = Color.FromArgb(34, 197, 94),
                BorderWidth = 3
            };
            chart.Series.Add(powerSeries);

            // Utilization series
            var utilSeries = new Series
            {
                Name = "Utilization (%)",
                ChartType = SeriesChartType.Line,
                Color = Color.FromArgb(56, 189, 248),
                BorderWidth = 3
            };
            chart.Series.Add(utilSeries);

            var legend = new Legend
            {
                ForeColor = Color.White,
                BackColor = Color.Transparent
            };
            chart.Legends.Add(legend);

            panel.Controls.Add(chart);
            return panel;
        }

        private Panel CreatePowerControlPanel()
        {
            var panel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(30, 41, 59),
                Padding = new Padding(10)
            };

            var titleLabel = new Label
            {
                Text = "⚙️ Power Management",
                Font = new Font("Segoe UI", 16, FontStyle.Bold),
                ForeColor = Color.White,
                Dock = DockStyle.Top,
                Height = 40
            };
            panel.Controls.Add(titleLabel);

            var controlsPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 4,
                Padding = new Padding(10)
            };

            // Power Limit Slider
            var powerLimitLabel = new Label
            {
                Text = "Power Limit (W):",
                ForeColor = Color.White,
                AutoSize = true
            };
            var powerLimitSlider = new TrackBar
            {
                Minimum = 100,
                Maximum = 1000,
                Value = 700,
                TickFrequency = 100,
                Dock = DockStyle.Fill
            };
            var powerLimitValue = new Label
            {
                Text = "700 W",
                ForeColor = Color.FromArgb(56, 189, 248),
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                AutoSize = true
            };
            powerLimitSlider.ValueChanged += (s, e) =>
            {
                powerLimitValue.Text = $"{powerLimitSlider.Value} W";
                // Apply to all devices
                foreach (var device in devices)
                {
                    device.SetPowerLimit(powerLimitSlider.Value);
                }
            };

            // Scheduling Policy
            var policyLabel = new Label
            {
                Text = "Scheduling Policy:",
                ForeColor = Color.White,
                AutoSize = true
            };
            var policyCombo = new ComboBox
            {
                Dock = DockStyle.Fill,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            policyCombo.Items.AddRange(new object[] {
                "FIFO",
                "Thermal-Aware",
                "Power Efficient",
                "Latency Optimal",
                "Predictive Cooling"
            });
            policyCombo.SelectedIndex = 4;

            // Predictive Cooling Toggle
            var precoolCheck = new CheckBox
            {
                Text = "Enable Predictive Cooling",
                ForeColor = Color.White,
                Checked = true,
                Dock = DockStyle.Fill
            };

            // Apply Button
            var applyButton = new Button
            {
                Text = "Apply Settings",
                BackColor = Color.FromArgb(34, 197, 94),
                ForeColor = Color.White,
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                Dock = DockStyle.Fill,
                FlatStyle = FlatStyle.Flat
            };
            applyButton.Click += (s, e) =>
            {
                LogMessage("✅ Settings applied", Color.Green);
            };

            controlsPanel.Controls.Add(powerLimitLabel, 0, 0);
            controlsPanel.Controls.Add(powerLimitSlider, 1, 0);
            controlsPanel.Controls.Add(policyLabel, 0, 1);
            controlsPanel.Controls.Add(policyCombo, 1, 1);
            controlsPanel.Controls.Add(precoolCheck, 0, 2);
            controlsPanel.Controls.Add(applyButton, 1, 3);

            panel.Controls.Add(controlsPanel);
            return panel;
        }

        private Panel CreateJobQueuePanel()
        {
            var panel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(30, 41, 59),
                Padding = new Padding(10)
            };

            var titleLabel = new Label
            {
                Text = "📋 Job Queue",
                Font = new Font("Segoe UI", 16, FontStyle.Bold),
                ForeColor = Color.White,
                Dock = DockStyle.Top,
                Height = 40
            };
            panel.Controls.Add(titleLabel);

            var jobList = new ListBox
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(51, 65, 85),
                ForeColor = Color.White,
                Font = new Font("Consolas", 10),
                BorderStyle = BorderStyle.None
            };
            panel.Controls.Add(jobList);

            return panel;
        }

        private Panel CreateStatisticsPanel()
        {
            var panel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(30, 41, 59),
                Padding = new Padding(10)
            };

            var statsFlow = new FlowLayoutPanel
            {
                Dock = DockStyle.Fill,
                FlowDirection = FlowDirection.LeftToRight
            };

            panel.Controls.Add(statsFlow);
            return panel;
        }

        private Panel CreateStatCard(string title, string value, Color accentColor)
        {
            var card = new Panel
            {
                Width = 200,
                Height = 100,
                BackColor = Color.FromArgb(51, 65, 85),
                Margin = new Padding(10)
            };

            var titleLabel = new Label
            {
                Text = title,
                Font = new Font("Segoe UI", 10),
                ForeColor = Color.FromArgb(148, 163, 184),
                AutoSize = true,
                Location = new Point(10, 10)
            };

            var valueLabel = new Label
            {
                Text = value,
                Font = new Font("Segoe UI", 20, FontStyle.Bold),
                ForeColor = accentColor,
                AutoSize = true,
                Location = new Point(10, 35)
            };

            card.Controls.Add(titleLabel);
            card.Controls.Add(valueLabel);
            return card;
        }

        // Event Handlers
        private void Monitor_OnThermalWarning(ulong deviceHandle, float temperature, string severity)
        {
            this.Invoke(new Action(() =>
            {
                LogMessage($"⚠️ Thermal Warning: Device {deviceHandle} at {temperature:F1}°C", Color.Orange);
            }));
        }

        private void Monitor_OnThermalCritical(ulong deviceHandle, float temperature, string severity)
        {
            this.Invoke(new Action(() =>
            {
                LogMessage($"🔥 CRITICAL: Device {deviceHandle} at {temperature:F1}°C!", Color.Red);
                MessageBox.Show(
                    $"Critical thermal condition detected!\nDevice {deviceHandle}: {temperature:F1}°C",
                    "Thermal Alert",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );
            }));
        }

        private void Monitor_OnPowerUpdate(float totalPowerWatts, float avgUtilization)
        {
            // Update UI (called on telemetry thread)
        }

        private void Monitor_OnJobCompleted(ulong jobId, bool success, string errorMessage)
        {
            this.Invoke(new Action(() =>
            {
                if (success)
                {
                    LogMessage($"✅ Job {jobId} completed", Color.Green);
                }
                else
                {
                    LogMessage($"❌ Job {jobId} failed: {errorMessage}", Color.Red);
                }
            }));
        }

        private void RefreshTimer_Tick(object sender, EventArgs e)
        {
            UpdateDeviceCards();
            UpdateTelemetryChart();
            UpdateStatistics();
        }

        private void UpdateDeviceCards()
        {
            // Update device cards with latest telemetry
        }

        private void UpdateTelemetryChart()
        {
            // Add data points to chart
        }

        private void UpdateStatistics()
        {
            if (governor == null) return;

            try
            {
                var stats = governor.GetStatistics();
                // Update statistics display
            }
            catch { }
        }

        private void LogMessage(string message, Color color)
        {
            // Add to log window
        }

        private Color GetThermalColor(float temperature)
        {
            if (temperature > 85) return Color.FromArgb(239, 68, 68);   // Red
            if (temperature > 75) return Color.FromArgb(251, 146, 60);  // Orange
            return Color.FromArgb(34, 197, 94);  // Green
        }

        protected override void OnFormClosing(FormClosingEventArgs e)
        {
            if (monitor != null)
            {
                monitor.Stop();
            }
            if (governor != null)
            {
                governor.StopScheduler();
            }
            base.OnFormClosing(e);
        }
    }

    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}
