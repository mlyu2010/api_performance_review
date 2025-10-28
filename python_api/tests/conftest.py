import pytest
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise
from app import app
from app.models.user import User


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function", autouse=True)
async def initialize_tests():
    await Tortoise.init(
        db_url="sqlite://:memory:",
        modules={"models": ["app.models"]}
    )
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user():
    """Create a test user"""
    user = await User.create(
        username="testuser",
        email="test@example.com",
        hashed_password=User.get_password_hash("testpassword")
    )
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, test_user):
    """Get authentication headers with JWT token"""
    response = await client.post(
        "/api/login",
        json={"username": "testuser", "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing endpoints without authentication"""
    response = await client.get("/api/agents")
    assert response.status_code == 401
