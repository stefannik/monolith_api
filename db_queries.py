import enum
from db_models import SourceTopic, ArticleTopic, db, Source, ValidatedSource, Article, ValidatedArticle, Topic, ValidatedTopic
from pydantic import ValidationError
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
    return []


def db_topic_select_list(topic_ids):
    return []


def db_topic_select(topic_id):
    return topic_id


def db_topic_insert(name, description):
    # check if name exists
    # insert
    topic_id = 0
    return topic_id


def db_topic_delete(topic_id):
    return topic_id


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SOURCE-TOPIC TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_sourcetopic_select_topics(source_id):
    topics_ids = []
    return topics_ids


def db_sourcetopic_select_sources(topic_id):
    source_ids = []
    return source_ids


def db_sourcetopic_insert(source_id, topic_id):
    return source_id, topic_id
    

def db_sourcetopic_delete(source_id, topic_id):
    return source_id, topic_id


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ARTICLE-TOPIC TABLE
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_articletopic_select_topics(article_id):
    topics_ids = []
    return topics_ids


def db_articletopic_select_sources(topic_id):
    article_ids = []
    return article_ids


def db_articletopic_insert(article_id, topic_id):
    return article_id, topic_id
    

def db_articletopic_delete(article_id, topic_id):
    return article_id, topic_id


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# COMBOS
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def db_select_source_alldata(source_id):
    source = db_source_select(source_id)
    source['topics'] = db_sourcetopic_select_topics(source_id)
    source['articles'] = db_article_select_list_by_source(source_id)
    return source


def db_insert_rss_source():
    # insert source
    # insert new topic (if not in table Topics)
    # insert source-topic relationships
    # insert articles
    return True












# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def db_get_articles(**kwargs):
    # Filter by: all, source, tag, type_of_article
    # Sort by: published, impact

    # Filter by Source
    # source1 = Source.get(Source.id == 1)
    # for art in source1.articles:
    #     print(art.title)
    query = Article.select().where(Article.published > datetime(2021, 4, 8)).order_by(Article.mono.desc())
    # query = Article.select().order_by(Article.mono.desc())
    articles = [art for art in query]
    fixed = []
    for art in articles[:50]:
        obs = {
            "id": int(art.id),
            "source": art.source_id,
            "title": art.title,
            "url": art.url,
            "published": art.published,
            "summary_raw": art.summary_raw,
            "summary": art.summary,
            "content_raw": art.content_raw,
            "content": art.content,
            "tags": art.tags.split(", ") if art.tags is not None else art.tags,
            "author": art.author,
            "images": art.images.split(", ") if art.images is not None else art.images,
            "type_of_article": art.type_of_article,
            "sense": art.sense,
            "portada": art.portada,
            "mono": art.mono
        }
        fixed.append(obs)
    return fixed



def db_source_exists(url):
    try: 
        Source.get(Source.url == url)
        return True
    except:
        return False


def db_insert_source(data):
    # Create Source object to be inserted
    source_data = Source(
        name=data["name"],
        url=data["url"],
        last_updated=data["last_updated"],
        topics=data["topics"],
        origin=data["origin"],
        status=data["status"]
    )
    if 'description' in data.keys():
        source_data.description = data['description']
    if 'logo' in data.keys():
        source_data.logo = data['logo']
    
    # Validate the object and insert into db
    try:
        ValidatedSource.from_orm(source_data)
        source_data.save()

        # Format, validate articles
        with db.atomic():
            for entry in data['entries']:
                article_data = entry
                article_data['source'] = source_data.id
                if 'tags' in article_data.keys():
                    article_data['tags'] = str(article_data['tags'])
                if 'images' in article_data.keys():
                    article_data['images'] = str(article_data['images'])

                try:
                    temp_article = Article(**article_data)
                    ValidatedArticle.from_orm(temp_article)
                    Article.create(**article_data)
                except ValidationError as e:
                    return e

        return {"source_id": source_data.id}
    
    except ValidationError as e:
        return e


def db_insert_topic(fields):
    # Create Source object to be inserted
    topic_fields = Topic(
        name=fields["name"],
    )
    if 'description' in fields.keys():
        topic_fields.description = fields['description']
    
    # Validate the object and insert into db
    try:
        print('here')
        ValidatedTopic.from_orm(topic_fields)
        topic_fields.save()

        return {"topic_id": topic_fields.id}
    
    except ValidationError as e:
        return e


def db_insert_sourcetopic_pair(source_id, topic_id):
    # Create Source object to be inserted
    source = Source.get(Source.id == source_id)
    topic = Topic.get(Topic.id == topic_id)

    try:
        SourceTopic.create(source=source, topic=topic)

        return {"source_topic_pair_added": True}
    
    except ValidationError as e:
        return e


def db_get_topic_sources(topic_id):
    query = SourceTopic.select().where(SourceTopic.topic_id == topic_id)
    pairs = [art.source_id for art in query]
    return pairs


def db_get_source_topics(source_id):
    query = SourceTopic.select().where(SourceTopic.source_id == source_id)
    pairs = [art.topic_id for art in query]
    return pairs


def db_delete_source_topics(source_id, topic_id):
    SourceTopic.delete().where(SourceTopic.source_id == source_id).where(SourceTopic.topic_id == topic_id).execute()
    return {"source_topic_pair_deleted": [source_id, topic_id]}



def db_get_topic_articles(topic_id):
    query = ArticleTopic.select().where(ArticleTopic.topic_id == topic_id)
    pairs = [art.source_id for art in query]
    return pairs


def db_get_article_topics(source_id):
    query = ArticleTopic.select().where(ArticleTopic.source_id == source_id)
    pairs = [art.topic_id for art in query]
    return pairs