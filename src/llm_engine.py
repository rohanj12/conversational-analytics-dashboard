import openai
import os

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_code_from_query(user_query, df):
    """
    Convert a natural language query into executable pandas code on DataFrame `df`,
    returning a new DataFrame named `result_df`.
    """

    column_names = df.columns.tolist()
    column_values_map = {
        col: df[col].dropna().astype(str).unique()[:10].tolist()  # preview up to 10 values per column
        for col in column_names if df[col].dtype == 'object' or df[col].dtype.name == 'category'
    }

    col_list = ", ".join([f'"{col}"' for col in column_names])
    val_list = "\n".join([f"{col}: {values}" for col, values in column_values_map.items()])

    prompt = f"""
You are a senior Python data analyst. Write working pandas code that performs the following user query on a DataFrame named `df`.

⚠️ Important Notes:
- The column names are: {col_list}
- Example values in these columns:
{val_list}
- Ensure comparisons are case-insensitive (use `.str.lower()`).
- Only return Python code. Do not print or explain anything.
- Your result must be stored in a DataFrame called `result_df`.
- If unsure, return `result_df = df.head(10)`

User query: {user_query}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        code = response.choices[0].message.content.strip()

        # Clean up markdown
        if code.startswith("```"):
            code = code.strip("`").replace("python", "").strip()

        return code

    except Exception as e:
        return f"# Failed to generate code: {e}"
