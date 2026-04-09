import sys
import os

# Add your project directory to the path
path = '/home/yourusername/themart-ecommerce'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['FLASK_APP'] = 'main.py'

# Import your app
from main import app as application

# For database initialization
with application.app_context():
    from main import db
    db.create_all()
