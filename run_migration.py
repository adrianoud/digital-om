"""Script to run all database migrations in order"""

import sys
import os
import re

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_migration_files():
    """获取所有迁移文件，按数字顺序排序"""
    migrations_dir = "./migrations"
    migration_files = []
    
    if os.path.exists(migrations_dir):
        files = os.listdir(migrations_dir)
        # 过滤出迁移文件并按数字排序
        migration_pattern = re.compile(r'^(\d+)_.*\.py$')
        for file in files:
            match = migration_pattern.match(file)
            if match:
                migration_files.append((int(match.group(1)), file))
        
        # 按数字顺序排序
        migration_files.sort(key=lambda x: x[0])
    
    return [file[1] for file in migration_files]

def run_migration(filename):
    """运行单个迁移脚本"""
    print(f"Running migration: {filename}")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("migration", f"./migrations/{filename}")
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        migration.upgrade()
        print(f"Migration {filename} completed successfully!\n")
        return True
    except Exception as e:
        print(f"Migration {filename} failed: {e}\n")
        return False

if __name__ == '__main__':
    print("Running all database migrations...")
    migration_files = get_migration_files()
    
    if not migration_files:
        print("No migration files found.")
        sys.exit(0)
    
    success_count = 0
    failed_count = 0
    
    for migration_file in migration_files:
        if run_migration(migration_file):
            success_count += 1
        else:
            failed_count += 1
    
    print(f"Migration Summary: {success_count} succeeded, {failed_count} failed")
    
    if failed_count > 0:
        sys.exit(1)
    else:
        print("All migrations completed successfully!")
        sys.exit(0)