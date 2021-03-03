from fastapi import FastAPI, HTTPException
from pydantic import HttpUrl, validate_arguments
from db_queries import *
from rss_handler import fetch_rss_feed


api = FastAPI()

@api.get("/")
async def root():
    return {"message": "This is Monolith API v0.1"}


# ARTICLES - Get all articles (sorted by date)
@api.get("/articles")
async def articles_get():
    articles = db_get_articles()
    return articles


# SOURCES - Get all feeds (sorted by A-Z)
@api.get("/sources")
async def sources_get():
    sources = db_get_sources()
    return sources


# SOURCE GET - Get a feed and all its articles
@api.get("/source/{id}")
async def source_get(id: int):
    source = db_get_source(id)
    return source.__data__


# SOURCE PUT - Update a feed and add new articles if necessary
@api.put("/source/{id}")
async def source_put():
    source = db_get_source(id)
    fetched = fetch_rss_feed(source.url)
    
    return {"message": "This is Monolith API v0.1"}


# SOURCE POST - Add new feed and all its articles
@validate_arguments
@api.post("/source")
async def source_post(url: HttpUrl, origin: str, topics: str):
    if db_source_exists(url) is False: # Check feed url doesn't exist in DB already
        fetched = fetch_rss_feed(url) # Call RSS handler, extract and format data
        if fetched["valid_feed"]:
            fetched['origin'] = origin
            fetched['topics'] = topics
            source_in_db_id = db_insert_source(fetched) # Insert into DB
            return source_in_db_id
        else:
            raise HTTPException(status_code=412, detail="The url is not a valid RSS feed or the feed's format is not supported.")
    else:
        raise HTTPException(status_code=412, detail="Url already exists in DB")



# SOURCE DELETE - Delete a feed and all its articles
@api.delete("/source")
async def source_delete():
    return {"message": "This is Monolith API v0.1"}


# ARTICLE PUT - Update an article
@api.put("/article")
async def article_put():
    return {"message": "This is Monolith API v0.1"}


# uvicorn main:api --reload