#!/usr/bin/env python3
"""
更新数据库结构以适应新的数据分析项目模型
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 在导入app之前设置环境变量
os.environ['FLASK_APP'] = 'app.py'

from app import app, db
from models import DataAnalysisProject

def update_database():
    """更新数据库结构"""
    with app.app_context():
        # 检查是否已存在analysis_type列
        try:
            # 尝试查询analysis_type字段
            db.session.query(DataAnalysisProject.analysis_type).first()
            print("数据库已包含 analysis_type 字段，无需更新")
        except Exception as e:
            if "doesn't exist" in str(e) or "no such column" in str(e):
                print("需要手动更新数据库结构")
                print("请使用SQLite工具执行以下SQL语句：")
                print("ALTER TABLE data_analysis_projects ADD COLUMN analysis_type VARCHAR(50);")
            else:
                print(f"检查数据库结构时出错: {e}")

if __name__ == "__main__":
    update_database()