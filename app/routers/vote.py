from fastapi import Depends, status, HTTPException, APIRouter

from app.database import SessionLocal, get_db
from .. import models, schemas, database, oauth2

router = APIRouter(prefix="/votes", tags=["Votes"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(
    vote: schemas.Vote,
    db: SessionLocal = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post with given id not found"
        )
    vote_query = (
        db.query(models.Vote)
        .filter(models.Vote.post_id == vote.post_id)
        .filter(models.Vote.user_id == current_user.id)
    )

    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vote already votes",
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        return {"message": "Vote created successfully"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote not found",
            )
        db.delete(found_vote)
        db.commit()
        return {"message": "Vote deleted successfully"}
