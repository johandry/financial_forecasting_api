from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models import User, Account, UserSettings
from app.core.database import SessionLocal, engine, Base

def seed():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash('$3cr3tP@a55w0rd!')
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    if not db.query(User).first():
        user = User(email="johandry@example.com", hashed_password=hashed_password, is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        account = Account(user_id=user.id, name="Checking", type="checking", current_balance=1000)
        db.add(account)
        settings = UserSettings(user_id=user.id, buffer_amount=50.0, forecast_horizon_months=3)
        db.add(settings)
        db.commit()
    db.close()

if __name__ == "__main__":
    seed()