"""Migration script to create data analysis projects table"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, DataAnalysisProject
from app import app

def upgrade():
    """Create data analysis projects table"""
    with app.app_context():
        db.create_all()
        print("Data analysis projects table created successfully!")


def downgrade():
    """Drop data analysis projects table"""
    with app.app_context():
        db.drop_all(DataAnalysisProject.__table__)
        print("Data analysis projects table dropped successfully!")


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    
    if action == 'downgrade':
        downgrade()
    else:
        upgrade()