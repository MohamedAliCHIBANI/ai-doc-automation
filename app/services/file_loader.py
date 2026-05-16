import io
import pandas as pd
import pdfplumber

SUPPORTED_TYPES = ["pdf", "csv", "txt"]


def get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()


def load_file(filename: str, content: bytes) -> str:
    ext = get_extension(filename)

    if ext not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == "txt":
        return content.decode("utf-8", errors="ignore")

    if ext == "csv":
        df = pd.read_csv(io.BytesIO(content))
        return df.to_string(index=False)

    if ext == "pdf":
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
