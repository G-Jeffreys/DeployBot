#!/usr/bin/env python3
"""
DeployBot Main Entry Point for Bundled Executable

This wrapper script helps avoid import conflicts when creating bundled executables.
"""

import sys
import os
from pathlib import Path

# Add the bundled modules to the path
if hasattr(sys, '_MEIPASS'):
    # Running as bundled executable - _MEIPASS is added by PyInstaller
    bundle_dir = Path(getattr(sys, '_MEIPASS'))
    sys.path.insert(0, str(bundle_dir / 'deploybot_backend'))
else:
    # Running from source
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

# Now import and run the main graph module
if __name__ == "__main__":
    # Import the main module after path setup
    import graph
    
    # Start the main function
    import asyncio
    asyncio.run(graph.main()) 