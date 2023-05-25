from typing import List
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import func
from app import oauth2, utils
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get(
    "/{account_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.PortfolioOut],
)
def get_portfolio(
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
    result = utils.get_portfolio(db=db, account_id=account_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
        )

    return result
