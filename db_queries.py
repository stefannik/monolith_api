from db_models import db, Source, ValidatedSource, Article, ValidatedArticle
from pydantic import ValidationError


def db_get_articles(**kwargs):
    # Filter by: all, source, tag, type_of_article
    # Sort by: published, impact

    # Filter by Source
    # source1 = Source.get(Source.id == 1)
    # for art in source1.articles:
    #     print(art.title)

    articles = [art for art in Article.select().order_by(Article.published.desc())]
    fixed = []
    for art in articles[:10]:
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
            "impact": art.impact,
            "trustworthy": art.trustworthy
        }
        fixed.append(obs)
    return fixed


def db_get_sources():
    # Filter by: all, topic, update frequency, origin, target_audience
    sources = {}
    for src in Source.select().order_by(Source.id):
        data = {
            'id': src.id,
            'name': src.name,
            'url': src.url,
            'last_updated': src.last_updated,
            'description': src.description,
            'logo': src.logo,
            'topics': src.topics,
            'target_audience': src.target_audience,
            'relevance': src.relevance,
            'trust': src.trust,
        }
        sources[src.id] = data
    return sources


def db_get_source(id):
    source = Source.get_by_id(id)
    return source


def db_get_source_all(id):
    source = Source.get_by_id(id)
    base = source.__data__
    arts = [art.__data__ for art in source.articles.order_by(Article.published.desc())]
    base['articles'] = arts
    return base


def db_delete_source(id):
    source = Source.get_by_id(id)
    deleted = source.delete_instance(recursive=True)
    return deleted



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ---------------------------production ready functions-------------------------------
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def db_article_update_impact(id, score):
    art = Article.get_by_id(id)
    art.impact = score
    art.save()
    return True


def db_article_update_type(id, score):
    art = Article.get_by_id(id)
    art.type_of_article = score
    art.save()
    return True


def db_article_update_trustworthy(id, score):
    art = Article.get_by_id(id)
    art.trustworthy = score
    art.save()
    return True


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

