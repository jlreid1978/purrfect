import sys
import os

# Add your project directory to the sys.path
project_home = '/Users/jreid/Documents/JLR_dev_code/purrfect_calories'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable for your Flask app
os.environ['FLASK_APP'] = 'app'

# Import the Flask app
from purrfect import app as application

print(application)