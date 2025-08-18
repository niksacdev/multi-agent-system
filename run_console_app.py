#!/usr/bin/env python3
"""
Launcher script for the Multi-Agent Loan Processing Console Application.

This script provides an easy way to run the console application from the project root.
The console application is now completely decoupled from the loan_processing backend.
"""

import sys
import os
from pathlib import Path

# Set up paths
project_root = Path(__file__).parent
console_app_dir = project_root / "console_app"
console_src_dir = console_app_dir / "src"

# Add both project root and console app to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(console_app_dir))
sys.path.insert(0, str(console_src_dir))

# Change working directory to console_app for relative config loading
os.chdir(console_app_dir)

if __name__ == "__main__":
    print("🚀 Starting Multi-Agent Loan Processing Console Application...")
    print(f"📁 Working directory: {console_app_dir}")
    print()
    
    try:
        # Import and run the console application
        from src.main import main
        import asyncio
        
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"❌ Failed to import console application: {e}")
        print("Please ensure you're running from the project root directory.")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Failed to start console application: {e}")
        sys.exit(1)