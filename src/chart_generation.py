import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import hashlib

def generate_chart_from_query(df, query):
    query = query.lower()
    query_hash = hashlib.md5(query.encode()).hexdigest()
    filename = f"assets/chart_{query_hash}.png"

    valid_columns = df.columns.tolist()

    x_col = None
    y_col = None

    for col in valid_columns:
        if col.lower() in query_lower and not x_col:
            x_col = col
        elif col.lower() in query_lower and not y_col:
            y_col = col

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not x_col or not y_col:
        if len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
        elif len(numeric_cols) == 1:
            x_col = numeric_cols[0]
            y_col = None
        else:
            return None

    fig, ax = plt.subplots(figsize=(10, 5))

    try:
        if "hist" in query_lower:
            df[x_col].plot(kind="hist", bins=20, ax=ax)
        elif "bar" in query_lower:
            df.groupby(x_col)[y_col].sum().plot(kind="bar", ax=ax)
        elif "line" in query_lower or "trend" in query_lower:
            df.plot(kind="line", x=x_col, y=y_col, ax=ax)
        elif "scatter" in query_lower:
            df.plot(kind="scatter", x=x_col, y=y_col, ax=ax)
        elif "pie" in query_lower:
            df.groupby(x_col)[y_col].sum().plot(kind="pie", ax=ax, autopct='%1.1f%%')
        else:
            df.plot(x=x_col, y=y_col, kind="line", ax=ax)

        ax.set_title(f"{x_col} vs {y_col}" if y_col else f"{x_col} Histogram")
        plt.tight_layout()

        chart_path = "output_chart.png"
        fig.savefig(chart_path)
        plt.close(fig)

        return chart_path
    except Exception as e:
        print("Chart error:", e)
        return None
