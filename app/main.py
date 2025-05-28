from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (accounts, auth, bills, forecast, transactions,
                     user_settings, users)
from app.core.audit import register_audit_listeners
from app.core.config import settings
from app.core.database import Base, engine
from app.core.rate_limit import RateLimiterMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

# Allow frontend dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all origins (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(forecast.router)
app.include_router(users.router)

# Register audit listeners
register_audit_listeners()

# Create the database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"msg": f"{settings.PROJECT_NAME} is running"}
