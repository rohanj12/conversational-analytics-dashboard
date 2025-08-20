import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.llm_engine import generate_code_from_query
from src.chart_generation import generate_chart_from_query

st.set_page_config(page_title="Conversational Analytics Dashboard", layout="wide")

st.sidebar.header("💬 Example Queries")
st.sidebar.markdown("""
- Show top 10 ride types
- Histogram of fare amount
- Line chart of bookings over time
- Bar chart of bookings per day
""")
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by [@rohanj12](https://github.com/rohanj12)")

st.title("🧠 Conversational Analytics Dashboard")
st.markdown("Ask a question about your data in plain English, and get insights as **tables** or **charts**.")

uploaded_file = st.file_uploader("📤 Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"Uploaded `{uploaded_file.name}` successfully!")
    st.write(f"Shape: `{df.shape[0]} rows × {df.shape[1]} columns`")
    st.dataframe(df.head(5))

    user_query = st.text_input("🗨️ Ask your question")

    if user_query:
        with st.spinner("Processing..."):

            if any(keyword in user_query.lower() for keyword in ["chart", "plot", "trend", "distribution", "bar", "line", "hist", "scatter", "pie"]):
                chart_path = generate_chart_from_query(df, user_query)
                if chart_path and os.path.exists(chart_path):
                    st.success("📈 Chart generated:")
                    from PIL import Image
                    st.image(Image.open(chart_path))
                else:
                    st.error("❌ Could not generate a chart.")
            else:
                try:
                    code = generate_code_from_query(user_query, df.columns)

                    st.code(code, language="python")

                    local_vars = {"df": df.copy(), "np": np}
                    exec(code, globals(), local_vars)

                    result_df = local_vars.get("result_df", None)

                    if isinstance(result_df, pd.DataFrame):
                        st.success("📄 Table generated:")
                        st.dataframe(result_df.head(10))

                        csv = result_df.to_csv(index=False).encode("utf-8")
                        st.download_button("📥 Download CSV", csv, "result.csv", "text/csv")
                    else:
                        st.warning("⚠️ No DataFrame returned.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
else:
    st.info("⬆️ Upload a CSV file to begin.")
