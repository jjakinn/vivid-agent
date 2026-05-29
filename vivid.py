#!/usr/bin/env python3
# VIVID Agent — Main entry point
# Usage: vivid [command] [options]

import sys
import os
from pathlib import Path

# Ensure vivid module is importable
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from vivid.__main__ import main

if __name__ == "__main__":
    main()
