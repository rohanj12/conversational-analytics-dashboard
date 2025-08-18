import streamlit as st
import pandas as pd
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
    - Show top 10 selling products  
    - Sales by country  
    - Monthly sales trend  
    - Distribution of unit price  
    - Top customers by spend  
    - Which customers bought more than 100 units?  
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

            # --- Decide whether to render chart or table ---
            chart_keywords = ["chart", "plot", "trend", "distribution", "top products", "top customers", "sales"]
            is_chart_query = any(keyword in user_query.lower() for keyword in chart_keywords)

            if is_chart_query:
                chart_path = generate_chart_from_query(df, user_query)
                if chart_path and os.path.exists(chart_path):
                    st.success("📈 Chart generated successfully!")
                    st.image(Image.open(chart_path))
                else:
                    st.error("❌ Could not generate a chart for this query.")

            else:
                try:
                    # --- Generate and clean LLM code ---
                    code = generate_code_from_query(user_query, df.columns)
                    if code.startswith("```"):
                        code = code.strip("```").replace("python", "").strip()
                    st.code(code, language="python")

                    # --- Execute the code ---
                    local_vars = {"df": df.copy()}
                    exec(code, globals(), local_vars)

                    # --- Extract and show result_df ---
                    result_df = local_vars.get("result_df", None)
                    if isinstance(result_df, pd.DataFrame):
                        st.success("📄 Table generated successfully!")
                        st.dataframe(result_df.head(10))

                        # CSV Download
                        csv = result_df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download CSV", csv, "result.csv", "text/csv")
                    else:
                        st.warning("⚠️ Code ran, but no table was returned.")
                except Exception as e:
                    st.error(f"❌ Error while generating table:\n{e}")
else:
    st.info("⬆️ Upload a CSV to begin.")
