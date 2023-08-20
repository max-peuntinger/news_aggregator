from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient('localhost', 27017)
db = client['news_aggregator']


@app.get("/")
def read_root():
    return {"message": "Welcome to News Aggregator!"}


class Article(BaseModel):
    _id: str
    title: str
    link: str
    summary: str
    topic: str
    published_at: str


@app.get("/articles", response_model=List[Article])
def get_articles():
    articles_collection = db['articles']
    articles = list(articles_collection.find({}))
    
    # Convert ObjectId to string
    for article in articles:
        article['_id'] = str(article['_id'])
    
    return articles

print("app started")