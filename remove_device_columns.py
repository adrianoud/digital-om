import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('device_models.db')
cursor = conn.cursor()

# 检查并移除device_id列（如果存在）
try:
    cursor.execute("SELECT device_id FROM data_analysis_projects LIMIT 1")
    print("检测到 device_id 列，需要移除")
    
    # SQLite不支持直接删除列，需要重新创建表
    # 1. 创建新表（不包含device_id和property_id列）
    cursor.execute('''
        CREATE TABLE data_analysis_projects_new (
            id INTEGER PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            analysis_type VARCHAR(50),
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    
    # 2. 复制数据（只复制新表中存在的列）
    cursor.execute('''
        INSERT INTO data_analysis_projects_new 
        SELECT id, name, description, analysis_type, created_at, updated_at 
        FROM data_analysis_projects
    ''')
    
    # 3. 删除旧表
    cursor.execute('DROP TABLE data_analysis_projects')
    
    # 4. 重命名新表
    cursor.execute('ALTER TABLE data_analysis_projects_new RENAME TO data_analysis_projects')
    
    conn.commit()
    print("成功移除 device_id 和 property_id 列")
    
except sqlite3.OperationalError as e:
    if "no such column" in str(e):
        print("device_id 列不存在，无需移除")
    else:
        print(f"检查列时出错: {e}")
except Exception as e:
    print(f"移除列时出错: {e}")

conn.close()
print("数据库更新完成")