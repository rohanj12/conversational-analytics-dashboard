# test_llm.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file containing your API key and (optionally) org ID
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")  # Include only if you have org-based billing
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Use this temporarily to avoid quota errors
    messages=[
        {"role": "user", "content": "Write Python code to calculate the average of a list of numbers"}
    ],
    temperature=0.2,
)

print("✅ API working. Response:")
print(response.choices[0].message.content)
