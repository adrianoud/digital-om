#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request, redirect, url_for
import random
import time
import os
import threading
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

# 导入模型
from models import db, DeviceType, DeviceProperty, DeviceEvent, DeviceMethod, Device, ModbusPoint, DevicePropertyBinding, ServerConfig

# 添加新的模型导入
from models import PropertyHistory, EventHistory, DataAnalysisProject, DataAnalysisResult
from models import DecisionTree, DecisionTreeNode, KnowledgeGraph, KnowledgeGraphNode, KnowledgeGraphEdge

# 导入Modbus服务器类
from modbus_server_db import DatabaseModbusServer

app = Flask(__name__, static_folder='static', template_folder='templates')

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'device_models.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 配置上传文件夹
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制文件大小为16MB

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 初始化数据库
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/device-monitoring')
def device_monitoring():
    """设备监控页面"""
    # 尝试连接到Modbus服务器获取实时数据
    data = {}
    try:
        client = ModbusTcpClient('localhost', 5020)
        client.connect()
        
        # 读取寄存器数据
        # 读取CPU使用率 (寄存器0-1)
        response = client.read_holding_registers(0, 2)
        if not response.isError():
            low = response.registers[0]
            high = response.registers[1]
            data['cpu_usage'] = ((low << 16) | high) / 100.0
        
        # 读取内存使用率 (寄存器2-3)
        response = client.read_holding_registers(2, 2)
        if not response.isError():
            low = response.registers[0]
            high = response.registers[1]
            data['memory_usage'] = ((low << 16) | high) / 100.0
            
        # 读取磁盘使用率 (寄存器4-5)
        response = client.read_holding_registers(4, 2)
        if not response.isError():
            low = response.registers[0]
            high = response.registers[1]
            data['disk_usage'] = ((low << 16) | high) / 100.0
            
        # 读取网络流量 (寄存器6-7)
        response = client.read_holding_registers(6, 2)
        if not response.isError():
            low = response.registers[0]
            high = response.registers[1]
            data['network_traffic'] = ((low << 16) | high) / 100.0
            
        # 读取设备温度 (寄存器8-9)
        response = client.read_holding_registers(8, 2)
        if not response.isError():
            low = response.registers[0]
            high = response.registers[1]
            data['temperature'] = ((low << 16) | high) / 100.0
        
        client.close()
        
        # 如果无法从Modbus服务器获取数据，则使用模拟数据
        if not data:
            data = {
                'cpu_usage': round(random.uniform(10, 90), 2),
                'memory_usage': round(random.uniform(20, 80), 2),
                'disk_usage': round(random.uniform(30, 95), 2),
                'network_traffic': round(random.uniform(0, 1000), 2),
                'temperature': round(random.uniform(30, 70), 2)
            }
    except Exception as e:
        # 出现任何异常则使用模拟数据
        data = {
            'cpu_usage': round(random.uniform(10, 90), 2),
            'memory_usage': round(random.uniform(20, 80), 2),
            'disk_usage': round(random.uniform(30, 95), 2),
            'network_traffic': round(random.uniform(0, 1000), 2),
            'temperature': round(random.uniform(30, 70), 2)
        }
    
    return render_template('device_monitoring.html', data=data)

@app.route('/device-management', methods=['GET', 'POST'])
def device_management():
    message = None
    message_type = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            device_id = int(request.form.get('device_id'))
            try:
                device = Device.query.get(device_id)
                if device:
                    db.session.delete(device)
                    db.session.commit()
                    message = "设备信息删除成功！"
                    message_type = "success"
                else:
                    message = "未找到指定的设备"
                    message_type = "error"
            except Exception as e:
                db.session.rollback()
                message = f"删除失败：{str(e)}"
                message_type = "error"
    
    # 读取设备台账数据
    try:
        devices = Device.query.all()
        devices = [device.to_dict() for device in devices]
    except Exception as e:
        devices = []
        message = f"读取设备信息失败：{str(e)}"
        message_type = "error"
    
    return render_template('device_management.html', devices=devices, message=message, message_type=message_type)

@app.route('/device-edit/<int:device_id>', methods=['GET', 'POST'])
def device_edit(device_id):
    message = None
    message_type = None
    
    # 获取要编辑的设备
    device = Device.query.get(device_id)
    if not device:
        message = "未找到指定的设备信息"
        message_type = "error"
        return render_template('device_ledger.html', message=message, message_type=message_type)
    
    if request.method == 'POST':
        # 获取表单数据
        name = request.form['name']
        code = request.form['code']
        type = request.form['type']
        model = request.form['model']
        purchase_date = request.form['purchase_date']
        
        # 更新数据库中的设备信息
        try:
            device.name = name
            device.code = code
            device.type = type
            device.model = model
            if purchase_date:
                device.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            
            db.session.commit()
            message = "设备信息更新成功！"
            message_type = "success"
        except Exception as e:
            db.session.rollback()
            message = f"更新失败：{str(e)}"
            message_type = "error"
    
    # 获取设备类型列表
    device_types = []
    try:
        with app.app_context():
            device_types = DeviceType.query.all()
    except Exception as e:
        print(f"获取设备类型列表失败: {e}")
    
    # 将设备对象转换为字典格式
    device_dict = device.to_dict()
    return render_template('device_edit.html', device=device_dict, device_types=device_types, message=message, message_type=message_type)

@app.route('/device-ledger', methods=['GET', 'POST'])
def device_ledger():
    if request.method == 'POST':
        # 获取表单数据
        name = request.form['name']
        code = request.form['code']
        type = request.form['type']
        model = request.form['model']
        purchase_date = request.form['purchase_date']
        
        # 保存到数据库
        try:
            device = Device(
                name=name,
                code=code,
                type=type,
                model=model,
                purchase_date=datetime.strptime(purchase_date, '%Y-%m-%d').date() if purchase_date else None
            )
            
            db.session.add(device)
            db.session.commit()
            message = "设备信息保存成功！"
            message_type = "success"
        except Exception as e:
            db.session.rollback()
            message = f"保存失败：{str(e)}"
            message_type = "error"
        
        return render_template('device_ledger.html', message=message, message_type=message_type)
    
    # 获取设备类型列表
    device_types = []
    try:
        with app.app_context():
            device_types = DeviceType.query.all()
    except Exception as e:
        print(f"获取设备类型列表失败: {e}")
    
    return render_template('device_ledger.html', device_types=device_types)

@app.route('/device-history')
def device_history():
    """设备历史数据页面"""
    return render_template('device_history.html')


@app.route('/device-models')
def device_models():
    """设备模型管理主页面"""
    return render_template('device_models.html')

@app.route('/api/device-types', methods=['GET'])
def api_get_device_types():
    """获取所有设备类型"""
    try:
        device_types = DeviceType.query.all()
        return jsonify({
            'success': True,
            'data': [dt.to_dict() for dt in device_types]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-types', methods=['POST'])
def api_create_device_type():
    """创建设备类型"""
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            return jsonify({
                'success': False,
                'message': '设备类型名称不能为空'
            }), 400
        
        # 检查是否已存在同名设备类型
        existing = DeviceType.query.filter_by(name=name).first()
        if existing:
            return jsonify({
                'success': False,
                'message': '设备类型名称已存在'
            }), 400
        
        # 处理图片上传
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # 生成唯一文件名
                extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
                filename = f"{uuid.uuid4().hex}.{extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_path = f"uploads/{filename}"
        
        device_type = DeviceType(name=name, description=description, image_path=image_path)
        db.session.add(device_type)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '设备类型创建成功',
            'data': device_type.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-types/<int:id>', methods=['PUT'])
def api_update_device_type(id):
    """更新设备类型"""
    try:
        device_type = DeviceType.query.get(id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            return jsonify({
                'success': False,
                'message': '设备类型名称不能为空'
            }), 400
        
        # 检查是否已存在同名设备类型（排除自己）
        existing = DeviceType.query.filter(DeviceType.name == name, DeviceType.id != id).first()
        if existing:
            return jsonify({
                'success': False,
                'message': '设备类型名称已存在'
            }), 400
        
        device_type.name = name
        device_type.description = description
        
        # 处理图片上传
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # 删除旧图片（如果存在）
                if device_type.image_path:
                    old_image_path = os.path.join(basedir, 'static', device_type.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # 保存新图片
                extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
                filename = f"{uuid.uuid4().hex}.{extension}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                device_type.image_path = f"uploads/{filename}"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '设备类型更新成功',
            'data': device_type.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-types/<int:id>', methods=['DELETE'])
def api_delete_device_type(id):
    """删除设备类型"""
    try:
        device_type = DeviceType.query.get(id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        db.session.delete(device_type)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '设备类型删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-types/<int:device_type_id>/properties', methods=['GET'])
def api_get_device_properties(device_type_id):
    """获取设备类型的所有属性"""
    try:
        device_type = DeviceType.query.get(device_type_id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        properties = DeviceProperty.query.filter_by(device_type_id=device_type_id).all()
        return jsonify({
            'success': True,
            'data': [prop.to_dict() for prop in properties]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-properties', methods=['POST'])
def api_create_device_property():
    """创建设备属性"""
    try:
        data = request.get_json()
        name = data.get('name')
        identifier = data.get('identifier')
        data_type = data.get('data_type')
        device_type_id = data.get('device_type_id')
        
        if not all([name, identifier, data_type, device_type_id]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 检查设备类型是否存在
        device_type = DeviceType.query.get(device_type_id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        # 检查同一设备类型下是否已存在相同标识符的属性
        existing = DeviceProperty.query.filter_by(
            device_type_id=device_type_id, 
            identifier=identifier
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': '该标识符已存在于当前设备类型中'
            }), 400
        
        property = DeviceProperty(
            name=name,
            identifier=identifier,
            data_type=data_type,
            unit=data.get('unit'),
            description=data.get('description'),
            read_write_flag=data.get('read_write_flag', 'rw'),
            min_value=data.get('min_value'),
            max_value=data.get('max_value'),
            device_type_id=device_type_id
        )
        
        db.session.add(property)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '属性创建成功',
            'data': property.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-properties/<int:id>', methods=['PUT'])
def api_update_device_property(id):
    """更新设备属性"""
    try:
        property = DeviceProperty.query.get(id)
        if not property:
            return jsonify({
                'success': False,
                'message': '属性不存在'
            }), 404
        
        data = request.get_json()
        # 更新属性信息
        property.name = data.get('name', property.name)
        property.identifier = data.get('identifier', property.identifier)
        property.data_type = data.get('data_type', property.data_type)
        property.unit = data.get('unit', property.unit)
        property.description = data.get('description', property.description)
        property.read_write_flag = data.get('read_write_flag', property.read_write_flag)
        property.min_value = data.get('min_value', property.min_value)
        property.max_value = data.get('max_value', property.max_value)
        
        # 如果改变了标识符，需要检查重复
        if 'identifier' in data and data['identifier'] != property.identifier:
            existing = DeviceProperty.query.filter(
                DeviceProperty.device_type_id == property.device_type_id,
                DeviceProperty.identifier == data['identifier'],
                DeviceProperty.id != id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': '该标识符已存在于当前设备类型中'
                }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '属性更新成功',
            'data': property.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-properties/<int:id>', methods=['DELETE'])
def api_delete_device_property(id):
    """删除设备属性"""
    try:
        property = DeviceProperty.query.get(id)
        if not property:
            return jsonify({
                'success': False,
                'message': '属性不存在'
            }), 404
        
        db.session.delete(property)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '属性删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-types/<int:device_type_id>/events', methods=['GET'])
def api_get_device_events(device_type_id):
    """获取设备类型的所有事件"""
    try:
        device_type = DeviceType.query.get(device_type_id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        events = DeviceEvent.query.filter_by(device_type_id=device_type_id).all()
        return jsonify({
            'success': True,
            'data': [event.to_dict() for event in events]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-events', methods=['POST'])
def api_create_device_event():
    """创建设备事件"""
    try:
        data = request.get_json()
        name = data.get('name')
        identifier = data.get('identifier')
        device_type_id = data.get('device_type_id')
        
        if not all([name, identifier, device_type_id]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 检查设备类型是否存在
        device_type = DeviceType.query.get(device_type_id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        # 检查同一设备类型下是否已存在相同标识符的事件
        existing = DeviceEvent.query.filter_by(
            device_type_id=device_type_id, 
            identifier=identifier
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': '该标识符已存在于当前设备类型中'
            }), 400
        
        event = DeviceEvent(
            name=name,
            identifier=identifier,
            description=data.get('description'),
            level=data.get('level', 'info'),
            condition=data.get('condition'),
            device_type_id=device_type_id
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '事件创建成功',
            'data': event.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-events/<int:id>', methods=['PUT'])
def api_update_device_event(id):
    """更新设备事件"""
    try:
        event = DeviceEvent.query.get(id)
        if not event:
            return jsonify({
                'success': False,
                'message': '事件不存在'
            }), 404
        
        data = request.get_json()
        # 更新事件信息
        event.name = data.get('name', event.name)
        event.identifier = data.get('identifier', event.identifier)
        event.description = data.get('description', event.description)
        event.level = data.get('level', event.level)
        event.condition = data.get('condition', event.condition)
        
        # 如果改变了标识符，需要检查重复
        if 'identifier' in data and data['identifier'] != event.identifier:
            existing = DeviceEvent.query.filter(
                DeviceEvent.device_type_id == event.device_type_id,
                DeviceEvent.identifier == data['identifier'],
                DeviceEvent.id != id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': '该标识符已存在于当前设备类型中'
                }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '事件更新成功',
            'data': event.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/knowledge-center')
def knowledge_center():
    """知识中心主页面"""
    return render_template('knowledge_center.html')

@app.route('/decision-tree')
def decision_tree():
    """决策树管理页面"""
    return render_template('decision_tree.html')

@app.route('/knowledge-graph')
def knowledge_graph():
    """知识图谱管理页面"""
    return render_template('knowledge_graph.html')

# 决策树 API 接口
@app.route('/api/decision-trees', methods=['GET'])
def api_get_decision_trees():
    """获取所有决策树"""
    try:
        trees = DecisionTree.query.all()
        return jsonify({
            'success': True,
            'data': [tree.to_dict() for tree in trees]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-trees', methods=['POST'])
def api_create_decision_tree():
    """创建决策树"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            return jsonify({
                'success': False,
                'message': '决策树名称不能为空'
            }), 400
        
        tree = DecisionTree(
            name=name,
            description=description
        )
        
        db.session.add(tree)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '决策树创建成功',
            'data': tree.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-tree-nodes/<int:id>', methods=['GET'])
def api_get_decision_tree_node(id):
    """获取单个决策树节点"""
    try:
        node = DecisionTreeNode.query.get(id)
        if not node:
            return jsonify({
                'success': False,
                'message': '节点不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': node.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-trees/<int:id>', methods=['GET'])
def api_get_decision_tree(id):
    """获取单个决策树"""
    try:
        tree = DecisionTree.query.get(id)
        if not tree:
            return jsonify({
                'success': False,
                'message': '决策树不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': tree.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500



@app.route('/api/decision-trees/<int:id>', methods=['PUT'])
def api_update_decision_tree(id):
    """更新决策树"""
    try:
        tree = DecisionTree.query.get(id)
        if not tree:
            return jsonify({
                'success': False,
                'message': '决策树不存在'
            }), 404
            
        data = request.get_json()
        tree.name = data.get('name', tree.name)
        tree.description = data.get('description', tree.description)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '决策树更新成功',
            'data': tree.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-trees/<int:id>', methods=['DELETE'])
def api_delete_decision_tree(id):
    """删除决策树"""
    try:
        tree = DecisionTree.query.get(id)
        if not tree:
            return jsonify({
                'success': False,
                'message': '决策树不存在'
            }), 404
            
        # 先删除所有相关的节点，需要特殊处理循环依赖
        nodes = DecisionTreeNode.query.filter_by(tree_id=id).all()
        
        # 先清除所有节点的外键引用
        for node in nodes:
            node.parent_id = None
            node.yes_child_id = None
            node.no_child_id = None
        
        # 提交外键更新
        db.session.flush()
        
        # 再删除所有节点
        for node in nodes:
            db.session.delete(node)
            
        # 最后删除决策树本身
        db.session.delete(tree)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '决策树删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 决策树节点 API 接口
@app.route('/api/decision-trees/<int:tree_id>/nodes', methods=['GET'])
def api_get_decision_tree_nodes(tree_id):
    """获取决策树的所有节点"""
    try:
        tree = DecisionTree.query.get(tree_id)
        if not tree:
            return jsonify({
                'success': False,
                'message': '决策树不存在'
            }), 404
        
        nodes = DecisionTreeNode.query.filter_by(tree_id=tree_id).all()
        return jsonify({
            'success': True,
            'data': [node.to_dict() for node in nodes]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-tree-nodes', methods=['POST'])
def api_create_decision_tree_node():
    """创建决策树节点"""
    try:
        data = request.get_json()
        tree_id = data.get('tree_id')
        name = data.get('name')
        node_type = data.get('node_type')
        
        if not all([tree_id, name, node_type]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 检查决策树是否存在
        tree = DecisionTree.query.get(tree_id)
        if not tree:
            return jsonify({
                'success': False,
                'message': '决策树不存在'
            }), 404
        
        # 检查节点类型是否合法
        valid_node_types = ['root', 'decision', 'leaf']
        if node_type not in valid_node_types:
            return jsonify({
                'success': False,
                'message': '节点类型不合法'
            }), 400
        
        # 对于根节点，检查是否已存在
        if node_type == 'root':
            existing_root = DecisionTreeNode.query.filter_by(tree_id=tree_id, node_type='root').first()
            if existing_root:
                return jsonify({
                    'success': False,
                    'message': '该决策树已存在根节点'
                }), 400
        
        # 创建节点
        node = DecisionTreeNode(
            tree_id=tree_id,
            name=name,
            node_type=node_type,
            parent_id=data.get('parent_id'),
            condition=data.get('condition'),
            result=data.get('result'),
            yes_child_id=data.get('yes_child_id'),
            no_child_id=data.get('no_child_id')
        )
        
        db.session.add(node)
        db.session.flush()  # 获取新节点的ID
        
        # 如果是分支节点，更新父节点的引用
        branch_type = data.get('branch_type')
        parent_id = data.get('parent_id')
        if parent_id and branch_type:
            parent_node = DecisionTreeNode.query.get(parent_id)
            if parent_node:
                if branch_type == 'yes':
                    parent_node.yes_child_id = node.id
                elif branch_type == 'no':
                    parent_node.no_child_id = node.id
                db.session.add(parent_node)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点创建成功',
            'data': node.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-tree-nodes/<int:id>', methods=['PUT'])
def api_update_decision_tree_node(id):
    """更新决策树节点"""
    try:
        node = DecisionTreeNode.query.get(id)
        if not node:
            return jsonify({
                'success': False,
                'message': '节点不存在'
            }), 404
        
        data = request.get_json()
        node.name = data.get('name', node.name)
        node.condition = data.get('condition', node.condition)
        node.result = data.get('result', node.result)
        node.yes_child_id = data.get('yes_child_id', node.yes_child_id)
        node.no_child_id = data.get('no_child_id', node.no_child_id)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点更新成功',
            'data': node.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/decision-tree-nodes/<int:id>', methods=['DELETE'])
def api_delete_decision_tree_node(id):
    """删除决策树节点"""
    try:
        node = DecisionTreeNode.query.get(id)
        if not node:
            return jsonify({
                'success': False,
                'message': '节点不存在'
            }), 404
            
        db.session.delete(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 知识图谱 API 接口
@app.route('/api/knowledge-graphs', methods=['GET'])
def api_get_knowledge_graphs():
    """获取所有知识图谱"""
    try:
        graphs = KnowledgeGraph.query.all()
        return jsonify({
            'success': True,
            'data': [graph.to_dict() for graph in graphs]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graphs', methods=['POST'])
def api_create_knowledge_graph():
    """创建知识图谱"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name:
            return jsonify({
                'success': False,
                'message': '知识图谱名称不能为空'
            }), 400
        
        graph = KnowledgeGraph(
            name=name,
            description=description
        )
        
        db.session.add(graph)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '知识图谱创建成功',
            'data': graph.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graphs/<int:id>', methods=['GET'])
def api_get_knowledge_graph(id):
    """获取单个知识图谱"""
    try:
        graph = KnowledgeGraph.query.get(id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': graph.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graphs/<int:id>', methods=['PUT'])
def api_update_knowledge_graph(id):
    """更新知识图谱"""
    try:
        graph = KnowledgeGraph.query.get(id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
            
        data = request.get_json()
        graph.name = data.get('name', graph.name)
        graph.description = data.get('description', graph.description)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '知识图谱更新成功',
            'data': graph.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graphs/<int:id>', methods=['DELETE'])
def api_delete_knowledge_graph(id):
    """删除知识图谱"""
    try:
        graph = KnowledgeGraph.query.get(id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
            
        db.session.delete(graph)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '知识图谱删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 知识图谱节点 API 接口
@app.route('/api/knowledge-graphs/<int:graph_id>/nodes', methods=['GET'])
def api_get_knowledge_graph_nodes(graph_id):
    """获取知识图谱的所有节点"""
    try:
        graph = KnowledgeGraph.query.get(graph_id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
        
        nodes = KnowledgeGraphNode.query.filter_by(graph_id=graph_id).all()
        return jsonify({
            'success': True,
            'data': [node.to_dict() for node in nodes]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graph-nodes', methods=['POST'])
def api_create_knowledge_graph_node():
    """创建知识图谱节点"""
    try:
        data = request.get_json()
        graph_id = data.get('graph_id')
        name = data.get('name')
        node_type = data.get('node_type')
        properties = data.get('properties')
        
        if not all([graph_id, name, node_type]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 检查知识图谱是否存在
        graph = KnowledgeGraph.query.get(graph_id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
        
        node = KnowledgeGraphNode(
            graph_id=graph_id,
            name=name,
            node_type=node_type,
            properties=properties
        )
        
        db.session.add(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点创建成功',
            'data': node.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graph-nodes/<int:id>', methods=['PUT'])
def api_update_knowledge_graph_node(id):
    """更新知识图谱节点"""
    try:
        node = KnowledgeGraphNode.query.get(id)
        if not node:
            return jsonify({
                'success': False,
                'message': '节点不存在'
            }), 404
        
        data = request.get_json()
        node.name = data.get('name', node.name)
        node.node_type = data.get('node_type', node.node_type)
        node.properties = data.get('properties', node.properties)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点更新成功',
            'data': node.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graph-nodes/<int:id>', methods=['DELETE'])
def api_delete_knowledge_graph_node(id):
    """删除知识图谱节点"""
    try:
        node = KnowledgeGraphNode.query.get(id)
        if not node:
            return jsonify({
                'success': False,
                'message': '节点不存在'
            }), 404
            
        db.session.delete(node)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '节点删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 知识图谱边 API 接口
@app.route('/api/knowledge-graphs/<int:graph_id>/edges', methods=['GET'])
def api_get_knowledge_graph_edges(graph_id):
    """获取知识图谱的所有边"""
    try:
        graph = KnowledgeGraph.query.get(graph_id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
        
        edges = KnowledgeGraphEdge.query.filter_by(graph_id=graph_id).all()
        return jsonify({
            'success': True,
            'data': [edge.to_dict() for edge in edges]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graph-edges', methods=['POST'])
def api_create_knowledge_graph_edge():
    """创建知识图谱边"""
    try:
        data = request.get_json()
        graph_id = data.get('graph_id')
        from_node_id = data.get('from_node_id')
        to_node_id = data.get('to_node_id')
        relation_type = data.get('relation_type')
        properties = data.get('properties')
        
        if not all([graph_id, from_node_id, to_node_id, relation_type]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 检查知识图谱是否存在
        graph = KnowledgeGraph.query.get(graph_id)
        if not graph:
            return jsonify({
                'success': False,
                'message': '知识图谱不存在'
            }), 404
        
        # 检查节点是否存在
        from_node = KnowledgeGraphNode.query.get(from_node_id)
        to_node = KnowledgeGraphNode.query.get(to_node_id)
        if not from_node or not to_node:
            return jsonify({
                'success': False,
                'message': '起始节点或目标节点不存在'
            }), 404
        
        edge = KnowledgeGraphEdge(
            graph_id=graph_id,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            relation_type=relation_type,
            properties=properties
        )
        
        db.session.add(edge)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '边创建成功',
            'data': edge.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graph-edges/<int:id>', methods=['PUT'])
def api_update_knowledge_graph_edge(id):
    """更新知识图谱边"""
    try:
        edge = KnowledgeGraphEdge.query.get(id)
        if not edge:
            return jsonify({
                'success': False,
                'message': '边不存在'
            }), 404
        
        data = request.get_json()
        edge.relation_type = data.get('relation_type', edge.relation_type)
        edge.properties = data.get('properties', edge.properties)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '边更新成功',
            'data': edge.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/knowledge-graph-edges/<int:id>', methods=['DELETE'])
def api_delete_knowledge_graph_edge(id):
    """删除知识图谱边"""
    try:
        edge = KnowledgeGraphEdge.query.get(id)
        if not edge:
            return jsonify({
                'success': False,
                'message': '边不存在'
            }), 404
            
        db.session.delete(edge)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '边删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/device-events/<int:id>', methods=['DELETE'])
def api_delete_device_event(id):
    """删除设备事件"""
    try:
        event = DeviceEvent.query.get(id)
        if not event:
            return jsonify({
                'success': False,
                'message': '事件不存在'
            }), 404
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '事件删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-types/<int:device_type_id>/methods', methods=['GET'])
def api_get_device_methods(device_type_id):
    """获取设备类型的所有方法"""
    try:
        device_type = DeviceType.query.get(device_type_id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        methods = DeviceMethod.query.filter_by(device_type_id=device_type_id).all()
        return jsonify({
            'success': True,
            'data': [method.to_dict() for method in methods]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-methods', methods=['POST'])
def api_create_device_method():
    """创建设备方法"""
    try:
        data = request.get_json()
        name = data.get('name')
        identifier = data.get('identifier')
        device_type_id = data.get('device_type_id')
        
        if not all([name, identifier, device_type_id]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 检查设备类型是否存在
        device_type = DeviceType.query.get(device_type_id)
        if not device_type:
            return jsonify({
                'success': False,
                'message': '设备类型不存在'
            }), 404
        
        # 检查同一设备类型下是否已存在相同标识符的方法
        existing = DeviceMethod.query.filter_by(
            device_type_id=device_type_id, 
            identifier=identifier
        ).first()
        if existing:
            return jsonify({
                'success': False,
                'message': '该标识符已存在于当前设备类型中'
            }), 400
        
        method = DeviceMethod(
            name=name,
            identifier=identifier,
            description=data.get('description'),
            input_params=data.get('input_params'),
            output_params=data.get('output_params'),
            device_type_id=device_type_id
        )
        
        db.session.add(method)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '方法创建成功',
            'data': method.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-methods/<int:id>', methods=['PUT'])
def api_update_device_method(id):
    """更新设备方法"""
    try:
        method = DeviceMethod.query.get(id)
        if not method:
            return jsonify({
                'success': False,
                'message': '方法不存在'
            }), 404
        
        data = request.get_json()
        # 更新方法信息
        method.name = data.get('name', method.name)
        method.identifier = data.get('identifier', method.identifier)
        method.description = data.get('description', method.description)
        method.input_params = data.get('input_params', method.input_params)
        method.output_params = data.get('output_params', method.output_params)
        
        # 如果改变了标识符，需要检查重复
        if 'identifier' in data and data['identifier'] != method.identifier:
            existing = DeviceMethod.query.filter(
                DeviceMethod.device_type_id == method.device_type_id,
                DeviceMethod.identifier == data['identifier'],
                DeviceMethod.id != id
            ).first()
            if existing:
                return jsonify({
                    'success': False,
                    'message': '该标识符已存在于当前设备类型中'
                }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '方法更新成功',
            'data': method.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-methods/<int:id>', methods=['DELETE'])
def api_delete_device_method(id):
    """删除设备方法"""
    try:
        method = DeviceMethod.query.get(id)
        if not method:
            return jsonify({
                'success': False,
                'message': '方法不存在'
            }), 404
        
        db.session.delete(method)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '方法删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def read_modbus_value(address):
    """
    从Modbus服务器读取指定地址的值
    """
    try:
        client = ModbusTcpClient('localhost', 5020)
        client.connect()
        
        # 读取两个连续的寄存器（用于浮点数）
        response = client.read_holding_registers(address, 2)
        if not response.isError():
            # 按照小端序组合两个16位值成32位整数，然后除以100得到原始浮点数
            low = response.registers[0]
            high = response.registers[1]
            value = ((high << 16) | low) / 100.0  # 修正为小端序处理
            print(f"读取寄存器地址 {address}: low={low}, high={high}, 计算值={value}")
            client.close()
            return value
        else:
            print(f"读取寄存器地址 {address} 时返回错误: {response}")
            client.close()
            return None
    except Exception as e:
        print(f"读取Modbus数据失败: {e}")
        import traceback
        traceback.print_exc()
        if 'client' in locals():
            client.close()
        return None

@app.route('/api/modbus-point/<int:point_id>/value', methods=['GET'])
def api_get_modbus_point_value(point_id):
    """获取Modbus点位的当前值"""
    try:
        from models import ModbusPoint
        # 获取点位信息
        point = ModbusPoint.query.get(point_id)
        if not point:
            return jsonify({
                'success': False,
                'message': '点位不存在'
            }), 404
        
        print(f"正在读取点位 {point_id} (地址: {point.address}, 名称: {point.name})")
        
        # 从Modbus服务器读取值
        value = read_modbus_value(point.address)
        if value is not None:
            return jsonify({
                'success': True,
                'value': value
            })
        else:
            return jsonify({
                'success': False,
                'message': '无法读取Modbus数据'
            }), 500
    except Exception as e:
        print(f"获取Modbus点位值时出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-monitoring-data')
def get_device_monitoring_data():
    """获取设备监控数据"""
    try:
        # 获取设备列表
        devices = []
        try:
            device_objects = Device.query.all()
            devices = [device.to_dict() for device in device_objects]
            print(f"查询到 {len(devices)} 个设备")  # 调试信息
        except Exception as e:
            print(f"读取设备信息失败: {e}")
        
        return jsonify({
            'success': True,
            'devices': devices
        })
    except Exception as e:
        print(f"获取设备监控数据时出错: {e}")  # 调试信息
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-type/<int:device_type_id>/details')
def get_device_type_details(device_type_id):
    """获取设备类型的详细信息（属性、方法、事件）"""
    try:
        with app.app_context():
            # 获取设备类型基本信息
            device_type = DeviceType.query.get(device_type_id)
            if not device_type:
                return jsonify({
                    'success': False,
                    'message': '设备类型不存在'
                }), 404
            
            # 获取属性、方法和事件
            properties = [p.to_dict() for p in device_type.properties]
            methods = [m.to_dict() for m in device_type.methods]
            events = [e.to_dict() for e in device_type.events]
            
            return jsonify({
                'success': True,
                'device_type': device_type.to_dict(),
                'properties': properties,
                'methods': methods,
                'events': events
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/device-type/by-name/<string:name>', methods=['GET'])
def get_device_type_by_name(name):
    """根据设备类型名称获取设备类型详细信息"""
    try:
        with app.app_context():
            # 获取设备类型基本信息
            device_type = DeviceType.query.filter_by(name=name).first()
            if not device_type:
                return jsonify({
                    'success': False,
                    'message': '设备类型不存在'
                }), 404
            
            # 获取属性、方法和事件
            properties = [p.to_dict() for p in device_type.properties]
            methods = [m.to_dict() for m in device_type.methods]
            events = [e.to_dict() for e in device_type.events]
            
            return jsonify({
                'success': True,
                'device_type': device_type.to_dict(),
                'properties': properties,
                'methods': methods,
                'events': events
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/device/<int:device_id>/property/<int:property_id>/modbus-binding', methods=['GET'])
def api_get_device_property_modbus_binding(device_id, property_id):
    """获取设备属性的Modbus绑定信息"""
    try:
        # 查询设备属性绑定
        binding = DevicePropertyBinding.query.filter_by(
            device_id=device_id,
            property_id=property_id
        ).first()
        
        if binding:
            return jsonify({
                'success': True,
                'data': binding.to_dict()
            })
        else:
            return jsonify({
                'success': True,
                'data': None
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 已删除所有与Excel相关的函数，现在使用数据库进行设备信息存储

@app.route('/predictive-maintenance')
def predictive_maintenance():
    return '<h1>预测性维护模块</h1><p>基于数据分析预测设备维护需求。</p>'

@app.route('/performance-analysis')
def performance_analysis():
    return '<h1>性能分析与优化模块</h1><p>分析系统性能并提供优化建议。</p>'


@app.route('/api/property-history', methods=['POST'])
def api_save_property_history():
    """保存设备属性历史数据"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        property_id = data.get('property_id')
        value = data.get('value')
        
        if not all([device_id, property_id, value is not None]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 创建历史记录
        history = PropertyHistory(
            device_id=device_id,
            property_id=property_id,
            value=str(value)
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '历史数据保存成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/property-history/<int:device_id>/<int:property_id>', methods=['GET'])
def api_get_property_history(device_id, property_id):
    """获取设备属性历史数据"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)
        
        # 查询历史数据
        histories = PropertyHistory.query.filter_by(
            device_id=device_id, 
            property_id=property_id
        ).order_by(PropertyHistory.timestamp.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'success': True,
            'data': [history.to_dict() for history in histories]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/event-history', methods=['POST'])
def api_save_event_history():
    """保存设备事件历史数据"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        event_id = data.get('event_id')
        status = data.get('status')
        
        if not all([device_id, event_id, status]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        # 创建历史记录
        history = EventHistory(
            device_id=device_id,
            event_id=event_id,
            status=status
        )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '事件历史数据保存成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/event-history/<int:device_id>/<int:event_id>', methods=['GET'])
def api_get_event_history(device_id, event_id):
    """获取设备事件历史数据"""
    try:
        # 获取查询参数
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)
        
        # 查询历史数据
        histories = EventHistory.query.filter_by(
            device_id=device_id, 
            event_id=event_id
        ).order_by(EventHistory.timestamp.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'success': True,
            'data': [history.to_dict() for history in histories]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 数据分析项目管理API
@app.route('/api/data-analysis-projects', methods=['GET'])
def api_get_data_analysis_projects():
    """获取所有数据分析项目"""
    try:
        projects = DataAnalysisProject.query.order_by(DataAnalysisProject.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [project.to_dict() for project in projects]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-projects', methods=['POST'])
def api_create_data_analysis_project():
    """创建数据分析项目"""
    try:
        data = request.get_json()
        
        project = DataAnalysisProject(
            name=data.get('name'),
            description=data.get('description'),
            analysis_type=data.get('analysis_type')
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '项目创建成功',
            'data': project.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-projects/<int:id>', methods=['GET'])
def api_get_data_analysis_project(id):
    """获取单个数据分析项目"""
    try:
        project = DataAnalysisProject.query.get(id)
        if not project:
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': project.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-projects/<int:id>', methods=['PUT'])
def api_update_data_analysis_project(id):
    """更新数据分析项目"""
    try:
        project = DataAnalysisProject.query.get(id)
        if not project:
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404
            
        data = request.get_json()
        project.name = data.get('name', project.name)
        project.description = data.get('description', project.description)
        project.analysis_type = data.get('analysis_type', project.analysis_type)
        # 新增字段
        if 'selected_points' in data:
            project.selected_points = data['selected_points']
        if 'analysis_instances' in data:
            project.analysis_instances = data['analysis_instances']
        if 'conclusion' in data:
            project.conclusion = data['conclusion']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '项目更新成功',
            'data': project.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-projects/<int:id>', methods=['DELETE'])
def api_delete_data_analysis_project(id):
    """删除数据分析项目"""
    try:
        project = DataAnalysisProject.query.get(id)
        if not project:
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404
            
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '项目删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# 数据分析结果API
@app.route('/api/data-analysis-results', methods=['POST'])
def api_create_data_analysis_result():
    """创建数据分析结果"""
    try:
        data = request.get_json()
        
        result = DataAnalysisResult(
            project_id=data.get('project_id'),
            name=data.get('name'),
            data_points=data.get('data_points', ''),
            chart_data=data.get('chart_data', ''),
            statistics=data.get('statistics', ''),
            analysis_result=data.get('analysis_result', '')
        )
        
        db.session.add(result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分析结果保存成功',
            'data': result.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-results/project/<int:project_id>', methods=['GET'])
def api_get_data_analysis_results(project_id):
    """获取项目的所有分析结果"""
    try:
        results = DataAnalysisResult.query.filter_by(project_id=project_id).order_by(DataAnalysisResult.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [result.to_dict() for result in results]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-results/<int:id>', methods=['GET'])
def api_get_data_analysis_result(id):
    """获取单个分析结果"""
    try:
        result = DataAnalysisResult.query.get(id)
        if not result:
            return jsonify({
                'success': False,
                'message': '分析结果不存在'
            }), 404
            
        return jsonify({
            'success': True,
            'data': result.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/data-analysis-results/<int:id>', methods=['DELETE'])
def api_delete_data_analysis_result(id):
    """删除分析结果"""
    try:
        result = DataAnalysisResult.query.get(id)
        if not result:
            return jsonify({
                'success': False,
                'message': '分析结果不存在'
            }), 404
            
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '分析结果删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/upload-excel', methods=['POST'])
def upload_excel():
    """处理Excel文件上传"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有文件被上传'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 检查文件类型
        if file and ('.xls' in file.filename or '.xlsx' in file.filename):
            # 生成唯一的文件名
            filename = f"{int(time.time())}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # 保存文件
            file.save(file_path)
            
            # 返回成功响应
            return jsonify({
                'success': True,
                'message': '文件上传成功',
                'filename': filename,
                'filepath': file_path
            })
        else:
            return jsonify({
                'success': False,
                'message': '只支持.xls和.xlsx格式的文件'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'文件上传失败: {str(e)}'
        }), 500


# 数据分析模块路由
@app.route('/data-analysis')
def data_analysis_list():
    """数据分析项目列表页面"""
    return render_template('data_analysis_list.html')


@app.route('/data-analysis/project/<int:project_id>')
def data_analysis_project(project_id):
    """具体的数据分析项目页面"""
    return render_template('data_analysis.html', project_id=project_id)


@app.route('/modbus-management')
def modbus_management():
    """Modbus点位管理页面"""
    return render_template('modbus_management.html')


@app.route('/device-property-binding')
def device_property_binding():
    """设备属性绑定管理页面"""
    device_id = request.args.get('device_id', type=int)
    if not device_id:
        return "缺少设备ID参数", 400
    
    # 获取设备信息
    device = Device.query.get(device_id)
    if not device:
        return "设备不存在", 404
    
    return render_template('device_property_binding.html', device=device)


# 添加全局变量来存储Modbus服务器实例
modbus_server_instance = None
modbus_server_thread = None


# 定义一个用于Modbus服务器的数据库会话函数
def modbus_db_session(get_config=False, save_config=None):
    """为Modbus服务器提供数据库会话的函数"""
    if get_config:
        # 获取配置
        return ServerConfig.query.all()
    elif save_config:
        # 保存配置
        config = ServerConfig.query.filter_by(key=save_config['key']).first()
        if config:
            config.value = save_config['value']
            config.updated_at = datetime.utcnow()
        else:
            config = ServerConfig(
                key=save_config['key'],
                value=save_config['value'],
                description='Modbus服务器更新间隔（秒）'
            )
            db.session.add(config)
        db.session.commit()
        return True
    else:
        # 获取激活的Modbus点位
        return ModbusPoint.query.filter_by(is_active=True).all()


# Modbus服务器API端点
@app.route('/api/modbus-server/status', methods=['GET'])
def api_modbus_server_status():
    """获取Modbus服务器状态"""
    try:
        global modbus_server_instance
        host = "localhost"
        port = 5020
        
        # 检查服务器是否在运行
        running = modbus_server_instance is not None and modbus_server_instance.running
        
        return jsonify({
            'success': True,
            'data': {
                'running': running,
                'host': host,
                'port': port
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/modbus-server/start', methods=['POST'])
def api_modbus_server_start():
    """启动Modbus服务器"""
    global modbus_server_instance, modbus_server_thread
    
    try:
        if modbus_server_instance is not None and modbus_server_instance.running:
            return jsonify({
                'success': False,
                'message': '服务器已在运行中'
            }), 400
        
        # 创建服务器实例，传递数据库会话函数
        modbus_server_instance = DatabaseModbusServer(modbus_db_session)
        
        # 在单独线程中启动服务器
        modbus_server_thread = threading.Thread(target=modbus_server_instance.start_server)
        modbus_server_thread.daemon = True
        modbus_server_thread.start()
        
        time.sleep(1)  # 等待服务器启动
        
        return jsonify({
            'success': True,
            'message': 'Modbus服务器启动成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'启动服务器失败: {str(e)}'
        }), 500


@app.route('/api/modbus-server/stop', methods=['POST'])
def api_modbus_server_stop():
    """停止Modbus服务器"""
    global modbus_server_instance, modbus_server_thread
    
    try:
        if modbus_server_instance is None or not modbus_server_instance.running:
            return jsonify({
                'success': False,
                'message': '服务器未在运行'
            }), 400
        
        # 停止服务器
        modbus_server_instance.stop_simulation()
        modbus_server_instance = None
        modbus_server_thread = None
        
        return jsonify({
            'success': True,
            'message': 'Modbus服务器已停止'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'停止服务器失败: {str(e)}'
        }), 500


@app.route('/api/modbus-server/update-interval', methods=['GET'])
def api_modbus_server_get_update_interval():
    """获取更新间隔"""
    try:
        interval = 2.0  # 默认值
        if modbus_server_instance:
            interval = modbus_server_instance.update_interval
        else:
            # 从数据库获取
            config = ServerConfig.query.filter_by(key='modbus_update_interval').first()
            if config:
                interval = float(config.value)
        
        return jsonify({
            'success': True,
            'data': {
                'interval': interval
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/modbus-server/update-interval', methods=['POST'])
def api_modbus_server_set_update_interval():
    """设置更新间隔"""
    try:
        data = request.get_json()
        interval = float(data.get('interval', 2.0))
        
        if interval <= 0:
            return jsonify({
                'success': False,
                'message': '更新间隔必须大于0'
            }), 400
        
        # 保存到数据库
        config = ServerConfig.query.filter_by(key='modbus_update_interval').first()
        if config:
            config.value = str(interval)
            config.updated_at = datetime.utcnow()
        else:
            config = ServerConfig(
                key='modbus_update_interval',
                value=str(interval),
                description='Modbus服务器更新间隔（秒）'
            )
            db.session.add(config)
        
        db.session.commit()
        
        # 如果服务器正在运行，更新其间隔
        if modbus_server_instance:
            modbus_server_instance.set_update_interval(interval)
        
        return jsonify({
            'success': True,
            'message': '更新间隔设置成功',
            'data': {
                'interval': interval
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# Modbus点位API端点
@app.route('/api/modbus-points', methods=['GET'])
def api_get_modbus_points():
    """获取所有Modbus点位"""
    try:
        points = ModbusPoint.query.all()
        return jsonify({
            'success': True,
            'data': [point.to_dict() for point in points]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/modbus-points/values', methods=['GET'])
def api_get_modbus_point_values():
    """获取所有Modbus点位的当前值"""
    try:
        global modbus_server_instance
        if modbus_server_instance is not None:
            values = modbus_server_instance.get_point_values()
            return jsonify({
                'success': True,
                'data': values
            })
        else:
            # 服务器未运行，返回空值
            points = ModbusPoint.query.all()
            values = {}
            for point in points:
                values[point.id] = {
                    'value': 'N/A',
                    'name': point.name
                }
            return jsonify({
                'success': True,
                'data': values
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/modbus-points', methods=['POST'])
def api_create_modbus_point():
    """创建Modbus点位"""
    try:
        data = request.get_json()
        
        point = ModbusPoint(
            name=data.get('name'),
            address=data.get('address'),
            data_type=data.get('data_type', 'float'),
            min_value=data.get('min_value', 0),
            max_value=data.get('max_value', 100),
            unit=data.get('unit', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(point)
        db.session.commit()
        
        # 如果服务器正在运行，重新加载点位
        if modbus_server_instance:
            # 传递数据库会话函数来重新加载点位
            modbus_server_instance.load_points_from_db()
        
        return jsonify({
            'success': True,
            'message': '点位创建成功',
            'data': point.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/modbus-points/<int:point_id>', methods=['PUT'])
def api_update_modbus_point(point_id):
    """更新Modbus点位"""
    try:
        point = ModbusPoint.query.get(point_id)
        if not point:
            return jsonify({
                'success': False,
                'message': '点位不存在'
            }), 404
        
        data = request.get_json()
        
        point.name = data.get('name', point.name)
        point.address = data.get('address', point.address)
        point.data_type = data.get('data_type', point.data_type)
        point.min_value = data.get('min_value', point.min_value)
        point.max_value = data.get('max_value', point.max_value)
        point.unit = data.get('unit', point.unit)
        point.description = data.get('description', point.description)
        point.is_active = data.get('is_active', point.is_active)
        point.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 如果服务器正在运行，重新加载点位
        if modbus_server_instance:
            # 传递数据库会话函数来重新加载点位
            modbus_server_instance.load_points_from_db()
        
        return jsonify({
            'success': True,
            'message': '点位更新成功',
            'data': point.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/modbus-points/<int:point_id>', methods=['DELETE'])
def api_delete_modbus_point(point_id):
    """删除Modbus点位"""
    try:
        point = ModbusPoint.query.get(point_id)
        if not point:
            return jsonify({
                'success': False,
                'message': '点位不存在'
            }), 404
        
        db.session.delete(point)
        db.session.commit()
        
        # 如果服务器正在运行，重新加载点位
        if modbus_server_instance:
            # 传递数据库会话函数来重新加载点位
            modbus_server_instance.load_points_from_db()
        
        return jsonify({
            'success': True,
            'message': '点位删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)

# 添加命令行命令用于更新数据库
@app.cli.command()
def update_db():
    """更新数据库结构"""
    import sqlite3
    
    # 连接到SQLite数据库
    conn = sqlite3.connect('device_models.db')
    cursor = conn.cursor()
    
    # 检查是否存在analysis_type列
    try:
        cursor.execute("SELECT analysis_type FROM data_analysis_projects LIMIT 1")
        print("数据库已包含 analysis_type 字段")
    except sqlite3.OperationalError as e:
        if "no such column" in str(e):
            print("添加 analysis_type 字段到 data_analysis_projects 表")
            try:
                cursor.execute("ALTER TABLE data_analysis_projects ADD COLUMN analysis_type VARCHAR(50)")
                conn.commit()
                print("成功添加 analysis_type 字段")
            except Exception as e:
                print(f"添加字段时出错: {e}")
        else:
            print(f"检查字段时出错: {e}")
    
    # 清除所有旧的数据分析项目
    try:
        cursor.execute("DELETE FROM data_analysis_projects")
        conn.commit()
        print("已清除所有旧的数据分析项目")
    except Exception as e:
        print(f"清除旧数据时出错: {e}")
    
    conn.close()
    print("数据库更新完成")
