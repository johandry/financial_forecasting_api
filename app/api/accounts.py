from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = models.Account(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/", response_model=list[schemas.Account])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(models.Account).filter(models.Account.deleted_at.is_(None)).all()

@router.delete("/{account_id}", response_model=schemas.Account)
def soft_delete_account(account_id: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(
        models.Account.id == account_id,
        models.Account.deleted_at.is_(None)
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    from datetime import datetime
    account.deleted_at = datetime.utcnow()
    db.commit()
    return account