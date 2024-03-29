from peewee import BooleanField, DateTimeField, ForeignKeyField, DecimalField, IntegerField, SqliteDatabase, Model, CharField, TextField, CompositeKey
from pydantic import BaseModel, constr, validator
from datetime import datetime
from typing import Optional

db = SqliteDatabase('database/database01_20210708.db')
# db = SqliteDatabase('/home/monolith_db/database01_20210708.db')


class Source(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    name = CharField(index=True, unique=True)
    url = TextField(index=True, unique=True, null=True)
    rss_url = TextField(index=True, unique=True)
    last_updated = DateTimeField(index=True)
    description = TextField(null=True)
    logo = TextField(null=True)
    subscription = BooleanField()
    media_type = TextField()
    origin = CharField(null=True)
    avg_update_gap = IntegerField()
    last_ping = DateTimeField()
    status = IntegerField()

    class Meta:
        database = db


class ValidatedSource(BaseModel):
    name: constr(max_length=255)
    url: str
    rss_url: str
    last_updated: datetime
    description: Optional[str]
    logo: Optional[str]
    subscription: bool
    media_type: str
    origin: constr(max_length=255)
    avg_update_gap: int
    last_ping: datetime
    status: int

    class Config:
        orm_mode = True
    

class Article(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    title = TextField(index=True)
    url = TextField(index=True, unique=True)
    published = DateTimeField(index=True)
    summary_raw = TextField(null=True)
    summary = TextField(null=True)
    content_raw = TextField(null=True)
    content = TextField(null=True)
    author = CharField(null=True)
    images = TextField(null=True)
    type_of_article = CharField(null=True)
    sense_score = DecimalField(null=True)
    portada_score = DecimalField(index=True, null=True)
    impact_score = DecimalField(index=True, null=True)

    class Meta:
        database = db


class ValidatedArticle(BaseModel):
    title: str
    url: str
    published: datetime
    summary_raw: Optional[str]
    summary: Optional[str]
    content_raw: Optional[str]
    content: Optional[str]
    author: Optional[constr(max_length=255)]
    images: Optional[str]
    type_of_article: Optional[constr(max_length=255)]
    sense_score: Optional[float]
    portada_score: Optional[float]
    impact_score: Optional[float]

    class Config:
        orm_mode = True


class Topic(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    name = TextField(index=True, unique=True)
    description = TextField(index=False, null=True)

    class Meta:
        database = db


class ValidatedTopic(BaseModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class SourceArticle(Model):  # Many-to-many relationship.
    source = ForeignKeyField(Source, backref='articles')
    article = ForeignKeyField(Article, backref="sources")

    class Meta:
        database = db
        primary_key = CompositeKey('source', 'article')


class SourceTopic(Model):  # Many-to-many relationship.
    source = ForeignKeyField(Source, backref='topics')
    topic = ForeignKeyField(Topic, backref="sources")

    class Meta:
        database = db
        primary_key = CompositeKey('source', 'topic')


class ArticleTopic(Model):  # Many-to-many relationship.
    article = ForeignKeyField(Article, backref='topics')
    topic = ForeignKeyField(Topic)

    class Meta:
        database = db
        primary_key = CompositeKey('article', 'topic')


# db.create_tables([Source, Article, Topic, SourceArticle, SourceTopic, ArticleTopic])