#!/usr/bin/env python3
"""
基于数据库配置的Modbus服务器
从数据库读取点位配置并提供模拟数据
"""

from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusSocketFramer
import threading
import time
import logging
import random
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModbusPoint:
    """
    Modbus点位类
    """
    def __init__(self, id, name, address, data_type, min_value, max_value, unit=None, description=None, is_active=True):
        self.id = id
        self.name = name
        self.address = address
        self.data_type = data_type
        self.min_value = min_value
        self.max_value = max_value
        self.unit = unit
        self.description = description
        self.is_active = is_active
        self.value = None
        
    def generate_value(self):
        """生成随机值"""
        if not self.is_active:
            return self.value if self.value is not None else 0
            
        if self.data_type == 'int':
            self.value = random.randint(int(self.min_value), int(self.max_value))
        elif self.data_type == 'float':
            self.value = round(random.uniform(self.min_value, self.max_value), 2)
        else:
            self.value = random.randint(int(self.min_value), int(self.max_value))
        return self.value

    def to_registers(self):
        """将值转换为Modbus寄存器值"""
        if self.value is None:
            self.generate_value()
            
        if self.data_type == 'float':
            # 将浮点数乘以100后转为整数，再拆分为两个16位值
            val = int(self.value * 100)
            # 使用小端序（根据实际测试结果调整）
            low = val & 0xFFFF
            high = (val >> 16) & 0xFFFF
            return [low, high]  # 小端序：低位在前
        else:
            # 整数直接拆分为两个16位值
            val = int(self.value)
            # 使用小端序
            low = val & 0xFFFF
            high = (val >> 16) & 0xFFFF
            return [low, high]  # 小端序：低位在前


class DatabaseModbusServer:
    """
    数据库驱动的Modbus服务器类
    从数据库读取点位配置并动态更新数据
    """

    def __init__(self, db_session_func, host="localhost", port=5020):
        self.db_session_func = db_session_func  # 数据库会话函数
        self.host = host
        self.port = port
        self.running = False
        self.points = []  # 点位列表
        self.update_interval = self._get_update_interval()  # 从数据库获取更新间隔
        
        # 创建数据存储区（使用足够大的数组）
        self.data_block = ModbusSequentialDataBlock(0x00, [0] * 1000)
        self.slave_context = ModbusSlaveContext(
            di=self.data_block,  # 离散输入
            co=self.data_block,  # 线圈
            hr=self.data_block,  # 保持寄存器
            ir=self.data_block,  # 输入寄存器
            zero_mode=True       # 使用零模式寻址
        )
        self.context = ModbusServerContext(slaves=self.slave_context, single=True)
        
        # 设置设备标识信息
        self.identity = ModbusDeviceIdentification()
        self.identity.VendorName = 'DataCenter Inc.'
        self.identity.ProductCode = 'DB-MODBUS-SERVER'
        self.identity.VendorUrl = 'http://www.datacenter.inc/'
        self.identity.ProductName = 'Database Modbus Simulator Server'
        self.identity.ModelName = 'DB-MODBUS-SIMU-01'
        self.identity.MajorMinorRevision = '1.0'

    def load_points_from_db(self):
        """从数据库加载点位配置"""
        try:
            # 使用传入的数据库会话函数，需要在应用上下文中执行
            from app import app
            with app.app_context():
                db_points = self.db_session_func()
                self.points = []
                for db_point in db_points:
                    point = ModbusPoint(
                        id=db_point.id,
                        name=db_point.name,
                        address=db_point.address,
                        data_type=db_point.data_type,
                        min_value=db_point.min_value,
                        max_value=db_point.max_value,
                        unit=db_point.unit,
                        description=db_point.description,
                        is_active=db_point.is_active
                    )
                    self.points.append(point)
            logger.info(f"从数据库加载了 {len(self.points)} 个点位")
            return True
        except Exception as e:
            logger.error(f"从数据库加载点位失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_modbus_registers(self):
        """
        更新Modbus寄存器中的数据
        """
        try:
            # 为每个点位生成新值并写入寄存器
            for point in self.points:
                if point.is_active and point.address >= 0:  # 确保点位启用且地址有效
                    # 生成新值
                    point.generate_value()
                    
                    # 转换为寄存器值
                    registers = point.to_registers()
                    
                    # 写入寄存器（每个点位占用两个寄存器）
                    print(f"Writing registers for point {point.name} (address {point.address}): {registers}")  # 调试信息
                    # 使用setValues方法写入寄存器值
                    self.data_block.setValues(point.address, registers)
            
            # 验证写入的值
            for point in self.points:
                if point.is_active and point.address >= 0:
                    verify = self.data_block.getValues(point.address, 2)
                    print(f"Verified registers for {point.name}: {verify}")  # 调试信息
            
            logger.info(f"更新了 {len([p for p in self.points if p.is_active])} 个点位的数据")
        except Exception as e:
            logger.error(f"更新Modbus寄存器时出错: {e}")
            import traceback
            traceback.print_exc()

    def get_point_values(self):
        """获取所有点位的当前值"""
        values = {}
        for point in self.points:
            values[point.id] = {
                'value': point.value,
                'name': point.name
            }
        return values

    def start_simulation(self):
        """启动数据模拟线程"""
        self.running = True
        self.simulation_thread = threading.Thread(target=self._simulation_worker)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        logger.info("数据模拟线程已启动")

    def _simulation_worker(self):
        """数据模拟工作线程"""
        while self.running:
            self.update_modbus_registers()
            time.sleep(self.update_interval)  # 使用可配置的更新间隔

    def _get_update_interval(self):
        """从数据库获取更新间隔配置"""
        try:
            # 使用传入的数据库会话函数获取配置，需要在应用上下文中执行
            from app import app
            with app.app_context():
                configs = self.db_session_func(get_config=True)
                for config in configs:
                    if config.key == 'modbus_update_interval':
                        return float(config.value)
            # 如果没有配置，默认为2秒
            return 2.0
        except Exception as e:
            logger.error(f"获取更新间隔配置失败: {e}")
            return 2.0

    def _save_update_interval(self, interval):
        """将更新间隔保存到数据库"""
        try:
            # 使用传入的数据库会话函数保存配置，需要在应用上下文中执行
            from app import app
            with app.app_context():
                self.db_session_func(save_config={'key': 'modbus_update_interval', 'value': str(interval)})
            return True
        except Exception as e:
            logger.error(f"保存更新间隔配置失败: {e}")
            return False

    def set_update_interval(self, interval):
        """设置更新间隔"""
        self.update_interval = interval
        self._save_update_interval(interval)
        return True

    def stop_simulation(self):
        """停止数据模拟"""
        self.running = False
        if hasattr(self, 'simulation_thread'):
            self.simulation_thread.join()
        logger.info("数据模拟线程已停止")

    def start_server(self):
        """启动Modbus TCP服务器"""
        # 首先从数据库加载点位
        if not self.load_points_from_db():
            logger.error("无法从数据库加载点位配置")
            return
            
        logger.info(f"启动Modbus TCP服务器 {self.host}:{self.port}")
        try:
            # 启动数据模拟
            self.start_simulation()
            
            # 启动Modbus服务器
            StartTcpServer(
                context=self.context,
                identity=self.identity,
                address=(self.host, self.port)
            )
        except Exception as e:
            logger.error(f"服务器启动失败: {e}")
        finally:
            self.stop_simulation()

# 添加全局变量来存储服务器实例
modbus_server_instance = None