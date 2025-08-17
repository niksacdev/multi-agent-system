#!/usr/bin/env python3
"""
Test runner script for MCP servers.

This script provides an easy way to run tests with different configurations
and generate comprehensive reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_tests(test_type: str = "all", verbose: bool = False, coverage: bool = True, html_report: bool = False) -> int:
    """
    Run tests with specified configuration.

    Args:
        test_type: Type of tests to run ("all", "unit", "integration", "server")
        verbose: Enable verbose output
        coverage: Enable coverage reporting
        html_report: Generate HTML coverage report

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    import subprocess

    cmd = [sys.executable, "-m", "pytest"]

    # Add test path based on type
    if test_type == "all":
        cmd.append("tests/")
    elif test_type == "unit":
        cmd.extend(["tests/", "-k", "not integration"])
    elif test_type == "integration":
        cmd.extend(["tests/tools_tests/test_integration.py"])
    elif test_type == "server":
        cmd.extend(
            [
                "tests/tools_tests/application_verification/test_server.py",
                "tests/tools_tests/document_processing/test_server.py",
                "tests/tools_tests/financial_calculations/test_server.py",
            ]
        )
    else:
        print(f"Unknown test type: {test_type}")
        return 1

    # Add common options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    if coverage:
        cmd.extend(["--cov=loan_processing", "--cov-report=term-missing"])
        if html_report:
            cmd.append("--cov-report=html")

    # Additional pytest options
    cmd.extend(["--tb=short", "--strict-markers", "--strict-config"])

    print(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, timeout=600)  # 10 minute timeout
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Tests timed out after 10 minutes")
        return 1
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1


def main() -> int:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run MCP server tests")

    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "server"],
        default="all",
        help="Type of tests to run (default: all)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")

    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")

    parser.add_argument("--quick", action="store_true", help="Run quick tests only (excludes slow tests)")

    args = parser.parse_args()

    # Check if pytest is available
    try:
        import pytest  # noqa: F401
    except ImportError:
        print("pytest is not installed. Please install it with: uv add --dev pytest pytest-cov")
        return 1

    # Coverage dependency check is optional - pytest-cov will fail gracefully if not installed

    return run_tests(test_type=args.type, verbose=args.verbose, coverage=not args.no_coverage, html_report=args.html)


if __name__ == "__main__":
    sys.exit(main())
