# ******************************************************************************
#    Copyright (c) 2026 RoXimn <roximn148@gmail.com>
#    This source code is licensed under the MIT license found in the
#    LICENSE.txt file in the root directory of this source tree.
# ******************************************************************************
"""Runs the command line interface as ``python -m romanalfaz``."""
import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
