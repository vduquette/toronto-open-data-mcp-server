#!/usr/bin/env python3
"""
Test runner for Toronto Open Data MCP Server

Usage:
    python run_tests.py                    # Run all unit tests
    python run_tests.py --unit             # Run only unit tests  
    python run_tests.py --integration      # Run integration tests (hits real API)
    python run_tests.py --all              # Run all tests including integration
    python run_tests.py --coverage         # Run with coverage report
"""

import subprocess
import sys
import argparse

def run_command(cmd):
    """Run a shell command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run tests for Toronto Open Data MCP Server")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests (default)")
    parser.add_argument("--integration", action="store_true", help="Run integration tests (hits real API)")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    if args.verbose:
        cmd.append("-v")
    
    if args.coverage:
        cmd.extend(["--cov=main", "--cov-report=html", "--cov-report=term"])
    
    # Determine which tests to run
    if args.integration:
        cmd.extend(["-m", "integration"])
        print("🔗 Running integration tests (will hit real Toronto Open Data API)")
    elif args.all:
        print("🚀 Running all tests (unit + integration)")
    else:
        # Default: run unit tests only (exclude integration)
        cmd.extend(["-m", "not integration"])
        print("🧪 Running unit tests only")
    
    # Add test file
    cmd.append("test_toronto_mcp.py")
    
    # Run the tests
    return_code = run_command(cmd)
    
    if return_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n❌ Tests failed with return code {return_code}")
    
    return return_code

if __name__ == "__main__":
    sys.exit(main()) 