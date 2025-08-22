import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

def map_synonyms(query, columns):
    for user_term, actual_col in COLUMN_SYNONYMS.items():
        if user_term.lower() in query.lower() and actual_col in columns:
            query = re.sub(rf"\b{user_term}\b", actual_col, query, flags=re.IGNORECASE)
    return query

def add_case_insensitive_matching(code):
    # Regex match patterns like: df[df["column"] == "value"]
    pattern = r'df\[(df\["(.*?)"\]\s*==\s*"(.*?)")\]'
    
    def replacer(match):
        col = match.group(2)
        val = match.group(3)
        return f'df[df["{col}"].str.lower().str.strip() == "{val.lower()}"]'

    return re.sub(pattern, replacer, code)

def generate_code_from_query(user_query, columns):
    # Clean query
    cleaned_query = map_synonyms(user_query, list(columns))

    prompt = f"""
You're a Python assistant generating pandas code for a DataFrame called `df`.
Write code to answer the question: "{cleaned_query}"

- Use pandas only.
- Name output as `result_df`
- Support partial and case-insensitive matching for values.
- Assume df.columns = {list(columns)}
- DO NOT use backticks, markdown, or triple quotes.
- Just return executable code.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    code = response.choices[0].message.content.strip()

    # Clean markdown syntax
    if code.startswith("```"):
        code = re.sub(r"```(python)?", "", code).strip("`").strip()

    # Fix strict comparisons to be case-insensitive
    code = add_case_insensitive_matching(code)

    return code
