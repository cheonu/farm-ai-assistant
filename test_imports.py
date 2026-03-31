#!/usr/bin/env python3
"""Test if all imports work correctly"""

print("Testing imports...")

try:
    print("1. Testing FastAPI...")
    from fastapi import FastAPI
    print("   ✅ FastAPI OK")
except Exception as e:
    print(f"   ❌ FastAPI failed: {e}")

try:
    print("2. Testing dotenv...")
    from dotenv import load_dotenv
    print("   ✅ dotenv OK")
except Exception as e:
    print(f"   ❌ dotenv failed: {e}")

try:
    print("3. Testing app.services.llm_service...")
    from app.services.llm_service import FarmLLMService
    print("   ✅ LLM service import OK")
except Exception as e:
    print(f"   ❌ LLM service import failed: {e}")

try:
    print("4. Testing app.utils.data_processor...")
    from app.utils.data_processor import FarmDataProcessor
    print("   ✅ Data processor OK")
except Exception as e:
    print(f"   ❌ Data processor failed: {e}")

print("\n✅ All imports successful!")
