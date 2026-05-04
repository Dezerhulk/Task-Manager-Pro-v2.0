"""Authorization and permission checking utilities."""

from enum import Enum
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .models_pro import User, UserRoleEnum, Project, Task


class PermissionError(HTTPException):
    """Custom permission error."""
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


async def check_user_exists(db: Session, user_id: int) -> User:
    """Check if user exists, raise 404 if not."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


async def check_project_access(
    db: Session, project_id: int, user_id: int, require_owner: bool = False
) -> Project:
    """Check if user has access to project.
    
    Args:
        db: Database session
        project_id: Project ID
        user_id: Current user ID
        require_owner: If True, user must be owner
        
    Returns:
        Project object
        
    Raises:
        404 if project not found
        403 if user doesn't have access
    """
    project = db.query(Project).filter(Project.id == project_id, Project.is_deleted == False).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    user = db.query(User).filter(User.id == user_id).first()

    # Admin can access any project
    if user and user.role == UserRoleEnum.admin:
        return project

    # Owner always has access
    if project.owner_id == user_id:
        return project

    # If owner is required but user is not owner
    if require_owner:
        raise PermissionError("Only project owner can perform this action")

    # Check if user is project member
    is_member = any(m.user_id == user_id for m in project.members)
    if not is_member:
        raise PermissionError("You don't have access to this project")

    return project


async def check_task_access(
    db: Session, task_id: int, user_id: int, require_creator: bool = False
) -> Task:
    """Check if user has access to task.
    
    Args:
        db: Database session
        task_id: Task ID
        user_id: Current user ID
        require_creator: If True, user must be creator
        
    Returns:
        Task object
        
    Raises:
        404 if task not found
        403 if user doesn't have access
    """
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    user = db.query(User).filter(User.id == user_id).first()

    # Admin can access any task
    if user and user.role == UserRoleEnum.admin:
        return task

    # Task creator has access
    if task.creator_id == user_id:
        return task

    # If creator is required but user is not creator
    if require_creator:
        raise PermissionError("Only task creator can perform this action")

    # Assignee has access
    if task.assignee_id == user_id:
        return task

    # Check if user is member of task's project
    project = task.project
    is_member = any(m.user_id == user_id for m in project.members)

    if not is_member:
        raise PermissionError("You don't have access to this task")

    return task


async def require_role(user: User, required_role: UserRoleEnum) -> None:
    """Check if user has required role.
    
    Raises:
        403 if user doesn't have required role
    """
    if user.role not in [UserRoleEnum.admin, required_role]:
        raise PermissionError(f"This action requires {required_role.value} role")


async def require_admin(user: User) -> None:
    """Check if user is admin.
    
    Raises:
        403 if user is not admin
    """
    if user.role != UserRoleEnum.admin:
        raise PermissionError("Admin access required")
