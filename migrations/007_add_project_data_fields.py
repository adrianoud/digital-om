"""
添加数据分析项目数据字段的迁移脚本
"""

def upgrade():
    """添加 selected_points, analysis_instances, conclusion 字段到 data_analysis_projects 表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 添加 selected_points 字段
        cursor.execute("ALTER TABLE data_analysis_projects ADD COLUMN selected_points TEXT")
        print("成功添加 selected_points 字段到 data_analysis_projects 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("字段 selected_points 已存在，无需添加")
        else:
            print(f"添加 selected_points 字段时出错: {e}")
    
    try:
        # 添加 analysis_instances 字段
        cursor.execute("ALTER TABLE data_analysis_projects ADD COLUMN analysis_instances TEXT")
        print("成功添加 analysis_instances 字段到 data_analysis_projects 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("字段 analysis_instances 已存在，无需添加")
        else:
            print(f"添加 analysis_instances 字段时出错: {e}")
    
    try:
        # 添加 conclusion 字段
        cursor.execute("ALTER TABLE data_analysis_projects ADD COLUMN conclusion TEXT")
        print("成功添加 conclusion 字段到 data_analysis_projects 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("字段 conclusion 已存在，无需添加")
        else:
            print(f"添加 conclusion 字段时出错: {e}")
    
    conn.commit()
    conn.close()
    print("数据库迁移完成")

def downgrade():
    """降级操作 - 注意：SQLite 不支持直接删除列"""
    print("注意：SQLite 不支持直接删除列操作")
    print("如需降级，请手动重建表结构")

if __name__ == '__main__':
    upgrade()