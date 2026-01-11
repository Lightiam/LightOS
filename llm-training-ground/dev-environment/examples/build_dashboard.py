#!/usr/bin/env python3
"""
Example: Build an Analytics Dashboard
Demonstrates building a data-heavy application with charts and visualizations.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator import DevOrchestrator


async def main():
    """Build an analytics dashboard"""

    print("="*80)
    print("Building Analytics Dashboard with GLM-4")
    print("="*80)
    print()

    orchestrator = DevOrchestrator()

    user_prompt = """
    Build a business analytics dashboard with:
    - Real-time metrics display (revenue, users, conversions)
    - Interactive charts (line, bar, pie) using Chart.js or Recharts
    - Date range selector for filtering data
    - Data export to CSV
    - Responsive grid layout
    - Dark mode support
    - API endpoints for:
      * GET /api/metrics - Overall metrics
      * GET /api/analytics - Time-series data
      * GET /api/export - Export data as CSV
    """

    print("This will create a production-ready analytics dashboard")
    print("with React, FastAPI, and PostgreSQL")
    print()

    success = await orchestrator.build_app_from_prompt(
        user_prompt,
        project_name="analytics-dashboard"
    )

    if success:
        print("\n✅ Dashboard built successfully!")
        print("\nOpen http://localhost:5173 to view your dashboard")
        print("API documentation: http://localhost:8000/docs")
    else:
        print("\n❌ Build failed - check logs above")


if __name__ == "__main__":
    asyncio.run(main())
