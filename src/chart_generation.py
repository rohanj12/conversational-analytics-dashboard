import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
import hashlib
import re

def generate_chart_from_query(df, query):
    query = query.lower()
    query_hash = hashlib.md5(query.encode()).hexdigest()
    filename = f"assets/chart_{query_hash}.png"

    try:
        # Convert columns to datetime if possible
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        categorical_cols = df.select_dtypes(include="object").columns.tolist()
        datetime_cols = df.select_dtypes(include="datetime").columns.tolist()

        # Histogram / Distribution
        if "histogram" in query or "distribution" in query:
            for col in numeric_cols:
                if col in query:
                    plt.figure(figsize=(10, 6))
                    sns.histplot(df[col], bins=30, kde=True)
                    plt.title(f"Histogram of {col}")
                    plt.tight_layout()
                    plt.savefig(filename)
                    plt.close()
                    return filename

        # Bar chart
        if "bar" in query or "top" in query or "count" in query:
            for col in categorical_cols:
                if col in query:
                    plt.figure(figsize=(10, 6))
                    value_counts = df[col].value_counts().nlargest(10)
                    sns.barplot(x=value_counts.values, y=value_counts.index)
                    plt.title(f"Top 10 {col}")
                    plt.tight_layout()
                    plt.savefig(filename)
                    plt.close()
                    return filename

        # Line chart / Trend over time
        if "line" in query or "trend" in query or "time" in query or "date" in query:
            if datetime_cols:
                time_col = datetime_cols[0]
                df_sorted = df.sort_values(by=time_col)
                for col in numeric_cols:
                    if col in query:
                        plt.figure(figsize=(10, 6))
                        sns.lineplot(x=df_sorted[time_col], y=df_sorted[col])
                        plt.title(f"{col.title()} Over Time")
                        plt.tight_layout()
                        plt.savefig(filename)
                        plt.close()
                        return filename

        # Pie chart
        if "pie" in query:
            for col in categorical_cols:
                if col in query:
                    plt.figure(figsize=(8, 8))
                    df[col].value_counts().nlargest(5).plot.pie(autopct="%1.1f%%", startangle=90)
                    plt.ylabel("")
                    plt.title(f"Pie Chart of {col}")
                    plt.tight_layout()
                    plt.savefig(filename)
                    plt.close()
                    return filename

        # Scatter plot
        if "scatter" in query:
            if len(numeric_cols) >= 2:
                for pair in [(x, y) for x in numeric_cols for y in numeric_cols if x != y]:
                    if f"{pair[0]} vs {pair[1]}" in query or f"{pair[1]} vs {pair[0]}" in query:
                        plt.figure(figsize=(10, 6))
                        sns.scatterplot(data=df, x=pair[0], y=pair[1])
                        plt.title(f"{pair[0]} vs {pair[1]}")
                        plt.tight_layout()
                        plt.savefig(filename)
                        plt.close()
                        return filename

        # Correlation heatmap
        if "correlation" in query or "heatmap" in query:
            plt.figure(figsize=(10, 6))
            corr = df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Heatmap")
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            return filename

        # Fallback generic chart (Top categories)
        if categorical_cols:
            fallback_col = categorical_cols[0]
            value_counts = df[fallback_col].value_counts().nlargest(10)
            plt.figure(figsize=(10, 6))
            sns.barplot(x=value_counts.values, y=value_counts.index)
            plt.title(f"Top 10 {fallback_col} (Fallback)")
            plt.tight_layout()
            plt.savefig(filename)
            plt.close()
            return filename

    except Exception as e:
        print("Chart generation error:", str(e))
        return None
