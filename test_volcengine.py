#!/usr/bin/env python3
"""
测试火山引擎SDK是否正常工作
"""

def test_volcengine_sdk():
    try:
        # 尝试导入火山引擎SDK的核心模块
        from volcengine.ark.runtime.v1 import ArkRuntimeClient, ChatCompletionRequest, Message
        print("成功导入火山引擎SDK")
        
        # 尝试创建客户端
        client = ArkRuntimeClient(region="cn-beijing")
        print("成功创建ArkRuntimeClient客户端")
        
        # 尝试创建消息对象
        message = Message(role="user", content="你好")
        print("成功创建Message对象")
        
        # 尝试创建请求对象
        request = ChatCompletionRequest(
            model="doubao-seed-1-8-251215",
            messages=[message],
            temperature=0.7,
            max_tokens=100
        )
        print("成功创建ChatCompletionRequest对象")
        
        print("火山引擎SDK测试通过，可以正常使用")
        return True
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("火山引擎SDK导入失败")
        return False
    except Exception as e:
        print(f"其他错误: {e}")
        print("火山引擎SDK测试失败")
        return False

if __name__ == "__main__":
    test_volcengine_sdk()