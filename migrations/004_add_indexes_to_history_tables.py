"""Migration script to add indexes to history tables"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, PropertyHistory, EventHistory
from app import app

def upgrade():
    """Add indexes to history tables"""
    with app.app_context():
        # For PropertyHistory table
        with db.engine.connect() as conn:
            # Check if indexes exist (SQLite specific)
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='property_histories'")
            indexes = [row[0] for row in result.fetchall()]
            
            # Add indexes if they don't exist
            if 'ix_property_histories_device_id' not in indexes:
                conn.execute("CREATE INDEX ix_property_histories_device_id ON property_histories (device_id)")
                
            if 'ix_property_histories_property_id' not in indexes:
                conn.execute("CREATE INDEX ix_property_histories_property_id ON property_histories (property_id)")
                
            if 'ix_property_histories_timestamp' not in indexes:
                conn.execute("CREATE INDEX ix_property_histories_timestamp ON property_histories (timestamp)")
        
        # For EventHistory table
        with db.engine.connect() as conn:
            # Check if indexes exist (SQLite specific)
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='event_histories'")
            indexes = [row[0] for row in result.fetchall()]
            
            # Add indexes if they don't exist
            if 'ix_event_histories_device_id' not in indexes:
                conn.execute("CREATE INDEX ix_event_histories_device_id ON event_histories (device_id)")
                
            if 'ix_event_histories_event_id' not in indexes:
                conn.execute("CREATE INDEX ix_event_histories_event_id ON event_histories (event_id)")
                
            if 'ix_event_histories_timestamp' not in indexes:
                conn.execute("CREATE INDEX ix_event_histories_timestamp ON event_histories (timestamp)")

        print("Indexes added successfully!")


def downgrade():
    """Remove indexes from history tables"""
    with app.app_context():
        with db.engine.connect() as conn:
            # Drop indexes for PropertyHistory table
            conn.execute("DROP INDEX IF EXISTS ix_property_histories_device_id")
            conn.execute("DROP INDEX IF EXISTS ix_property_histories_property_id")
            conn.execute("DROP INDEX IF EXISTS ix_property_histories_timestamp")
            
            # Drop indexes for EventHistory table
            conn.execute("DROP INDEX IF EXISTS ix_event_histories_device_id")
            conn.execute("DROP INDEX IF EXISTS ix_event_histories_event_id")
            conn.execute("DROP INDEX IF EXISTS ix_event_histories_timestamp")
        
        print("Indexes removed successfully!")


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    
    if action == 'downgrade':
        downgrade()
    else:
        upgrade()