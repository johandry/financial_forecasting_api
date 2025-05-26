from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.Bill)
def create_bill(bill: schemas.BillCreate, db: Session = Depends(get_db)):
    db_bill = models.Bill(**bill.model_dump())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("/", response_model=list[schemas.Bill])
def list_bills(db: Session = Depends(get_db)):
    return db.query(models.Bill).filter(models.Bill.deleted_at.is_(None)).all()


@router.delete("/{bill_id}", response_model=schemas.Bill)
def soft_delete_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = (
        db.query(models.Bill)
        .filter(models.Bill.id == bill_id, models.Bill.deleted_at.is_(None))
        .first()
    )
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    from datetime import datetime, timezone

    bill.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return bill
