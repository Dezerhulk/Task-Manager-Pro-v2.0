"""FastAPI application with REST API endpoints."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import auth, users, projects, tasks, comments, tags, audit

# FastAPI app
app = FastAPI(
    title="Task Manager Pro API",
    description="Advanced task management with SQLAlchemy + SQLite/PostgreSQL + FastAPI",
    version="2.0.0",
)

# CORS middleware - configured from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# ===================== Include Routers =====================

app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(comments.router)
app.include_router(tags.router)
app.include_router(audit.router)


# ===================== Health & Root =====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "Task Manager Pro API",
        "version": "2.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

