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
    return {"message": "This is Monolith API v0.1.8"}


@api.get("/test")
async def test():
    sources = db_select_source_alldata(32)
    return sources


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FEEDS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@api.get("/feeds/collection")
async def feeds_collection(topic_id, order_by: Optional[str] = 'latest'):
    sources = db_sourcetopic_select_topic_sources(topic_id)
    articles = [db_article_select_list_by_source(src['id'], order_by) for src in sources]
    return articles


@api.get("/feeds/source")
async def feeds_source(source_id, order_by: Optional[str] = 'latest'):
    source = db_source_select(source_id)
    source['topics'] = db_sourcetopic_select_source_topics(source_id)
    source['articles'] = db_article_select_list_by_source(source_id, order_by)
    return source


@api.get("/feeds/tag")
async def feeds_tag(topic_id, order_by: Optional[str] = 'latest'):
    articles = db_articletopic_select_topic_articles(topic_id)
    return articles


@api.get("/feeds/today")
async def feeds_today(order_by: Optional[str] = 'latest'):
    articles = db_article_select_today()
    return articles


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# REFERENCES
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@api.get("/references/sources")
async def references_sources(featured: Optional[bool] = False):
    if featured:
        sources = db_source_select_all()
        return []
    else:
        sources = db_source_select_all()
        return sources


@api.get("/references/collections")
async def references_collections(featured: Optional[bool] = False):
    if featured:
        return []
    else:
        collections = []
        topic_ids_with_sources = [s.topic_id for s in SourceTopic.select()]
        topic_ids = set(topic_ids_with_sources)
        for topic_id in topic_ids:
            topic = db_topic_select(topic_id)
            topic['sources'] = db_sourcetopic_select_topic_sources(topic_id)
            collections.append(topic)
        return collections


@api.get("/references/tags")
async def references_tags(featured: Optional[bool] = False):
    if featured:
        return []
    else:
        tags = []
        topic_ids_with_sources = [s.topic_id for s in ArticleTopic.select()]
        topic_ids = set(topic_ids_with_sources)
        for topic_id in topic_ids:
            topic = db_topic_select(topic_id)
            tags.append(topic)
        return tags


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SEARCH
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@api.get("/search/articles")
async def search_articles(query):
    results = db_search_articles(query)
    return results


@api.get("/search/sources")
async def search_feeds(query):
    results = db_search_feeds(query)
    return results


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONTENT
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@api.get("/content/article")
async def content_article(article_id):
    article = db_article_select(article_id)
    return article



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++