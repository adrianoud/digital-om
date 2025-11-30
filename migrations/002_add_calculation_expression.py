"""
添加计算表达式字段到设备属性绑定表的迁移脚本
"""

def upgrade():
    """添加 calculation_expression 字段到 device_property_bindings 表"""
    import sqlite3
    import os
    
    # 获取项目根目录
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_dir, 'device_models.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 添加 calculation_expression 字段
        cursor.execute("ALTER TABLE device_property_bindings ADD COLUMN calculation_expression TEXT")
        conn.commit()
        print("成功添加 calculation_expression 字段到 device_property_bindings 表")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("字段 calculation_expression 已存在，无需添加")
        else:
            print(f"添加字段时出错: {e}")
    finally:
        conn.close()

def downgrade():
    """降级操作 - 注意：SQLite 不支持直接删除列"""
    print("注意：SQLite 不支持直接删除列操作")
    print("如需降级，请手动重建表结构")

if __name__ == '__main__':
    upgrade()