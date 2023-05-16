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
def get_news(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    news = db.query(models.News).order_by(models.News.id.desc()).all()
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
        )
    return news


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
