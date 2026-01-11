#!/usr/bin/env python3
"""
LightOS Development Orchestrator
Manages the build-run-fix loop, integrating GLM-4 app builder with build server.
Provides a complete autonomous development environment.
"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import requests
import yaml


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestratorState(Enum):
    """Orchestrator state"""
    IDLE = "idle"
    PLANNING = "planning"
    BUILDING = "building"
    TESTING = "testing"
    FIXING = "fixing"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class BuildLog:
    """Build log entry"""
    timestamp: float
    state: OrchestratorState
    message: str
    details: Optional[Dict] = None


class DevOrchestrator:
    """
    Orchestrates the complete development cycle:
    1. GLM-4 generates app plan
    2. GLM-4 builds initial app
    3. Build server compiles and runs
    4. Tests are executed
    5. Errors are fed back to GLM-4
    6. GLM-4 fixes errors
    7. Repeat until working
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        build_server_url: str = "http://localhost:3000"
    ):
        # Load config
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "dev_config.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.build_server_url = build_server_url
        self.state = OrchestratorState.IDLE
        self.build_logs: List[BuildLog] = []

        # GLM-4 builder (lazy load)
        self._glm4_builder = None

        # Current project
        self.project_path: Optional[Path] = None
        self.project_name: Optional[str] = None

    @property
    def glm4_builder(self):
        """Lazy load GLM-4 builder"""
        if self._glm4_builder is None:
            from glm4_app_builder import GLM4AppBuilder
            logger.info("Loading GLM-4 app builder...")
            self._glm4_builder = GLM4AppBuilder(
                model_size=self.config.get('glm4_builder', {}).get('model_size', '9b')
            )
        return self._glm4_builder

    def _log(self, state: OrchestratorState, message: str, details: Optional[Dict] = None):
        """Log a build event"""
        log_entry = BuildLog(
            timestamp=time.time(),
            state=state,
            message=message,
            details=details
        )
        self.build_logs.append(log_entry)
        logger.info(f"[{state.value}] {message}")

    async def check_build_server(self) -> bool:
        """Check if build server is running"""
        try:
            response = requests.get(f"{self.build_server_url}/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Build server not available: {e}")
            return False

    async def start_build_server(self):
        """Start the build server in background"""
        logger.info("Starting build server...")

        # Start build server as subprocess
        build_server_path = Path(__file__).parent / "build_server.py"

        process = subprocess.Popen(
            ["/opt/lightos/venv/bin/python", str(build_server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for server to start
        max_wait = 30
        for i in range(max_wait):
            if await self.check_build_server():
                logger.info("Build server started successfully")
                return process

            await asyncio.sleep(1)

        raise RuntimeError("Build server failed to start")

    async def load_project(self, project_path: Path) -> bool:
        """Load project in build server"""
        try:
            response = requests.post(
                f"{self.build_server_url}/api/project/load",
                params={"path": str(project_path)},
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                self._log(
                    OrchestratorState.BUILDING,
                    f"Project loaded: {project_path}",
                    result
                )
                return True
            else:
                self._log(
                    OrchestratorState.FAILED,
                    f"Failed to load project: {response.text}"
                )
                return False

        except Exception as e:
            self._log(OrchestratorState.FAILED, f"Error loading project: {e}")
            return False

    async def build_project(self) -> Tuple[bool, List[str]]:
        """Build the project and return success status and errors"""
        try:
            response = requests.post(
                f"{self.build_server_url}/api/project/build",
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                errors = result.get('errors', [])

                if status == 'success':
                    self._log(
                        OrchestratorState.BUILDING,
                        "Build successful",
                        result
                    )
                    return True, []
                else:
                    self._log(
                        OrchestratorState.FAILED,
                        f"Build failed with {len(errors)} errors",
                        result
                    )
                    return False, errors

            else:
                self._log(
                    OrchestratorState.FAILED,
                    f"Build request failed: {response.text}"
                )
                return False, [response.text]

        except Exception as e:
            self._log(OrchestratorState.FAILED, f"Build error: {e}")
            return False, [str(e)]

    async def start_dev_server(self) -> bool:
        """Start the development server"""
        try:
            response = requests.post(
                f"{self.build_server_url}/api/server/start",
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'started':
                    self._log(
                        OrchestratorState.RUNNING,
                        "Dev server started"
                    )
                    return True

            self._log(OrchestratorState.FAILED, "Failed to start dev server")
            return False

        except Exception as e:
            self._log(OrchestratorState.FAILED, f"Error starting dev server: {e}")
            return False

    async def get_server_logs(self) -> str:
        """Get dev server logs"""
        try:
            response = requests.get(
                f"{self.build_server_url}/api/server/logs",
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return result.get('logs', '')

            return ""

        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return ""

    async def run_tests(self) -> Tuple[bool, List[str]]:
        """Run tests and return success status and errors"""
        if not self.project_path:
            return True, []

        errors = []

        try:
            # Check for test scripts
            package_json = self.project_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    pkg = json.load(f)

                if "test" in pkg.get("scripts", {}):
                    logger.info("Running tests...")

                    result = subprocess.run(
                        ["npm", "test"],
                        cwd=self.project_path,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )

                    if result.returncode != 0:
                        errors.append(f"Tests failed: {result.stderr}")
                        self._log(
                            OrchestratorState.TESTING,
                            f"Tests failed",
                            {"output": result.stderr}
                        )
                        return False, errors

                    self._log(OrchestratorState.TESTING, "Tests passed")
                    return True, []

            # No tests found
            self._log(OrchestratorState.TESTING, "No tests configured")
            return True, []

        except Exception as e:
            logger.error(f"Test error: {e}")
            return False, [str(e)]

    async def fix_errors(self, errors: List[str]) -> bool:
        """Use GLM-4 to fix errors"""
        if not errors:
            return True

        self._log(
            OrchestratorState.FIXING,
            f"Attempting to fix {len(errors)} errors"
        )

        try:
            # This is where you would use GLM-4 to analyze errors and generate fixes
            # For now, we log the errors
            logger.info("Errors to fix:")
            for error in errors:
                logger.info(f"  - {error}")

            # TODO: Implement actual error fixing with GLM-4
            # 1. Feed errors to GLM-4
            # 2. Get suggested fixes
            # 3. Apply fixes to files
            # 4. Return success

            return False  # Not implemented yet

        except Exception as e:
            self._log(OrchestratorState.FAILED, f"Error fixing: {e}")
            return False

    async def build_app_from_prompt(
        self,
        user_prompt: str,
        project_name: Optional[str] = None
    ) -> bool:
        """
        Main orchestration loop:
        1. Generate app with GLM-4
        2. Load in build server
        3. Build and run
        4. Test
        5. Fix errors if needed
        6. Iterate
        """
        # Setup project
        if project_name is None:
            project_name = user_prompt.lower().replace(' ', '-')[:50]

        self.project_name = project_name
        projects_dir = Path(__file__).parent / "projects"
        projects_dir.mkdir(exist_ok=True)
        self.project_path = projects_dir / project_name

        self._log(
            OrchestratorState.IDLE,
            f"Starting app build: {user_prompt}",
            {"project_name": project_name, "project_path": str(self.project_path)}
        )

        # Ensure build server is running
        if not await self.check_build_server():
            logger.info("Build server not running, starting...")
            await self.start_build_server()

        # Phase 1: Plan and Build with GLM-4
        self.state = OrchestratorState.PLANNING
        self._log(OrchestratorState.PLANNING, "Planning app with GLM-4...")

        try:
            success = self.glm4_builder.build_app(user_prompt, self.project_path)

            if not success:
                self._log(OrchestratorState.FAILED, "GLM-4 failed to generate app")
                return False

            self._log(OrchestratorState.BUILDING, "App generated by GLM-4")

        except Exception as e:
            self._log(OrchestratorState.FAILED, f"GLM-4 error: {e}")
            return False

        # Phase 2: Load project in build server
        if not await self.load_project(self.project_path):
            return False

        # Phase 3: Iterative build-run-fix loop
        max_iterations = self.config.get('glm4_builder', {}).get('max_iterations', 10)
        max_auto_fixes = self.config.get('glm4_builder', {}).get('max_auto_fixes', 3)

        for iteration in range(max_iterations):
            self._log(
                OrchestratorState.BUILDING,
                f"Build iteration {iteration + 1}/{max_iterations}"
            )

            # Build
            build_success, build_errors = await self.build_project()

            if not build_success:
                if iteration < max_auto_fixes:
                    # Try to fix
                    fixed = await self.fix_errors(build_errors)
                    if fixed:
                        continue
                    else:
                        self._log(
                            OrchestratorState.FAILED,
                            "Auto-fix not yet implemented - manual intervention required"
                        )
                        return False
                else:
                    self._log(
                        OrchestratorState.FAILED,
                        f"Build failed after {max_auto_fixes} fix attempts"
                    )
                    return False

            # Tests
            if self.config.get('glm4_builder', {}).get('testing', True):
                test_success, test_errors = await self.run_tests()

                if not test_success:
                    if iteration < max_auto_fixes:
                        fixed = await self.fix_errors(test_errors)
                        if fixed:
                            continue
                        else:
                            self._log(
                                OrchestratorState.FAILED,
                                "Test failures - manual intervention required"
                            )
                            return False

            # Start dev server
            if await self.start_dev_server():
                self.state = OrchestratorState.RUNNING
                self._log(
                    OrchestratorState.COMPLETE,
                    f"App successfully built and running!",
                    {
                        "project_path": str(self.project_path),
                        "preview_url": f"http://localhost:{self.config.get('preview_server', {}).get('port', 5173)}",
                        "iterations": iteration + 1
                    }
                )
                return True
            else:
                self._log(
                    OrchestratorState.FAILED,
                    "Failed to start dev server"
                )
                return False

        self._log(
            OrchestratorState.FAILED,
            f"Max iterations ({max_iterations}) reached"
        )
        return False

    def get_build_summary(self) -> Dict:
        """Get summary of the build process"""
        return {
            "project_name": self.project_name,
            "project_path": str(self.project_path) if self.project_path else None,
            "state": self.state.value,
            "total_logs": len(self.build_logs),
            "logs": [
                {
                    "timestamp": log.timestamp,
                    "state": log.state.value,
                    "message": log.message,
                    "details": log.details
                }
                for log in self.build_logs
            ]
        }


async def main():
    """Example usage"""
    orchestrator = DevOrchestrator()

    # Build an app from a prompt
    user_prompt = "Build a todo app with user authentication, task creation, and completion tracking"

    success = await orchestrator.build_app_from_prompt(user_prompt)

    if success:
        summary = orchestrator.get_build_summary()
        print("\n" + "="*80)
        print("BUILD SUCCESSFUL!")
        print("="*80)
        print(f"Project: {summary['project_name']}")
        print(f"Path: {summary['project_path']}")
        print(f"Preview: http://localhost:5173")
        print(f"API: http://localhost:8000")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("BUILD FAILED")
        print("="*80)
        summary = orchestrator.get_build_summary()
        print(f"State: {summary['state']}")
        print("\nLogs:")
        for log in summary['logs'][-10:]:  # Last 10 logs
            print(f"  [{log['state']}] {log['message']}")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
