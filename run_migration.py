"""Script to run database migrations"""

import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the migration module dynamically
import importlib.util
spec = importlib.util.spec_from_file_location("migration", "./migrations/004_add_indexes_to_history_tables.py")
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)

if __name__ == '__main__':
    print("Running migration to add indexes...")
    try:
        migration.upgrade()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)