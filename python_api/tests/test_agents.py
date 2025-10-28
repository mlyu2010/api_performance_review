import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_agent(client: AsyncClient, auth_headers):
    """Test creating a new agent"""
    response = await client.post(
        "/api/agents",
        json={"name": "Test Agent", "description": "A test agent"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"
    assert data["description"] == "A test agent"
    assert "id" in data


@pytest.mark.anyio
async def test_get_all_agents(client: AsyncClient, auth_headers):
    """Test getting all agents"""
    # Create test agents
    await client.post(
        "/api/agents",
        json={"name": "Agent 1", "description": "First agent"},
        headers=auth_headers
    )
    await client.post(
        "/api/agents",
        json={"name": "Agent 2", "description": "Second agent"},
        headers=auth_headers
    )

    response = await client.get("/api/agents", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.anyio
async def test_get_agent_by_id(client: AsyncClient, auth_headers):
    """Test getting agent by ID"""
    # Create agent
    create_response = await client.post(
        "/api/agents",
        json={"name": "Test Agent", "description": "A test agent"},
        headers=auth_headers
    )
    agent_id = create_response.json()["id"]

    response = await client.get(f"/api/agents/{agent_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == "Test Agent"


@pytest.mark.anyio
async def test_update_agent(client: AsyncClient, auth_headers):
    """Test updating an agent"""
    # Create agent
    create_response = await client.post(
        "/api/agents",
        json={"name": "Original Name", "description": "Original description"},
        headers=auth_headers
    )
    agent_id = create_response.json()["id"]

    # Update agent
    response = await client.put(
        f"/api/agents/{agent_id}",
        json={"name": "Updated Name"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


@pytest.mark.anyio
async def test_delete_agent(client: AsyncClient, auth_headers):
    """Test soft deleting an agent"""
    # Create agent
    create_response = await client.post(
        "/api/agents",
        json={"name": "To Delete", "description": "Will be deleted"},
        headers=auth_headers
    )
    agent_id = create_response.json()["id"]

    # Delete agent
    response = await client.delete(f"/api/agents/{agent_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify agent is not accessible
    get_response = await client.get(f"/api/agents/{agent_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing endpoints without authentication"""
    response = await client.get("/api/agents")
    assert response.status_code == 401
