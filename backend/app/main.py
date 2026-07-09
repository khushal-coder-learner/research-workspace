from fastapi import FastAPI

from app.documents.router import router as documents_router
from app.projects.router import router as projects_router

app = FastAPI(
    title="Research Workspace API",
    version="0.1.0",
)

app.include_router(projects_router)
app.include_router(documents_router)

@app.get("/")
def root():
    return {"message": "Research Workspace API"}
