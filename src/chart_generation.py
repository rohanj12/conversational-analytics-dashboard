import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import uuid
import re
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def generate_chart_from_query(df, query):
    try:
        # Normalize query
        query = query.lower()

        # Infer chart type
        if "hist" in query or "distribution" in query:
            chart_type = "histogram"
        elif "bar" in query:
            chart_type = "bar"
        elif "line" in query or "trend" in query:
            chart_type = "line"
        elif "scatter" in query:
            chart_type = "scatter"
        elif "box" in query:
            chart_type = "box"
        else:
            chart_type = "default"

        # Try to extract potential columns from query
        tokens = re.findall(r"\b[\w']+\b", query)
        candidate_columns = [col for col in df.columns if any(tok in col.lower() for tok in tokens)]

        # Choose numeric and categorical columns
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(include='object').columns.tolist()

        # Fallback if no candidates match
        x_col = None
        y_col = None

        if chart_type == "histogram":
            y_col = candidate_columns[0] if candidate_columns else (numeric_cols[0] if numeric_cols else None)

        elif chart_type == "bar":
            x_col = candidate_columns[0] if candidate_columns else (categorical_cols[0] if categorical_cols else None)
            y_col = candidate_columns[1] if len(candidate_columns) > 1 else (numeric_cols[0] if numeric_cols else None)

        elif chart_type == "line":
            x_col = candidate_columns[0] if candidate_columns else (df.columns[0])
            y_col = candidate_columns[1] if len(candidate_columns) > 1 else (numeric_cols[0] if numeric_cols else None)

        elif chart_type == "scatter":
            if len(numeric_cols) >= 2:
                x_col, y_col = numeric_cols[:2]

        elif chart_type == "box":
            x_col = candidate_columns[0] if candidate_columns else (categorical_cols[0] if categorical_cols else None)
            y_col = candidate_columns[1] if len(candidate_columns) > 1 else (numeric_cols[0] if numeric_cols else None)

        # Generate plot
        plt.figure(figsize=(10, 6))

        if chart_type == "histogram" and y_col:
            sns.histplot(df[y_col].dropna(), kde=True)
            plt.xlabel(y_col)
            plt.title(f"Histogram of {y_col}")

        elif chart_type == "bar" and x_col and y_col:
            grouped = df.groupby(x_col)[y_col].sum().sort_values(ascending=False).head(10)
            sns.barplot(x=grouped.values, y=grouped.index)
            plt.xlabel(y_col)
            plt.ylabel(x_col)
            plt.title(f"Top {x_col} by {y_col}")

        elif chart_type == "line" and x_col and y_col:
            df_sorted = df.sort_values(x_col)
            plt.plot(df_sorted[x_col], df_sorted[y_col])
            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(f"{y_col} over {x_col}")

        elif chart_type == "scatter" and x_col and y_col:
            sns.scatterplot(data=df, x=x_col, y=y_col)
            plt.title(f"{y_col} vs {x_col}")

        elif chart_type == "box" and x_col and y_col:
            sns.boxplot(data=df, x=x_col, y=y_col)
            plt.title(f"Boxplot of {y_col} by {x_col}")

        else:
            return None  # If no valid chart

        chart_path = f"chart_{uuid.uuid4().hex}.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    except Exception as e:
        print("Chart generation error:", e)
        return None
