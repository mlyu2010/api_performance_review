import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_task_with_single_agent(client: AsyncClient, auth_headers):
    """Test creating a task with a single agent"""
    # Create agent
    agent_response = await client.post(
        "/api/agents",
        json={"name": "Task Agent", "description": "An agent for tasks"},
        headers=auth_headers
    )
    agent_id = agent_response.json()["id"]

    # Create task
    response = await client.post(
        "/api/tasks",
        json={
            "title": "Test Task",
            "description": "A test task",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert len(data["agents"]) == 1
    assert data["agents"][0]["id"] == agent_id


@pytest.mark.anyio
async def test_create_task_with_multiple_agents(client: AsyncClient, auth_headers):
    """Test creating a task with multiple agents"""
    # Create agents
    agent1_response = await client.post(
        "/api/agents",
        json={"name": "Agent 1", "description": "First agent"},
        headers=auth_headers
    )
    agent2_response = await client.post(
        "/api/agents",
        json={"name": "Agent 2", "description": "Second agent"},
        headers=auth_headers
    )
    agent_ids = [agent1_response.json()["id"], agent2_response.json()["id"]]

    # Create task
    response = await client.post(
        "/api/tasks",
        json={
            "title": "Multi-Agent Task",
            "description": "A task for multiple agents",
            "supported_agent_ids": agent_ids
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["agents"]) == 2


@pytest.mark.anyio
async def test_create_task_with_invalid_agent(client: AsyncClient, auth_headers):
    """Test creating a task with non-existent agent"""
    response = await client.post(
        "/api/tasks",
        json={
            "title": "Invalid Task",
            "description": "Task with invalid agent",
            "supported_agent_ids": [9999]
        },
        headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_all_tasks(client: AsyncClient, auth_headers):
    """Test getting all tasks"""
    # Create agent and task
    agent_response = await client.post(
        "/api/agents",
        json={"name": "Agent", "description": "An agent"},
        headers=auth_headers
    )
    agent_id = agent_response.json()["id"]

    await client.post(
        "/api/tasks",
        json={
            "title": "Task 1",
            "description": "First task",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )

    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.anyio
async def test_update_task(client: AsyncClient, auth_headers):
    """Test updating a task"""
    # Create agent and task
    agent_response = await client.post(
        "/api/agents",
        json={"name": "Agent", "description": "An agent"},
        headers=auth_headers
    )
    agent_id = agent_response.json()["id"]

    task_response = await client.post(
        "/api/tasks",
        json={
            "title": "Original Task",
            "description": "Original description",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )
    task_id = task_response.json()["id"]

    # Update task
    response = await client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Updated Task"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"


@pytest.mark.anyio
async def test_delete_task(client: AsyncClient, auth_headers):
    """Test soft deleting a task"""
    # Create agent and task
    agent_response = await client.post(
        "/api/agents",
        json={"name": "Agent", "description": "An agent"},
        headers=auth_headers
    )
    agent_id = agent_response.json()["id"]

    task_response = await client.post(
        "/api/tasks",
        json={
            "title": "To Delete",
            "description": "Will be deleted",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )
    task_id = task_response.json()["id"]

    # Delete task
    response = await client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify task is not accessible
    get_response = await client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_response.status_code == 404
