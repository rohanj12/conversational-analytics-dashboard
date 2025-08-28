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
    Unified LLM-powered function for generating either:
        - Filtered/Summarized tables
        - Accurate charts (matplotlib/seaborn)
    Handles fuzzy intent detection and guarantees chart generation when explicitly requested.
    """

    # -----------------------
    # 1. Detect Chart Intent
    # -----------------------
    chart_keywords = [
        "chart", "plot", "graph", "histogram", "distribution",
        "visualize", "scatter", "bar", "line", "trend", "heatmap", "pie"
    ]
    is_chart_query = any(kw in user_query.lower() for kw in chart_keywords)

    # -----------------------
    # 2. Build Prompt Dynamically
    # -----------------------
    columns_list = ", ".join(df.columns)

    if is_chart_query:
        prompt = f"""
        You are a Python data visualization expert.
        The user has asked: "{user_query}"

        You are given a pandas DataFrame called df with columns: {columns_list}.

        Instructions:
        - ALWAYS generate Python code that creates the requested chart using matplotlib or seaborn.
        - Save the figure to the provided `chart_path`.
        - DO NOT return a DataFrame.
        - Do NOT call plt.show() or print anything.
        """
    else:
        prompt = f"""
        You are a Python data analytics assistant.
        The user has asked: "{user_query}"

        You are given a pandas DataFrame called df with columns: {columns_list}.

        Instructions:
        - Generate Python code to filter, summarize, or aggregate data as requested.
        - Store the resulting DataFrame in a variable called `result_df`.
        - Do NOT return the entire dataset unless explicitly asked.
        - Do NOT print anything.
        """

    # -----------------------
    # 3. Ask LLM for Code
    # -----------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python analytics and visualization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        code = response.choices[0].message.content.strip()
        if code.startswith("```"):
            code = code.strip("```").replace("python", "").strip()

    except Exception as e:
        return {"type": "error", "data": f"OpenAI request failed: {e}"}

    # -----------------------
    # 4. Execute Generated Code
    # -----------------------
    try:
        # Unique chart path
        chart_id = f"chart_{uuid.uuid4().hex}.png"
        chart_path = os.path.join("streamlit_app", "temp_charts", chart_id)
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)

        # Execution environment
        local_env = {
            "df": df.copy(),
            "pd": pd,
            "plt": plt,
            "sns": sns,
            "chart_path": chart_path
        }

        exec(code, {}, local_env)

        # Handle table output
        if not is_chart_query:
            result_df = local_env.get("result_df", None)
            if isinstance(result_df, pd.DataFrame):
                return {"type": "table", "data": result_df}
            else:
                return {"type": "error", "data": "No valid DataFrame returned."}

        # Handle chart output
        if is_chart_query:
            if os.path.exists(chart_path):
                return {"type": "chart", "data": chart_path}
            else:
                # -------- HARD FALLBACK FOR CHARTS --------
                numeric_cols = df.select_dtypes(include="number").columns[:2]
                if len(numeric_cols) >= 1:
                    df[numeric_cols].plot(kind="line")
                    plt.savefig(chart_path)
                    return {"type": "chart", "data": chart_path}
                return {"type": "error", "data": "Couldn't generate a chart from this dataset."}

        # Fallback for unexpected behavior
        return {"type": "error", "data": "No valid output generated from the query."}

    except Exception as e:
        return {"type": "error", "data": f"Execution failed: {e}"}
