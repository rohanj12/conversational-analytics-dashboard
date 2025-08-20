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

    # Preprocess dataframe
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    datetime_cols = df.select_dtypes(include="datetime").columns.tolist()

    try:
        # Histogram
        if "histogram" in query or "distribution" in query:
            target_col = numeric_cols[0] if numeric_cols else None
            if target_col:
                plt.figure(figsize=(10, 6))
                sns.histplot(df[target_col], bins=30, kde=True)
                plt.title(f"Histogram of {target_col}")
                plt.tight_layout()
                plt.savefig(filename)
                plt.close()
                return filename

        # Bar Chart
        if "bar" in query or "top" in query or "most" in query:
            target_col = categorical_cols[0] if categorical_cols else None
            if target_col:
                value_counts = df[target_col].value_counts().nlargest(10)
                plt.figure(figsize=(10, 6))
                sns.barplot(x=value_counts.values, y=value_counts.index)
                plt.title(f"Top 10 {target_col}")
                plt.tight_layout()
                plt.savefig(filename)
                plt.close()
                return filename

        # Line Plot
        if "line" in query or "trend" in query:
            if datetime_cols and numeric_cols:
                time_col = datetime_cols[0]
                metric_col = numeric_cols[0]
                df_sorted = df.sort_values(by=time_col)
                plt.figure(figsize=(10, 6))
                sns.lineplot(x=df_sorted[time_col], y=df_sorted[metric_col])
                plt.title(f"{metric_col.title()} over Time")
                plt.tight_layout()
                plt.savefig(filename)
                plt.close()
                return filename

        # Pie Chart
        if "pie" in query:
            target_col = categorical_cols[0] if categorical_cols else None
            if target_col:
                plt.figure(figsize=(8, 8))
                df[target_col].value_counts().nlargest(5).plot.pie(autopct="%1.1f%%")
                plt.title(f"Pie Chart of {target_col}")
                plt.tight_layout()
                plt.savefig(filename)
                plt.close()
                return filename

        # Scatter Plot
        if "scatter" in query:
            if len(numeric_cols) >= 2:
                plt.figure(figsize=(10, 6))
                sns.scatterplot(data=df, x=numeric_cols[0], y=numeric_cols[1])
                plt.title(f"{numeric_cols[0]} vs {numeric_cols[1]}")
                plt.tight_layout()
                plt.savefig(filename)
                plt.close()
                return filename

        # Correlation Heatmap
        if "correlation" in query or "heatmap" in query:
            if len(numeric_cols) >= 2:
                plt.figure(figsize=(10, 6))
                sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm")
                plt.title("Correlation Heatmap")
                plt.tight_layout()
                plt.savefig(filename)
                plt.close()
                return filename

        # Fallback bar chart
        if categorical_cols:
            fallback_col = categorical_cols[0]
            value_counts = df[fallback_col].value_counts().nlargest(10)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=value_counts.values, y=value_counts.index)
            plt.title(f"Fallback Chart: Top 10 {fallback_col}")
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            return filename

    except Exception as e:
        print("Chart generation error:", e)
        return None
