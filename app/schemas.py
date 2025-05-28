from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr


# ---------- User Schemas ----------
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- Account Schemas ----------
class AccountBase(BaseModel):
    name: str
    type: Optional[str] = None
    current_balance: float = 0.0


class AccountCreate(AccountBase):
    user_id: int


class Account(AccountBase):
    id: int
    user_id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- Bill Schemas ----------
class BillBase(BaseModel):
    """
    Base schema for Bill.
    TODO: Add validation for recurrence rules and support for forecasting.
    """

    name: str
    amount: float
    start_date: datetime
    end_date: Optional[datetime] = None
    recurrence: Optional[str] = None  # e.g., "MONTHLY", "EOM"
    notes: Optional[str] = None


class BillCreate(BillBase):
    account_id: int


class Bill(BillBase):
    id: int
    account_id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- Transaction Schemas ----------
class TransactionBase(BaseModel):
    """
    Base schema for Transaction.
    TODO: Add validation for recurrence and forecasting fields.
    """

    name: str
    amount: float
    date: datetime
    is_recurring: bool = False
    recurrence: Optional[str] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    account_id: int


class Transaction(TransactionBase):
    id: int
    account_id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- UserSettings Schemas ----------
class UserSettingsBase(BaseModel):
    buffer_amount: float = 50.0
    forecast_horizon_months: int = 3


class UserSettingsCreate(UserSettingsBase):
    user_id: int


class UserSettings(UserSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------- Forecast Override Schemas ----------
class ForecastOverrideCreate(BaseModel):
    user_id: int
    account_id: int
    event_type: str  # "bill" or "transaction"
    event_id: int
    event_date: date
    skip: bool = False
    override_amount: Optional[float] = None


class ForecastResponse(BaseModel):
    balances: Dict[str, float]
    alerts: List[str]
    events: List[dict]


class OverrideResponse(BaseModel):
    status: str
    override_id: int
