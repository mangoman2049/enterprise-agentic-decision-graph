"""
NOTCRM - Regression Test Runner
================================
Automated Regression Runner enforcing the 0-Regression Policy.
Usage:
    python run_tests.py
"""

import sys
import os
import unittest
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def check_server():
    """Checks if NOTCRM server is reachable."""
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/sample-datasets", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    print("=" * 70)
    print("  NOTCRM AUTOMATED REGRESSION HARNESS (0-REGRESSION POLICY)")
    print("=" * 70)
    
    if not check_server():
        print(f"[ERROR] NOTCRM server is not reachable at {BASE_URL}.")
        print("Please start the server first in another terminal via:")
        print("    python app.py")
        sys.exit(1)
        
    print(f"[OK] Connected to live NOTCRM server at {BASE_URL}")
    print("[RUN] Executing full regression test suite (tests/test_notcrm_suite.py)...\n")
    
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"  [SUCCESS] 0 REGRESSIONS DETECTED ({result.testsRun} tests passed)")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"  [FAIL] REGRESSION DETECTED: {len(result.failures)} failures, {len(result.errors)} errors")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
