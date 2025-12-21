"""创建设备属性绑定表的迁移脚本"""

def upgrade():
    """创建设备属性绑定表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 创建设备属性绑定表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_property_bindings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                modbus_point_id INTEGER,
                calculation_expression TEXT,
                FOREIGN KEY (device_id) REFERENCES devices (id),
                FOREIGN KEY (property_id) REFERENCES device_properties (id),
                FOREIGN KEY (modbus_point_id) REFERENCES modbus_points (id)
            )
        ''')
        conn.commit()
        print("设备属性绑定表创建成功")
    except sqlite3.Error as e:
        print(f"创建设备属性绑定表时出错: {e}")
    finally:
        conn.close()

def downgrade():
    """删除设备属性绑定表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 删除设备属性绑定表
        cursor.execute("DROP TABLE IF EXISTS device_property_bindings")
        conn.commit()
        print("设备属性绑定表删除成功")
    except sqlite3.Error as e:
        print(f"删除设备属性绑定表时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade()