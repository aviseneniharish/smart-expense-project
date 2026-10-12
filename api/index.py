"""
Vercel Serverless Function entry point for Python runtime.
Exposes the Flask 'app' instance to Vercel's serverless handler.
"""
import sys
import os

# Ensure root directory is on the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel WSGI entry point
# 'app' is recognized automatically by @vercel/python
