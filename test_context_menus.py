#!/usr/bin/env python3
"""
Context Menu Test Runner
Runs all context menu tests and provides a summary of results
"""

import sys
import subprocess
from pathlib import Path

def run_context_menu_tests():
    """Run all context menu tests"""
    print("=" * 60)
    print("FileOrbit Context Menu Test Suite")
    print("=" * 60)
    
    # Test files to run
    test_files = [
        "tests/ui/test_context_menus.py",
        "tests/integration/test_context_menu_integration.py", 
        "tests/performance/test_context_menu_performance.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = "MISSING"
            continue
            
        print(f"\n🔧 Running {test_file}...")
        print("-" * 50)
        
        try:
            # Run pytest for the specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, 
                "-v", "--tb=short", "--no-header"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {test_file}: PASSED")
                results[test_file] = "PASSED"
            else:
                print(f"❌ {test_file}: FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                results[test_file] = "FAILED"
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file}: TIMEOUT")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {test_file}: ERROR - {e}")
            results[test_file] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for status in results.values() if status == "PASSED")
    failed = sum(1 for status in results.values() if status == "FAILED")
    errors = sum(1 for status in results.values() if status in ["ERROR", "TIMEOUT", "MISSING"])
    total = len(results)
    
    for test_file, status in results.items():
        status_icon = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "ERROR": "💥",
            "TIMEOUT": "⏰",
            "MISSING": "⚠️"
        }.get(status, "❓")
        
        print(f"{status_icon} {test_file}: {status}")
    
    print(f"\nResults: {passed} passed, {failed} failed, {errors} errors out of {total} total")
    
    return passed, failed, errors

def test_context_menu_functionality():
    """Quick functional test of context menu features"""
    print("\n🧪 Quick Functional Test")
    print("-" * 30)
    
    try:
        # Import and test basic functionality
        sys.path.append('.')
        from src.services.cross_platform_shell_integration import get_shell_integration
        from pathlib import Path
        import tempfile
        import shutil
        
        # Create test environment
        temp_dir = Path(tempfile.mkdtemp())
        test_file = temp_dir / "test.txt"
        test_dir = temp_dir / "subfolder"
        
        test_file.write_text("Test content")
        test_dir.mkdir()
        
        shell = get_shell_integration()
        
        # Test file context menu
        file_menu = shell.get_context_menu_items(str(test_file))
        file_actions = [item.get('text', '') for item in file_menu if not item.get('separator')]
        
        # Test directory context menu  
        dir_menu = shell.get_context_menu_items(str(test_dir))
        dir_actions = [item.get('text', '') for item in dir_menu if not item.get('separator')]
        
        # Test empty area context menu
        empty_menu = shell.get_empty_area_context_menu()
        empty_actions = [item.get('text', '') for item in empty_menu if not item.get('separator')]
        
        # Verify key functionality
        checks = {
            "File menu has items": len(file_menu) > 0,
            "Directory menu has items": len(dir_menu) > 0,
            "Empty area menu has items": len(empty_menu) > 0,
            "Directory has 'Open in new tab'": any('new tab' in action.lower() for action in dir_actions),
            "File menu has 'Copy'": any('copy' in action.lower() for action in file_actions),
            "File menu has 'Delete'": any('delete' in action.lower() for action in file_actions),
            "Empty menu has 'Refresh'": any('refresh' in action.lower() for action in empty_actions),
            "Empty menu has 'New'": any('new' in action.lower() for action in empty_actions),
        }
        
        # Report results
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
            if not result:
                all_passed = False
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        print(f"\n🎯 Functional test: {'PASSED' if all_passed else 'FAILED'}")
        return all_passed
        
    except Exception as e:
        print(f"💥 Functional test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting FileOrbit Context Menu Test Suite...\n")
    
    # Run functional test first
    functional_passed = test_context_menu_functionality()
    
    # Run full test suite if functional test passes
    if functional_passed:
        passed, failed, errors = run_context_menu_tests()
        
        # Exit with appropriate code
        if failed > 0 or errors > 0:
            sys.exit(1)
        else:
            print("\n🎉 All tests passed! Context menu functionality is working correctly.")
            sys.exit(0)
    else:
        print("\n💥 Functional test failed - skipping full test suite")
        sys.exit(1)