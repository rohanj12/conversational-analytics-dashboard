import openai
import os

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_code_from_query(user_query, df):
    """
    Converts a natural language query into working pandas code.
    Ensures result is in `result_df` and filters properly.
    """

    # Gather column info
    column_names = df.columns.tolist()
    column_examples = {
        col: df[col].dropna().astype(str).unique()[:5].tolist()
        for col in df.select_dtypes(include=["object", "category"])
    }

    prompt = f"""
You are a senior data analyst using Python and pandas.
Your goal is to write clean, correct Python code using pandas that fulfills the following user request.

📌 DataFrame is named `df`.
📌 Do NOT lowercase or transform the full DataFrame.
📌 Only apply `.str.lower()` on string **comparison** values (for case-insensitive filters).
📌 Only output valid pandas code. NO explanation, print statements, or markdown formatting.
📌 Store the final result in a new DataFrame called `result_df`.

---

**Available Columns**:
{column_names}

**Sample Values**:
{column_examples}

---

User Query:
{user_query}

Again, just return Python code, no commentary. The result should always be assigned to `result_df`.
If unsure, return `result_df = df.head(10)`
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        code = response.choices[0].message.content.strip()

        # Clean up any formatting
        if code.startswith("```"):
            code = code.strip("`").replace("python", "").strip()

        return code

    except Exception as e:
        return f"# Failed to generate code: {e}"
