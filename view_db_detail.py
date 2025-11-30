from app import app, db
from models import Device, DevicePropertyBinding, ModbusPoint

def view_database_details():
    with app.app_context():
        print("=== Devices ===")
        devices = Device.query.all()
        for device in devices:
            print(f"ID: {device.id}, Name: {device.name}, Code: {device.code}, Type: {device.type}")
        
        print("\n=== Device Property Bindings ===")
        bindings = DevicePropertyBinding.query.all()
        for binding in bindings:
            print(f"Binding ID: {binding.id}, Device ID: {binding.device_id}, Property ID: {binding.property_id}, Modbus Point ID: {binding.modbus_point_id}")
        
        print("\n=== Modbus Points ===")
        points = ModbusPoint.query.all()
        for point in points:
            print(f"ID: {point.id}, Name: {point.name}, Address: {point.address}, Data Type: {point.data_type}, Min: {point.min_value}, Max: {point.max_value}, Unit: {point.unit}")

if __name__ == "__main__":
    view_database_details()