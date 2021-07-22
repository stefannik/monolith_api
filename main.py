from copy import Error
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl, validate_arguments
from db_queries import *
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
    return {"message": "This is Monolith API v0.1.18"}


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FEEDS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@api.get("/feeds/recent")
async def feeds_recent(timeframe: int, limit: Optional[int] = 50, order_by: Optional[str] = 'relevance'):
    feed = db_article_select_recent(timeframe, limit, order_by)
    return feed


@api.get("/feeds/source")
async def feeds_source(source_id: int, page: Optional[int] = 1, ids: Optional[str] = '0', order_by: Optional[str] = 'latest'):
    payload = {'page': page}

    if page == 1:
        articles = db_source_articles(source_id, order_by)
        payload['articles'] = articles[:50]
        payload['feed_ids'] = [a['id'] for a in articles]
        return payload
    else:
        payload['feed_ids'] = [int(id) for id in ids.split(',')],
        end = (page*50)
        start = end-50
        page_ids = payload['feed_ids'][start:end]
        payload['articles'] = db_article_select_list(page_ids, order_by)
        return payload


@api.get("/feeds/topic")
async def feeds_topic(topic_id, timeframe: int, limit: Optional[int] = 50, order_by: Optional[str] = 'relevance'):
    payload = {
        "topic": db_topic_select(topic_id),
        "sources": db_sourcetopic_select_topic_sources(topic_id),
    }
    sources_ids = [src['id'] for src in payload['sources']]
    payload['articles'] = db_sourcearticle_select_multi(sources_ids, timeframe, limit, order_by)
    return payload


@api.get("/feeds/tag")
async def feeds_tag(topic_id, timeframe: int, limit: Optional[int] = 50, order_by: Optional[str] = 'relevance'):
    payload = {
        "topic": db_topic_select(topic_id),
        "sources": db_sourcetopic_select_topic_sources(topic_id),
    }
    sources_ids = [src['id'] for src in payload['sources']]
    payload['articles'] = db_sourcearticle_select_multi(sources_ids, timeframe, limit, order_by)
    return payload



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


@api.get("/references/topics")
async def references_topics(featured: Optional[bool] = False):
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
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SCHEDULER
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# from fastapi_utils.tasks import repeat_every
# from update_deamon import SourceUpdater
# import time

# @api.on_event("startup")
# @repeat_every(seconds=10, wait_first=2)
# def periodic():
#     # 1. Repeat every 10 seconds
#     # 2. Check every source for avg_update_time * 20% distance from now
#     # 3. Queue update
    
#     sources = [src['id'] for src in db_source_full_list()]

#     for src_id in sources:
#         print("UPDATING ", src_id)
#         src = SourceUpdater(src_id)
#         src.setup()
#         src.run()

