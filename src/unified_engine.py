import os
import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import traceback

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_output_from_query(df: pd.DataFrame, user_query: str):
    """
    Unified function to return either a table or chart based on user query.
    Returns:
        dict: {
            "type": "table" | "chart" | "error",
            "data": pd.DataFrame | chart_path | error message
        }
    """
    column_list = ", ".join([f'"{col}"' for col in df.columns])
    chart_path = os.path.join("streamlit_app", "temp_charts", f"chart_{uuid.uuid4().hex}.png")

    # Build prompt
    prompt = f"""
You are a Python data analytics assistant.

Given a DataFrame `df` with columns: {column_list}, answer the following query:
"{user_query}"

Rules:
- If it's about summarizing, filtering, counting, sorting, aggregating, output a DataFrame named `result_df`.
- If it asks to plot/visualize/chart, use matplotlib or seaborn and save the figure to `chart_path`. Do not use plt.show().
- Do not print anything.
- Never return markdown. Just valid Python code.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're a Python expert who works with pandas, matplotlib, seaborn."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        code = response.choices[0].message.content.strip()
        if code.startswith("```"):
            code = code.strip("```").replace("python", "").strip()

        # Debug: print the generated code to terminal
        print("\n=== Generated Code ===")
        print(code)
        print("======================\n")

        # Setup environment
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        exec_env = {
            "df": df.copy(),
            "pd": pd,
            "plt": plt,
            "sns": sns,
            "chart_path": chart_path,
        }

        exec(code, {}, exec_env)

        # Return table
        if "result_df" in exec_env and isinstance(exec_env["result_df"], pd.DataFrame):
            return {"type": "table", "data": exec_env["result_df"]}

        # Return chart
        elif os.path.exists(chart_path):
            return {"type": "chart", "data": chart_path}

        return {"type": "error", "data": "⚠️ Code executed but no result_df or chart_path was found."}

    except Exception as e:
        return {
            "type": "error",
            "data": f"❌ Execution failed: {e}\n\n{traceback.format_exc()}"
        }
