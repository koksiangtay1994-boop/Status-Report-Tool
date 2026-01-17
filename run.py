#!/usr/bin/env python3
"""Runner script for the status report generator."""

import sys
from pathlib import Path

# Add src/main/python to path for imports
src_path = Path(__file__).parent / "src" / "main" / "python"
sys.path.insert(0, str(src_path))

from core.main import main

if __name__ == "__main__":
    sys.exit(main())
