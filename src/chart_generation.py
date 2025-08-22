import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI
import uuid

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def generate_chart_from_query(df: pd.DataFrame, query: str, output_path="chart.png") -> str:
    prompt = f"""
You are a Python data visualization assistant. Given a user query and a pandas DataFrame called `df`, generate Python code to create an appropriate chart using `matplotlib` or `seaborn`.

Rules:
- Only use columns that exist in df: {list(df.columns)}
- Save the figure using `plt.savefig("chart.png")` at the end.
- Do not show the plot using `plt.show()`.
- The DataFrame is already loaded as `df`.
- Wrap your code in a Python code block.

User query: "{query}"

Respond with only the code, wrapped like this:

```python
# your chart code
"""
# Get chart code from OpenAI
try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    chart_code = response.choices[0].message.content.strip()

    # Remove ```python block if present
    if chart_code.startswith("```"):
        chart_code = chart_code.strip("```").replace("python", "").strip()

    # Unique filename for chart
    chart_path = f"chart_{uuid.uuid4().hex}.png"

    # Prepare local execution environment
    local_env = {"df": df.copy(), "plt": plt, "sns": sns}
    exec(chart_code, {}, local_env)

    # Replace chart.png with unique path if needed
    if os.path.exists("chart.png"):
        os.rename("chart.png", chart_path)

    return chart_path if os.path.exists(chart_path) else None

except Exception as e:
    print("❌ Chart generation failed:", str(e))
    return None
