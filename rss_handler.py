from html import parser
import feedparser
from feedparser.api import parse
import html2text
import requests
import io
from numpy import average
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from time import mktime


class RSSFeedEntry:
    def __init__(self, data):
        self.data = data
        self.title = False
        self.url = False
        self.published_date = False
    
    def add_attributes(self):
        if 'title' in self.data.keys() and len(self.data.title) > 0:
            self.title = self.data.title
        if 'link' in self.data.keys() and len(urlparse(self.data.link).scheme) > 0:
            self.url = self.data.link
        if 'published_parsed' in self.data.keys():
            self.published = datetime.fromtimestamp(mktime(self.data.published_parsed))

        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_tables = True

        images = []

        if 'author' in self.data.keys():
            self.author = self.data.author
        if 'summary' in self.data.keys():
            self.summary_raw = self.data.summary
            self.summary = h.handle(self.data.summary)
            summary_html = BeautifulSoup(self.data.summary, "html.parser")
            for img in summary_html.findAll("img"):
                images.append(img['src'])
        if 'content' in self.data.keys():
            self.content_raw = self.data.content[0].value
            self.content = h.handle(self.data.content[0].value)
            content_html = BeautifulSoup(self.data.content[0].value, "html.parser")
            for img in content_html.findAll("img"):
                images.append(img['src'])
        if 'tags' in self.data.keys():
            self.tags = ", ".join([tag.term for tag in self.data.tags])
        if len(images) > 0:
            self.images = ", ".join(images)
        
    def valid_article(self):
        if self.title and self.url and self.published:
            return True
        else:
            return False


class RSSFeed:
    def __init__(self, rss_url):
        self.rss_url = rss_url
        self.status = False
        self.name = False
        self.entries = []

    def fetcher(self):
        try:
            headers = {'User-Agent': 'RSS Monolith Agent', 'From': 'stefan.nikolaev.d@gmail.com'}
            resp = requests.get(self.rss_url, headers=headers, timeout=(1.0, 1.0))
            content = io.BytesIO(resp.content)
            self.status = True
            self.raw_content = content
            self.parsed_content = feedparser.parse(content)

        except Exception as e:
            self.status = False
            self.raw_content = e
    
    def parser_main(self):
        if 'title' in self.parsed_content.feed.keys():
            self.name = self.parsed_content.feed.title
        if 'subtitle' in self.parsed_content.feed.keys() and len(self.parsed_content.feed.subtitle) > 0:
            self.description = self.parsed_content.feed.subtitle
        if 'image' in self.parsed_content.feed.keys() and len(urlparse(self.parsed_content.feed.image.href).scheme) > 0:
            self.logo = self.parsed_content.feed.image.href
        if 'link' in self.parsed_content.feed.keys():
            self.url = self.parsed_content.feed.link
        
    def parser_entries(self):
        for art in self.parsed_content.entries:
            # print(type(dict(art)), dict(art).keys())
            article = RSSFeedEntry(art)
            article.add_attributes()
            if article.valid_article():
                self.entries.append(article)
    
    def sort_entries(self):
        self.entries_dates = sorted([ent.published for ent in self.entries], reverse=True)
        self.last_updated = self.entries_dates[0]

        gaps = []
        for ind, date in enumerate(self.entries_dates):
            if ind != len(self.entries_dates)-1:
                diff = date - self.entries_dates[ind+1]
                gaps.append(diff.total_seconds())
        self.update_gap = average(gaps)
    
    def valid_feed(self):
        if self.status and self.name and len(self.entries) > 0:
            return True
        else:
            return False
    
    def setup(self):
        self.fetcher()
        if self.status:
            self.parser_main()
        if self.name:
            self.parser_entries()
        if len(self.entries) > 0:
            self.sort_entries()


test = RSSFeed('https://www.techradar.com/rss')
test.setup()
print(test.valid_feed())
if test.valid_feed():
    print(test.update_gap)
else:
    print(test.raw_content)
