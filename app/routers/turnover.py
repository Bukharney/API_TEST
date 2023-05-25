from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2, utils
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/turnover", tags=["Turnover"])


@router.get(
    "/",
)
def get_turnover(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    turnover = (
        db.query(models.Turnover)
        .filter(models.Turnover.user_id == current_user.id)
        .first()
    )
    if not turnover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Turnover not found"
        )

    return turnover


@router.get("/api")
def get_quote(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not authorized to access this resource",
        )
    return utils.get_quote(db)


@router.get(
    "/{symbol}",
)
def get_turnover_symbol(
    symbol: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    turnover = (
        db.query(models.Turnover).filter(models.Turnover.symbol == symbol).first()
    )
    if not turnover:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Turnover not found"
        )

    return turnover
