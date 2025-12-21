"""运行所有数据库迁移脚本"""

import os
import sys
import importlib.util

# 添加项目目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

def run_migration(filename):
    """运行单个迁移脚本"""
    print(f"正在运行迁移脚本: {filename}")
    try:
        spec = importlib.util.spec_from_file_location(
            "migration", 
            os.path.join("./migrations", filename)
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        
        # 在应用上下文中运行升级函数
        with app.app_context():
            migration.upgrade()
            
        print(f"迁移脚本 {filename} 运行成功\n")
    except Exception as e:
        print(f"运行迁移脚本 {filename} 失败: {e}\n")

def main():
    """运行所有迁移脚本"""
    migration_files = [
        "001_create_device_property_bindings.py",
        "002_add_calculation_expression.py",
        "003_create_history_tables.py",
        "004_add_indexes_to_history_tables.py",
        "005_create_data_analysis_projects_table.py",
        "006_create_analysis_results_table.py",
        "007_add_project_data_fields.py",
        "008_create_knowledge_center_tables.py"
    ]
    
    print("开始运行所有数据库迁移脚本...")
    
    with app.app_context():
        for filename in migration_files:
            if os.path.exists(os.path.join("./migrations", filename)):
                run_migration(filename)
            else:
                print(f"迁移脚本 {filename} 不存在，跳过...")
    
    print("所有迁移脚本运行完成!")

if __name__ == "__main__":
    main()