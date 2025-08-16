# src/query_executor.py
import pandas as pd

def run_generated_code(code: str, df: pd.DataFrame):
    # Provide the DataFrame as a variable in scope
    local_vars = {"df": df.copy()}
    try:
        exec(code, {}, local_vars)
        if "result" in local_vars:
            return local_vars["result"]
        else:
            return "⚠️ Code executed but no 'result' variable returned."
    except Exception as e:
        return f"❌ Error executing code: {e}"
