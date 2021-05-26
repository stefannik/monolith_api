import feedparser
import html2text
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from time import mktime


def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    
    # REVIEW ALL ENTRIES
    entries = []
    for entry in feed.entries:
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

            entries.append(valid_entry)
    

    # VALIDITY CHECK
    has_title = 'title' in feed.feed.keys()     # Feed has title
    has_updated = 'updated_parsed' in feed.feed.keys() # Feed has date last updated
    has_valid_entries = len(entries) > 0        # Feed hast more than 0 valid entries
    
    # RETURN DATA
    if has_title and has_updated and has_valid_entries:
        feed_data = {
            "valid_feed": True,
            "name": feed.feed.title,
            "url": feed.feed.link,
            "rss_url": feed.href,
            "last_updated": datetime.fromtimestamp(mktime(feed.feed.updated_parsed)),
            "status": feed.status
        }

        if 'subtitle' in feed.feed.keys() and len(feed.feed.subtitle) > 0:
            feed_data['description'] = feed.feed.subtitle

        if 'image' in feed.feed.keys() and len(urlparse(feed.feed.image.href).scheme) > 0:
            feed_data['logo'] = feed.feed.image.href

        feed_data['entries'] = entries

        # OUTPUT --> {valid_feed, name, url, rss_url, last_updated, status, description, logo, entries}
        return feed_data
    
    # RETURN ERROR - NOT VALID FEED
    else:
        return {"valid_feed": False}


# guardian_source = fetch_rss_feed("http://www.buzzmachine.com/feed/")
# print(guardian_source["url"])

# test = ['https://buzzmachine.com/wp-content/uploads/tea-party-640x416.jpg']
# test_st = ", ".join(test)
# test_ne = test_st.split(", ")


