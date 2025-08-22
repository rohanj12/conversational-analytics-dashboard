# src/llm_engine.py

import openai
import os

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_code_from_query(user_query, column_names):
    """
    Generate robust pandas code from a natural language query on a DataFrame `df`.
    The function returns code that defines a new variable `result_df` as the result.
    """

    column_list = ", ".join([f'"{col}"' for col in column_names])

    prompt = f"""
You are a senior Python data analyst. Convert the following user query into working pandas code that operates on a DataFrame named `df`. The goal is to generate a new DataFrame called `result_df`.

Only return code – no explanations or markdown. Make sure of the following:

1. Column names in the dataset are: [{column_list}]
2. Be tolerant to case mismatches in both column values and query.
3. If filtering for values (e.g., "where vehicle is ebike"), use `.str.lower() == 'value'` logic for comparison.
4. If querying or grouping by a column mentioned indirectly (like "average trips by user type"), map natural phrases to real column names.
5. Avoid printing or displaying anything. Only define `result_df`.
6. If the query asks for multiple steps (e.g., filter then group), chain them logically in one statement or break them in 2 lines.
7. If nothing is returned from query intent, return a slice of the dataframe: `result_df = df.head(10)`

User query: **{user_query}**
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            temperature=0
        )

        code = response.choices[0].message.content.strip()

        # Remove markdown backticks if included
        if code.startswith("```"):
            code = code.strip("`").replace("python", "").strip()

        return code

    except Exception as e:
        return f"# Failed to generate code: {e}"
