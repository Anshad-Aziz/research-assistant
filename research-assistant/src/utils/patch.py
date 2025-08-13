import os
import sys
import platform

# Only patch on Windows
if platform.system() == "Windows":
    # Create a mock pwd module
    class MockPwd:
        def getpwuid(self, uid):
            """Mock implementation of getpwuid for Windows."""
            class MockStruct:
                def __init__(self):
                    try:
                        self.pw_name = os.getlogin()
                    except:
                        self.pw_name = "unknown"
                    self.pw_dir = os.path.expanduser('~')
                    self.pw_shell = "cmd.exe"
            return MockStruct()
        
        def getpwall(self):
            """Mock implementation of getpwall for Windows."""
            return [self.getpwuid(0)]
    
    # Replace the pwd module with our mock
    sys.modules['pwd'] = MockPwd()