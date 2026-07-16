import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_fields_with_llm(text):
    """Send invoice text to Groq LLM and return structured data as a dict."""
    prompt = f"""
Extract the following fields from this invoice text and return ONLY valid JSON, nothing else, no markdown formatting:
- invoice_number
- invoice_date
- due_date
- total_amount
- items (list of objects with description, quantity, unit_price, gst_percent, amount)

Invoice text:
{text}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    raw_output = response.choices[0].message.content.strip()

    # Remove markdown code fences if the model added them
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        raw_output = raw_output.replace("json", "", 1).strip()

    return json.loads(raw_output)