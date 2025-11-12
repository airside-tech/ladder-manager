"""
Test configuration to ensure local source modules in ../ are importable.

This adjusts sys.path so that `from ladder import ...` resolves to
`src/ladder.py` rather than any similarly named third-party package.
"""

import os
import sys

# Add the parent directory (src) to sys.path
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Debug: show which ladder module is imported
try:
    import ladder  # type: ignore
    import inspect
    print(f"[conftest] ladder module path: {getattr(ladder, '__file__', 'built-in')} ")
    try:
        print(f"[conftest] Section signature: {inspect.signature(ladder.Section)}")
    except Exception as _e_sig:
        print(f"[conftest] Failed to inspect Section signature: {_e_sig}")
except Exception as e:
    print(f"[conftest] Failed to import ladder for debug: {e}")
