package runtime

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/Lightiam/LightOS/lightos-container-runtime/pkg/config"
	"github.com/Lightiam/LightOS/lightos-container-runtime/pkg/devices"
	oci "github.com/opencontainers/runtime-spec/specs-go"
)

// Requirements specifies container GPU requirements
type Requirements struct {
	DeviceType string // nvidia, amd, intel, apple, any
	MinVRAM    string // e.g., "8GB"
	Strategy   string // performance, cost, balanced
}

// Manager handles runtime operations
type Manager struct {
	config   *config.Config
	detector *devices.Detector
}

// ContainerState represents OCI container state
type ContainerState struct {
	Version     string `json:"ociVersion"`
	ID          string `json:"id"`
	Status      string `json:"status"`
	Pid         int    `json:"pid"`
	Bundle      string `json:"bundle"`
	Annotations map[string]string `json:"annotations"`
}

// NewManager creates a new runtime manager
func NewManager(cfg *config.Config) *Manager {
	return &Manager{
		config:   cfg,
		detector: devices.NewDetector(),
	}
}

// SelectDevice selects the best device based on requirements
func (m *Manager) SelectDevice(req *Requirements) (*devices.Device, error) {
	// Parse min VRAM
	minVRAM, err := parseVRAM(req.MinVRAM)
	if err != nil {
		return nil, fmt.Errorf("invalid min-vram: %v", err)
	}

	// Get devices
	var candidates []*devices.Device

	if req.DeviceType == "any" {
		all, err := m.detector.DetectAll()
		if err != nil {
			return nil, fmt.Errorf("failed to detect devices: %v", err)
		}
		candidates = all
	} else {
		// Convert string to DeviceType
		deviceType := devices.DeviceType(req.DeviceType)
		devs, err := m.detector.GetByType(deviceType)
		if err != nil {
			return nil, fmt.Errorf("failed to get %s devices: %v", req.DeviceType, err)
		}
		candidates = devs
	}

	// Filter by VRAM
	var filtered []*devices.Device
	for _, dev := range candidates {
		if dev.Available && dev.VRAMBytes >= minVRAM {
			filtered = append(filtered, dev)
		}
	}

	if len(filtered) == 0 {
		return nil, fmt.Errorf("no devices available with >= %s VRAM", req.MinVRAM)
	}

	// Select best based on strategy
	return m.selectBestDevice(filtered, req.Strategy), nil
}

func (m *Manager) selectBestDevice(devices []*devices.Device, strategy string) *devices.Device {
	if len(devices) == 0 {
		return nil
	}

	best := devices[0]

	switch strategy {
	case "performance":
		for _, dev := range devices {
			if dev.PerformanceScore > best.PerformanceScore {
				best = dev
			}
		}

	case "cost":
		for _, dev := range devices {
			if dev.CostPerHour < best.CostPerHour {
				best = dev
			}
		}

	case "balanced":
		fallthrough
	default:
		for _, dev := range devices {
			// Calculate value score (performance / cost)
			score := float64(dev.PerformanceScore) / (dev.CostPerHour + 0.01)
			bestScore := float64(best.PerformanceScore) / (best.CostPerHour + 0.01)
			if score > bestScore {
				best = dev
			}
		}
	}

	return best
}

// ModifySpec modifies the OCI runtime spec to add device access
func (m *Manager) ModifySpec(specPath string, device *devices.Device) error {
	// Read existing spec
	data, err := os.ReadFile(specPath)
	if err != nil {
		return fmt.Errorf("failed to read spec: %v", err)
	}

	var spec oci.Spec
	if err := json.Unmarshal(data, &spec); err != nil {
		return fmt.Errorf("failed to unmarshal spec: %v", err)
	}

	// Add device files
	deviceFiles := device.GetDeviceFiles()
	for _, devFile := range deviceFiles {
		// Add to devices list
		spec.Linux.Devices = append(spec.Linux.Devices, oci.LinuxDevice{
			Path:  devFile,
			Type:  "c",
			Major: 0,
			Minor: 0,
		})

		// Add device cgroup
		spec.Linux.Resources.Devices = append(spec.Linux.Resources.Devices, oci.LinuxDeviceCgroup{
			Allow:  true,
			Type:   "c",
			Access: "rwm",
		})
	}

	// Add environment variables
	if spec.Process.Env == nil {
		spec.Process.Env = []string{}
	}

	switch device.Type {
	case devices.DeviceTypeNVIDIA:
		spec.Process.Env = append(spec.Process.Env,
			fmt.Sprintf("NVIDIA_VISIBLE_DEVICES=%d", device.Index),
			"NVIDIA_DRIVER_CAPABILITIES=compute,utility",
			fmt.Sprintf("CUDA_VISIBLE_DEVICES=%d", device.Index),
		)

	case devices.DeviceTypeAMD:
		spec.Process.Env = append(spec.Process.Env,
			fmt.Sprintf("ROCR_VISIBLE_DEVICES=%d", device.Index),
			fmt.Sprintf("GPU_DEVICE_ORDINAL=%d", device.Index),
			"HSA_OVERRIDE_GFX_VERSION=9.0.0",
		)

	case devices.DeviceTypeIntel:
		spec.Process.Env = append(spec.Process.Env,
			fmt.Sprintf("ONEAPI_DEVICE_SELECTOR=level_zero:%d", device.Index),
			fmt.Sprintf("ZE_AFFINITY_MASK=%d", device.Index),
		)

	case devices.DeviceTypeApple:
		spec.Process.Env = append(spec.Process.Env,
			fmt.Sprintf("METAL_DEVICE_WRAPPER_TYPE=1"),
		)
	}

	// Add library paths based on device type
	m.addLibraryPaths(&spec, device)

	// Add annotations
	if spec.Annotations == nil {
		spec.Annotations = make(map[string]string)
	}

	spec.Annotations["io.lightos.device.type"] = string(device.Type)
	spec.Annotations["io.lightos.device.index"] = fmt.Sprintf("%d", device.Index)
	spec.Annotations["io.lightos.device.name"] = device.Name
	spec.Annotations["io.lightos.device.vram"] = fmt.Sprintf("%d", device.VRAMBytes)

	// Write modified spec
	modifiedData, err := json.MarshalIndent(&spec, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal spec: %v", err)
	}

	if err := os.WriteFile(specPath, modifiedData, 0644); err != nil {
		return fmt.Errorf("failed to write spec: %v", err)
	}

	return nil
}

func (m *Manager) addLibraryPaths(spec *oci.Spec, device *devices.Device) {
	var libPaths []string

	switch device.Type {
	case devices.DeviceTypeNVIDIA:
		libPaths = []string{
			"/usr/local/cuda/lib64",
			"/usr/local/cuda/lib",
			"/usr/lib/x86_64-linux-gnu",
		}

	case devices.DeviceTypeAMD:
		libPaths = []string{
			"/opt/rocm/lib",
			"/opt/rocm/lib64",
		}

	case devices.DeviceTypeIntel:
		libPaths = []string{
			"/opt/intel/oneapi/compiler/latest/linux/lib",
			"/opt/intel/oneapi/compiler/latest/linux/lib/x64",
		}
	}

	// Add to LD_LIBRARY_PATH
	if len(libPaths) > 0 {
		ldLibPath := strings.Join(libPaths, ":")
		spec.Process.Env = append(spec.Process.Env,
			fmt.Sprintf("LD_LIBRARY_PATH=%s:${LD_LIBRARY_PATH}", ldLibPath),
		)
	}

	// Add library mounts
	if spec.Mounts == nil {
		spec.Mounts = []oci.Mount{}
	}

	for _, libPath := range libPaths {
		// Check if path exists
		if _, err := os.Stat(libPath); err == nil {
			spec.Mounts = append(spec.Mounts, oci.Mount{
				Source:      libPath,
				Destination: libPath,
				Type:        "bind",
				Options:     []string{"ro", "rbind"},
			})
		}
	}
}

// Prestart is called before the container starts
func (m *Manager) Prestart(state *ContainerState) error {
	// Extract device info from annotations
	deviceType, ok := state.Annotations["io.lightos.device.type"]
	if !ok {
		return nil // No device configured
	}

	// Validate device is still available
	indexStr := state.Annotations["io.lightos.device.index"]
	index, _ := strconv.Atoi(indexStr)

	all, err := m.detector.DetectAll()
	if err != nil {
		return fmt.Errorf("failed to detect devices: %v", err)
	}

	// Find the device
	var found bool
	for _, dev := range all {
		if string(dev.Type) == deviceType && dev.Index == index {
			if !dev.Available {
				return fmt.Errorf("device %s:%d is not available", deviceType, index)
			}
			found = true
			break
		}
	}

	if !found {
		return fmt.Errorf("device %s:%d not found", deviceType, index)
	}

	// Additional setup can go here
	return nil
}

// Helper functions

func parseVRAM(vramStr string) (uint64, error) {
	if vramStr == "" || vramStr == "0" || vramStr == "0GB" {
		return 0, nil
	}

	vramStr = strings.ToUpper(strings.TrimSpace(vramStr))

	// Extract number
	var numStr string
	var unit string

	for i, c := range vramStr {
		if c >= '0' && c <= '9' || c == '.' {
			numStr += string(c)
		} else {
			unit = vramStr[i:]
			break
		}
	}

	num, err := strconv.ParseFloat(numStr, 64)
	if err != nil {
		return 0, fmt.Errorf("invalid VRAM number: %s", numStr)
	}

	// Convert to bytes
	var bytes uint64
	switch unit {
	case "GB", "G":
		bytes = uint64(num * 1024 * 1024 * 1024)
	case "MB", "M":
		bytes = uint64(num * 1024 * 1024)
	case "KB", "K":
		bytes = uint64(num * 1024)
	case "B", "":
		bytes = uint64(num)
	default:
		return 0, fmt.Errorf("unknown unit: %s", unit)
	}

	return bytes, nil
}
