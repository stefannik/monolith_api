from html import parser
import feedparser
from feedparser.api import parse
import html2text
import requests
import io
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from time import mktime
from requests.exceptions import ConnectTimeout, ReadTimeout


def rss_pull(url):
    headers = {'User-Agent': 'RSS Parser'}
    resp = requests.get(url, timeout=(2.0, 5.0), headers=headers)
    status = resp.status_code
    content = io.BytesIO(resp.content)
    return {'status': status, 'content': content}


def rss_parse_entries(entries):
    articles = []
    for entry in entries:
        entry_has_title = 'title' in entry.keys() and len(entry.title) > 0
        entry_has_url = 'link' in entry.keys() and len(urlparse(entry.link).scheme) > 0
        entry_has_published_date = 'published_parsed' in entry.keys()

        if entry_has_title and entry_has_url and entry_has_published_date:
            valid_entry = {
                "title": entry.title,
                "url": entry.link,
                "published": datetime.fromtimestamp(mktime(entry.published_parsed)),
            }

            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.ignore_tables = True

            images = []

            if 'author' in entry.keys():
                valid_entry['author'] = entry.author
            if 'summary' in entry.keys():
                valid_entry['summary_raw'] = entry.summary
                valid_entry['summary'] = h.handle(entry.summary)
                summary_html = BeautifulSoup(entry.summary, "html.parser")
                for img in summary_html.findAll("img"):
                    images.append(img['src'])
            if 'content' in entry.keys():
                valid_entry['content_raw'] = entry.content[0].value
                valid_entry['content'] = h.handle(entry.content[0].value)
                content_html = BeautifulSoup(entry.content[0].value, "html.parser")
                for img in content_html.findAll("img"):
                    images.append(img['src'])
            if 'tags' in entry.keys():
                valid_entry['tags'] = ", ".join([tag.term for tag in entry.tags])
            if len(images) > 0:
                valid_entry['images'] = ", ".join(images)

            articles.append(valid_entry)
    return articles


def rss_content_parser(content):
    parsed_content = feedparser.parse(content)
    parsed_entries = rss_parse_entries(parsed_content.entries)

    article_dates = sorted([ent['published'] for ent in parsed_entries], reverse=True)
    last_updated = article_dates[0]


    has_title = 'title' in parsed_content.feed.keys()
    has_valid_entries = len(parsed_entries) > 0

    if has_title and has_valid_entries:

        feed = {
            "name": parsed_content.feed.title,
            "articles": parsed_entries,
            "last_updated": last_updated
        }

        if 'subtitle' in parsed_content.feed.keys() and len(parsed_content.feed.subtitle) > 0:
            feed['description'] = parsed_content.feed.subtitle

        if 'image' in parsed_content.feed.keys() and len(urlparse(parsed_content.feed.image.href).scheme) > 0:
            feed['logo'] = parsed_content.feed.image.href
        
        return feed

    else:
        raise Exception("The RSS feed doesn't have a valid title or any entries")

def rss_fetch(url):
    try:
        content = rss_pull(url)
        processed_content = rss_content_parser(content['content'])

        if content['status'] == 301:
            print("do something")
        
        return {'status': content['status'], 'payload': processed_content}

    except ConnectTimeout:
        return {'status': 408, 'payload': "Connect Timeout Error"}

    except ReadTimeout:
        return {'status': 408, 'payload': "Read Timeout Error"}

    # except BaseException:
        # return {'status': 400, 'payload': "Invalid RSS feed: no title or entries"}

    except Exception as e:
        return {'status': 400, 'payload': e}


# print(rss_fetch("http://www.esa.int/rss/TopNews.xml")['status'])

# content = rss_pull("https://phys.org/rss-feed/")
# processed_content = rss_content_parser(content['content'])
# print(processed_content)


# import csv
# with open('database/base_sources.csv', 'r') as csvfile:
#     datareader = csv.reader(csvfile)
#     for row in datareader:
#         print(rss_fetch(row[2])['status'])
