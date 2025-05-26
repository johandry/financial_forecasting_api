from fastapi import FastAPI

from app.api import accounts, auth, bills, transactions, user_settings
from app.core.audit import register_audit_listeners
from app.core.config import settings
from app.core.rate_limit import RateLimiterMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

# Add rate limiting middleware
app.add_middleware(RateLimiterMiddleware, max_requests=100, window_seconds=60)

# Include routers for each API module
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(bills.router, prefix="/bills", tags=["bills"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(
    user_settings.router, prefix="/user_settings", tags=["user_settings"]
)

# Register audit listeners
register_audit_listeners()


@app.get("/")
def read_root():
    return {"msg": f"{settings.PROJECT_NAME} is running"}
