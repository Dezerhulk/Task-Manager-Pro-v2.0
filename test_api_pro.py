"""API endpoint tests for Task Manager Pro."""

import pytest


class TestUserAPI:
    """User API endpoint tests."""
    
    def test_create_user(self, client, test_user_data):
        """Test creating a user via API."""
        response = client.post("/api/users", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    def test_get_user(self, client, test_user_data):
        """Test getting user details."""
        # Create user first
        response = client.post("/api/users", json=test_user_data)
        user_id = response.json()["id"]
        
        # Get user
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/api/users/99999")
        assert response.status_code == 404
    
    def test_get_users_pagination(self, client, test_user_data):
        """Test getting users list with pagination."""
        # Create users
        for i in range(3):
            data = test_user_data.copy()
            data["username"] = f"user{i}"
            data["email"] = f"user{i}@example.com"
            client.post("/api/users", json=data)
        
        # Get users
        response = client.get("/api/users?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) <= 2
    
    def test_update_user(self, client, test_user_data):
        """Test updating user."""
        # Create user
        response = client.post("/api/users", json=test_user_data)
        user_id = response.json()["id"]
        
        # Update user
        update_data = {"username": "newusername"}
        response = client.put(f"/api/users/{user_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"
    
    def test_delete_user(self, client, test_user_data):
        """Test deleting user."""
        # Create user
        response = client.post("/api/users", json=test_user_data)
        user_id = response.json()["id"]
        
        # Delete user
        response = client.delete(f"/api/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True


class TestProjectAPI:
    """Project API endpoint tests."""
    
    def test_create_project(self, client, test_user_data, test_project_data):
        """Test creating a project."""
        # Create user first
        user_response = client.post("/api/users", json=test_user_data)
        owner_id = user_response.json()["id"]
        
        # Create project
        response = client.post(f"/api/projects?owner_id={owner_id}", json=test_project_data)
        assert response.status_code == 200
        assert response.json()["title"] == test_project_data["title"]
    
    def test_get_project(self, client, test_user_data, test_project_data):
        """Test getting project."""
        # Create user and project
        user_response = client.post("/api/users", json=test_user_data)
        owner_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={owner_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        # Get project
        response = client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200
        assert response.json()["id"] == project_id
    
    def test_get_all_projects(self, client, test_user_data, test_project_data):
        """Test getting all projects."""
        response = client.get("/api/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_search_projects(self, client, test_user_data, test_project_data):
        """Test searching projects."""
        # Create project first
        user_response = client.post("/api/users", json=test_user_data)
        owner_id = user_response.json()["id"]
        client.post(f"/api/projects?owner_id={owner_id}", json=test_project_data)
        
        # Search
        response = client.post("/api/projects/search", json={"search": "Test"})
        assert response.status_code == 200
    
    def test_update_project(self, client, test_user_data, test_project_data):
        """Test updating project."""
        # Create user and project
        user_response = client.post("/api/users", json=test_user_data)
        owner_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={owner_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        # Update project
        update_data = {"title": "Updated Title"}
        response = client.put(f"/api/projects/{project_id}?user_id={owner_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"
    
    def test_delete_project(self, client, test_user_data, test_project_data):
        """Test deleting project."""
        # Create user and project
        user_response = client.post("/api/users", json=test_user_data)
        owner_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={owner_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        # Delete project
        response = client.delete(f"/api/projects/{project_id}?user_id={owner_id}")
        assert response.status_code == 200
        assert response.json()["deleted"] is True
    
    def test_add_project_member(self, client, test_user_data, test_project_data):
        """Test adding project member."""
        # Create users
        user1_response = client.post("/api/users", json=test_user_data)
        user1_id = user1_response.json()["id"]
        
        user2_data = test_user_data.copy()
        user2_data["username"] = "user2"
        user2_data["email"] = "user2@example.com"
        user2_response = client.post("/api/users", json=user2_data)
        user2_id = user2_response.json()["id"]
        
        # Create project
        project_response = client.post(f"/api/projects?owner_id={user1_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        # Add member
        response = client.post(f"/api/projects/{project_id}/members/{user2_id}?actor_id={user1_id}")
        assert response.status_code == 200


class TestTaskAPI:
    """Task API endpoint tests."""
    
    def test_create_task(self, client, test_user_data, test_project_data, test_task_data):
        """Test creating a task."""
        # Create user and project
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        # Create task
        task_data = {**test_task_data, "project_id": project_id}
        response = client.post(f"/api/tasks?creator_id={user_id}", json=task_data)
        assert response.status_code == 200
        assert response.json()["title"] == test_task_data["title"]
    
    def test_get_task(self, client, test_user_data, test_project_data, test_task_data):
        """Test getting task."""
        # Setup
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        task_data = {**test_task_data, "project_id": project_id}
        task_response = client.post(f"/api/tasks?creator_id={user_id}", json=task_data)
        task_id = task_response.json()["id"]
        
        # Get task
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id
    
    def test_get_project_tasks(self, client, test_user_data, test_project_data, test_task_data):
        """Test getting project tasks."""
        # Setup
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        # Get tasks
        response = client.get(f"/api/projects/{project_id}/tasks")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_search_tasks(self, client, test_user_data, test_project_data, test_task_data):
        """Test searching tasks."""
        response = client.post("/api/tasks/search", json={})
        assert response.status_code == 200
    
    def test_update_task(self, client, test_user_data, test_project_data, test_task_data):
        """Test updating task."""
        # Setup
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        task_data = {**test_task_data, "project_id": project_id}
        task_response = client.post(f"/api/tasks?creator_id={user_id}", json=task_data)
        task_id = task_response.json()["id"]
        
        # Update task
        update_data = {"status": "in_progress"}
        response = client.put(f"/api/tasks/{task_id}?user_id={user_id}", json=update_data)
        assert response.status_code == 200
    
    def test_delete_task(self, client, test_user_data, test_project_data, test_task_data):
        """Test deleting task."""
        # Setup
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        task_data = {**test_task_data, "project_id": project_id}
        task_response = client.post(f"/api/tasks?creator_id={user_id}", json=task_data)
        task_id = task_response.json()["id"]
        
        # Delete task
        response = client.delete(f"/api/tasks/{task_id}?user_id={user_id}")
        assert response.status_code == 200


class TestCommentAPI:
    """Comment API endpoint tests."""
    
    def test_create_comment(self, client, test_user_data, test_project_data, test_task_data, test_comment_data):
        """Test creating a comment."""
        # Setup
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        task_data = {**test_task_data, "project_id": project_id}
        task_response = client.post(f"/api/tasks?creator_id={user_id}", json=task_data)
        task_id = task_response.json()["id"]
        
        # Create comment
        response = client.post(f"/api/tasks/{task_id}/comments?user_id={user_id}", json=test_comment_data)
        assert response.status_code == 200
    
    def test_get_task_comments(self, client, test_user_data, test_project_data, test_task_data):
        """Test getting task comments."""
        # Setup
        user_response = client.post("/api/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        project_response = client.post(f"/api/projects?owner_id={user_id}", json=test_project_data)
        project_id = project_response.json()["id"]
        
        task_data = {**test_task_data, "project_id": project_id}
        task_response = client.post(f"/api/tasks?creator_id={user_id}", json=task_data)
        task_id = task_response.json()["id"]
        
        # Get comments
        response = client.get(f"/api/tasks/{task_id}/comments")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestTagAPI:
    """Tag API endpoint tests."""
    
    def test_create_tag(self, client, test_tag_data):
        """Test creating a tag."""
        response = client.post("/api/tags", json=test_tag_data)
        assert response.status_code == 200
        assert response.json()["name"] == test_tag_data["name"]
    
    def test_get_tag(self, client, test_tag_data):
        """Test getting tag."""
        # Create tag
        tag_response = client.post("/api/tags", json=test_tag_data)
        tag_id = tag_response.json()["id"]
        
        # Get tag
        response = client.get(f"/api/tags/{tag_id}")
        assert response.status_code == 200
        assert response.json()["id"] == tag_id
    
    def test_get_all_tags(self, client):
        """Test getting all tags."""
        response = client.get("/api/tags")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestHealthAndRoot:
    """Health and root endpoint tests."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
