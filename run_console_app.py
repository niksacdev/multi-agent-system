#!/usr/bin/env python3
"""Simple console app launcher."""

import os
import sys
from pathlib import Path

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

        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
