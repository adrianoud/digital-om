"""
创建设备属性绑定表的迁移脚本
"""

from models import db, DevicePropertyBinding

def upgrade():
    """创建设备属性绑定表"""
    db.create_all()
    print("设备属性绑定表创建成功")

def downgrade():
    """删除设备属性绑定表"""
    db.drop_all()
    print("设备属性绑定表删除成功")

if __name__ == '__main__':
    upgrade()