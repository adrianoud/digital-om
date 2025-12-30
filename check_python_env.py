import sys
print("Python版本:", sys.version)
print("Python路径:", sys.executable)

try:
    import volcengine
    print("成功导入volcengine模块")
    # print("volcengine版本:", volcengine.__version__)
except ImportError as e:
    print("无法导入volcengine:", e)

try:
    from volcengine.ark.runtime.v1 import ArkRuntimeClient
    print("成功导入ArkRuntimeClient")
except ImportError as e:
    print("无法导入ArkRuntimeClient:", e)
    
try:
    from volcengine.ark.runtime.v1 import Message
    print("成功导入Message")
except ImportError as e:
    print("无法导入Message:", e)
    
try:
    from volcengine.ark.runtime.v1 import ChatCompletionRequest
    print("成功导入ChatCompletionRequest")
except ImportError as e:
    print("无法导入ChatCompletionRequest:", e)