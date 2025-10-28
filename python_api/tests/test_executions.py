import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_execution(client: AsyncClient, auth_headers):
    """Test starting a task execution"""
    # Create agent
    agent_response = await client.post(
        "/api/agents",
        json={"name": "Execution Agent", "description": "An agent for execution"},
        headers=auth_headers
    )
    agent_id = agent_response.json()["id"]

    # Create task
    task_response = await client.post(
        "/api/tasks",
        json={
            "title": "Executable Task",
            "description": "A task to execute",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )
    task_id = task_response.json()["id"]

    # Create execution
    response = await client.post(
        "/api/executions",
        json={"task_id": task_id, "agent_id": agent_id},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["task_id"] == task_id
    assert data["agent_id"] == agent_id
    assert data["status"] == "running"


@pytest.mark.anyio
async def test_create_execution_with_unauthorized_agent(client: AsyncClient, auth_headers):
    """Test creating execution with agent not authorized for task"""
    # Create two agents
    agent1_response = await client.post(
        "/api/agents",
        json={"name": "Agent 1", "description": "First agent"},
        headers=auth_headers
    )
    agent1_id = agent1_response.json()["id"]

    agent2_response = await client.post(
        "/api/agents",
        json={"name": "Agent 2", "description": "Second agent"},
        headers=auth_headers
    )
    agent2_id = agent2_response.json()["id"]

    # Create task with only agent1
    task_response = await client.post(
        "/api/tasks",
        json={
            "title": "Restricted Task",
            "description": "Task for agent1 only",
            "supported_agent_ids": [agent1_id]
        },
        headers=auth_headers
    )
    task_id = task_response.json()["id"]

    # Try to execute with agent2
    response = await client.post(
        "/api/executions",
        json={"task_id": task_id, "agent_id": agent2_id},
        headers=auth_headers
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_all_executions(client: AsyncClient, auth_headers):
    """Test getting all executions"""
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
            "title": "Task",
            "description": "A task",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )
    task_id = task_response.json()["id"]

    # Create execution
    await client.post(
        "/api/executions",
        json={"task_id": task_id, "agent_id": agent_id},
        headers=auth_headers
    )

    # Get all executions
    response = await client.get("/api/executions", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.anyio
async def test_get_running_executions(client: AsyncClient, auth_headers):
    """Test getting only running executions"""
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
            "title": "Task",
            "description": "A task",
            "supported_agent_ids": [agent_id]
        },
        headers=auth_headers
    )
    task_id = task_response.json()["id"]

    # Create execution
    await client.post(
        "/api/executions",
        json={"task_id": task_id, "agent_id": agent_id},
        headers=auth_headers
    )

    # Get running executions
    response = await client.get("/api/executions/running", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert all(exec["status"] == "running" for exec in data)
