from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import redis
from app.core.config import settings
from app.core.security import get_user_id_from_token

redis_client = redis.Redis.from_url(settings.REDIS_URL)

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # Extract user ID from JWT if present
        auth_header = request.headers.get("Authorization", "")
        user_id = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
            user_id = get_user_id_from_token(token)
        if user_id:
            key = f"rl:user:{user_id}"
        else:
            key = f"rl:ip:{request.client.host}"

        now = int(time.time())
        window = now // self.window_seconds
        redis_key = f"{key}:{window}"

        # Increment the count for this window
        count = redis_client.incr(redis_key)
        if count == 1:
            redis_client.expire(redis_key, self.window_seconds)

        if count > self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        response = await call_next(request)
        return response