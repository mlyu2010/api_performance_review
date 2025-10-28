"""
Rate Limiter Middleware Module
=============================

This module provides a middleware implementation for rate limiting requests in FastAPI applications.
It tracks requests per client IP address and enforces request limits within specified time windows.

Features:
- IP-based rate limiting
- Configurable request limits and time windows
- Automatic cleanup of expired request records
- Bypass for API documentation endpoints
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for implementing rate limiting based on client IP addresses.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance
    calls_limit : int, optional
        Maximum number of requests allowed per time window (default: 100)
    time_window : int, optional
        Time window in seconds for rate limiting (default: 60)

    Examples
    --------
    Add middleware to FastAPI app:
        app = FastAPI()
        app.add_middleware(RateLimitMiddleware, calls_limit=100, time_window=60)
    """

    def __init__(self, app, calls_limit: int = 100, time_window: int = 60):
        super().__init__(app)
        self.calls_limit = calls_limit
        self.time_window = time_window
        self.clients = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        """
        Process incoming requests and apply rate limiting.

        Parameters
        ----------
        request : Request
            The incoming HTTP request
        call_next : Callable
            The next middleware or route handler in the chain

        Returns
        -------
        Response
            The HTTP response from the next handler

        Raises
        ------
        HTTPException
            When rate limit is exceeded (HTTP 429)
        """
        # Skip rate limiting for docs endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        client_ip = request.client.host
        current_time = time.time()

        # Clean old timestamps
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if current_time - timestamp < self.time_window
        ]

        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.calls_limit} requests per {self.time_window} seconds."
            )

        # Add current request timestamp
        self.clients[client_ip].append(current_time)

        response = await call_next(request)
        return response
