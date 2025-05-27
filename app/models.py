import datetime

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Float,
                        ForeignKey, Integer, String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    deleted_at = Column(DateTime, nullable=True)

    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=True)
    current_balance = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="accounts")
    bills = relationship("Bill", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship(
        "Transaction", back_populates="account", cascade="all, delete-orphan"
    )


class Bill(Base):
    """
    Represents a bill, which may be recurring.
    TODO: Implement recurrence expansion logic for forecasting.
    """

    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    recurrence = Column(String(20), nullable=True)  # e.g., "MONTHLY", "EOM"
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    deleted_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="bills")


class Transaction(Base):
    """
    Represents a transaction, which may be recurring.
    TODO: Implement recurrence and forecasting logic for recurring transactions.
    """

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurrence = Column(String(20), nullable=True)  # e.g., "MONTHLY", "EOM"
    end_date = Column(DateTime, nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    deleted_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="transactions")


class UserSettings(Base):
    __tablename__ = "user_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    buffer_amount = Column(Float, default=50.0)
    forecast_horizon_months = Column(Integer, default=3)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="settings")


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    table_name = Column(String(50), nullable=False)
    row_id = Column(Integer, nullable=False)
    action = Column(String(20), nullable=False)  # e.g., "CREATE", "UPDATE", "DELETE"
    timestamp = Column(DateTime, server_default=func.now())
    diff = Column(JSON, nullable=True)  # Store changes as JSON
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="audit_logs")


class ForecastOverride(Base):
    __tablename__ = "forecast_overrides"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    event_type = Column(String, nullable=False)  # "bill" or "transaction"
    event_id = Column(Integer, nullable=False)  # Bill or Transaction ID
    event_date = Column(Date, nullable=False)  # Date to skip/override
    skip = Column(Boolean, default=False)  # If True, skip this event
    override_amount = Column(Float, nullable=True)  # If set, use this amount instead

    user = relationship("User")
    account = relationship("Account")
