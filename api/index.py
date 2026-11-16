"""
Vercel Serverless API Proxy for AuraLife OS
Author: Shubhi Mathur
"""

import sys
import os

# Guarantee root path is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import app, application, handler

__all__ = ["app", "application", "handler"]
