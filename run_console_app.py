#!/usr/bin/env python3
"""Simple console app launcher."""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Set up paths
project_root = Path(__file__).parent
console_app_dir = project_root / "console_app"
console_src_dir = console_app_dir / "src"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(console_app_dir))
sys.path.insert(0, str(console_src_dir))
os.chdir(console_app_dir)

if __name__ == "__main__":
    try:
        import asyncio

        from src.main import main

        # Get scenario type from command line argument
        scenario_type = sys.argv[1] if len(sys.argv) > 1 else "random"

        # Validate scenario type
        valid_scenarios = ["random", "approval", "conditional", "manual_review", "denial"]
        if scenario_type not in valid_scenarios:
            print(f"❌ Invalid scenario type: {scenario_type}")
            print(f"   Valid options: {', '.join(valid_scenarios)}")
            sys.exit(1)

        exit_code = asyncio.run(main(scenario_type))
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
