import bcrypt
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List

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

@app.get("/articles", response_model=List[Article])
def get_articles():
    articles_collection = db['articles']
    articles = list(articles_collection.find({}))
    
    # Convert ObjectId to string and published_at to datetime
    for article in articles:
        article['_id'] = str(article['_id'])
        article['published_at'] = parse_date(article['published_at'])
    articles.sort(key=lambda x: x['published_at'], reverse=True)
    for article in articles:
        article['published_at'] = article['published_at'].isoformat()
    
    return articles


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
