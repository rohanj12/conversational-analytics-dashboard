import streamlit as st
import pandas as pd
from PIL import Image
import os
import sys

# Enable src module import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.llm_engine import generate_code_from_query
from src.chart_generation import generate_chart_from_query

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="Conversational Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("💬 Example Queries")
    st.markdown("""
    - Show top 10 selling products  
    - Sales trend by month  
    - Distribution of unit prices  
    - Top customers by revenue  
    - Plot a histogram of trip durations  
    """)
    st.markdown("---")
    st.markdown("Made with ❤️ by [@rohanj12](https://github.com/rohanj12)")

# -------------------- MAIN UI --------------------
st.title("🧠 Conversational Analytics Dashboard")
st.markdown("Upload a CSV file and ask your data questions in plain English to generate **tables** or **charts** automatically.")

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("📤 Upload your CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    st.write(f"📊 Shape: `{df.shape[0]} rows × {df.shape[1]} columns`")
    st.dataframe(df.head())

    # -------------------- QUERY SECTION --------------------
    user_query = st.text_input("🗨️ Ask a question about your data")

    if user_query:
        with st.spinner("💡 Thinking..."):

            is_chart_query = any(
                keyword in user_query.lower()
                for keyword in ["plot", "chart", "graph", "histogram", "distribution", "bar", "line", "trend", "scatter", "visualize"]
            )

            if is_chart_query:
                chart_path = generate_chart_from_query(df, user_query)
                if chart_path and os.path.exists(chart_path):
                    st.success("📈 Chart generated successfully!")
                    st.image(Image.open(chart_path))
                else:
                    st.error("❌ Could not generate a chart for this query.")

            else:
                try:
                    code = generate_code_from_query(user_query, df.columns)

                    # Clean up code block formatting
                    if code.startswith("```"):
                        code = code.strip("```").replace("python", "").strip()

                    st.code(code, language="python")

                    # Execute code safely
                    local_env = {"df": df.copy()}
                    exec(code, {}, local_env)

                    result_df = None
                    for var in local_env.values():
                        if isinstance(var, pd.DataFrame) and not var.equals(df):
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
                    st.error(f"❌ Error while generating table:\n{e}")

else:
    st.info("⬆️ Upload a CSV to begin.")
