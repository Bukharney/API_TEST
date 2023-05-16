from fastapi import Depends, status, HTTPException, APIRouter
from app import api, oauth2
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


@router.get("/api")
def get_quote(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    symbol = db.query(models.Stock).all()
    for i in symbol:
        res = api.get_quote_symbol(i.symbol)
        if (
            not db.query(models.Turnover)
            .filter(models.Turnover.symbol == i.symbol)
            .first()
        ):
            turnover = models.Turnover(
                symbol=i.symbol,
                pbv=res["pbv"],
                eps=res["eps"],
            )
            db.add(turnover)
            db.commit()
            db.refresh(turnover)
        else:
            update_turnover = (
                db.query(models.Turnover)
                .filter(models.Turnover.symbol == i.symbol)
                .first()
            )
            update_turnover.pbv = res["pbv"]
            update_turnover.eps = res["eps"]
            db.commit()
            db.refresh(update_turnover)

    return {
        "message": "success",
    }
