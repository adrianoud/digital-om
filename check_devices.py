#!/usr/bin/env python3
"""检查数据库中的设备信息"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import Device, db

def check_devices():
    """检查设备信息"""
    with app.app_context():
        try:
            devices = Device.query.all()
            print(f"设备数量: {len(devices)}")
            if devices:
                for device in devices:
                    print(f"{device.id}: {device.name} ({device.type})")
            else:
                print("数据库中没有设备")
        except Exception as e:
            print(f"查询设备时出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_devices()