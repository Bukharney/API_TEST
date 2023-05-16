from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import (
    post,
    user,
    auth,
    vote,
    account,
    stock,
    broker,
    bank_tsc,
    order,
    news,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(account.router)
app.include_router(stock.router)
app.include_router(broker.router)
app.include_router(bank_tsc.router)
app.include_router(order.router)
app.include_router(news.router)


@app.get("/")
def root():
    return "Hello World, from tradekub!"
