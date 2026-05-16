from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.file_loader import load_file
from app.services.ai_summarizer import summarize

app = FastAPI(
    title="AI Document Automation API",
    description="Upload PDF, CSV, or TXT and get AI-powered summaries",
    version="1.0.0",
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Document Automation API is running"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = load_file(filename=file.filename, content=content)
        result = summarize(text=text, doc_type=file.filename.rsplit(".", 1)[-1].upper())

        return {"filename": file.filename, "analysis": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
