"""
Test script for Hugging Face API integration.
Run with: python test_huggingface.py
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_huggingface_api():
    """Test the Hugging Face API connection."""
    
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    api_url = os.getenv("HUGGINGFACE_API_URL", "https://router.huggingface.co/v1/chat/completions")
    model = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY not found in .env file")
        return
    
    print(f"🔧 Testing Hugging Face API...")
    print(f"   URL: {api_url}")
    print(f"   Model: {model}")
    print(f"   API Key: {api_key[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Generate 2 simple interview questions for a Python developer. Respond in JSON format as an array of objects with 'question_text' and 'category' fields."}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                print(f"\n📡 Response Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"\n✅ Success! API Response:\n")
                    print(content)
                else:
                    error_text = await response.text()
                    print(f"\n❌ Error: {error_text}")
                    
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_huggingface_api())
