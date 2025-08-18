import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def generate_chart_from_query(df, query):
    query = query.lower()
    chart_path = "assets/chart_output.png"
    
    if "distribution" in query or "histogram" in query:
        # Find a numeric column to plot
        for col in df.select_dtypes(include="number").columns:
            if col in query or "fare" in query and "fare" in col:
                plt.figure(figsize=(10, 6))
                sns.histplot(df[col], kde=True, bins=30)
                plt.title(f"Distribution of {col}")
                plt.tight_layout()
                plt.savefig(chart_path)
                plt.close()
                return chart_path

    elif "trend" in query or "line" in query or "over time" in query:
        # Look for datetime and numeric columns
        df = df.copy()
        datetime_col = None
        for col in df.columns:
            if "date" in col.lower() or "time" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")
                datetime_col = col
                break

        if datetime_col:
            df = df.dropna(subset=[datetime_col])
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) > 0:
                df = df.groupby(df[datetime_col].dt.date)[numeric_cols[0]].sum()
                plt.figure(figsize=(10, 6))
                df.plot()
                plt.title(f"{numeric_cols[0]} Trend Over Time")
                plt.tight_layout()
                plt.savefig(chart_path)
                plt.close()
                return chart_path

    elif "top" in query or "bar" in query:
        # Look for categorical vs numeric
        numeric_col = None
        cat_col = None

        for col in df.select_dtypes(include="object").columns:
            if "name" in col.lower() or "pickup" in col.lower():
                cat_col = col
                break

        for col in df.select_dtypes(include="number").columns:
            if "fare" in col.lower() or "amount" in col.lower():
                numeric_col = col
                break

        if cat_col and numeric_col:
            top_vals = df.groupby(cat_col)[numeric_col].sum().sort_values(ascending=False).head(10)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=top_vals.values, y=top_vals.index)
            plt.title(f"Top 10 {cat_col} by {numeric_col}")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            return chart_path

    return None
