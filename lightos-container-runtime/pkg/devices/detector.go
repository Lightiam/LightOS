package devices

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

// DeviceType represents the vendor/type of accelerator
type DeviceType string

const (
	DeviceTypeNVIDIA DeviceType = "nvidia"
	DeviceTypeAMD    DeviceType = "amd"
	DeviceTypeIntel  DeviceType = "intel"
	DeviceTypeApple  DeviceType = "apple"
	DeviceTypeUnknown DeviceType = "unknown"
)

// Device represents an accelerator device
type Device struct {
	Type              DeviceType
	Index             int
	Name              string
	VRAMBytes         uint64
	ComputeCapability string
	DriverVersion     string
	PCIBusID          string
	Available         bool
	Utilization       float64
	PowerDraw         float64
	Temperature       int

	// Cost metrics (estimated)
	CostPerHour       float64
	PerformanceScore  int
}

// Detector detects available accelerators
type Detector struct {
	cache []*Device
}

// NewDetector creates a new device detector
func NewDetector() *Detector {
	return &Detector{}
}

// DetectAll detects all available accelerators
func (d *Detector) DetectAll() ([]*Device, error) {
	if d.cache != nil {
		return d.cache, nil
	}

	var devices []*Device

	// Detect NVIDIA devices
	nvidiaDevs, err := d.detectNVIDIA()
	if err == nil {
		devices = append(devices, nvidiaDevs...)
	}

	// Detect AMD devices
	amdDevs, err := d.detectAMD()
	if err == nil {
		devices = append(devices, amdDevs...)
	}

	// Detect Intel devices
	intelDevs, err := d.detectIntel()
	if err == nil {
		devices = append(devices, intelDevs...)
	}

	// Detect Apple devices
	appleDevs, err := d.detectApple()
	if err == nil {
		devices = append(devices, appleDevs...)
	}

	d.cache = devices
	return devices, nil
}

// detectNVIDIA detects NVIDIA GPUs using nvidia-smi
func (d *Detector) detectNVIDIA() ([]*Device, error) {
	// Check if nvidia-smi exists
	if _, err := exec.LookPath("nvidia-smi"); err != nil {
		return nil, fmt.Errorf("nvidia-smi not found")
	}

	// Query GPU info
	cmd := exec.Command("nvidia-smi",
		"--query-gpu=index,name,memory.total,compute_cap,driver_version,pci.bus_id,utilization.gpu,power.draw,temperature.gpu",
		"--format=csv,noheader,nounits")

	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run nvidia-smi: %v", err)
	}

	var devices []*Device
	scanner := bufio.NewScanner(strings.NewReader(string(output)))

	for scanner.Scan() {
		line := scanner.Text()
		fields := strings.Split(line, ",")

		if len(fields) < 9 {
			continue
		}

		index, _ := strconv.Atoi(strings.TrimSpace(fields[0]))
		vramMB, _ := strconv.ParseUint(strings.TrimSpace(fields[2]), 10, 64)
		util, _ := strconv.ParseFloat(strings.TrimSpace(fields[6]), 64)
		power, _ := strconv.ParseFloat(strings.TrimSpace(fields[7]), 64)
		temp, _ := strconv.Atoi(strings.TrimSpace(fields[8]))

		device := &Device{
			Type:              DeviceTypeNVIDIA,
			Index:             index,
			Name:              strings.TrimSpace(fields[1]),
			VRAMBytes:         vramMB * 1024 * 1024,
			ComputeCapability: strings.TrimSpace(fields[3]),
			DriverVersion:     strings.TrimSpace(fields[4]),
			PCIBusID:          strings.TrimSpace(fields[5]),
			Available:         true,
			Utilization:       util,
			PowerDraw:         power,
			Temperature:       temp,
		}

		// Estimate cost and performance
		device.estimateMetrics()
		devices = append(devices, device)
	}

	return devices, nil
}

// detectAMD detects AMD GPUs using rocm-smi
func (d *Detector) detectAMD() ([]*Device, error) {
	// Check if rocm-smi exists
	if _, err := exec.LookPath("rocm-smi"); err != nil {
		return nil, fmt.Errorf("rocm-smi not found")
	}

	// Try to query using rocm-smi
	cmd := exec.Command("rocm-smi", "--showid", "--showmeminfo", "vram")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run rocm-smi: %v", err)
	}

	var devices []*Device

	// Parse rocm-smi output (format varies, this is a simplified parser)
	scanner := bufio.NewScanner(strings.NewReader(string(output)))
	deviceIndex := 0

	for scanner.Scan() {
		line := scanner.Text()

		// Look for GPU entries
		if strings.Contains(line, "GPU") && strings.Contains(line, "0x") {
			device := &Device{
				Type:      DeviceTypeAMD,
				Index:     deviceIndex,
				Name:      d.extractAMDName(line),
				Available: true,
			}

			// Try to get VRAM info
			device.VRAMBytes = d.getAMDVRAM(deviceIndex)
			device.DriverVersion = d.getAMDDriverVersion()
			device.estimateMetrics()

			devices = append(devices, device)
			deviceIndex++
		}
	}

	return devices, nil
}

// detectIntel detects Intel GPUs using sycl-ls or clinfo
func (d *Detector) detectIntel() ([]*Device, error) {
	// Check for Intel oneAPI tools
	if _, err := exec.LookPath("sycl-ls"); err != nil {
		// Try clinfo as fallback
		return d.detectIntelCLInfo()
	}

	cmd := exec.Command("sycl-ls")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run sycl-ls: %v", err)
	}

	var devices []*Device
	scanner := bufio.NewScanner(strings.NewReader(string(output)))
	deviceIndex := 0

	for scanner.Scan() {
		line := scanner.Text()

		// Look for Intel GPU entries
		if strings.Contains(strings.ToLower(line), "intel") &&
		   strings.Contains(strings.ToLower(line), "gpu") {
			device := &Device{
				Type:      DeviceTypeIntel,
				Index:     deviceIndex,
				Name:      strings.TrimSpace(line),
				Available: true,
			}

			device.estimateMetrics()
			devices = append(devices, device)
			deviceIndex++
		}
	}

	return devices, nil
}

// detectIntelCLInfo detects Intel GPUs using clinfo
func (d *Detector) detectIntelCLInfo() ([]*Device, error) {
	if _, err := exec.LookPath("clinfo"); err != nil {
		return nil, fmt.Errorf("clinfo not found")
	}

	cmd := exec.Command("clinfo")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run clinfo: %v", err)
	}

	var devices []*Device
	scanner := bufio.NewScanner(strings.NewReader(string(output)))
	deviceIndex := 0
	var currentDevice *Device

	for scanner.Scan() {
		line := scanner.Text()

		if strings.Contains(line, "Device Name") && strings.Contains(strings.ToLower(line), "intel") {
			if currentDevice != nil {
				devices = append(devices, currentDevice)
			}

			currentDevice = &Device{
				Type:      DeviceTypeIntel,
				Index:     deviceIndex,
				Name:      strings.TrimSpace(strings.Split(line, ":")[1]),
				Available: true,
			}
			deviceIndex++
		}

		if currentDevice != nil && strings.Contains(line, "Global memory size") {
			// Extract memory size
			re := regexp.MustCompile(`(\d+)`)
			matches := re.FindStringSubmatch(line)
			if len(matches) > 0 {
				vram, _ := strconv.ParseUint(matches[0], 10, 64)
				currentDevice.VRAMBytes = vram
			}
		}
	}

	if currentDevice != nil {
		devices = append(devices, currentDevice)
	}

	for _, dev := range devices {
		dev.estimateMetrics()
	}

	return devices, nil
}

// detectApple detects Apple Silicon GPUs
func (d *Detector) detectApple() ([]*Device, error) {
	// Check if running on macOS
	if _, err := os.Stat("/System/Library"); err != nil {
		return nil, fmt.Errorf("not running on macOS")
	}

	// Use system_profiler to get GPU info
	cmd := exec.Command("system_profiler", "SPDisplaysDataType")
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run system_profiler: %v", err)
	}

	var devices []*Device
	scanner := bufio.NewScanner(strings.NewReader(string(output)))
	deviceIndex := 0

	for scanner.Scan() {
		line := scanner.Text()

		// Look for Apple GPU entries
		if strings.Contains(line, "Chipset Model") &&
		   (strings.Contains(line, "Apple") || strings.Contains(line, "M1") ||
		    strings.Contains(line, "M2") || strings.Contains(line, "M3")) {
			device := &Device{
				Type:      DeviceTypeApple,
				Index:     deviceIndex,
				Name:      strings.TrimSpace(strings.Split(line, ":")[1]),
				Available: true,
			}

			// Apple Silicon unified memory - estimate based on chip
			device.VRAMBytes = d.estimateAppleVRAM(device.Name)
			device.estimateMetrics()

			devices = append(devices, device)
			deviceIndex++
		}
	}

	return devices, nil
}

// Helper functions

func (d *Detector) extractAMDName(line string) string {
	// Extract GPU name from rocm-smi output
	parts := strings.Fields(line)
	for i, part := range parts {
		if part == "GPU" && i+1 < len(parts) {
			return strings.Join(parts[i:], " ")
		}
	}
	return "AMD GPU"
}

func (d *Detector) getAMDVRAM(index int) uint64 {
	// Try to read from sysfs
	vramPath := fmt.Sprintf("/sys/class/drm/card%d/device/mem_info_vram_total", index)
	data, err := os.ReadFile(vramPath)
	if err == nil {
		vram, _ := strconv.ParseUint(strings.TrimSpace(string(data)), 10, 64)
		return vram
	}
	return 8 * 1024 * 1024 * 1024 // Default 8GB
}

func (d *Detector) getAMDDriverVersion() string {
	// Try to get ROCm version
	rocmPath := "/opt/rocm/.info/version"
	data, err := os.ReadFile(rocmPath)
	if err == nil {
		return strings.TrimSpace(string(data))
	}
	return "unknown"
}

func (d *Detector) estimateAppleVRAM(name string) uint64 {
	// Estimate based on chip model
	name = strings.ToLower(name)
	switch {
	case strings.Contains(name, "m3 max"):
		return 96 * 1024 * 1024 * 1024 // 96GB
	case strings.Contains(name, "m3 pro"):
		return 36 * 1024 * 1024 * 1024 // 36GB
	case strings.Contains(name, "m3"):
		return 24 * 1024 * 1024 * 1024 // 24GB
	case strings.Contains(name, "m2 ultra"):
		return 192 * 1024 * 1024 * 1024 // 192GB
	case strings.Contains(name, "m2 max"):
		return 96 * 1024 * 1024 * 1024 // 96GB
	case strings.Contains(name, "m2 pro"):
		return 32 * 1024 * 1024 * 1024 // 32GB
	case strings.Contains(name, "m2"):
		return 24 * 1024 * 1024 * 1024 // 24GB
	case strings.Contains(name, "m1 ultra"):
		return 128 * 1024 * 1024 * 1024 // 128GB
	case strings.Contains(name, "m1 max"):
		return 64 * 1024 * 1024 * 1024 // 64GB
	case strings.Contains(name, "m1 pro"):
		return 32 * 1024 * 1024 * 1024 // 32GB
	default:
		return 16 * 1024 * 1024 * 1024 // 16GB default
	}
}

// estimateMetrics estimates cost and performance for a device
func (d *Device) estimateMetrics() {
	// Performance scoring (0-100)
	vramGB := float64(d.VRAMBytes) / (1024 * 1024 * 1024)

	switch d.Type {
	case DeviceTypeNVIDIA:
		// NVIDIA scoring based on compute capability and VRAM
		ccParts := strings.Split(d.ComputeCapability, ".")
		if len(ccParts) >= 2 {
			major, _ := strconv.Atoi(ccParts[0])
			d.PerformanceScore = major * 10 + int(vramGB)

			// Cost estimation ($/hour, approximate)
			switch {
			case strings.Contains(d.Name, "A100"):
				d.CostPerHour = 3.06
			case strings.Contains(d.Name, "H100"):
				d.CostPerHour = 4.50
			case strings.Contains(d.Name, "V100"):
				d.CostPerHour = 2.48
			case strings.Contains(d.Name, "T4"):
				d.CostPerHour = 0.35
			case strings.Contains(d.Name, "RTX 4090"):
				d.CostPerHour = 1.20
			case strings.Contains(d.Name, "RTX 4080"):
				d.CostPerHour = 0.90
			default:
				d.CostPerHour = 0.50 // Generic estimate
			}
		}

	case DeviceTypeAMD:
		d.PerformanceScore = int(vramGB) * 8
		// AMD typically cheaper
		d.CostPerHour = 0.40

	case DeviceTypeIntel:
		d.PerformanceScore = int(vramGB) * 6
		d.CostPerHour = 0.30

	case DeviceTypeApple:
		d.PerformanceScore = int(vramGB) * 7
		d.CostPerHour = 0.00 // Local device, no cloud cost
	}
}

// GetByType returns devices of a specific type
func (d *Detector) GetByType(deviceType DeviceType) ([]*Device, error) {
	all, err := d.DetectAll()
	if err != nil {
		return nil, err
	}

	var filtered []*Device
	for _, dev := range all {
		if dev.Type == deviceType {
			filtered = append(filtered, dev)
		}
	}

	return filtered, nil
}

// GetBestDevice returns the best device based on strategy
func (d *Detector) GetBestDevice(strategy string, minVRAM uint64) (*Device, error) {
	all, err := d.DetectAll()
	if err != nil {
		return nil, err
	}

	// Filter by VRAM requirement
	var candidates []*Device
	for _, dev := range all {
		if dev.Available && dev.VRAMBytes >= minVRAM {
			candidates = append(candidates, dev)
		}
	}

	if len(candidates) == 0 {
		return nil, fmt.Errorf("no devices meet requirements")
	}

	// Select based on strategy
	var best *Device
	switch strategy {
	case "performance":
		// Highest performance score
		for _, dev := range candidates {
			if best == nil || dev.PerformanceScore > best.PerformanceScore {
				best = dev
			}
		}

	case "cost":
		// Lowest cost per hour
		for _, dev := range candidates {
			if best == nil || dev.CostPerHour < best.CostPerHour {
				best = dev
			}
		}

	case "balanced":
		fallthrough
	default:
		// Best performance/cost ratio
		for _, dev := range candidates {
			score := float64(dev.PerformanceScore) / (dev.CostPerHour + 0.01) // Avoid division by zero
			if best == nil {
				best = dev
			} else {
				bestScore := float64(best.PerformanceScore) / (best.CostPerHour + 0.01)
				if score > bestScore {
					best = dev
				}
			}
		}
	}

	return best, nil
}

// GetDeviceFiles returns the device files to mount for a device
func (d *Device) GetDeviceFiles() []string {
	var devices []string

	switch d.Type {
	case DeviceTypeNVIDIA:
		devices = append(devices, "/dev/nvidiactl", "/dev/nvidia-uvm", "/dev/nvidia-uvm-tools")
		devices = append(devices, fmt.Sprintf("/dev/nvidia%d", d.Index))

	case DeviceTypeAMD:
		devices = append(devices, "/dev/kfd", "/dev/dri")
		devices = append(devices, fmt.Sprintf("/dev/dri/card%d", d.Index))
		devices = append(devices, fmt.Sprintf("/dev/dri/renderD%d", 128+d.Index))

	case DeviceTypeIntel:
		devices = append(devices, "/dev/dri")
		devices = append(devices, fmt.Sprintf("/dev/dri/card%d", d.Index))
		devices = append(devices, fmt.Sprintf("/dev/dri/renderD%d", 128+d.Index))
	}

	// Filter to only existing devices
	var existing []string
	for _, dev := range devices {
		// Handle glob patterns
		matches, _ := filepath.Glob(dev)
		if len(matches) > 0 {
			existing = append(existing, matches...)
		} else if _, err := os.Stat(dev); err == nil {
			existing = append(existing, dev)
		}
	}

	return existing
}
