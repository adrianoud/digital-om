"""创建设备属性和事件历史表的迁移脚本"""

def upgrade():
    """创建历史表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建设备属性历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS property_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (property_id) REFERENCES device_properties (id)
            )
        ''')
        
        # 创建设备事件历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (event_id) REFERENCES device_events (id)
            )
        ''')
        
        conn.commit()
        print("设备属性和事件历史表创建成功")
    except sqlite3.Error as e:
        print(f"创建历史表时出错: {e}")
    finally:
        conn.close()

def downgrade():
    """删除历史表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 删除历史表
        cursor.execute("DROP TABLE IF EXISTS property_histories")
        cursor.execute("DROP TABLE IF EXISTS event_histories")
        conn.commit()
        print("设备属性和事件历史表删除成功")
    except sqlite3.Error as e:
        print(f"删除历史表时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade()