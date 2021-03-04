from db_models import db, Source, ValidatedSource, Article, ValidatedArticle
from pydantic import ValidationError


def db_get_articles(**kwargs):
    # Filter by: all, source, tag, type_of_article
    # Sort by: published, impact

    # Filter by Source
    # source1 = Source.get(Source.id == 1)
    # for art in source1.articles:
    #     print(art.title)

    articles = [art for art in Article.select().order_by(Article.published.desc()).namedtuples()]
    return articles


def db_get_sources():
    # Filter by: all, topic, update frequency, origin, target_audience
    sources = [src for src in Source.select().order_by(Source.name).namedtuples()]
    return sources


def db_get_source(id):
    source = Source.get_by_id(id)
    return source


def db_delete_source(id):
    source = Source.get_by_id(id)
    deleted = source.delete_instance(recursive=True)
    return deleted



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ---------------------------production ready functions-------------------------------
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


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

