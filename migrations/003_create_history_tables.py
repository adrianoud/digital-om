"""
创建设备属性和事件历史表的迁移脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import PropertyHistory, EventHistory

def upgrade():
    """创建历史表"""
    with app.app_context():
        db.create_all()
        print("设备属性和事件历史表创建成功")

def downgrade():
    """删除历史表"""
    with app.app_context():
        db.drop_all()
        print("设备属性和事件历史表删除成功")

if __name__ == '__main__':
    upgrade()