from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models import User
from app.schemas import UserCreate

router = APIRouter()


@router.get(
    "/users",
    summary="List all users",
    description="Returns a list of all users in the system.",
    response_description="A list of user objects.",
)
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.post(
    "/users",
    summary="Create a new user",
    description="""
Create a new user with an email and password.

**Example request:**
```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```
""",
    response_description="The created user object.",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    user_obj = User(email=user.email, hashed_password=hashed_password)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj
