"""
Standalone Context Menu Test Runner
Run this script to test context menu behavior in FileOrbit
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main test runner function"""
    try:
        from tests.test_context_menu_comparison import run_context_menu_comparison_tests
        run_context_menu_comparison_tests()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory")
        sys.exit(1)
    except Exception as e:
        print(f"Test execution error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()