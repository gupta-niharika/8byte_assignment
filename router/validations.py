from fastapi import HTTPException

def validate_pdf(file):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")
    
def validate_query(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
def validate_top_k(top_k: int):
    if top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be greater than 0.")
    if top_k > 100:
        raise HTTPException(status_code=400, detail="top_k must be less than or equal to 100.")

def validate_file_contents(contents):
    if not contents:
        raise HTTPException(status_code=400, detail="File is empty or unreadable.")
