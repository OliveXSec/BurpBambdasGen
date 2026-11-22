#!/usr/bin/env python3
"""Entry point for Bambda Generator CLI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.main import app

if __name__ == "__main__":
    app()
