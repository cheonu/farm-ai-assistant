"""
Quick test to verify the Farm AI Assistant API is working
"""
import sys
from datetime import datetime

# Test imports
try:
    from app.main import app
    from app.services.llm_service import FarmLLMService
    from app.utils.data_processor import FarmDataProcessor
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test data processor
try:
    processor = FarmDataProcessor()
    test_data = {
        "pigs": [
            {
                "tagNumber": "PIG-001",
                "gender": "Sow",
                "crossedDate": "2024-01-01",
                "expectedDeliveryDate": "2024-04-25"
            },
            {
                "tagNumber": "PIG-002",
                "gender": "Boar"
            }
        ]
    }
    
    result = processor.process_farm_data(test_data)
    assert "summary" in result
    assert "breeding_status" in result
    assert "health_status" in result
    assert "alerts" in result
    assert result["summary"]["total"] == 2
    print("✓ Data processor working correctly")
except Exception as e:
    print(f"✗ Data processor error: {e}")
    sys.exit(1)

# Test LLM service initialization
try:
    llm_service = FarmLLMService()
    print("✓ LLM service initialized successfully")
except Exception as e:
    print(f"✗ LLM service error: {e}")
    sys.exit(1)

# Test validation
try:
    validation = processor.validate_pig_data({
        "tagNumber": "PIG-003",
        "gender": "Sow"
    })
    assert validation["is_valid"] == True
    print("✓ Validation working correctly")
except Exception as e:
    print(f"✗ Validation error: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("🎉 All tests passed! Your Farm AI Assistant is ready!")
print("="*50)
print("\nTo start the server, run:")
print("  uvicorn app.main:app --reload")
print("\nOr:")
print("  python3 -m uvicorn app.main:app --reload")
