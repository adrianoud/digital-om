import sqlite3
import os

# 连接到数据库
conn = sqlite3.connect('device_models.db')
cursor = conn.cursor()

# 查看decision_trees表结构
try:
    cursor.execute("PRAGMA table_info(decision_trees)")
    columns = cursor.fetchall()
    print("decision_trees表结构:")
    for col in columns:
        print(f"  列名: {col[1]}, 类型: {col[2]}, 是否非空: {col[3]}, 默认值: {col[4]}, 是否为主键: {col[5]}")
except sqlite3.Error as e:
    print(f"查询decision_trees表结构时出错: {e}")

# 查看decision_tree_nodes表结构
try:
    cursor.execute("PRAGMA table_info(decision_tree_nodes)")
    columns = cursor.fetchall()
    print("\ndecision_tree_nodes表结构:")
    for col in columns:
        print(f"  列名: {col[1]}, 类型: {col[2]}, 是否非空: {col[3]}, 默认值: {col[4]}, 是否为主键: {col[5]}")
except sqlite3.Error as e:
    print(f"查询decision_tree_nodes表结构时出错: {e}")

conn.close()