from fastapi import FastAPI
from router.search_router import router as search_router

app = FastAPI(
    title="PDF Semantic Search API",
    description="Task for 8byte.ai",
    version="0.1.6",
)

app.include_router(search_router, prefix="/search")
