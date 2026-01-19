package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"path"
	"time"

	"github.com/Lightiam/LightOS/lightos-container-runtime/pkg/devices"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	pluginapi "k8s.io/kubelet/pkg/apis/deviceplugin/v1beta1"
)

const (
	resourceNamespace = "lightos.io/"
	socketPath        = pluginapi.DevicePluginPath + "lightos-"
)

var log = logrus.New()

type LightOSDevicePlugin struct {
	deviceType devices.DeviceType
	devices    []*devices.Device
	socket     string
	server     *grpc.Server
	detector   *devices.Detector
}

func NewLightOSDevicePlugin(deviceType devices.DeviceType) *LightOSDevicePlugin {
	return &LightOSDevicePlugin{
		deviceType: deviceType,
		socket:     socketPath + string(deviceType) + ".sock",
		detector:   devices.NewDetector(),
	}
}

func (p *LightOSDevicePlugin) GetDevicePluginOptions(context.Context, *pluginapi.Empty) (*pluginapi.DevicePluginOptions, error) {
	return &pluginapi.DevicePluginOptions{
		PreStartRequired:                false,
		GetPreferredAllocationAvailable: true,
	}, nil
}

func (p *LightOSDevicePlugin) ListAndWatch(e *pluginapi.Empty, s pluginapi.DevicePlugin_ListAndWatchServer) error {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		// Detect devices
		devs, err := p.detector.GetByType(p.deviceType)
		if err != nil {
			log.Errorf("Failed to detect %s devices: %v", p.deviceType, err)
			time.Sleep(5 * time.Second)
			continue
		}

		p.devices = devs

		// Build device list
		var deviceList []*pluginapi.Device
		for _, dev := range devs {
			device := &pluginapi.Device{
				ID:     fmt.Sprintf("%s-%d", p.deviceType, dev.Index),
				Health: pluginapi.Healthy,
			}

			if !dev.Available {
				device.Health = pluginapi.Unhealthy
			}

			deviceList = append(deviceList, device)
		}

		// Send device list
		if err := s.Send(&pluginapi.ListAndWatchResponse{Devices: deviceList}); err != nil {
			log.Errorf("Failed to send devices: %v", err)
			return err
		}

		<-ticker.C
	}
}

func (p *LightOSDevicePlugin) Allocate(ctx context.Context, req *pluginapi.AllocateRequest) (*pluginapi.AllocateResponse, error) {
	responses := &pluginapi.AllocateResponse{}

	for _, containerReq := range req.ContainerRequests {
		containerResp := &pluginapi.ContainerAllocateResponse{}

		for _, deviceID := range containerReq.DevicesIDs {
			// Find device
			var dev *devices.Device
			for _, d := range p.devices {
				if fmt.Sprintf("%s-%d", p.deviceType, d.Index) == deviceID {
					dev = d
					break
				}
			}

			if dev == nil {
				return nil, fmt.Errorf("device %s not found", deviceID)
			}

			// Add device files
			deviceFiles := dev.GetDeviceFiles()
			for _, devFile := range deviceFiles {
				containerResp.Devices = append(containerResp.Devices, &pluginapi.DeviceSpec{
					ContainerPath: devFile,
					HostPath:      devFile,
					Permissions:   "rwm",
				})
			}

			// Add environment variables
			switch dev.Type {
			case devices.DeviceTypeNVIDIA:
				containerResp.Envs = map[string]string{
					"NVIDIA_VISIBLE_DEVICES":      fmt.Sprintf("%d", dev.Index),
					"NVIDIA_DRIVER_CAPABILITIES":  "compute,utility",
					"CUDA_VISIBLE_DEVICES":        fmt.Sprintf("%d", dev.Index),
				}

			case devices.DeviceTypeAMD:
				containerResp.Envs = map[string]string{
					"ROCR_VISIBLE_DEVICES":  fmt.Sprintf("%d", dev.Index),
					"GPU_DEVICE_ORDINAL":    fmt.Sprintf("%d", dev.Index),
					"HSA_OVERRIDE_GFX_VERSION": "9.0.0",
				}

			case devices.DeviceTypeIntel:
				containerResp.Envs = map[string]string{
					"ONEAPI_DEVICE_SELECTOR": fmt.Sprintf("level_zero:%d", dev.Index),
					"ZE_AFFINITY_MASK":       fmt.Sprintf("%d", dev.Index),
				}
			}

			// Add mounts for driver libraries
			mounts := p.getLibraryMounts(dev)
			containerResp.Mounts = append(containerResp.Mounts, mounts...)
		}

		responses.ContainerResponses = append(responses.ContainerResponses, containerResp)
	}

	return responses, nil
}

func (p *LightOSDevicePlugin) GetPreferredAllocation(ctx context.Context, req *pluginapi.PreferredAllocationRequest) (*pluginapi.PreferredAllocationResponse, error) {
	response := &pluginapi.PreferredAllocationResponse{}

	for _, containerReq := range req.ContainerRequests {
		// Simple strategy: prefer devices with lowest utilization
		available := containerReq.AvailableDeviceIDs
		if len(available) == 0 {
			continue
		}

		// For now, just return the first available device
		// In a real implementation, we'd check utilization and select the best
		deviceIDs := []string{available[0]}

		if int(containerReq.AllocationSize) > len(deviceIDs) {
			deviceIDs = available[:containerReq.AllocationSize]
		}

		response.ContainerResponses = append(response.ContainerResponses,
			&pluginapi.ContainerPreferredAllocationResponse{
				DeviceIDs: deviceIDs,
			})
	}

	return response, nil
}

func (p *LightOSDevicePlugin) PreStartContainer(context.Context, *pluginapi.PreStartContainerRequest) (*pluginapi.PreStartContainerResponse, error) {
	return &pluginapi.PreStartContainerResponse{}, nil
}

func (p *LightOSDevicePlugin) getLibraryMounts(dev *devices.Device) []*pluginapi.Mount {
	var mounts []*pluginapi.Mount

	switch dev.Type {
	case devices.DeviceTypeNVIDIA:
		paths := []string{
			"/usr/local/cuda/lib64",
			"/usr/lib/x86_64-linux-gnu",
		}
		for _, path := range paths {
			if _, err := os.Stat(path); err == nil {
				mounts = append(mounts, &pluginapi.Mount{
					ContainerPath: path,
					HostPath:      path,
					ReadOnly:      true,
				})
			}
		}

	case devices.DeviceTypeAMD:
		paths := []string{
			"/opt/rocm/lib",
			"/opt/rocm/lib64",
		}
		for _, path := range paths {
			if _, err := os.Stat(path); err == nil {
				mounts = append(mounts, &pluginapi.Mount{
					ContainerPath: path,
					HostPath:      path,
					ReadOnly:      true,
				})
			}
		}

	case devices.DeviceTypeIntel:
		paths := []string{
			"/opt/intel/oneapi/compiler/latest/linux/lib",
		}
		for _, path := range paths {
			if _, err := os.Stat(path); err == nil {
				mounts = append(mounts, &pluginapi.Mount{
					ContainerPath: path,
					HostPath:      path,
					ReadOnly:      true,
				})
			}
		}
	}

	return mounts
}

func (p *LightOSDevicePlugin) Start() error {
	// Remove old socket
	if err := os.Remove(p.socket); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to remove old socket: %v", err)
	}

	// Create listener
	listener, err := net.Listen("unix", p.socket)
	if err != nil {
		return fmt.Errorf("failed to listen on socket: %v", err)
	}

	// Create gRPC server
	p.server = grpc.NewServer()
	pluginapi.RegisterDevicePluginServer(p.server, p)

	go func() {
		if err := p.server.Serve(listener); err != nil {
			log.Errorf("Failed to serve: %v", err)
		}
	}()

	// Wait for server to start
	time.Sleep(1 * time.Second)

	// Register with kubelet
	return p.register()
}

func (p *LightOSDevicePlugin) Stop() error {
	if p.server != nil {
		p.server.Stop()
	}
	return os.Remove(p.socket)
}

func (p *LightOSDevicePlugin) register() error {
	conn, err := grpc.Dial(
		pluginapi.KubeletSocket,
		grpc.WithInsecure(),
		grpc.WithDialer(func(addr string, timeout time.Duration) (net.Conn, error) {
			return net.DialTimeout("unix", addr, timeout)
		}),
	)
	if err != nil {
		return fmt.Errorf("failed to dial kubelet: %v", err)
	}
	defer conn.Close()

	client := pluginapi.NewRegistrationClient(conn)

	request := &pluginapi.RegisterRequest{
		Version:      pluginapi.Version,
		Endpoint:     path.Base(p.socket),
		ResourceName: resourceNamespace + string(p.deviceType),
	}

	if _, err := client.Register(context.Background(), request); err != nil {
		return fmt.Errorf("failed to register: %v", err)
	}

	log.Infof("Registered device plugin for %s", p.deviceType)
	return nil
}

func main() {
	log.SetLevel(logrus.InfoLevel)
	log.Info("Starting LightOS Kubernetes Device Plugin")

	// Detect what device types are available
	detector := devices.NewDetector()
	allDevices, err := detector.DetectAll()
	if err != nil {
		log.Fatalf("Failed to detect devices: %v", err)
	}

	// Group by type
	deviceTypes := make(map[devices.DeviceType]bool)
	for _, dev := range allDevices {
		deviceTypes[dev.Type] = true
	}

	if len(deviceTypes) == 0 {
		log.Fatal("No devices detected")
	}

	// Start a plugin for each device type
	var plugins []*LightOSDevicePlugin
	for deviceType := range deviceTypes {
		plugin := NewLightOSDevicePlugin(deviceType)
		if err := plugin.Start(); err != nil {
			log.Fatalf("Failed to start %s plugin: %v", deviceType, err)
		}
		plugins = append(plugins, plugin)
		log.Infof("Started device plugin for %s", deviceType)
	}

	// Wait forever
	select {}
}
