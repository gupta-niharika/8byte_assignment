from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from faiss import IndexFlatIP
from tempfile import NamedTemporaryFile
from os import remove
from utils.pdf_utils import extract_text_chunks
from .validations import *

router = APIRouter()

model = SentenceTransformer('all-MiniLM-L6-v2')
index = None
texts = []
metadata = []

@router.post("/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)) -> dict|str:
    """
    Upload PDF files and index their content.
    Args:
        files (list[UploadFile]): List of PDF files to upload.
    Returns:
        dict: A message indicating the number of files uploaded and indexed.
    """

    global index, texts, metadata
    all_chunks, meta = [], []

    for file in files:
        validate_pdf(file)

        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            
            validate_file_contents(file)
            
            tmp.write(contents)
            tmp_path = tmp.name

        chunks = extract_text_chunks(tmp_path, original_filename=file.filename)
        remove(tmp_path)

        for chunk, source in chunks:
            all_chunks.append(chunk)
            meta.append(source)

    texts = all_chunks
    metadata = meta

    embeddings = model.encode(texts, convert_to_numpy=True)
    normalized_embeddings = normalize(embeddings, norm='l2')

    dim = normalized_embeddings.shape[1]
    index = IndexFlatIP(dim)
    index.add(normalized_embeddings)

    return {"message": f"Uploaded {len(files)} PDF(s), indexed {len(texts)} chunks."}

@router.get("/query")
async def semantic_query(q: str = Form(...), top_k: int = Form(...)) -> dict|str:
    """
    Perform a semantic search on the indexed documents.
    Args:
        q (str): The query string.
        top_k (int): The number of top results to return.
    Returns:
        dict: A dictionary containing the query and the top_k results along with their cosine similarity scores and the source.
    """

    validate_query(q)
    validate_top_k(top_k)

    global index, texts, metadata
    if index is None:
        return JSONResponse(status_code=400, content={"error": "No documents indexed."})

    query_embedding = model.encode([q], convert_to_numpy=True)
    normalized_query = normalize(query_embedding, norm='l2')

    D, I = index.search(x=normalized_query, k=top_k)

    results = []
    for idx, score in zip(I[0], D[0]):
        results.append({
            "text": texts[idx],
            "source": metadata[idx], 
            "cosine_similarity": float(score)

        })

    return {"query": q, "results": results}
