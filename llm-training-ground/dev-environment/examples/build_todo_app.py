#!/usr/bin/env python3
"""
Example: Build a Todo App with GLM-4 App Builder
This demonstrates the basic usage of the autonomous app builder.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import DevOrchestrator


async def main():
    """Build a todo app from a single prompt"""

    print("="*80)
    print("LightOS Dev Environment - Todo App Example")
    print("="*80)
    print()

    # Initialize orchestrator
    orchestrator = DevOrchestrator()

    # Define the app we want to build
    user_prompt = """
    Build a todo application with the following features:
    - User authentication (signup, login, logout)
    - Create, read, update, delete todos
    - Mark todos as complete/incomplete
    - Filter todos by status (all, active, completed)
    - Dark mode toggle
    - Responsive design for mobile and desktop
    """

    print("Building app from prompt:")
    print(user_prompt)
    print()
    print("This will:")
    print("1. Generate app plan with GLM-4")
    print("2. Build React frontend with Tailwind CSS")
    print("3. Build FastAPI backend")
    print("4. Set up PostgreSQL models")
    print("5. Start development server with hot-reload")
    print("6. Open preview in browser")
    print()
    print("Estimated time: 3-5 minutes")
    print()

    # Build the app
    success = await orchestrator.build_app_from_prompt(
        user_prompt,
        project_name="todo-app"
    )

    # Display results
    print()
    print("="*80)

    if success:
        print("✅ APP BUILT SUCCESSFULLY!")
        print("="*80)
        summary = orchestrator.get_build_summary()

        print(f"\nProject: {summary['project_name']}")
        print(f"Location: {summary['project_path']}")
        print(f"\nPreview URLs:")
        print(f"  Frontend: http://localhost:5173")
        print(f"  Backend API: http://localhost:8000")
        print(f"  API Docs: http://localhost:8000/docs")

        print(f"\nBuild completed in {len(summary['logs'])} steps")

        print("\nNext steps:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Create a user account")
        print("3. Start adding todos!")
        print("4. Edit the code - changes will auto-reload")

        print("\nProject structure:")
        print(f"  {summary['project_path']}/")
        print("    ├── src/              (React frontend)")
        print("    ├── backend/          (FastAPI backend)")
        print("    ├── package.json")
        print("    └── README.md")

    else:
        print("❌ BUILD FAILED")
        print("="*80)
        summary = orchestrator.get_build_summary()

        print(f"\nFinal state: {summary['state']}")
        print("\nLast 5 log entries:")

        for log in summary['logs'][-5:]:
            print(f"  [{log['state']}] {log['message']}")

        print("\nTroubleshooting:")
        print("1. Check if build server is running")
        print("2. Verify all dependencies are installed")
        print("3. Check the full logs in orchestrator output")
        print("4. Try running: lightos-dev server")

    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
