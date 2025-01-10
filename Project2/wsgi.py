import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from flask_app import app as application
