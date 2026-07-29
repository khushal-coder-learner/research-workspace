from fastapi import FastAPI

from app.documents.router import router as documents_router
from app.projects.router import router as projects_router
from app.query.router import router as query_router
from app.core.exception_handlers import register_exception_handlers

app = FastAPI(
    title="Research Workspace API",
    version="0.1.0",
)

app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(query_router)

register_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "Research Workspace API"}

@app.get("/health")
def health():
    return {"status": "ok"}
