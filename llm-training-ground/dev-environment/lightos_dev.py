#!/usr/bin/env python3
"""
LightOS Development Environment CLI
Main entry point for the autonomous app builder with preview.
"""

import argparse
import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from orchestrator import DevOrchestrator


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print LightOS Dev Environment banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗     ██╗ ██████╗ ██╗  ██╗████████╗ ██████╗ ███████╗    ║
║   ██║     ██║██╔════╝ ██║  ██║╚══██╔══╝██╔═══██╗██╔════╝    ║
║   ██║     ██║██║  ███╗███████║   ██║   ██║   ██║███████╗    ║
║   ██║     ██║██║   ██║██╔══██║   ██║   ██║   ██║╚════██║    ║
║   ███████╗██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝███████║    ║
║   ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝    ║
║                                                               ║
║          Development Environment with GLM-4 AI               ║
║        Turn ideas into apps with build + preview             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def cmd_build(args):
    """Build an app from a prompt"""
    print_banner()

    if args.prompt:
        # Build from command line prompt
        prompt = ' '.join(args.prompt)
    elif args.file:
        # Build from prompt file
        with open(args.file) as f:
            prompt = f.read().strip()
    else:
        # Interactive prompt
        print("\nDescribe the app you want to build:")
        print("(Type your description, press Enter twice when done)\n")

        lines = []
        empty_count = 0

        while empty_count < 1:
            line = input()
            if line:
                lines.append(line)
                empty_count = 0
            else:
                empty_count += 1

        prompt = '\n'.join(lines)

    if not prompt:
        print("Error: No prompt provided")
        return 1

    print(f"\n{'='*70}")
    print("Building app from prompt:")
    print(f"{'='*70}")
    print(prompt)
    print(f"{'='*70}\n")

    # Initialize orchestrator
    orchestrator = DevOrchestrator()

    # Build the app
    success = await orchestrator.build_app_from_prompt(
        prompt,
        project_name=args.name
    )

    # Show results
    summary = orchestrator.get_build_summary()

    print(f"\n{'='*70}")
    if success:
        print("✅ BUILD SUCCESSFUL!")
        print(f"{'='*70}")
        print(f"\nProject: {summary['project_name']}")
        print(f"Location: {summary['project_path']}")
        print(f"\n🌐 Preview URLs:")
        print(f"   Frontend: http://localhost:5173")
        print(f"   API:      http://localhost:8000")
        print(f"   Docs:     http://localhost:8000/docs")
        print(f"\n📝 Build Steps: {len(summary['logs'])}")
        print(f"\n💡 The app is now running with hot-reload!")
        print(f"   Edit files and see changes instantly.")
        return 0
    else:
        print("❌ BUILD FAILED")
        print(f"{'='*70}")
        print(f"State: {summary['state']}")
        print("\nRecent logs:")
        for log in summary['logs'][-5:]:
            print(f"  [{log['state']}] {log['message']}")
        return 1


def cmd_server(args):
    """Start the build server"""
    print_banner()
    print("\n🚀 Starting LightOS Build Server...")
    print(f"   Port: {args.port}")
    print(f"   Host: {args.host}\n")

    from build_server import BuildServer

    server = BuildServer()
    server.config['build_server']['host'] = args.host
    server.config['build_server']['port'] = args.port

    try:
        server.run()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
        return 0


def cmd_examples(args):
    """List or run examples"""
    examples_dir = Path(__file__).parent / "examples"

    if args.list:
        print_banner()
        print("\n📚 Available Examples:\n")

        examples = [
            ("todo_app", "Todo application with auth and CRUD", "build_todo_app.py"),
            ("dashboard", "Analytics dashboard with charts", "build_dashboard.py"),
        ]

        for name, description, file in examples:
            print(f"  {name:15} - {description}")
            print(f"                    Run: lightos-dev examples {name}\n")

        return 0

    # Run an example
    example_name = args.example
    example_file = examples_dir / f"build_{example_name}.py"

    if not example_file.exists():
        print(f"Error: Example '{example_name}' not found")
        print("Run 'lightos-dev examples --list' to see available examples")
        return 1

    print(f"\n🏃 Running example: {example_name}\n")

    result = subprocess.run([sys.executable, str(example_file)])
    return result.returncode


def cmd_templates(args):
    """Show available templates"""
    print_banner()
    print("\n📋 Project Templates:\n")

    templates = [
        {
            "name": "React + FastAPI",
            "stack": "React, Vite, Tailwind, FastAPI, PostgreSQL",
            "best_for": "Data-driven apps, dashboards, admin panels"
        },
        {
            "name": "Next.js + Supabase",
            "stack": "Next.js, Tailwind, Supabase",
            "best_for": "Content sites, blogs, e-commerce"
        },
        {
            "name": "Vue + Express",
            "stack": "Vue 3, Vite, Express, PostgreSQL",
            "best_for": "Progressive web apps, real-time apps"
        },
        {
            "name": "Python Full Stack",
            "stack": "Streamlit, FastAPI, PostgreSQL",
            "best_for": "Data science apps, ML dashboards"
        }
    ]

    for template in templates:
        print(f"  {template['name']}")
        print(f"    Stack: {template['stack']}")
        print(f"    Best for: {template['best_for']}\n")

    print("💡 Templates are auto-selected based on your prompt.")
    print("   Or configure in: dev-environment/config/dev_config.yaml\n")

    return 0


def cmd_config(args):
    """Show or edit configuration"""
    config_file = Path(__file__).parent / "config" / "dev_config.yaml"

    if args.edit:
        import os
        editor = os.environ.get('EDITOR', 'nano')
        subprocess.run([editor, str(config_file)])
    else:
        print_banner()
        print(f"\n⚙️  Configuration: {config_file}\n")

        with open(config_file) as f:
            print(f.read())

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="LightOS Development Environment - Build apps with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build an app from interactive prompt
  lightos-dev build

  # Build from command line
  lightos-dev build "Build a blog with user auth"

  # Build from file
  lightos-dev build --file my-app-idea.txt

  # Start build server
  lightos-dev server

  # Run an example
  lightos-dev examples todo_app

  # Show templates
  lightos-dev templates

For more info: https://github.com/Lightiam/LightOS
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build an app from a prompt')
    build_parser.add_argument('prompt', nargs='*', help='App description')
    build_parser.add_argument('--file', '-f', help='Read prompt from file')
    build_parser.add_argument('--name', '-n', help='Project name')

    # Server command
    server_parser = subparsers.add_parser('server', help='Start the build server')
    server_parser.add_argument('--host', default='0.0.0.0', help='Server host')
    server_parser.add_argument('--port', type=int, default=3000, help='Server port')

    # Examples command
    examples_parser = subparsers.add_parser('examples', help='Run example builds')
    examples_parser.add_argument('example', nargs='?', help='Example name')
    examples_parser.add_argument('--list', '-l', action='store_true', help='List examples')

    # Templates command
    templates_parser = subparsers.add_parser('templates', help='Show available templates')

    # Config command
    config_parser = subparsers.add_parser('config', help='Show or edit configuration')
    config_parser.add_argument('--edit', '-e', action='store_true', help='Edit config file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to command handler
    if args.command == 'build':
        return asyncio.run(cmd_build(args))
    elif args.command == 'server':
        return cmd_server(args)
    elif args.command == 'examples':
        return cmd_examples(args)
    elif args.command == 'templates':
        return cmd_templates(args)
    elif args.command == 'config':
        return cmd_config(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
