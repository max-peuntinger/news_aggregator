import bcrypt
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


@app.get("/articles", response_model=List[Article])
def get_articles():
    articles_collection = db['articles']
    articles = list(articles_collection.find({}))
    
    # Convert ObjectId to string
    for article in articles:
        article['_id'] = str(article['_id'])
    
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