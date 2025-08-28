import os
import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import re

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_generated_code(code: str) -> str:
    """
    Cleans up code returned by the LLM:
    - Removes markdown fences, 'python' tags, and stray quotes.
    - Ensures consistent indentation.
    """
    # Remove triple backticks and language hints
    code = re.sub(r"^```[a-zA-Z]*", "", code)
    code = re.sub(r"```$", "", code)
    return code.strip()

def generate_output_from_query(df: pd.DataFrame, user_query: str):
    """
    Unified LLM-powered function to handle both table and chart generation based on natural language queries.
    """
    columns_list = ", ".join(df.columns)

    # Detect if the query is about charts (chart mode)
    chart_keywords = ["plot", "chart", "graph", "histogram", "distribution", 
                      "bar", "line", "trend", "scatter", "visualize", "pie"]
    is_chart_query = any(keyword in user_query.lower() for keyword in chart_keywords)

    # --------------------------
    # 1. Build the prompt
    # --------------------------
    base_rules = """
    You are a Python data analytics and visualization assistant.
    Given a pandas DataFrame called df, write **clean and minimal Python code** to answer the following user query.

    Rules:
    - Use ONLY columns exactly as they appear: {columns_list}.
    - For table queries → create a DataFrame called `result_df`.
    - For chart queries → use matplotlib/seaborn, save to `chart_path`, **DO NOT** call plt.show().
    - Do not print anything or add extra explanations.
    - Do not return markdown code blocks.
    """

    prompt = base_rules.format(columns_list=columns_list) + f'\n\nUser query: "{user_query}"\n'

    # --------------------------
    # 2. Get Python code from OpenAI
    # --------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python data analytics and visualization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        code = clean_generated_code(response.choices[0].message.content)

    except Exception as e:
        return {"type": "error", "data": f"OpenAI request failed: {e}"}

    # --------------------------
    # 3. Execute the generated code safely
    # --------------------------
    try:
        chart_id = f"chart_{uuid.uuid4().hex}.png"
        chart_path = os.path.join("streamlit_app", "temp_charts", chart_id)
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)

        # Prepare execution environment
        local_env = {
            "df": df.copy(),
            "pd": pd,
            "plt": plt,
            "sns": sns,
            "chart_path": chart_path
        }

        # Debugging: log generated code
        print("\n🔹 Generated Code:\n", code, "\n")

        # Execute code securely
        exec(code, {}, local_env)

        # If table output exists
        if "result_df" in local_env and isinstance(local_env["result_df"], pd.DataFrame):
            return {"type": "table", "data": local_env["result_df"]}

        # If chart exists
        if os.path.exists(chart_path):
            return {"type": "chart", "data": chart_path}

        # If nothing returned
        return {"type": "error", "data": "No valid output generated from the query."}

    except Exception as e:
        return {"type": "error", "data": f"Execution failed: {e}"}
