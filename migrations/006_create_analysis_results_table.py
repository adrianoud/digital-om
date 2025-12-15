"""
创建数据分析结果表的迁移脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, DataAnalysisResult
from app import app

def upgrade():
    """创建数据分析结果表"""
    with app.app_context():
        db.create_all()
        print("数据分析结果表创建成功")


def downgrade():
    """删除数据分析结果表"""
    with app.app_context():
        db.drop_all(DataAnalysisResult.__table__)
        print("数据分析结果表删除成功")


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    
    if action == 'downgrade':
        downgrade()
    else:
        upgrade()