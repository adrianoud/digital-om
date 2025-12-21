"""创建数据分析结果表的迁移脚本"""

def upgrade():
    """创建数据分析结果表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建数据分析结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                data_points TEXT NOT NULL,
                chart_data TEXT,
                statistics TEXT,
                analysis_result TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES data_analysis_projects (id)
            )
        ''')
        conn.commit()
        print("数据分析结果表创建成功")
    except sqlite3.Error as e:
        print(f"创建数据分析结果表时出错: {e}")
    finally:
        conn.close()


def downgrade():
    """删除数据分析结果表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 删除数据分析结果表
        cursor.execute("DROP TABLE IF EXISTS data_analysis_results")
        conn.commit()
        print("数据分析结果表删除成功")
    except sqlite3.Error as e:
        print(f"删除数据分析结果表时出错: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    
    if action == 'downgrade':
        downgrade()
    else:
        upgrade()