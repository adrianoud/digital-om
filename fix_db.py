import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('device_models.db')
cursor = conn.cursor()

# 检查是否存在analysis_type列
try:
    cursor.execute("SELECT analysis_type FROM data_analysis_projects LIMIT 1")
    print("数据库已包含 analysis_type 字段")
except sqlite3.OperationalError as e:
    if "no such column" in str(e):
        print("添加 analysis_type 字段到 data_analysis_projects 表")
        try:
            cursor.execute("ALTER TABLE data_analysis_projects ADD COLUMN analysis_type VARCHAR(50)")
            conn.commit()
            print("成功添加 analysis_type 字段")
        except Exception as e:
            print(f"添加字段时出错: {e}")
    else:
        print(f"检查字段时出错: {e}")

# 清除所有旧的数据分析项目
try:
    cursor.execute("DELETE FROM data_analysis_projects")
    deleted_count = cursor.rowcount
    conn.commit()
    print(f"已清除 {deleted_count} 个旧的数据分析项目")
except Exception as e:
    print(f"清除旧数据时出错: {e}")

conn.close()
print("数据库更新完成")