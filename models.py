from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class DeviceType(db.Model):
    """设备类型模型"""
    __tablename__ = 'device_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # 设备类型名称
    description = db.Column(db.Text)  # 设备类型描述
    image_path = db.Column(db.String(255))  # 设备类型图片路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联的属性、事件和方法
    properties = db.relationship('DeviceProperty', backref='device_type', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('DeviceEvent', backref='device_type', lazy=True, cascade='all, delete-orphan')
    methods = db.relationship('DeviceMethod', backref='device_type', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<DeviceType {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DeviceProperty(db.Model):
    """设备属性模型"""
    __tablename__ = 'device_properties'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 属性名称
    identifier = db.Column(db.String(100), nullable=False)  # 属性标识符
    data_type = db.Column(db.String(50), nullable=False)  # 数据类型 (int, float, string, bool等)
    unit = db.Column(db.String(50))  # 单位
    description = db.Column(db.Text)  # 描述
    read_write_flag = db.Column(db.String(10), default='rw')  # 读写标志 (r:只读, w:只写, rw:读写)
    min_value = db.Column(db.Float)  # 最小值
    max_value = db.Column(db.Float)  # 最大值
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeviceProperty {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'identifier': self.identifier,
            'data_type': self.data_type,
            'unit': self.unit,
            'description': self.description,
            'read_write_flag': self.read_write_flag,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'device_type_id': self.device_type_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DeviceEvent(db.Model):
    """设备事件模型"""
    __tablename__ = 'device_events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 事件名称
    identifier = db.Column(db.String(100), nullable=False)  # 事件标识符
    description = db.Column(db.Text)  # 描述
    level = db.Column(db.String(20), default='info')  # 事件级别 (info, warning, error等)
    condition = db.Column(db.Text)  # 触发条件表达式
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeviceEvent {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'identifier': self.identifier,
            'description': self.description,
            'level': self.level,
            'condition': self.condition,
            'device_type_id': self.device_type_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DeviceMethod(db.Model):
    """设备方法模型"""
    __tablename__ = 'device_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 方法名称
    identifier = db.Column(db.String(100), nullable=False)  # 方法标识符
    description = db.Column(db.Text)  # 描述
    input_params = db.Column(db.Text)  # 输入参数 (JSON格式)
    output_params = db.Column(db.Text)  # 输出参数 (JSON格式)
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeviceMethod {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'identifier': self.identifier,
            'description': self.description,
            'input_params': self.input_params,
            'output_params': self.output_params,
            'device_type_id': self.device_type_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Device(db.Model):
    """设备模型"""
    __tablename__ = 'devices'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 设备名称
    code = db.Column(db.String(100), nullable=False, unique=True)  # 设备编码
    type = db.Column(db.String(100), nullable=False)  # 设备类型
    model = db.Column(db.String(100))  # 设备型号
    purchase_date = db.Column(db.Date)  # 采购日期
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)  # 录入时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Device {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'type': self.type,
            'model': self.model,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ModbusPoint(db.Model):
    """Modbus点位模型"""
    __tablename__ = 'modbus_points'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 点位名称
    address = db.Column(db.Integer, nullable=False)  # 寄存器地址
    data_type = db.Column(db.String(50), nullable=False, default='float')  # 数据类型
    min_value = db.Column(db.Float, nullable=False, default=0.0)  # 最小值
    max_value = db.Column(db.Float, nullable=False, default=100.0)  # 最大值
    unit = db.Column(db.String(50))  # 单位
    description = db.Column(db.Text)  # 描述
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ModbusPoint {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'data_type': self.data_type,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'unit': self.unit,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DevicePropertyBinding(db.Model):
    """设备属性与Modbus寄存器绑定模型"""
    __tablename__ = 'device_property_bindings'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)  # 设备ID
    property_id = db.Column(db.Integer, db.ForeignKey('device_properties.id'), nullable=False)  # 属性ID（来自设备类型）
    modbus_point_id = db.Column(db.Integer, db.ForeignKey('modbus_points.id'), nullable=True)  # 绑定的Modbus点位ID
    calculation_expression = db.Column(db.Text, nullable=True)  # 计算表达式，用于通过其他属性计算得出值
    
    # 关系
    device = db.relationship('Device', backref='property_bindings')
    property = db.relationship('DeviceProperty', backref='device_bindings')
    modbus_point = db.relationship('ModbusPoint', backref='property_bindings')
    
    def __repr__(self):
        return f'<DevicePropertyBinding Device:{self.device_id} Property:{self.property_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'property_id': self.property_id,
            'modbus_point_id': self.modbus_point_id,
            'calculation_expression': self.calculation_expression
        }


class ServerConfig(db.Model):
    """服务器配置模型"""
    __tablename__ = 'server_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)  # 配置键
    value = db.Column(db.String(255), nullable=False)  # 配置值
    description = db.Column(db.Text)  # 描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ServerConfig {self.key}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PropertyHistory(db.Model):
    """设备属性历史数据模型"""
    __tablename__ = 'property_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)  # 设备ID
    property_id = db.Column(db.Integer, db.ForeignKey('device_properties.id'), nullable=False, index=True)  # 属性ID
    value = db.Column(db.String(100), nullable=False)  # 属性值
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)  # 时间戳
    
    # 关系
    device = db.relationship('Device', backref='property_histories')
    property = db.relationship('DeviceProperty', backref='histories')
    
    def __repr__(self):
        return f'<PropertyHistory Device:{self.device_id} Property:{self.property_id} Value:{self.value}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'property_id': self.property_id,
            'value': self.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class EventHistory(db.Model):
    """设备事件历史数据模型"""
    __tablename__ = 'event_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False, index=True)  # 设备ID
    event_id = db.Column(db.Integer, db.ForeignKey('device_events.id'), nullable=False, index=True)  # 事件ID
    status = db.Column(db.String(50), nullable=False)  # 事件状态
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)  # 时间戳
    
    # 关系
    device = db.relationship('Device', backref='event_histories')
    event = db.relationship('DeviceEvent', backref='histories')
    
    def __repr__(self):
        return f'<EventHistory Device:{self.device_id} Event:{self.event_id} Status:{self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'event_id': self.event_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class DataAnalysisProject(db.Model):
    """数据分析项目模型"""
    __tablename__ = 'data_analysis_projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 项目名称
    description = db.Column(db.Text)  # 项目描述
    # 为了向后兼容，设置默认值和可为空
    analysis_type = db.Column(db.String(50), nullable=True)  # 分析类型 (descriptive, diagnostic, predictive, prescriptive)
    selected_points = db.Column(db.Text, nullable=True)  # 选中的数据点信息 (JSON格式)
    analysis_instances = db.Column(db.Text, nullable=True)  # 分析实例信息 (JSON格式)
    conclusion = db.Column(db.Text, nullable=True)  # 结论说明
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)  # 更新时间
    
    def __repr__(self):
        return f'<DataAnalysisProject {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'analysis_type': self.analysis_type if self.analysis_type is not None else '',
            'selected_points': self.selected_points,
            'analysis_instances': self.analysis_instances,
            'conclusion': self.conclusion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DataAnalysisResult(db.Model):
    """数据分析结果模型"""
    __tablename__ = 'data_analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('data_analysis_projects.id'), nullable=False)  # 项目ID
    name = db.Column(db.String(200), nullable=False)  # 结果名称
    data_points = db.Column(db.Text, nullable=False)  # 数据点信息 (JSON格式)
    chart_data = db.Column(db.Text, nullable=True)  # 图表数据 (JSON格式)
    statistics = db.Column(db.Text, nullable=True)  # 统计数据 (JSON格式)
    analysis_result = db.Column(db.Text, nullable=True)  # 分析结果描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # 创建时间
    
    # 关系
    project = db.relationship('DataAnalysisProject', backref='analysis_results')
    
    def __repr__(self):
        return f'<DataAnalysisResult {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'data_points': self.data_points,
            'chart_data': self.chart_data,
            'statistics': self.statistics,
            'analysis_result': self.analysis_result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DecisionTreeNode(db.Model):
    """决策树节点模型"""
    __tablename__ = 'decision_tree_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    tree_id = db.Column(db.Integer, db.ForeignKey('decision_trees.id'), nullable=False)  # 所属决策树ID
    parent_id = db.Column(db.Integer, db.ForeignKey('decision_tree_nodes.id'), nullable=True)  # 父节点ID
    name = db.Column(db.String(200), nullable=False)  # 节点名称
    node_type = db.Column(db.String(20), nullable=False)  # 节点类型: root(根节点), decision(决策节点), leaf(叶子节点)
    condition = db.Column(db.Text, nullable=True)  # 判定条件（仅决策节点使用）
    result = db.Column(db.Text, nullable=True)  # 节点结果（仅叶子节点使用）
    decision_input = db.Column(db.Text, nullable=True)  # 待决策内容（仅根节点使用）
    yes_child_id = db.Column(db.Integer, db.ForeignKey('decision_tree_nodes.id'), nullable=True)  # 是分支子节点ID
    no_child_id = db.Column(db.Integer, db.ForeignKey('decision_tree_nodes.id'), nullable=True)  # 否分支子节点ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    tree = db.relationship('DecisionTree', backref='nodes')
    parent = db.relationship('DecisionTreeNode', remote_side=[id], backref='children', foreign_keys=[parent_id])
    yes_child = db.relationship('DecisionTreeNode', foreign_keys=[yes_child_id])
    no_child = db.relationship('DecisionTreeNode', foreign_keys=[no_child_id])
    
    def __repr__(self):
        return f'<DecisionTreeNode {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tree_id': self.tree_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'node_type': self.node_type,
            'condition': self.condition,
            'result': self.result,
            'decision_input': self.decision_input,
            'yes_child_id': self.yes_child_id,
            'no_child_id': self.no_child_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DecisionTree(db.Model):
    """决策树模型"""
    __tablename__ = 'decision_trees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 决策树名称
    description = db.Column(db.Text, nullable=True)  # 描述
    device_type_id = db.Column(db.Integer, db.ForeignKey('device_types.id'), nullable=True)  # 关联的设备类型ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    device_type = db.relationship('DeviceType', backref='decision_trees')
    
    def __repr__(self):
        return f'<DecisionTree {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'device_type_id': self.device_type_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class KnowledgeGraph(db.Model):
    """知识图谱模型"""
    __tablename__ = 'knowledge_graphs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 知识图谱名称
    description = db.Column(db.Text, nullable=True)  # 描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<KnowledgeGraph {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class KnowledgeGraphNode(db.Model):
    """知识图谱节点模型"""
    __tablename__ = 'knowledge_graph_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    graph_id = db.Column(db.Integer, db.ForeignKey('knowledge_graphs.id'), nullable=False)  # 所属知识图谱ID
    name = db.Column(db.String(200), nullable=False)  # 节点名称
    node_type = db.Column(db.String(50), nullable=False)  # 节点类型
    properties = db.Column(db.Text, nullable=True)  # 节点属性（JSON格式）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    graph = db.relationship('KnowledgeGraph', backref='nodes')
    
    def __repr__(self):
        return f'<KnowledgeGraphNode {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'graph_id': self.graph_id,
            'name': self.name,
            'node_type': self.node_type,
            'properties': self.properties,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class KnowledgeGraphEdge(db.Model):
    """知识图谱边模型"""
    __tablename__ = 'knowledge_graph_edges'
    
    id = db.Column(db.Integer, primary_key=True)
    graph_id = db.Column(db.Integer, db.ForeignKey('knowledge_graphs.id'), nullable=False)  # 所属知识图谱ID
    from_node_id = db.Column(db.Integer, db.ForeignKey('knowledge_graph_nodes.id'), nullable=False)  # 起始节点ID
    to_node_id = db.Column(db.Integer, db.ForeignKey('knowledge_graph_nodes.id'), nullable=False)  # 目标节点ID
    relation_type = db.Column(db.String(100), nullable=False)  # 关系类型
    properties = db.Column(db.Text, nullable=True)  # 边属性（JSON格式）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    graph = db.relationship('KnowledgeGraph', backref='edges')
    from_node = db.relationship('KnowledgeGraphNode', foreign_keys=[from_node_id])
    to_node = db.relationship('KnowledgeGraphNode', foreign_keys=[to_node_id])
    
    def __repr__(self):
        return f'<KnowledgeGraphEdge {self.relation_type}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'graph_id': self.graph_id,
            'from_node_id': self.from_node_id,
            'to_node_id': self.to_node_id,
            'relation_type': self.relation_type,
            'properties': self.properties,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }