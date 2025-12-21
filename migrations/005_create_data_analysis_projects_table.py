"""Migration script to create data analysis projects table"""

def upgrade():
    """Create data analysis projects table"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建数据分析项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_analysis_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print("Data analysis projects table created successfully!")
    except sqlite3.Error as e:
        print(f"创建数据分析项目表时出错: {e}")
    finally:
        conn.close()


def downgrade():
    """Drop data analysis projects table"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 删除数据分析项目表
        cursor.execute("DROP TABLE IF EXISTS data_analysis_projects")
        conn.commit()
        print("Data analysis projects table dropped successfully!")
    except sqlite3.Error as e:
        print(f"删除数据分析项目表时出错: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    
    if action == 'downgrade':
        downgrade()
    else:
        upgrade()