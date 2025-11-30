from app import app, db
from models import DeviceType, DeviceProperty, DeviceEvent, DeviceMethod, Device, ModbusPoint, ServerConfig

with app.app_context():
    # 只创建不存在的表，不删除现有数据
    db.create_all()
    print('Database tables initialized successfully')