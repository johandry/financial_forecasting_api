from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=schemas.UserSettings)
def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    settings = (
        db.query(models.UserSettings)
        .filter(
            models.UserSettings.user_id == user_id,
            models.UserSettings.deleted_at.is_(None),
        )
        .first()
    )
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings


@router.put("/", response_model=schemas.UserSettings)
def update_user_settings(
    user_id: int,
    settings_update: schemas.UserSettingsBase,
    db: Session = Depends(get_db),
):
    settings = (
        db.query(models.UserSettings)
        .filter(
            models.UserSettings.user_id == user_id,
            models.UserSettings.deleted_at.is_(None),
        )
        .first()
    )
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    for field, value in settings_update.model_dump().items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
