import enum
from db_models import SourceTopic, ArticleTopic, db, Source, ValidatedSource, Article, ValidatedArticle, Topic, ValidatedTopic
from pydantic import ValidationError
from peewee import IntegrityError
from datetime import datetime
import numpy as np


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SOURCE TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_source_select_all():
    sources = {'data': {}}
    templist = np.array([w.topics for w in Source.select()])
    sources['topics'] = list(np.unique(templist))

    for src in Source.select().order_by(Source.id):
        data = {
            'id': src.id,
            'name': src.name,
            'url': src.url,
            'last_updated': src.last_updated,
            'description': src.description,
            'logo': src.logo,
        }
        sources['data'][src.id] = data
    return sources


def db_source_select_list(list_of_source_ids):
    sources = []
    for source_id in list_of_source_ids:
        query = Source.get_by_id(source_id)
        sources.append(query.__data__)
    return sources


def db_source_select(source_id):
    source = Source.get_by_id(source_id)
    return source.__data__


def db_source_update(source_id, **fields):
    query = Source.update(fields).where(Source.id == source_id)
    query.execute()
    return 0


def db_source_insert(**fields):
    # required fields: name, url, last_updated, status
    insert_source = Source.insert(fields).execute()
    return insert_source


def db_source_delete(source_id):
    source = Source.get_by_id(source_id)
    deleted = source.delete_instance(recursive=True)
    return deleted


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ARTICLE TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_article_select_list(list_of_article_ids):
    articles = []
    for art_id in list_of_article_ids:
        query = Article.get_by_id(art_id)
        articles.append(query.__data__)
    return articles


def db_article_select_list_by_source(source_id):
    # sort & filter, add topics field
    # query = Article.select().where(Article.source == source_id).order_by(Article.published.desc())
    # return [transform_article(art) for art in query]
    source_articles = Source.get_by_id(source_id).articles
    return [article.__data__ for article in source_articles]


def db_article_select(article_id):
    article = Article.get_by_id(article_id)
    return article.__data__


def db_article_update(article_id, **fields):
    query = Article.update(fields).where(Article.id == article_id)
    query.execute()
    return True


def db_article_insert(**fields):
    # required fields: source_id, url, published, title
    insert_article = Article.insert(fields).execute()
    return insert_article


def db_article_bulk_insert(list_of_articles):
    inserted_articles = []
    with db.atomic():
        for article_data in list_of_articles:
            article_id = Article.create(**article_data)
            inserted_articles.append(article_id.__data__)
    return inserted_articles


def db_article_delete(article_id):
    article = Article.get_by_id(article_id)
    deleted = article.delete_instance(recursive=True)
    return deleted


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TOPIC TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_topic_select_all():
    topics = Topic.select().order_by(Topic.name)
    return [t.__data__ for t in topics]


def db_topic_select_list(list_of_topic_ids):
    topics = []
    for topic_id in list_of_topic_ids:
        query = Topic.get_by_id(topic_id)
        topics.append(query.__data__)
    return topics


def db_topic_select(topic_id):
    topic = Topic.get_by_id(topic_id)
    return topic.__data__


def db_topic_insert(**fields):
    try:
        insert_topic = Topic.insert(fields).execute()
        return insert_topic
    except IntegrityError:
        return {"ERROR": "The required values were not provided."}


def db_topic_delete(topic_id):
    topic = Topic.get_by_id(topic_id)
    deleted = topic.delete_instance(recursive=True)
    return deleted


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SOURCE-TOPIC TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_sourcetopic_select_source_topics(source_id):
    source_topics = SourceTopic.select().where(SourceTopic.source_id == source_id)
    source_topics_ids = [t.topic_id for t in source_topics]
    return db_topic_select_list(source_topics_ids)


def db_sourcetopic_select_topic_sources(topic_id):
    topic_sources = SourceTopic.select().where(SourceTopic.topic_id == topic_id)
    source_sources_ids = [s.source_id for s in topic_sources]
    return db_source_select_list(source_sources_ids)


def db_sourcetopic_insert(source_id, topic_id):
    SourceTopic.create(source=source_id, topic=topic_id)
    return source_id, topic_id
    

def db_sourcetopic_delete(source_id, topic_id):
    pair = SourceTopic.get(SourceTopic.source_id == source_id, SourceTopic.topic_id == topic_id)
    deleted = pair.delete_instance()
    return deleted


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ARTICLE-TOPIC TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_articletopic_select_article_topics(article_id):
    article_topics = ArticleTopic.select().where(ArticleTopic.article_id == article_id)
    article_topics_ids = [t.topic_id for t in article_topics]
    return db_topic_select_list(article_topics_ids)


def db_articletopic_select_topic_articles(topic_id):
    topic_articles = ArticleTopic.select().where(ArticleTopic.topic_id == topic_id)
    topic_article_ids = [t.article_id for t in topic_articles]
    return db_article_select_list(topic_article_ids)


def db_articletopic_insert(article_id, topic_id):
    ArticleTopic.create(article=article_id, topic=topic_id)
    return article_id, topic_id
    

def db_articletopic_delete(article_id, topic_id):
    pair = ArticleTopic.get(ArticleTopic.article_id == article_id, ArticleTopic.topic_id == topic_id)
    deleted = pair.delete_instance()
    return deleted


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# COMBOS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def db_select_source_alldata(source_id):
    source = db_source_select(source_id)
    source['topics'] = db_sourcetopic_select_source_topics(source_id)
    source['articles'] = db_article_select_list_by_source(source_id)
    return source


def db_insert_rss_source():
    # insert source
    # insert new topic (if not in table Topics)
    # insert source-topic relationships
    # insert articles
    return True

