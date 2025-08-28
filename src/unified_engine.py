import os
import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_output_from_query(df: pd.DataFrame, user_query: str):
    """
    Unified LLM-powered function to handle both table and chart generation based on natural language queries.
    Decides automatically whether to:
      1. Generate a DataFrame output (table)
      2. Generate a chart (PNG) with matplotlib/seaborn

    Returns:
        dict: {
            "type": "table" | "chart" | "error",
            "data": pd.DataFrame | chart_path | str
        }
    """
    columns_list = ", ".join(df.columns)

    # --------------------------------
    # 1. Build the dynamic prompt
    # --------------------------------
    prompt = f"""
    You are a Python data analytics and visualization assistant.
    Given a pandas DataFrame called df with columns: {columns_list},
    write Python code to answer the following user query:

    "{user_query}"

    Rules:
    - If the query suggests filtering, grouping, or summarizing data → return a DataFrame.
    - If the query suggests plotting, visualizing, histogram, chart, bar, scatter, pie, line, trend, or similar → generate a matplotlib/seaborn chart.
    - Match column names EXACTLY, considering case sensitivity.
    - For charts, save the figure as a PNG at the given variable: chart_path.
    - Do not display the plot (no plt.show()).
    - Do not print anything.
    - The result should be stored in a variable named result_df if it's a DataFrame.
    """

    # --------------------------------
    # 2. Ask LLM to generate Python code
    # --------------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python data analytics and visualization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        code = response.choices[0].message.content.strip()

        # Clean any triple quotes
        if code.startswith("```"):
            code = code.strip("```").replace("python", "").strip()

    except Exception as e:
        return {"type": "error", "data": f"OpenAI request failed: {e}"}

    # --------------------------------
    # 3. Execute the generated code
    # --------------------------------
    try:
        # Prepare a unique path for charts
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

        exec(code, {}, local_env)

        # Check if the code generated a DataFrame
        result_df = local_env.get("result_df", None)

        # If result_df exists → table output
        if isinstance(result_df, pd.DataFrame):
            return {"type": "table", "data": result_df}

        # Else, if a chart was saved → chart output
        elif os.path.exists(chart_path):
            return {"type": "chart", "data": chart_path}

        # Fallback if nothing matched
        else:
            return {"type": "error", "data": "No valid output generated from the query."}

    except Exception as e:
        return {"type": "error", "data": f"Execution failed: {e}"}
