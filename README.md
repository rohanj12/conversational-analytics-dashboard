# 🧠 Conversational Analytics Dashboard

A Streamlit-based application that allows users to interact with data using natural language queries. Powered by OpenAI and Pandas, this project bridges the gap between LLMs and business intelligence.

## 🚀 Features

- Ask questions about your data in plain English
- AI generates and runs valid Python (Pandas) code
- Displays charts, tables, and summaries
- Extendable for SQL, dashboards, or insights

## 📁 Folder Structure
-> data/ # CSV datasets
-> notebooks/ # EDA or prototype notebooks
-> src/ # LLM interaction logic
-> streamlit_app/ # Streamlit frontend
-> assets/ # Screenshots
-> requirements.txt
-> README.md


## 🔧 Technologies

- Streamlit
- OpenAI API
- Pandas / Matplotlib
- Git & GitHub

## 📊 Visual Analytics (Phase 4)

The Conversational Analytics Dashboard supports dynamic chart generation based on user queries using Matplotlib and Seaborn.

### 🔧 How It Works
When a user enters a query like "Show top products by quantity sold", the system:
1. Parses the intent of the query.
2. Matches it to one of the predefined visualization types.
3. Generates the chart.
4. Saves it to the `assets/` directory for display.

### ✅ Supported Chart Types

| Query Intent                            | Chart Type                | File Output Path                    |
|-----------------------------------------|---------------------------|-------------------------------------|
| "Top products by quantity sold"         | Horizontal Bar Chart      | `assets/top_products.png`           |
| "Sales by country"                      | Bar Chart                 | `assets/sales_by_country.png`       |
| "Monthly sales trend"                   | Line Plot                 | `assets/monthly_sales_trend.png`    |
| "Unit price distribution"              | Histogram (with KDE)      | `assets/unit_price_distribution.png`|
| "Top customers by total spend"          | Bar Chart                 | `assets/top_customers.png`          |

## 🔗 End-to-End Architecture


text
User Query
   │
   ▼
🔎 Streamlit Frontend (app.py)
   │
   ├── Determines Query Type (Table vs Chart)
   │
   ▼
🧠 LLM Engine (src/llm_engine.py)
   │
   ├── Uses OpenAI to generate Python code
   ├── Fuzzy matches column names
   ├── Cleans and validates code
   │
   ▼
📊 Output Handler
   ├── If table → Executes Pandas code
   ├── If chart → Generates Matplotlib/Seaborn chart
   │
   ▼
✅ Final Output
   ├── Streamlit displays table or chart
   └── Allows CSV export or image preview




