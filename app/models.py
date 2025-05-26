import datetime

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Text)
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
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    recurrence = Column(
        String(50), nullable=True
    )  # e.g., "MONTHLY", "WEEKLY", RRULE string
    end_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    deleted_at = Column(DateTime, nullable=True)

    account = relationship("Account", back_populates="bills")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
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
