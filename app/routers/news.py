import time
from fastapi import Depends, status, HTTPException, APIRouter
from app import oauth2
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from newsdataapi import NewsDataApiClient

# API key authorization, Initialize the client with your API key

api = NewsDataApiClient(apikey="pub_2223171d433ff38e0ba97b5fe05231fd2750d")

# You can pass empty or with request parameters {ex. (country = "us")}

router = APIRouter(tags=["news"], prefix="/news")


@router.get("/", status_code=status.HTTP_200_OK)
def get_news(db: Session = Depends(get_db)):
    news = db.query(models.News).all()
    return news


@router.get("/api", status_code=status.HTTP_200_OK)
def get_news(db: Session = Depends(get_db)):
    response = api.news_api(country="th", category="business")

    for i in range(5):
        news = response["results"][i]
        if news["image_url"]:
            new_news = models.News(
                topic=news["title"],
                content=news["description"],
                file=news["image_url"],
                news_time=news["pubDate"],
            )
            db.add(new_news)
            db.commit()
            db.refresh(new_news)
    return news
