import os
import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid

from io import BytesIO

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_chart_from_query(df: pd.DataFrame, user_query: str):
    """
    Generates a chart based on a user's natural language query using the same LLM pipeline
    as generate_code_from_query for consistent accuracy.
    """

    # -----------------------
    # 1. Prepare the prompt
    # -----------------------
    columns_list = ", ".join(df.columns)
    prompt = f"""
    You are a Python data visualization assistant. 
    Given a pandas DataFrame called df with these columns: {columns_list},
    write Python code using matplotlib or seaborn to create a chart based on this request: "{user_query}".

    Requirements:
    - Do NOT print any data.
    - Use the columns EXACTLY as provided, matching their names and case.
    - Automatically infer chart type (bar, line, scatter, histogram, pie, etc.) from the query.
    - Save the chart as a PNG file.
    - The chart should be saved with a unique filename.
    - Do NOT show() the plot.
    ""

    # -----------------------
    # 2. Ask the LLM
    # -----------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python visualization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        code = response.choices[0].message.content.strip()

        # Clean code block markers if present
        if code.startswith("```"):
            code = code.strip("```").replace("python", "").strip()

    except Exception as e:
        print(f"LLM request failed: {e}")
        return None

    # -----------------------
    # 3. Execute the code
    # -----------------------
    try:
        # Set up a unique file path for the chart
        chart_id = f"chart_{uuid.uuid4().hex}.png"
        chart_path = os.path.join("streamlit_app", "temp_charts", chart_id)
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)

        # Local environment with df and chart_path
        local_env = {"df": df, "plt": plt, "sns": sns, "pd": pd, "chart_path": chart_path}

        # Inject savefig if not explicitly handled
        code += f"\nplt.savefig(r'{chart_path}')\nplt.close()"

        exec(code, {}, local_env)

        return chart_path

    except Exception as e:
        print(f"Chart generation failed: {e}")
        return None
