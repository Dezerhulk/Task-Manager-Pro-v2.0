"""FastAPI application with REST API endpoints."""

from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .database_pro import get_db, init_db
from . import crud_pro
from .schemas_pro import (
    UserCreate, UserUpdate, UserResponse, UserDetailResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse,
    TaskCreate, TaskUpdate, TaskResponse, TaskDetailResponse,
    CommentCreate, CommentUpdate, CommentResponse, CommentDetailResponse,
    TagCreate, TagUpdate, TagResponse,
    TaskFilterParams, ProjectFilterParams,
    AuditLogResponse,
)
from .auth import get_current_user

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


# ===================== Startup Events =====================

@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


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
        "version": "1.0.0",
        "docs": "/docs",
    }


# ===================== User Endpoints =====================

@app.post("/api/users", response_model=UserResponse)
async def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    try:
        return crud_pro.create_user(db, user_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    """Get user details."""
    user = crud_pro.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/users", response_model=list[UserResponse])
async def get_users_list(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Get list of users."""
    users, _ = crud_pro.get_users(db, skip=skip, limit=limit)
    return users


@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user."""
    user = crud_pro.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Soft delete user."""
    success = crud_pro.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"deleted": True}


# ===================== Project Endpoints =====================

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project_create: ProjectCreate, owner_id: int = Query(...), db: Session = Depends(get_db)):
    """Create a new project."""
    return crud_pro.create_project(db, project_create, owner_id)


@app.get("/api/projects/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    """Get project details."""
    project = crud_pro.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/api/projects", response_model=list[ProjectResponse])
async def get_projects_list(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    """Get list of projects."""
    projects, _ = crud_pro.get_projects(db, skip=skip, limit=limit)
    return projects


@app.get("/api/users/{user_id}/projects", response_model=list[ProjectResponse])
async def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    """Get user's projects."""
    projects = crud_pro.get_user_projects(db, user_id)
    return projects


@app.post("/api/projects/search", response_model=list[ProjectResponse])
async def search_projects(params: ProjectFilterParams, db: Session = Depends(get_db)):
    """Search/filter projects."""
    projects, _ = crud_pro.search_projects(db, params)
    return projects


@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project_update: ProjectUpdate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Update project."""
    project = crud_pro.update_project(db, project_id, project_update, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Soft delete project."""
    success = crud_pro.delete_project(db, project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}


@app.post("/api/projects/{project_id}/members/{user_id}")
async def add_project_member(project_id: int, user_id: int, actor_id: int = Query(...), db: Session = Depends(get_db)):
    """Add member to project."""
    success = crud_pro.add_project_member(db, project_id, user_id, actor_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to add member")
    return {"added": True}


@app.delete("/api/projects/{project_id}/members/{user_id}")
async def remove_project_member(project_id: int, user_id: int, actor_id: int = Query(...), db: Session = Depends(get_db)):
    """Remove member from project."""
    success = crud_pro.remove_project_member(db, project_id, user_id, actor_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to remove member")
    return {"removed": True}


# ===================== Task Endpoints =====================

@app.post("/api/tasks", response_model=TaskResponse)
async def create_task(task_create: TaskCreate, creator_id: int = Query(...), db: Session = Depends(get_db)):
    """Create a new task."""
    task = crud_pro.create_task(db, task_create, creator_id)
    if not task:
        raise HTTPException(status_code=400, detail="Failed to create task")
    return task


@app.get("/api/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """Get task details."""
    task = crud_pro.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/api/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def get_project_tasks(project_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Get tasks for a project."""
    tasks, _ = crud_pro.get_project_tasks(db, project_id, skip=skip, limit=limit)
    return tasks


@app.post("/api/tasks/search", response_model=list[TaskResponse])
async def search_tasks(params: TaskFilterParams, db: Session = Depends(get_db)):
    """Search/filter tasks."""
    tasks, _ = crud_pro.search_tasks(db, params)
    return tasks


@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Update task."""
    task = crud_pro.update_task(db, task_id, task_update, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Soft delete task."""
    success = crud_pro.delete_task(db, task_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


# ===================== Comment Endpoints =====================

@app.post("/api/tasks/{task_id}/comments", response_model=CommentResponse)
async def create_comment(task_id: int, comment_create: CommentCreate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Create a comment."""
    comment = crud_pro.create_comment(db, task_id, user_id, comment_create)
    if not comment:
        raise HTTPException(status_code=400, detail="Failed to create comment")
    return comment


@app.get("/api/comments/{comment_id}", response_model=CommentDetailResponse)
async def get_comment_detail(comment_id: int, db: Session = Depends(get_db)):
    """Get comment details."""
    comment = crud_pro.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@app.get("/api/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_task_comments(task_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Get comments for a task."""
    comments, _ = crud_pro.get_task_comments(db, task_id, skip=skip, limit=limit)
    return comments


@app.put("/api/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_update: CommentUpdate, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Update comment."""
    comment = crud_pro.update_comment(db, comment_id, comment_update, user_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@app.delete("/api/comments/{comment_id}")
async def delete_comment(comment_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Soft delete comment."""
    success = crud_pro.delete_comment(db, comment_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"deleted": True}


# ===================== Tag Endpoints =====================

@app.post("/api/tags", response_model=TagResponse)
async def create_tag(tag_create: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    try:
        return crud_pro.create_tag(db, tag_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tags/{tag_id}", response_model=TagResponse)
async def get_tag_detail(tag_id: int, db: Session = Depends(get_db)):
    """Get tag details."""
    tag = crud_pro.get_tag(db, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.get("/api/tags", response_model=list[TagResponse])
async def get_tags_list(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500), db: Session = Depends(get_db)):
    """Get list of tags."""
    tags, _ = crud_pro.get_tags(db, skip=skip, limit=limit)
    return tags


@app.put("/api/tags/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, tag_update: TagUpdate, db: Session = Depends(get_db)):
    """Update tag."""
    tag = crud_pro.update_tag(db, tag_id, tag_update)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@app.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete tag."""
    success = crud_pro.delete_tag(db, tag_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")
    return {"deleted": True}


# ===================== Audit Log Endpoints =====================

@app.get("/api/audit-logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    entity_type: str = Query(None),
    entity_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get audit logs."""
    logs, _ = crud_pro.get_audit_logs(db, entity_type=entity_type, entity_id=entity_id, skip=skip, limit=limit)
    return logs


@app.get("/api/tasks/{task_id}/audit-logs", response_model=list[AuditLogResponse])
async def get_task_audit_logs(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get audit logs for a task."""
    logs, _ = crud_pro.get_audit_logs(db, entity_type="task", entity_id=task_id, skip=skip, limit=limit)
    return logs


@app.get("/api/projects/{project_id}/audit-logs", response_model=list[AuditLogResponse])
async def get_project_audit_logs(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get audit logs for a project."""
    logs, _ = crud_pro.get_audit_logs(db, entity_type="project", entity_id=project_id, skip=skip, limit=limit)
    return logs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
