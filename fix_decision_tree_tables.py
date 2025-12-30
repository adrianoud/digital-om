"""修复决策树表结构的脚本"""

def upgrade():
    """确保 decision_trees 和 decision_tree_nodes 表包含所有必需的字段"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查并添加 decision_trees 表的 device_type_id 字段
        cursor.execute("PRAGMA table_info(decision_trees)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'device_type_id' not in columns:
            cursor.execute("ALTER TABLE decision_trees ADD COLUMN device_type_id INTEGER")
            print("成功添加 device_type_id 字段到 decision_trees 表")
        else:
            print("decision_trees 表已包含 device_type_id 字段")
            
        # 检查并添加 decision_tree_nodes 表的 decision_input 字段
        cursor.execute("PRAGMA table_info(decision_tree_nodes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'decision_input' not in columns:
            cursor.execute("ALTER TABLE decision_tree_nodes ADD COLUMN decision_input TEXT")
            print("成功添加 decision_input 字段到 decision_tree_nodes 表")
        else:
            print("decision_tree_nodes 表已包含 decision_input 字段")
            
        conn.commit()
    except sqlite3.Error as e:
        print(f"修复表结构时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    upgrade()