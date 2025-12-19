"""创建知识中心相关表的迁移脚本"""
import sqlite3
import os

def migrate():
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'device_models.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建决策树表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_trees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    ''')
    
    # 创建决策树节点表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS decision_tree_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tree_id INTEGER NOT NULL,
            parent_id INTEGER,
            name VARCHAR(200) NOT NULL,
            node_type VARCHAR(20) NOT NULL,
            condition TEXT,
            result TEXT,
            yes_child_id INTEGER,
            no_child_id INTEGER,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (tree_id) REFERENCES decision_trees (id),
            FOREIGN KEY (parent_id) REFERENCES decision_tree_nodes (id),
            FOREIGN KEY (yes_child_id) REFERENCES decision_tree_nodes (id),
            FOREIGN KEY (no_child_id) REFERENCES decision_tree_nodes (id)
        )
    ''')
    
    # 创建知识图谱表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_graphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
    ''')
    
    # 创建知识图谱节点表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_graph_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            graph_id INTEGER NOT NULL,
            name VARCHAR(200) NOT NULL,
            node_type VARCHAR(50) NOT NULL,
            properties TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (graph_id) REFERENCES knowledge_graphs (id)
        )
    ''')
    
    # 创建知识图谱边表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_graph_edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            graph_id INTEGER NOT NULL,
            from_node_id INTEGER NOT NULL,
            to_node_id INTEGER NOT NULL,
            relation_type VARCHAR(100) NOT NULL,
            properties TEXT,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL,
            FOREIGN KEY (graph_id) REFERENCES knowledge_graphs (id),
            FOREIGN KEY (from_node_id) REFERENCES knowledge_graph_nodes (id),
            FOREIGN KEY (to_node_id) REFERENCES knowledge_graph_nodes (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("知识中心相关表创建成功")

if __name__ == "__main__":
    migrate()