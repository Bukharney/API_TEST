from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy import text
from app import oauth2
from .. import models
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
    news = db.query(models.News).order_by(models.News.news_time.desc()).all()
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
        )
    return news


@router.get("/update", status_code=status.HTTP_200_OK)
def update_news(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    sql = text("DELETE FROM news;")
    db.execute(sql)
    db.commit()

    response1 = api.news_api(country="th", category="business")
    response2 = api.news_api(country="th", category="politics")

    for i in range(len(response1["results"])):
        news = response1["results"][i]
        if not news["description"] != None:
            new_news = models.News(
                topic=news["title"],
                content=news["description"] or "",
                file=news["image_url"],
                news_time=news["pubDate"],
            )
            db.add(new_news)
            db.commit()
            db.refresh(new_news)

    for i in range(len(response2["results"])):
        news = response2["results"][i]
        if news["description"] != None:
            new_news = models.News(
                topic=news["title"],
                content=news["description"] or "",
                file=news["image_url"],
                news_time=news["pubDate"],
            )
            db.add(new_news)
            db.commit()
            db.refresh(new_news)

    return {"message": "News created"}
