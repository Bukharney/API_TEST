from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import text
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from newsdataapi import NewsDataApiClient

api = NewsDataApiClient(apikey="pub_2223171d433ff38e0ba97b5fe05231fd2750d")

router = APIRouter(tags=["news"], prefix="/news")


@router.get("/", status_code=status.HTTP_200_OK)
def get_news(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    news = db.query(models.News).order_by(models.News.id.desc()).all()

    return news


@router.get("/reset", status_code=status.HTTP_200_OK)
def get_news(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    sql = text(
        "DROP TABLE IF EXISTS login_logout, stocks, brokers, users, accounts, bank_tsc, orders, transactions, news, turnover, dividend, alembic_version CASCADE;"
    )
    res = db.execute(sql)
    db.commit()
    return res


@router.get("/api", status_code=status.HTTP_200_OK)
def get_news(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    response = api.news_api(country="th", category="business")

    for i in range(10):
        news = response["results"][i]
        new_news = models.News(
            topic=news["title"],
            content=news["description"],
            file=news["image_url"],
            news_time=news["pubDate"],
        )
        db.add(new_news)
        db.commit()
        db.refresh(new_news)
    return {"message": "News created"}
