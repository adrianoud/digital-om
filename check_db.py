import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('device_models.db')
cursor = conn.cursor()

# 列出所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

# 检查modbus_points表
try:
    cursor.execute("SELECT COUNT(*) FROM modbus_points")
    count = cursor.fetchone()[0]
    print(f"\nModbus点位数量: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, name, address, is_active FROM modbus_points")
        points = cursor.fetchall()
        print("\n点位详情:")
        for point in points:
            print(f"  ID: {point[0]}, 名称: {point[1]}, 地址: {point[2]}, 激活: {point[3]}")
    else:
        print("\n没有找到Modbus点位")
except sqlite3.Error as e:
    print(f"查询modbus_points表时出错: {e}")

# 检查server_configs表
try:
    cursor.execute("SELECT COUNT(*) FROM server_configs")
    count = cursor.fetchone()[0]
    print(f"\n服务器配置数量: {count}")
    
    if count > 0:
        cursor.execute("SELECT key, value FROM server_configs")
        configs = cursor.fetchall()
        print("\n配置详情:")
        for config in configs:
            print(f"  Key: {config[0]}, Value: {config[1]}")
except sqlite3.Error as e:
    print(f"查询server_configs表时出错: {e}")

conn.close()