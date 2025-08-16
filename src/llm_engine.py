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

def generate_code_from_query(user_query, dataframe_columns):
    prompt = f"""
You are an intelligent data assistant. 
Given the following dataframe columns: {', '.join(dataframe_columns)},
generate clean, executable pandas code to answer this question: "{user_query}"

Always store the final result in a DataFrame called `result_df`.
Only return the code, no explanations.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content

    