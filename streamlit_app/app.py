import streamlit as st
import pandas as pd
from PIL import Image
import os
import sys

# Enable src module import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.unified_engine import generate_output_from_query

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
    - Show top 10 most selling products  
    - Sales trend by month as a line chart  
    - Distribution of unit prices  
    - Count of orders by region  
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
            result = generate_output_from_query(df, user_query)

            if result["type"] == "table":
                st.success("📄 Table generated successfully!")
                st.dataframe(result["data"].head(10))

                # Download button
                csv = result["data"].to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, "result.csv", "text/csv")

            elif result["type"] == "chart":
                st.success("📈 Chart generated successfully!")
                st.image(Image.open(result["data"]))

            else:
                st.error(result["data"])

else:
    st.info("⬆️ Upload a CSV to begin.")
