#!/usr/bin/env python3
"""
Test runner script for askgpt

This script provides convenient commands for running different types of tests:
- Basic test run
- Test run with coverage report
- Test run with verbose output
- Integration tests (when available)

Usage:
    python run_tests.py              # Basic test run
    python run_tests.py --coverage   # With coverage report
    python run_tests.py --verbose    # Verbose output
    python run_tests.py --help       # Show help
"""

import subprocess
import sys
import argparse
import os


def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"\n[RUNNING] {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"[SUCCESS] {description} completed successfully")
    else:
        print(f"[FAILED] {description} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Test runner for askgpt")
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage report')
    parser.add_argument('--verbose', action='store_true',
                       help='Run tests with verbose output')
    parser.add_argument('--integration', action='store_true',
                       help='Include integration tests (requires API key)')
    parser.add_argument('--html-coverage', action='store_true',
                       help='Generate HTML coverage report')
    
    args = parser.parse_args()
    
    # Check if pytest is available
    try:
        subprocess.run(['python3', '-m', 'pytest', '--version'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("[ERROR] pytest is not installed. Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Build the pytest command
    cmd = ['python3', '-m', 'pytest', 'tests/']
    
    if args.verbose:
        cmd.extend(['-v', '-s'])
    
    if args.coverage:
        cmd.extend(['--cov=askgpt'])
        if args.html_coverage:
            cmd.extend(['--cov-report=html'])
        cmd.extend(['--cov-report=term-missing'])
    
    if not args.integration:
        cmd.extend(['-m', 'not integration'])
    
    # Run the tests
    run_command(cmd, "Running askgpt tests")
    
    if args.coverage and args.html_coverage:
        print(f"\n[INFO] HTML coverage report generated in: {os.path.abspath('htmlcov/index.html')}")
        print("Open this file in your browser to view detailed coverage information.")


if __name__ == '__main__':
    main()