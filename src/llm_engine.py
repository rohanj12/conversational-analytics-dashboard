import os
from openai import OpenAI
from dotenv import load_dotenv
import re

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

# Define optional column synonym mapping
COLUMN_SYNONYMS = {
    "location": "city",
    "region": "city",
    "area": "pickup_area",
    "date": "booking_date",
    "fare": "fare_amount",
    "duration": "trip_duration",
    # Add more if needed
}

def map_synonyms(query, columns):
    for user_term, actual_col in COLUMN_SYNONYMS.items():
        if user_term.lower() in query.lower() and actual_col in columns:
            query = re.sub(rf"\b{user_term}\b", actual_col, query, flags=re.IGNORECASE)
    return query

def generate_code_from_query(user_query, columns):
    # Apply column mapping to user query
    clean_query = map_synonyms(user_query, list(columns))

    prompt = f"""
You are a data assistant that writes Python (pandas) code for tabular analysis.

Given a DataFrame called `df` and this user query:
"{clean_query}"

Write a Python code snippet that:
- Performs the operation asked.
- Does fuzzy value matching (ignore case, trim whitespace).
- Returns a new DataFrame named `result_df`.
- Assume all columns come from: {list(columns)}.

Don't use backticks or triple quotes.
Don't include explanations or print statements.

Just output the code.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    code = response.choices[0].message.content.strip()

    # Cleanup if it accidentally adds ```python or triple quotes
    if code.startswith("```"):
        code = re.sub(r"```(python)?", "", code).strip("`").strip()

    return code
