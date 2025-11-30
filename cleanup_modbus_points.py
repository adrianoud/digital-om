#!/usr/bin/env python3
"""
清理过时的Modbus点位配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import ModbusPoint

def cleanup_old_points():
    """清理过时的点位"""
    with app.app_context():
        # 查找并删除过时的点位（CPU使用率、内存使用率等）
        old_points = ModbusPoint.query.filter(
            ModbusPoint.name.in_([
                "CPU使用率",
                "内存使用率", 
                "磁盘使用率",
                "网络流量",
                "设备温度"
            ])
        ).all()
        
        if old_points:
            print(f"找到 {len(old_points)} 个过时点位，正在删除...")
            for point in old_points:
                print(f"  删除点位: {point.name} (地址: {point.address})")
                db.session.delete(point)
            
            db.session.commit()
            print("过时点位已删除")
        else:
            print("未找到过时点位")

if __name__ == "__main__":
    cleanup_old_points()