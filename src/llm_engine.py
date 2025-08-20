# src/llm_engine.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_code_from_query(query, columns):
    prompt = f"""
You are a Python data analyst. Write a single line of pandas code that answers the question:
'{query}'
Only use these columns: {', '.join(columns)}.
Always assign your output to a variable named result_df.

Only return the code, without explanation, markdown, or comments.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    code = response.choices[0].message.content.strip()

    if code.startswith("```"):
        code = code.strip("```").replace("python", "").strip()

    # Ensure output is assigned to result_df
    if "result_df" not in code:
        code = f"result_df = {code}"

    return code

    
