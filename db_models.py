from peewee import BooleanField, DateTimeField, ForeignKeyField, IntegerField, SqliteDatabase, Model, CharField, TextField, Check
from pydantic import BaseModel, constr, validator
from datetime import datetime
from typing import Optional

db = SqliteDatabase('test.db')


class Source(Model):
    # No need for ID field, peewee adds one automatically as a primary key autoincrement
    name = CharField(index=True, unique=True)
    url = TextField(index=True, unique=True)
    last_updated = DateTimeField(index=True)
    topics = CharField()
    target_audience = CharField(null=True)
    description = TextField(null=True)
    logo = TextField(null=True)
    origin = CharField(null=True)
    relevance = IntegerField(null=True)
    trust = IntegerField(null=True)
    status = IntegerField()

    class Meta:
        database = db


class ValidatedSource(BaseModel):
    name: constr(max_length=255)
    url: str
    last_updated: datetime
    topics: str
    target_audience: Optional[constr(max_length=255)]
    description: Optional[str]
    logo: Optional[str]
    origin: constr(max_length=255)
    trust: Optional[int]
    relevance: Optional[int]
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
    impact = IntegerField(index=True, null=True)

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
    impact: Optional[int]

    class Config:
        orm_mode = True


db.create_tables([Source, Article])