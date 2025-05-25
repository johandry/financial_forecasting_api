from fastapi import FastAPI
from app.core.config import settings
from app.api import bills, transactions, auth, accounts, user_settings
from app.core.rate_limit import RateLimiterMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

# Add rate limiting middleware
app.add_middleware(RateLimiterMiddleware, max_requests=100, window_seconds=60)

# Include routers for each API module
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(bills.router, prefix="/bills", tags=["bills"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(user_settings.router, prefix="/user_settings", tags=["user_settings"])

@app.get("/")
def read_root():
    return {"msg": f"{settings.PROJECT_NAME} is running"}