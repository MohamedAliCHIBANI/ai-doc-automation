import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize(text: str, doc_type: str = "document") -> dict:

    trimmed = text[:8000]

    prompt = f"""You are a document analysis assistant.
Analyze the following {doc_type} content and return a structured response with:

1. **Summary** — a clear, concise summary (3-5 sentences)
2. **Key Points** — top 5 bullet points
3. **Document Type** — what kind of document this is
4. **Sentiment** — overall tone (positive / neutral / negative)
5. **Word Count** — approximate word count of the original

Document content:
{trimmed}

Respond in clean JSON format only. No markdown, no explanation, no backticks."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())
