import google.generativeai as genai
import os

# 1. Setup
# (We will ask for your key securely in the terminal)
api_key = input("Paste your API Key here: ")
genai.configure(api_key=api_key)

print("\n🔍 Checking available models...\n")

# 2. List them
try:
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")
