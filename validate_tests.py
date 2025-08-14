#!/usr/bin/env python3
"""
Quick validation script for MCP server test setup.

This script validates that the test environment is properly configured
and can run a subset of tests to verify everything is working.
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check that required dependencies are available."""
    required_modules = [
        'pytest',
        'mcp_servers.application_verification',
        'mcp_servers.document_processing', 
        'mcp_servers.financial_calculations'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        return False
    
    print("✅ All required dependencies are available")
    return True


def validate_test_structure():
    """Validate that test files are in the correct structure."""
    expected_files = [
        "tests/__init__.py",
        "tests/conftest.py", 
        "tests/mcp_servers/__init__.py",
        "tests/mcp_servers/test_integration.py",
        "tests/mcp_servers/test_utils.py",
        "tests/mcp_servers/test_performance.py",
        "tests/mcp_servers/application_verification/__init__.py",
        "tests/mcp_servers/application_verification/test_server.py",
        "tests/mcp_servers/document_processing/__init__.py",
        "tests/mcp_servers/document_processing/test_server.py",
        "tests/mcp_servers/financial_calculations/__init__.py",
        "tests/mcp_servers/financial_calculations/test_server.py",
    ]
    
    missing_files = []
    project_root = Path(__file__).parent
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing test files: {', '.join(missing_files)}")
        return False
    
    print("✅ All test files are present")
    return True


def run_quick_tests():
    """Run a quick subset of tests to validate setup."""
    print("\n🧪 Running quick validation tests...")
    
    # Run a small subset of tests
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/mcp_servers/application_verification/test_server.py::TestApplicationVerificationServiceImpl::test_retrieve_credit_report",
        "tests/mcp_servers/financial_calculations/test_server.py::TestFinancialCalculationsServiceImpl::test_calculate_debt_to_income_ratio_excellent",
        "-v", "--tb=short"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Quick validation tests passed")
            return True
        else:
            print("❌ Quick validation tests failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main validation function."""
    print("🔍 Validating MCP Server Test Setup")
    print("=" * 40)
    
    all_good = True
    
    # Check dependencies
    if not check_dependencies():
        all_good = False
    
    # Check test structure
    if not validate_test_structure():
        all_good = False
    
    # Run quick tests if structure is ok
    if all_good:
        if not run_quick_tests():
            all_good = False
    
    print("\n" + "=" * 40)
    if all_good:
        print("🎉 Test setup validation PASSED!")
        print("\nYou can now run the full test suite:")
        print("  python run_tests.py")
        print("  python run_tests.py --type unit")
        print("  python run_tests.py --type integration")
        return 0
    else:
        print("💥 Test setup validation FAILED!")
        print("\nPlease fix the issues above before running tests.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
