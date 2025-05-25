from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, models
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/", response_model=list[schemas.Transaction])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(models.Transaction).filter(models.Transaction.deleted_at.is_(None)).all()

@router.delete("/{transaction_id}", response_model=schemas.Transaction)
def soft_delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id, models.Transaction.deleted_at.is_(None)).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    from datetime import datetime
    transaction.deleted_at = datetime.utcnow()
    db.commit()
    return transaction