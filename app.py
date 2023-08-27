import bcrypt
from datetime import datetime
from dateutil.parser import parse as parse_date
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient('localhost', 27017)
db = client['news_aggregator']
users_collection = db["users"]

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


def parse_date(date_string): 
    #TODO: articles has mixed types, so this is needed -> should look for simpler solution, maybe transform when inserted to get uniform format
    formats = [
        '%a, %d %b %Y %H:%M:%S %z', # 'Fri, 18 Aug 2023 12:10:00 +0000'
        '%Y-%m-%dT%H:%M:%S%z',      # '2023-08-18T17:20:22+02:00'
        # Add other formats as needed
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Time data {date_string} does not match any known formats")


# @app.get("/articles")
# async def get_articles_page(request: Request):
#     articles_collection = db['articles']
#     articles = list(articles_collection.find({}))
#     # Convert ObjectId to string and published_at to datetime
#     for article in articles:
#         article['_id'] = str(article['_id'])
#         article['published_at'] = parse_date(article['published_at'])
#     articles.sort(key=lambda x: x['published_at'], reverse=True)
#     for article in articles:
#         article['published_at'] = article['published_at'].isoformat()
#     return templates.TemplateResponse("articles.html", {"request": request, "articles": articles})


@app.get("/articles")
async def get_articles_page(request: Request):
    articles_collection = db['articles']
    articles = list(articles_collection.find({}))
    topics = articles_collection.distinct('topic')  # Assuming 'topic' is the field name
    categories = ['All'] + list(set([format_category(topic.split('/').pop()) for topic in topics if topic]))
    for article in articles:
        article['_id'] = str(article['_id'])
        article['published_at'] = parse_date(article['published_at'])
    articles.sort(key=lambda x: x['published_at'], reverse=True)
    for article in articles:
        article['published_at'] = article['published_at'].isoformat()
    return templates.TemplateResponse("articles.html", {"request": request, "articles": articles, "categories": categories})

def format_category(category):
    return category.replace('_', ' ').title()


@app.get("/articles2")
async def get_filtered_articles(request: Request, topic: Optional[str] = None):
    articles_collection = db['articles']
    if topic and topic != 'All':
        formatted_topic = topic.replace(' ', '_').lower()
        articles = list(articles_collection.find({"topic": {"$regex": formatted_topic, "$options": "i"}}))
    else:
        articles = list(articles_collection.find({}))
    for article in articles:
        article['_id'] = str(article['_id'])
        article['published_at'] = parse_date(article['published_at'])
    articles.sort(key=lambda x: x['published_at'], reverse=True)
    for article in articles:
        article['published_at'] = article['published_at'].isoformat()
    return templates.TemplateResponse("articles_list.html", {"request": request, "articles": articles})


@app.get("/articles_list")
async def get_articles2(request: Request, q: Optional[str] = None):
    articles_collection = db['articles']
    
    # If a query is provided, filter articles by title
    if q:
        articles = list(articles_collection.find({"title": {"$regex": q, "$options": "i"}}))
    else:
        articles = list(articles_collection.find({}))
    
    # Convert ObjectId to string and published_at to datetime
    for article in articles:
        article['_id'] = str(article['_id'])
        article['published_at'] = parse_date(article['published_at'])
    
    # Sort articles by published date
    # articles.sort(key=lambda x: x['published_at'], reverse=True)
    
    # Convert datetime back to string for rendering
    for article in articles:
        article['published_at'] = article['published_at'].isoformat()
    
    print(articles)
    return templates.TemplateResponse("articles_list.html", {"request": request, "articles": articles})


class UserRegistration(BaseModel):
    username: str
    email: str
    password: str


@app.post("/register")
def register_user(user: UserRegistration):
    # Check if the user already exists
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # Store user in the database
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    })

    return {"message": "Registration successful"}


class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/login")
def login_user(user: UserLogin):
    # Find the user in the database
    existing_user = users_collection.find_one({"username": user.username})
    if not existing_user:
        raise HTTPException(status_code=400, detail="Username not found")

    # Verify the password
    hashed_password = existing_user["password"]
    if bcrypt.checkpw(user.password.encode('utf-8'), hashed_password):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect password")
