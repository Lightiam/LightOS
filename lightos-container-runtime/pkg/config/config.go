package config

import (
	"encoding/json"
	"os"
)

// Config represents runtime configuration
type Config struct {
	// Runtime settings
	Debug           bool   `json:"debug"`
	LogFile         string `json:"logFile"`
	RuntimePath     string `json:"runtimePath"`

	// Device settings
	DefaultStrategy string   `json:"defaultStrategy"` // performance, cost, balanced
	PreferredVendor string   `json:"preferredVendor"` // nvidia, amd, intel, apple, any
	BlacklistDevices []string `json:"blacklistDevices"`
	WhitelistDevices []string `json:"whitelistDevices"`

	// Scheduling settings
	EnableMultiGPU  bool `json:"enableMultiGPU"`
	MaxGPUPerContainer int `json:"maxGPUPerContainer"`

	// Driver injection
	InjectDrivers   bool     `json:"injectDrivers"`
	CUDAPath        string   `json:"cudaPath"`
	ROCmPath        string   `json:"rocmPath"`
	OneAPIPath      string   `json:"oneAPIPath"`

	// Monitoring
	EnableMetrics   bool   `json:"enableMetrics"`
	MetricsPort     int    `json:"metricsPort"`
	MetricsPath     string `json:"metricsPath"`

	// Cost tracking
	EnableCostTracking bool `json:"enableCostTracking"`
}

// Default returns default configuration
func Default() *Config {
	return &Config{
		Debug:              false,
		LogFile:            "/var/log/lightos-runtime.log",
		RuntimePath:        "/usr/bin/runc",
		DefaultStrategy:    "balanced",
		PreferredVendor:    "any",
		EnableMultiGPU:     false,
		MaxGPUPerContainer: 1,
		InjectDrivers:      true,
		CUDAPath:           "/usr/local/cuda",
		ROCmPath:           "/opt/rocm",
		OneAPIPath:         "/opt/intel/oneapi",
		EnableMetrics:      true,
		MetricsPort:        9100,
		MetricsPath:        "/metrics",
		EnableCostTracking: true,
	}
}

// Load loads configuration from file
func Load(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}

	// Set defaults for missing fields
	defaultCfg := Default()
	if cfg.RuntimePath == "" {
		cfg.RuntimePath = defaultCfg.RuntimePath
	}
	if cfg.DefaultStrategy == "" {
		cfg.DefaultStrategy = defaultCfg.DefaultStrategy
	}
	if cfg.CUDAPath == "" {
		cfg.CUDAPath = defaultCfg.CUDAPath
	}
	if cfg.ROCmPath == "" {
		cfg.ROCmPath = defaultCfg.ROCmPath
	}
	if cfg.OneAPIPath == "" {
		cfg.OneAPIPath = defaultCfg.OneAPIPath
	}

	return &cfg, nil
}

// Save saves configuration to file
func (c *Config) Save(path string) error {
	data, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(path, data, 0644)
}
