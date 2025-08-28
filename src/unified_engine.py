import os
import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import re

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_code_block(code: str) -> str:
    """Remove markdown fences and language hints."""
    return re.sub(r"^```(?:python)?|```$", "", code.strip(), flags=re.MULTILINE).strip()

def generate_output_from_query(df: pd.DataFrame, user_query: str):
    """
    Unified function to generate either tables or charts reliably.
    """
    columns_list = ", ".join(df.columns)

    # Detect if the query is for charts
    chart_keywords = ["plot", "chart", "graph", "histogram", "distribution", "scatter", "bar", "line", "trend", "visualize"]
    is_chart_query = any(keyword in user_query.lower() for keyword in chart_keywords)

    # Build prompt dynamically
    if is_chart_query:
        prompt = f"""
        You are a Python data visualization assistant.
        Given a pandas DataFrame df with columns: {columns_list},
        write Python code to answer the user's chart request:

        "{user_query}"

        Rules:
        - Use matplotlib or seaborn only.
        - Save the chart to the given variable 'chart_path'.
        - Do NOT call plt.show().
        - Do NOT return a DataFrame.
        - Do NOT print anything.
        """
    else:
        prompt = f"""
        You are a Python data analytics assistant.
        Given a pandas DataFrame df with columns: {columns_list},
        write Python code to answer the user's query:

        "{user_query}"

        Rules:
        - Always store your final DataFrame in a variable named 'result_df'.
        - Do NOT generate charts here.
        - Do NOT call plt.show().
        - Do NOT print anything.
        """

    # Query LLM
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python analytics and visualization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        code = clean_code_block(response.choices[0].message.content)
    except Exception as e:
        return {"type": "error", "data": f"OpenAI request failed: {e}"}

    # Prepare environment
    chart_id = f"chart_{uuid.uuid4().hex}.png"
    chart_path = os.path.join("streamlit_app", "temp_charts", chart_id)
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)

    local_env = {
        "df": df.copy(),
        "pd": pd,
        "plt": plt,
        "sns": sns,
        "chart_path": chart_path
    }

    # Execute generated code safely
    try:
        exec(code, {}, local_env)
        if is_chart_query:
            if os.path.exists(chart_path):
                return {"type": "chart", "data": chart_path}
            else:
                return {"type": "error", "data": "Chart code executed but no chart was saved."}
        else:
            result_df = local_env.get("result_df", None)
            if isinstance(result_df, pd.DataFrame):
                return {"type": "table", "data": result_df}
            else:
                return {"type": "error", "data": "No DataFrame was generated."}
    except Exception as e:
        return {"type": "error", "data": f"Execution failed: {e}"}
