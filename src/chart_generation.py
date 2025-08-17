import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

def generate_chart_from_query(df, user_query):
    os.makedirs("assets", exist_ok=True)

    if "top products" in user_query.lower():
        result_df = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        sns.barplot(x=result_df.values, y=result_df.index)
        plt.title("Top 10 Selling Products")
        plt.xlabel("Quantity Sold")
        plt.ylabel("Product")
        chart_path = "assets/top_products.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    elif "sales by country" in user_query.lower():
        result_df = df.groupby("Country")["Quantity"].sum().sort_values(ascending=False)

        plt.figure(figsize=(12, 6))
        sns.barplot(x=result_df.index[:10], y=result_df.values[:10])
        plt.title("Sales by Country (Top 10)")
        plt.xlabel("Country")
        plt.ylabel("Quantity Sold")
        chart_path = "assets/sales_by_country.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    elif "monthly sales trend" in user_query.lower():
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
        df["Month"] = df["InvoiceDate"].dt.to_period("M")
        monthly_sales = df.groupby("Month")["Quantity"].sum()

        plt.figure(figsize=(12, 6))
        monthly_sales.plot(kind="line", marker='o')
        plt.title("Monthly Sales Trend")
        plt.xlabel("Month")
        plt.ylabel("Quantity Sold")
        chart_path = "assets/monthly_sales_trend.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    elif "unit price distribution" in user_query.lower():
        plt.figure(figsize=(10, 6))
        sns.histplot(df["UnitPrice"], bins=50, kde=True)
        plt.title("Unit Price Distribution")
        plt.xlabel("Unit Price")
        plt.ylabel("Frequency")
        chart_path = "assets/unit_price_distribution.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    elif "top customers" in user_query.lower():
        df["TotalSpent"] = df["Quantity"] * df["UnitPrice"]
        result_df = df.groupby("CustomerID")["TotalSpent"].sum().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        sns.barplot(x=result_df.values, y=result_df.index.astype(str))
        plt.title("Top 10 Customers by Spend")
        plt.xlabel("Total Spent")
        plt.ylabel("Customer ID")
        chart_path = "assets/top_customers.png"
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    else:
        return None
