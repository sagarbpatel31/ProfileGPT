# WSGI configuration for PythonAnywhere deployment
import sys
import os

# Add the backend directory to Python path
project_home = '/home/yourusername/ProfileGPT/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the FastAPI application
from main import app

# For PythonAnywhere WSGI compatibility
application = app