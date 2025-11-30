"""Script to create the data analysis projects table"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        print("All tables created successfully!")