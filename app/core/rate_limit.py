from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests = {}

    async def dispatch(self, request: Request, call_next):
        user = request.headers.get("Authorization", "anonymous")
        now = int(time.time())
        window = now // self.window_seconds

        key = f"{user}:{window}"
        count = self.user_requests.get(key, 0)
        if count >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        self.user_requests[key] = count + 1

        response = await call_next(request)
        return response