#!/usr/bin/env python3
"""
Run all test suites for QueueStorm Copilot
"""

import subprocess
import sys
import os

def run_test(file_name, description):
    """Run a single test file"""
    print("\n" + "="*70)
    print(f"🧪 {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, file_name],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("❌ Errors/Warnings:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Failed to run {file_name}: {e}")
        return False

def main():
    print("🚀 QueueStorm Copilot - Complete Test Suite")
    print("="*70)
    
    tests = [
        ("test_api.py", "Basic API Tests"),
        ("test_samples.py", "Official Sample Cases (10 cases)"),
        ("test_variations.py", "Variation Tests (8 cases)"),
        ("test_edge_cases.py", "Edge Cases (6 cases)"),
        ("test_classifier.py", "Classifier Unit Tests"),
    ]
    
    results = {}
    for test_file, description in tests:
        if os.path.exists(test_file):
            passed = run_test(test_file, description)
            results[test_file] = passed
        else:
            print(f"⚠️ {test_file} not found - skipping")
            results[test_file] = None
    
    # Summary
    print("\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    
    for test_file, passed in results.items():
        if passed is None:
            status = "⏭️ SKIPPED"
        elif passed:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {test_file}")
    
    print("\n💡 Tests completed!")

if __name__ == "__main__":
    main()
