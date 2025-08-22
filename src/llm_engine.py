import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

# Optional aliases for natural language matching
COLUMN_SYNONYMS = {
    "location": "city",
    "region": "city",
    "fare": "fare_amount",
    "area": "pickup_area",
    "drop": "drop_area",
    "pickup": "pickup_area",
    "date": "booking_date",
    "duration": "trip_duration"
}

def map_synonyms(query, columns):
    for user_term, actual_col in COLUMN_SYNONYMS.items():
        if user_term.lower() in query.lower() and actual_col in columns:
            query = re.sub(rf"\b{user_term}\b", actual_col, query, flags=re.IGNORECASE)
    return query

def add_case_insensitive_filtering(code):
    # Modify any == comparisons to lowercase string matches
    pattern = r'df\[(df\["(.*?)"\]\s*==\s*"(.*?)")\]'
    
    def replace_match(m):
        col = m.group(1)
        val = m.group(2)
        return f'df[df["{col}"].str.lower().str.strip() == "{val.lower()}"]'

    return re.sub(pattern, replace_match, code)

def generate_code_from_query(user_query, columns):
    cleaned_query = map_synonyms(user_query, list(columns))

    prompt = f"""
You are a Python data assistant. 
Generate only executable pandas code to analyze a DataFrame called `df` with columns: {list(columns)}.

The user query is: "{cleaned_query}"

Requirements:
- Return code that creates a filtered DataFrame called `result_df`
- Use pandas filtering, aggregations, or sorting as needed
- Use only the column names from df
- Avoid markdown/triple quotes
- No explanations or comments
- Ensure output is smaller than the original df (filtered or aggregated)

Only return the code.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    code = response.choices[0].message.content.strip()

    # Clean markdown/triple quotes
    if code.startswith("```"):
        code = re.sub(r"```(python)?", "", code).strip("`").strip()

    # Fix to apply lowercase filter matching
    code = add_case_insensitive_filtering(code)

    return code
