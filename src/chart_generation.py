import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import uuid
import os
import numpy as np

def generate_chart_from_query(df, user_query):
    user_query = user_query.lower()
    chart_path = f"assets/chart_{uuid.uuid4().hex[:8]}.png"

    # Get column types
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    # Step 1: Determine chart type
    if any(kw in user_query for kw in ["trend", "line", "time", "monthly", "over time", "daily"]):
        chart_type = "line"
    elif any(kw in user_query for kw in ["bar", "top", "count", "frequency", "by"]):
        chart_type = "bar"
    elif any(kw in user_query for kw in ["histogram", "distribution", "spread"]):
        chart_type = "hist"
    elif any(kw in user_query for kw in ["scatter", "relationship", "vs", "correlation"]):
        chart_type = "scatter"
    elif any(kw in user_query for kw in ["pie", "portion", "percentage"]):
        chart_type = "pie"
    else:
        chart_type = "hist"  # fallback

    # Step 2: Try to guess columns from query
    x_col = y_col = None
    for col in df.columns:
        if col.lower() in user_query:
            if df[col].dtype == 'object' and not x_col:
                x_col = col
            elif df[col].dtype in ['int64', 'float64'] and not y_col:
                y_col = col

    # Default fallback if nothing found
    if not x_col and categorical_cols:
        x_col = categorical_cols[0]
    if not y_col and numeric_cols:
        y_col = numeric_cols[0]

    # Step 3: Generate chart
    plt.figure(figsize=(10, 6))
    try:
        if chart_type == "line":
            if x_col and y_col:
                df_sorted = df.sort_values(x_col)
                sns.lineplot(data=df_sorted, x=x_col, y=y_col)
                plt.title(f"{y_col} over {x_col}")
            else:
                raise ValueError("Line chart needs numeric + categorical columns.")

        elif chart_type == "bar":
            if x_col:
                value_counts = df[x_col].value_counts().head(10)
                sns.barplot(x=value_counts.index, y=value_counts.values)
                plt.xticks(rotation=45)
                plt.title(f"Top 10 {x_col}")
                plt.xlabel(x_col)
                plt.ylabel("Count")
            else:
                raise ValueError("No categorical column for bar chart.")

        elif chart_type == "hist":
            if y_col:
                sns.histplot(df[y_col], bins=30, kde=True)
                plt.title(f"Distribution of {y_col}")
                plt.xlabel(y_col)
                plt.ylabel("Frequency")
            else:
                raise ValueError("No numeric column for histogram.")

        elif chart_type == "scatter":
            if x_col and y_col:
                sns.scatterplot(data=df, x=x_col, y=y_col)
                plt.title(f"{y_col} vs {x_col}")
            else:
                raise ValueError("Scatter plot requires numeric x and y.")

        elif chart_type == "pie":
            if x_col:
                pie_data = df[x_col].value_counts().head(5)
                plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%')
                plt.title(f"Distribution of {x_col}")
            else:
                raise ValueError("No suitable column for pie chart.")

        else:
            raise ValueError("Unknown chart type.")

        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    except Exception as e:
        print(f"[Chart error] {e}")
        plt.close()
        return None
