import os
import openai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import uuid

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Keywords that indicate chart-based queries
CHART_KEYWORDS = [
    "plot", "chart", "graph", "histogram", "distribution", "bar", 
    "line", "trend", "scatter", "visualize", "heatmap", "boxplot"
]

def generate_output_from_query(df: pd.DataFrame, user_query: str):
    """
    Unified LLM-powered function to handle both table and chart generation based on natural language queries.
    Prioritizes chart generation if keywords indicate visualization.
    """
    columns_list = ", ".join(df.columns)
    is_chart_query = any(keyword in user_query.lower() for keyword in CHART_KEYWORDS)

    # -------------------------------
    # Build prompt based on query type
    # -------------------------------
    if is_chart_query:
        task_description = (
            "Write Python code to generate a CHART using matplotlib or seaborn based on the query. "
            "The DataFrame is called df and has these columns: "
            f"{columns_list}. "
            "Save the chart as a PNG using the variable 'chart_path'. "
            "Do not use plt.show(). Do not print anything. "
            "If grouping or aggregation is required, do it internally before plotting."
        )
    else:
        task_description = (
            "Write Python code to generate a pandas DataFrame as output based on the query. "
            f"The DataFrame is called df and has these columns: {columns_list}. "
            "Always assign the final result to a variable called result_df."
        )

    # -------------------------------
    # Get LLM-generated code
    # -------------------------------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python data analytics and visualization expert."},
                {"role": "user", "content": f"User query: {user_query}\n\n{task_description}"}
            ],
            temperature=0
        )

        code = response.choices[0].message.content.strip()

        # Clean up triple quotes and language tags
        if code.startswith("```"):
            code = code.strip("```").replace("python", "").strip()

    except Exception as e:
        return {"type": "error", "data": f"OpenAI request failed: {e}"}

    # -------------------------------
    # Execute generated code safely
    # -------------------------------
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

        # If chart query, return saved chart path
        if is_chart_query:
            if os.path.exists(chart_path):
                return {"type": "chart", "data": chart_path}
            else:
                return {"type": "error", "data": "Chart generation failed."}

        # For table queries, return result_df
        result_df = local_env.get("result_df", None)
        if isinstance(result_df, pd.DataFrame):
            return {"type": "table", "data": result_df}

        return {"type": "error", "data": "No valid output generated."}

    except Exception as e:
        return {"type": "error", "data": f"Execution failed: {e}"}
