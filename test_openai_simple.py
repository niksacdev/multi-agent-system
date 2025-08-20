#!/usr/bin/env python3
"""
Simple test to check OpenAI API connectivity and quota.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_api():
    """Test basic OpenAI API connectivity."""
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    print(f"🔑 API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        # Create OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Test simple completion
        print("🧪 Testing simple chat completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, world!' and nothing else."}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        
        # Test model listing (to check quota/permissions)
        print("🧪 Testing model listing...")
        models = client.models.list()
        available_models = [model.id for model in models.data if model.id.startswith("gpt")]
        print(f"✅ Available GPT models: {available_models[:5]}...")  # Show first 5
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check for specific error types
        if "insufficient_quota" in str(e):
            print("   💡 Issue: API quota exceeded - need to add billing/credits")
        elif "invalid_api_key" in str(e):
            print("   💡 Issue: Invalid API key")
        elif "model_not_found" in str(e):
            print("   💡 Issue: Model not accessible with this key")
        elif "rate_limit" in str(e):
            print("   💡 Issue: Rate limit hit - try again in a moment")
        else:
            print("   💡 Issue: Unknown error - check OpenAI status")
        
        return False

if __name__ == "__main__":
    print("🚀 Testing OpenAI API connectivity...")
    success = test_openai_api()
    
    if success:
        print("\n🎉 OpenAI API is working correctly!")
    else:
        print("\n💥 OpenAI API test failed!")
        print("   Check your API key and billing status at: https://platform.openai.com/")