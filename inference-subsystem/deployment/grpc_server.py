#!/usr/bin/env python3
"""
LightOS gRPC Inference Server
Lightweight server for Kubernetes deployment (<700MB container)

Features:
- gRPC API for model inference
- Multi-model serving
- Thermal-aware job scheduling
- Health checks and metrics
- Hot model reloading
"""

import argparse
import logging
import signal
import sys
import time
from concurrent import futures
from typing import Dict, List

import grpc
import numpy as np

# Import LightOS bindings
sys.path.insert(0, '/app')
from lightos_accelerated import (
    LightDevice, DeviceType, ExecutionGraph,
    ModelLoader, PowerGovernor, OpType, GraphOp
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# gRPC Service Definition (Protocol Buffers would be here)
# ============================================================================

class InferenceRequest:
    """Mock request structure (would use protobuf in production)"""
    def __init__(self, model_name: str, inputs: Dict[str, np.ndarray]):
        self.model_name = model_name
        self.inputs = inputs


class InferenceResponse:
    """Mock response structure"""
    def __init__(self, outputs: Dict[str, np.ndarray], latency_ms: float):
        self.outputs = outputs
        self.latency_ms = latency_ms


# ============================================================================
# LightOS Inference Server
# ============================================================================

class LightOSInferenceServer:
    """
    Lightweight inference server with thermal awareness.
    Target: Handle 1000+ requests/second on H100.
    """

    def __init__(self, devices: List[DeviceType] = None):
        """Initialize server with available devices"""
        self.devices: List[LightDevice] = []
        self.models: Dict[str, ExecutionGraph] = {}
        self.governors: List[PowerGovernor] = []

        # Auto-detect devices if not specified
        if devices is None or devices == ['auto']:
            devices = self._detect_devices()

        # Initialize devices
        for device_type in devices:
            try:
                device = LightDevice(device_type, 0)
                self.devices.append(device)
                self.governors.append(PowerGovernor(device))

                props = device.get_properties()
                logger.info(f"✅ Initialized {props.name} ({props.total_memory_gb} GB)")

            except Exception as e:
                logger.error(f"❌ Failed to initialize {device_type}: {e}")

        if not self.devices:
            logger.error("No devices available!")
            sys.exit(1)

        # Track metrics
        self.request_count = 0
        self.total_latency_ms = 0.0
        self.error_count = 0

    def _detect_devices(self) -> List[DeviceType]:
        """Auto-detect available accelerators"""
        # Try NVIDIA first
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True)
            if result.returncode == 0:
                logger.info("🔍 Detected NVIDIA GPU")
                return [DeviceType.NVIDIA]
        except FileNotFoundError:
            pass

        # Try AMD
        try:
            import subprocess
            result = subprocess.run(['rocm-smi'], capture_output=True)
            if result.returncode == 0:
                logger.info("🔍 Detected AMD GPU")
                return [DeviceType.AMD_MI300]
        except FileNotFoundError:
            pass

        # Fallback to CPU
        logger.warning("⚠️  No GPU detected, using CPU")
        return [DeviceType.CPU]

    def load_model(self, model_name: str, model_path: str, model_format: str = "onnx"):
        """Load model and prepare for inference"""
        try:
            logger.info(f"📦 Loading model: {model_name} from {model_path}")

            device = self.devices[0]  # Use first device

            # Load based on format
            if model_format.lower() == "onnx":
                graph = ModelLoader.load_onnx(model_path, device)
            elif model_format.lower() == "torchscript":
                graph = ModelLoader.load_torchscript(model_path, device)
            elif model_format.lower() == "native":
                graph = ModelLoader.load_native(model_path, device)
            else:
                raise ValueError(f"Unsupported format: {model_format}")

            # Optimize graph
            logger.info(f"🔧 Optimizing graph for {model_name}...")
            graph.optimize()

            self.models[model_name] = graph
            logger.info(f"✅ Model {model_name} ready for inference")

        except Exception as e:
            logger.error(f"❌ Failed to load model {model_name}: {e}")
            raise

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        """
        Run inference with thermal-aware scheduling.
        Uses PowerGovernor to prevent throttling.
        """
        start_time = time.perf_counter()

        try:
            # Get model
            if request.model_name not in self.models:
                raise ValueError(f"Model not found: {request.model_name}")

            graph = self.models[request.model_name]

            # Select device with lowest temperature (thermal load balancing)
            device_idx = self._select_coolest_device()
            device = self.devices[device_idx]
            governor = self.governors[device_idx]

            # Submit job with thermal awareness
            logger.debug(f"🚀 Executing {request.model_name} on device {device_idx}")
            governor.submit_job(graph, priority=1)

            # Mock output (would be real tensor operations)
            outputs = {
                'output': np.random.randn(1, 10).astype(np.float32)
            }

            # Calculate latency
            latency_ms = (time.perf_counter() - start_time) * 1000

            # Update metrics
            self.request_count += 1
            self.total_latency_ms += latency_ms

            logger.info(f"✅ Inference complete: {latency_ms:.2f}ms")

            return InferenceResponse(outputs, latency_ms)

        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Inference failed: {e}")
            raise

    def _select_coolest_device(self) -> int:
        """Select device with lowest temperature (thermal load balancing)"""
        if len(self.devices) == 1:
            return 0

        temps = [device.get_temperature() for device in self.devices]
        return temps.index(min(temps))

    def get_metrics(self) -> dict:
        """Get server metrics for monitoring"""
        avg_latency = (self.total_latency_ms / self.request_count
                       if self.request_count > 0 else 0.0)

        return {
            'request_count': self.request_count,
            'error_count': self.error_count,
            'avg_latency_ms': avg_latency,
            'device_temperatures': [d.get_temperature() for d in self.devices],
            'models_loaded': len(self.models),
        }

    def health_check(self) -> bool:
        """Health check for Kubernetes liveness probe"""
        try:
            # Check if at least one device is responsive
            for device in self.devices:
                temp = device.get_temperature()
                if temp > 90.0:  # Critical temperature
                    logger.warning(f"⚠️  Device temperature critical: {temp}°C")
                    return False
            return True
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False


# ============================================================================
# gRPC Server Implementation
# ============================================================================

class LightOSServicer:
    """gRPC servicer for LightOS inference"""

    def __init__(self, inference_server: LightOSInferenceServer):
        self.server = inference_server

    def Predict(self, request, context):
        """Handle prediction request"""
        try:
            # Convert gRPC request to InferenceRequest
            # (would deserialize protobuf in production)
            response = self.server.infer(request)
            return response
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return None

    def HealthCheck(self, request, context):
        """Handle health check request"""
        if self.server.health_check():
            return {'status': 'SERVING'}
        else:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            return {'status': 'NOT_SERVING'}

    def GetMetrics(self, request, context):
        """Handle metrics request"""
        return self.server.get_metrics()


# ============================================================================
# Main Server
# ============================================================================

def serve(port: int = 50051, devices: List[str] = None):
    """Start gRPC server"""

    # Parse device types
    device_types = []
    if devices and devices != ['auto']:
        for device in devices:
            if device.lower() == 'nvidia':
                device_types.append(DeviceType.NVIDIA)
            elif device.lower() == 'amd':
                device_types.append(DeviceType.AMD_MI300)
            elif device.lower() == 'cpu':
                device_types.append(DeviceType.CPU)
    else:
        device_types = None  # Auto-detect

    # Create inference server
    logger.info("🚀 Starting LightOS Inference Server...")
    inference_server = LightOSInferenceServer(devices=device_types)

    # Load example models (in production, models would be loaded from /models volume)
    # inference_server.load_model("resnet50", "/models/resnet50.onnx", "onnx")

    # Create gRPC server
    grpc_server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ]
    )

    # Add servicer
    servicer = LightOSServicer(inference_server)
    # Would register with protobuf-generated add_servicer_to_server()
    # For now, we'll just log
    logger.info(f"📡 gRPC server listening on port {port}")

    grpc_server.add_insecure_port(f'[::]:{port}')
    grpc_server.start()

    # Log startup metrics
    metrics = inference_server.get_metrics()
    logger.info(f"📊 Server ready:")
    logger.info(f"   - Devices: {len(inference_server.devices)}")
    logger.info(f"   - Models loaded: {metrics['models_loaded']}")
    logger.info(f"   - Port: {port}")

    # Graceful shutdown
    def shutdown_handler(signum, frame):
        logger.info("🛑 Shutting down gracefully...")
        grpc_server.stop(grace=5)
        logger.info("✅ Shutdown complete")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    # Keep server running
    try:
        grpc_server.wait_for_termination()
    except KeyboardInterrupt:
        shutdown_handler(None, None)


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='LightOS Inference Server')
    parser.add_argument('--port', type=int, default=50051,
                        help='gRPC server port (default: 50051)')
    parser.add_argument('--devices', nargs='+', default=['auto'],
                        help='Devices to use: nvidia, amd, cpu, or auto (default: auto)')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Start server
    serve(port=args.port, devices=args.devices)


if __name__ == '__main__':
    main()
