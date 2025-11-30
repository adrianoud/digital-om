#!/usr/bin/env python3
"""
初始化默认的Modbus点位配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import ModbusPoint

def init_default_points():
    """初始化默认点位"""
    with app.app_context():
        # 检查是否已存在点位
        existing_points = ModbusPoint.query.count()
        if existing_points > 0:
            print(f"数据库中已存在 {existing_points} 个点位，跳过初始化")
            return

        # 创建默认点位
        default_points = [
            ModbusPoint(
                name="CPU使用率",
                address=0,
                data_type="float",
                min_value=0.0,
                max_value=100.0,
                unit="%",
                description="CPU使用率百分比"
            ),
            ModbusPoint(
                name="内存使用率",
                address=2,
                data_type="float",
                min_value=0.0,
                max_value=100.0,
                unit="%",
                description="内存使用率百分比"
            ),
            ModbusPoint(
                name="磁盘使用率",
                address=4,
                data_type="float",
                min_value=0.0,
                max_value=100.0,
                unit="%",
                description="磁盘使用率百分比"
            ),
            ModbusPoint(
                name="网络流量",
                address=6,
                data_type="float",
                min_value=0.0,
                max_value=1000.0,
                unit="Mbps",
                description="网络流量"
            ),
            ModbusPoint(
                name="设备温度",
                address=8,
                data_type="float",
                min_value=30.0,
                max_value=70.0,
                unit="°C",
                description="设备温度"
            )
        ]

        # 添加到数据库
        for point in default_points:
            db.session.add(point)

        db.session.commit()
        print(f"成功初始化 {len(default_points)} 个默认点位")

if __name__ == "__main__":
    init_default_points()