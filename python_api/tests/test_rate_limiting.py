import pytest
from httpx import AsyncClient
from fastapi.exceptions import HTTPException


@pytest.mark.anyio
async def test_rate_limiting(client: AsyncClient, auth_headers):
    """Test that rate limiting works"""
    # Note: This test may need adjustment based on actual rate limit settings
    # Making many requests quickly to trigger rate limit
    responses = []
    rate_limit_hit = False

    for _ in range(150):  # Exceeds default limit of 100
        try:
            response = await client.get("/api/agents", headers=auth_headers)
            responses.append(response.status_code)
        except HTTPException as e:
            if e.status_code == 429:
                rate_limit_hit = True
                responses.append(429)
            else:
                raise

    # Should have at least one 429 (Too Many Requests) response
    assert 429 in responses or rate_limit_hit, "Rate limiting did not trigger as expected"
