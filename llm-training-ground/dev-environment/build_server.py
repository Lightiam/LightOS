#!/usr/bin/env python3
"""
LightOS Build Server with Hot-Reload and Preview
Provides a full development environment with build, preview, and auto-reload capabilities.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BuildStatus(Enum):
    """Build status enumeration"""
    IDLE = "idle"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


@dataclass
class BuildResult:
    """Build result data class"""
    status: BuildStatus
    timestamp: float
    duration: float
    errors: List[str]
    warnings: List[str]
    output: str

    def to_dict(self):
        return {
            **asdict(self),
            'status': self.status.value
        }


class ProjectBuilder:
    """Handles building and running projects"""

    def __init__(self, project_path: Path, config: Dict):
        self.project_path = project_path
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.build_status = BuildStatus.IDLE
        self.last_build: Optional[BuildResult] = None

    async def detect_project_type(self) -> str:
        """Detect project type based on files"""
        if (self.project_path / "package.json").exists():
            return "node"
        elif (self.project_path / "requirements.txt").exists():
            return "python"
        elif (self.project_path / "go.mod").exists():
            return "go"
        else:
            return "unknown"

    async def install_dependencies(self) -> BuildResult:
        """Install project dependencies"""
        start_time = time.time()
        errors = []
        warnings = []
        output = ""

        try:
            project_type = await self.detect_project_type()

            if project_type == "node":
                # Check for package.json
                if not (self.project_path / "package.json").exists():
                    logger.warning("No package.json found, skipping dependency installation")
                    return BuildResult(
                        status=BuildStatus.SUCCESS,
                        timestamp=time.time(),
                        duration=0,
                        errors=[],
                        warnings=["No package.json found"],
                        output="Skipped dependency installation"
                    )

                # Install npm dependencies
                logger.info("Installing npm dependencies...")
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                output = result.stdout + result.stderr

                if result.returncode != 0:
                    errors.append(f"npm install failed: {result.stderr}")
                    return BuildResult(
                        status=BuildStatus.FAILED,
                        timestamp=time.time(),
                        duration=time.time() - start_time,
                        errors=errors,
                        warnings=warnings,
                        output=output
                    )

            elif project_type == "python":
                # Install Python dependencies
                logger.info("Installing Python dependencies...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                output = result.stdout + result.stderr

                if result.returncode != 0:
                    errors.append(f"pip install failed: {result.stderr}")
                    return BuildResult(
                        status=BuildStatus.FAILED,
                        timestamp=time.time(),
                        duration=time.time() - start_time,
                        errors=errors,
                        warnings=warnings,
                        output=output
                    )

            return BuildResult(
                status=BuildStatus.SUCCESS,
                timestamp=time.time(),
                duration=time.time() - start_time,
                errors=[],
                warnings=warnings,
                output=output
            )

        except Exception as e:
            logger.error(f"Error installing dependencies: {e}")
            return BuildResult(
                status=BuildStatus.FAILED,
                timestamp=time.time(),
                duration=time.time() - start_time,
                errors=[str(e)],
                warnings=warnings,
                output=output
            )

    async def build(self) -> BuildResult:
        """Build the project"""
        start_time = time.time()
        self.build_status = BuildStatus.BUILDING
        errors = []
        warnings = []
        output = ""

        try:
            project_type = await self.detect_project_type()

            if project_type == "node":
                # Check for build script in package.json
                package_json = self.project_path / "package.json"
                if package_json.exists():
                    with open(package_json) as f:
                        pkg = json.load(f)

                    if "build" in pkg.get("scripts", {}):
                        logger.info("Running npm build...")
                        result = subprocess.run(
                            ["npm", "run", "build"],
                            cwd=self.project_path,
                            capture_output=True,
                            text=True,
                            timeout=300
                        )
                        output = result.stdout + result.stderr

                        if result.returncode != 0:
                            errors.append(f"Build failed: {result.stderr}")
                            self.build_status = BuildStatus.FAILED
                        else:
                            self.build_status = BuildStatus.SUCCESS
                    else:
                        logger.info("No build script found, assuming development build")
                        self.build_status = BuildStatus.SUCCESS
                        warnings.append("No build script found in package.json")

            elif project_type == "python":
                # Python projects typically don't need a build step
                logger.info("Python project detected, no build needed")
                self.build_status = BuildStatus.SUCCESS
                warnings.append("Python projects don't require build step")

            duration = time.time() - start_time

            self.last_build = BuildResult(
                status=self.build_status,
                timestamp=time.time(),
                duration=duration,
                errors=errors,
                warnings=warnings,
                output=output
            )

            return self.last_build

        except Exception as e:
            logger.error(f"Build error: {e}")
            self.build_status = BuildStatus.FAILED

            self.last_build = BuildResult(
                status=BuildStatus.FAILED,
                timestamp=time.time(),
                duration=time.time() - start_time,
                errors=[str(e)],
                warnings=warnings,
                output=output
            )

            return self.last_build

    async def start_dev_server(self) -> bool:
        """Start the development server"""
        try:
            # Stop existing process
            await self.stop()

            project_type = await self.detect_project_type()

            if project_type == "node":
                # Check for dev script
                package_json = self.project_path / "package.json"
                if package_json.exists():
                    with open(package_json) as f:
                        pkg = json.load(f)

                    if "dev" in pkg.get("scripts", {}):
                        logger.info("Starting dev server: npm run dev")
                        self.process = subprocess.Popen(
                            ["npm", "run", "dev"],
                            cwd=self.project_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    elif "start" in pkg.get("scripts", {}):
                        logger.info("Starting dev server: npm start")
                        self.process = subprocess.Popen(
                            ["npm", "start"],
                            cwd=self.project_path,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )
                    else:
                        logger.error("No dev or start script found in package.json")
                        return False

            elif project_type == "python":
                # Look for main.py, app.py, or server.py
                main_files = ["main.py", "app.py", "server.py"]
                main_file = None

                for f in main_files:
                    if (self.project_path / f).exists():
                        main_file = f
                        break

                if main_file:
                    logger.info(f"Starting Python dev server: {main_file}")
                    self.process = subprocess.Popen(
                        [sys.executable, main_file],
                        cwd=self.project_path,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                else:
                    logger.error("No main Python file found")
                    return False

            self.build_status = BuildStatus.RUNNING
            return True

        except Exception as e:
            logger.error(f"Error starting dev server: {e}")
            return False

    async def stop(self):
        """Stop the development server"""
        if self.process:
            logger.info("Stopping dev server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            self.build_status = BuildStatus.IDLE

    def get_logs(self, lines: int = 100) -> str:
        """Get recent logs from the dev server"""
        if not self.process:
            return "No process running"

        # This is a simplified version - in production you'd use a proper log buffer
        return "Dev server logs would appear here"


class FileWatcher(FileSystemEventHandler):
    """Watches for file changes and triggers rebuilds"""

    def __init__(self, builder: ProjectBuilder, websocket_manager, config: Dict):
        self.builder = builder
        self.websocket_manager = websocket_manager
        self.config = config
        self.debounce_timer: Optional[asyncio.Task] = None
        self.pending_changes: Set[str] = set()

    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event"""
        if event.is_directory:
            return

        # Ignore files based on config
        ignore_paths = self.config.get('build_server', {}).get('ignore_paths', [])
        for ignore in ignore_paths:
            if ignore in event.src_path:
                return

        # Check file extension
        watch_extensions = self.config.get('build_server', {}).get('watch_extensions', [])
        if not any(event.src_path.endswith(ext) for ext in watch_extensions):
            return

        logger.info(f"File changed: {event.src_path}")
        self.pending_changes.add(event.src_path)

        # Debounce rebuilds
        if self.debounce_timer:
            self.debounce_timer.cancel()

        self.debounce_timer = asyncio.create_task(self._debounced_rebuild())

    async def _debounced_rebuild(self):
        """Rebuild after a short delay to batch changes"""
        await asyncio.sleep(0.5)  # 500ms debounce

        if self.pending_changes:
            logger.info(f"Rebuilding due to {len(self.pending_changes)} file changes")

            # Notify clients
            await self.websocket_manager.broadcast({
                'type': 'build_started',
                'files': list(self.pending_changes)
            })

            self.pending_changes.clear()

            # Rebuild
            result = await self.builder.build()

            # Notify clients
            await self.websocket_manager.broadcast({
                'type': 'build_completed',
                'result': result.to_dict()
            })

            # Restart dev server if configured
            if self.config.get('build_server', {}).get('auto_restart', False):
                if result.status == BuildStatus.SUCCESS:
                    await self.builder.start_dev_server()
                    await self.websocket_manager.broadcast({
                        'type': 'server_restarted'
                    })


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


class BuildServer:
    """Main build server application"""

    def __init__(self, config_path: Optional[Path] = None):
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "dev_config.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize FastAPI
        self.app = FastAPI(title="LightOS Build Server", version="1.0.0")

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # WebSocket manager
        self.ws_manager = WebSocketManager()

        # Project builder (will be set when project is loaded)
        self.builder: Optional[ProjectBuilder] = None
        self.observer: Optional[Observer] = None

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register API routes"""

        @self.app.get("/")
        async def root():
            return {"message": "LightOS Build Server", "status": "running"}

        @self.app.post("/api/project/load")
        async def load_project(path: str):
            """Load a project"""
            try:
                project_path = Path(path).resolve()
                if not project_path.exists():
                    raise HTTPException(status_code=404, detail="Project path not found")

                # Create builder
                self.builder = ProjectBuilder(project_path, self.config)

                # Install dependencies
                install_result = await self.builder.install_dependencies()

                # Initial build
                build_result = await self.builder.build()

                # Start file watcher
                if self.observer:
                    self.observer.stop()

                self.observer = Observer()
                event_handler = FileWatcher(self.builder, self.ws_manager, self.config)
                self.observer.schedule(event_handler, str(project_path), recursive=True)
                self.observer.start()

                return {
                    "status": "success",
                    "project_path": str(project_path),
                    "install_result": install_result.to_dict(),
                    "build_result": build_result.to_dict()
                }

            except Exception as e:
                logger.error(f"Error loading project: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/project/build")
        async def build_project():
            """Trigger a manual build"""
            if not self.builder:
                raise HTTPException(status_code=400, detail="No project loaded")

            result = await self.builder.build()
            return result.to_dict()

        @self.app.post("/api/server/start")
        async def start_server():
            """Start the development server"""
            if not self.builder:
                raise HTTPException(status_code=400, detail="No project loaded")

            success = await self.builder.start_dev_server()
            return {"status": "started" if success else "failed"}

        @self.app.post("/api/server/stop")
        async def stop_server():
            """Stop the development server"""
            if not self.builder:
                raise HTTPException(status_code=400, detail="No project loaded")

            await self.builder.stop()
            return {"status": "stopped"}

        @self.app.get("/api/server/logs")
        async def get_logs(lines: int = 100):
            """Get dev server logs"""
            if not self.builder:
                raise HTTPException(status_code=400, detail="No project loaded")

            logs = self.builder.get_logs(lines)
            return {"logs": logs}

        @self.app.get("/api/build/status")
        async def build_status():
            """Get current build status"""
            if not self.builder:
                return {"status": "no_project"}

            return {
                "status": self.builder.build_status.value,
                "last_build": self.builder.last_build.to_dict() if self.builder.last_build else None
            }

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.ws_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    # Echo back for now
                    await websocket.send_json({"type": "echo", "data": data})
            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)

    def run(self):
        """Run the build server"""
        config = self.config.get('build_server', {})
        host = config.get('host', '0.0.0.0')
        port = config.get('port', 3000)

        logger.info(f"Starting LightOS Build Server on {host}:{port}")

        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )


def main():
    """Main entry point"""
    server = BuildServer()
    server.run()


if __name__ == "__main__":
    main()
