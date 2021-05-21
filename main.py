from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl, validate_arguments
from db_queries import *
from rss_handler import fetch_rss_feed
from funcs import sync_source_item
from typing import Optional


# uvicorn main:api --reload


api = FastAPI()

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/")
async def root():
    return {"message": "This is Monolith API v0.1"}


@api.get("/test")
async def test():
    # sources = db_article_update(1, type_of_article="report")
    # sources = db_source_update(1)
    # test = {
    #     'source': 1,
    #     'title': "UFOs are coming for all of us",
    #     'url': "https://www.google.com",
    #     'published': "2021-04-09 23:22:39",
    # }
    # sources = db_article_insert(**test)
    test = {
            'name': "Test bla",
            'url': "https://www.google.com/ufo2",
            'last_updated': "2021-04-09 23:22:39",
            'status': 301
        }
    
    sources = db_select_source_alldata(32)
    return sources





# ARTICLES - Get all articles (sorted by date)
@api.get("/articles/recommended")
async def articles_recommended_get():
    articles = db_get_articles()
    return articles


# SOURCES - Get all feeds (sorted by A-Z)
@api.get("/sources")
async def sources_get():
    sources = db_source_select_all()
    return sources


# SOURCES - Get all feeds (sorted by A-Z)
@api.get("/sources/sync")
async def sources_sync():
    
    return True


# SOURCE GET - Get a feed and all its articles
@api.get("/source/{id}")
async def source_get(id: int):
    source = db_get_source_all(id)
    return source



# SOURCE SYNC - Update a feed and add new articles if necessary
@api.put("/source/sync/{id}")
async def source_put(id: int):
    source = db_get_source(id)
    fetched = fetch_rss_feed(source.url)

    # Check if source is up to date
    if source.last_updated == fetched['last_updated']:
        updated_parts = {
            "name": False,
            "description": False,
            "logo": False,
            "status": False,
            "entries": False
        }
        return {"updated": updated_parts}
    else:
        # Check basic info about the source
        synced_name = sync_source_item(source, fetched, 'name')
        synced_description = sync_source_item(source, fetched, 'description')
        synced_logo = sync_source_item(source, fetched, 'logo')
        synced_status = sync_source_item(source, fetched, 'status')
        source.last_updated = fetched['last_updated']
        source.save()

        entries = fetched['entries']
        entries_sorted = sorted(entries, key=lambda item: item.get("published"), reverse=True)
        added_entries = 0

        # Check list of articles and add new ones
        with db.atomic():
            for entry in entries_sorted:
                article_exists = Article.select(Article.id, Article.url).where(Article.url == entry['url']).exists()
                if not article_exists:
                    article_data = entry
                    article_data['source'] = source.id
                    if 'tags' in article_data.keys():
                        article_data['tags'] = str(article_data['tags'])
                    if 'images' in article_data.keys():
                        article_data['images'] = str(article_data['images'])

                    try:
                        temp_article = Article(**article_data)
                        ValidatedArticle.from_orm(temp_article)
                        Article.create(**article_data)
                        added_entries += 1
                    except ValidationError as e:
                        print(e)

        new_entries = True if added_entries > 0 else False

        updated_parts = {
            "name": synced_name,
            "description": synced_description,
            "logo": synced_logo,
            "status": synced_status,
            "entries": new_entries
        }
        source_from_db = db_get_source_all(id)

        return {"updated": updated_parts, "source": source_from_db}


# SOURCE UPDATE - Update basic info about the source
@api.put("/source/{id}")
async def source_sync_put():

    #Update topics, target_audience, relevance, trust

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
@api.delete("/source/{id}")
async def source_delete(id: int):
    deleted_id = db_delete_source(id)
    return {"Deleted Source": deleted_id}


# ARTICLE PUT - Update an article
@api.put("/article/{id}")
async def article_put(id: int, impact: Optional[int] = None, type_of_article: Optional[str] = None, trustworthy: Optional[bool] = None):
    print(impact)
    if impact:
        try:
            updated = db_article_update_impact(id, impact)
        except:
            raise HTTPException(status_code=412, detail="Update not possible")
    if type_of_article:
        try:
            updated = db_article_update_type(id, type_of_article)
        except:
            raise HTTPException(status_code=412, detail="Update not possible")
    if trustworthy != None:
        try:
            updated = db_article_update_trustworthy(id, trustworthy)
        except:
            raise HTTPException(status_code=412, detail="Update not possible")
    return {"Score updated": True}

