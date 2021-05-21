from peewee import BooleanField, DateTimeField, ForeignKeyField, DecimalField, IntegerField, SqliteDatabase, Model, CharField, TextField, CompositeKey
from pydantic import BaseModel, constr, validator
from datetime import datetime
from typing import Optional

db = SqliteDatabase('test.db')


class Source(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    name = CharField(index=True, unique=True)
    url = TextField(index=True, unique=True)
    last_updated = DateTimeField(index=True)
    description = TextField(null=True)
    logo = TextField(null=True)
    origin = CharField(null=True)
    status = IntegerField()

    class Meta:
        database = db


class ValidatedSource(BaseModel):
    name: constr(max_length=255)
    url: str
    last_updated: datetime
    target_audience: Optional[constr(max_length=255)]
    description: Optional[str]
    logo: Optional[str]
    origin: constr(max_length=255)
    status: int

    class Config:
        orm_mode = True
    


class Article(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    source = ForeignKeyField(Source, backref='articles')
    title = TextField(index=True)
    url = TextField(index=True, unique=True)
    published = DateTimeField(index=True)
    summary_raw = TextField(null=True)
    summary = TextField(null=True)
    content_raw = TextField(null=True)
    content = TextField(null=True)
    tags = TextField(null=True)
    author = CharField(null=True)
    images = TextField(null=True)
    type_of_article = CharField(null=True)
    sense = DecimalField(null=True)
    portada = DecimalField(index=True, null=True)
    mono = DecimalField(index=True, null=True)

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
    tags: Optional[str]
    author: Optional[constr(max_length=255)]
    images: Optional[str]
    type_of_article: Optional[constr(max_length=255)]
    sense: Optional[float]
    portada: Optional[float]
    mono: Optional[float]

    class Config:
        orm_mode = True


class Topic(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    name = TextField(index=True)
    description = TextField(index=False, null=True)

    class Meta:
        database = db


class ValidatedTopic(BaseModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class SourceTopic(Model):  # Many-to-many relationship.
    source = ForeignKeyField(Source, backref='topics')
    topic = ForeignKeyField(Topic)

    class Meta:
        database = db
        primary_key = CompositeKey('source', 'topic')


class ArticleTopic(Model):  # Many-to-many relationship.
    article = ForeignKeyField(Article, backref='topics')
    topic = ForeignKeyField(Topic)

    class Meta:
        database = db
        primary_key = CompositeKey('article', 'topic')


# db.create_tables([Source, Article, Topic, SourceTopic, ArticleTopic])