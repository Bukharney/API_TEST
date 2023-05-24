from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import text
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from newsdataapi import NewsDataApiClient

router = APIRouter(prefix="/noti", tags=["Notification"])


@router.get(
    "/{account_id}",
)
def get_notification(
    account_id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == account_id)
        .filter(models.Accounts.user_id == current_user.id)
        .first()
    )
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    noti = (
        db.query(models.Notifications)
        .filter(models.Notifications.account_id == account_id)
        .all()
    )
    if not noti:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )

    return noti


@router.get(
    "/delete/{noti_id}",
)
def delete_notification(
    noti_id: int,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    noti = (
        db.query(models.Notifications)
        .filter(models.Notifications.id == noti_id)
        .first()
    )
    if not noti:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
        )
    db.delete(noti)
    db.commit()
    return {"detail": "Notification deleted"}
