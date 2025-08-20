import streamlit as st
import pandas as pd
import os
import numpy as np
from src.llm_engine import generate_code_from_query
from src.chart_generation import generate_chart_from_query
import os
from PIL import Image

# ----------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Conversational Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SIDEBAR -------------------
with st.sidebar:
    st.header("💬 Example Queries")
    st.markdown("""
    - Show top 10 booking sources  
    - Histogram of ride durations  
    - Ride trends over time  
    - Correlation between fare and distance  
    - Generate a pie chart of ride types  
    """)
    st.markdown("---")
    st.markdown("Made with ❤️ by [@rohanj12](https://github.com/rohanj12)")

# ----------------- MAIN TITLE -------------------
st.title("🧠 Conversational Analytics Dashboard")
st.markdown("Ask a question about your data in plain English, and get answers instantly as **tables** or **charts**.")

# ----------------- FILE UPLOAD -------------------
uploaded_file = st.file_uploader("📤 Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    st.write(f"📊 Shape: `{df.shape[0]} rows × {df.shape[1]} columns`")
    st.dataframe(df.head(5))

    # ----------------- QUERY INPUT -------------------
    user_query = st.text_input("🗨️ Ask a question about your data")

    if user_query:
        with st.spinner("💡 Processing your query..."):

            # Detect chart-related keywords
            chart_keywords = [
                "chart", "plot", "distribution", "trend", "graph",
                "line", "bar", "histogram", "pie", "scatter", "top", "correlation", "heatmap"
            ]

            if any(kw in user_query.lower() for kw in chart_keywords):
                chart_path = generate_chart_from_query(df, user_query)
                if chart_path and os.path.exists(chart_path):
                    st.success("📈 Chart generated successfully!")
                    st.image(Image.open(chart_path))
                else:
                    st.error("❌ Could not generate a chart for this query.")
            else:
                try:
                    # LLM-based table code generation
                    code = generate_code_from_query(user_query, df.columns)
                    if code.startswith("```"):
                        code = code.strip("```").replace("python", "").strip()

                    st.code(code, language="python")

                    local_vars = {"df": df.copy(), "pd": pd, "np": __import__("numpy")}
                    exec(code, globals(), local_vars)

                    result_df = None
                    for var in local_vars.values():
                        if isinstance(var, pd.DataFrame) and var is not df:
                            result_df = var
                            break

                    if result_df is not None:
                        st.success("📄 Table generated successfully!")
                        st.dataframe(result_df.head(10))

                        csv = result_df.to_csv(index=False).encode("utf-8")
                        st.download_button("📥 Download CSV", csv, "result.csv", "text/csv")
                    else:
                        st.warning("⚠️ No tabular output returned.")

                except Exception as e:
                    st.error(f"❌ Error while generating table:\n\n{e}")
else:
    st.info("⬆️ Upload a CSV to begin.")
