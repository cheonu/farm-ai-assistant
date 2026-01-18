from datetime import datetime
from typing import Dict, List

class TestClass:
    def __init__(self):
        self.test_property = "hello"
        self.test_list = [1, 2, 3]
    
    def test_method(self):
        # Try typing "self." here - you should see test_property and test_list
        # Try typing "datetime." here - you should see now(), fromisoformat(), etc.
        pass

# Test it here:
test = TestClass()
# Type "test." here - you should see test_property, test_list, test_method