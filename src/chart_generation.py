import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import re
from io import BytesIO
import uuid

def generate_chart_from_query(df: pd.DataFrame, user_query: str):
    """
    Generates a chart based on a user's natural language query.
    Works for bar, line, scatter, histogram, pie, and distribution plots.
    """

    # --------------------------
    # 1. Clean Inputs & Prepare
    # --------------------------
    user_query = user_query.lower()
    chart_type = "bar"  # default fallback
    valid_chart_types = ["bar", "line", "scatter", "histogram", "pie", "distribution"]

    # --------------------------
    # 2. Detect Chart Type
    # --------------------------
    for ctype in valid_chart_types:
        if ctype in user_query:
            chart_type = ctype
            break

    # --------------------------
    # 3. Identify Likely Columns
    # --------------------------
    # Match columns ignoring case & spacing
    clean_cols = {col.lower().replace(" ", "_"): col for col in df.columns}
    found_cols = []

    for col_key, orig_col in clean_cols.items():
        if re.search(rf"\b{col_key}\b", user_query):
            found_cols.append(orig_col)

    # --------------------------
    # 4. Choose Columns to Plot
    # --------------------------
    # Default: use first 2 numeric columns if nothing matched
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    if len(found_cols) >= 2:
        x_col, y_col = found_cols[:2]
    elif len(found_cols) == 1 and len(numeric_cols) > 0:
        x_col = found_cols[0]
        y_col = numeric_cols[0] if numeric_cols[0] != x_col else numeric_cols[1]
    elif len(numeric_cols) >= 2:
        x_col, y_col = numeric_cols[:2]
    else:
        return None  # can't plot anything meaningful

    # --------------------------
    # 5. Generate Chart
    # --------------------------
    plt.figure(figsize=(10, 6))

    try:
        if chart_type == "bar":
            sns.barplot(data=df, x=x_col, y=y_col)
        elif chart_type == "line":
            sns.lineplot(data=df, x=x_col, y=y_col)
        elif chart_type == "scatter":
            sns.scatterplot(data=df, x=x_col, y=y_col)
        elif chart_type == "histogram":
            sns.histplot(df[x_col], bins=20, kde=True)
        elif chart_type == "pie":
            df[x_col].value_counts().plot.pie(autopct='%1.1f%%')
        elif chart_type == "distribution":
            sns.kdeplot(df[x_col], fill=True)
        else:
            sns.barplot(data=df, x=x_col, y=y_col)  # safe fallback

        plt.title(f"{chart_type.capitalize()} of {x_col} vs {y_col}")
        plt.tight_layout()

        # Save chart with a unique name
        chart_id = f"chart_{uuid.uuid4().hex}.png"
        chart_path = os.path.join("streamlit_app", "temp_charts", chart_id)
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        plt.savefig(chart_path)
        plt.close()

        return chart_path

    except Exception as e:
        print(f"Chart generation failed: {e}")
        return None
