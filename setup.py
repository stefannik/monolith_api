# 1. Add inital list of topics to DB
# 2. Add RSS sources

from rss_handler import RSSFeed
from db_queries import db_topic_insert, db_topic_exists, db_source_insert, db_sourcetopic_insert
import csv

filename = 'database/base_sources_short.csv'

with open(filename, 'r') as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        subscription = row[3]
        media_type = row[4]
        category = row[5]

        feed = RSSFeed(row[2])
        feed.setup()

        if feed.valid_feed():
            # 1. ADD SOURCE
            source = {
                "name": feed.name,
                "url": feed.url,
                "rss_url": feed.rss_url,
                "last_updated": feed.last_updated,
                "subscription": subscription,
                "media_type": media_type,
                "origin": "RSS",
                "update_gap": feed.update_gap,
                "status": feed.valid_feed(),
            }

            if 'description' in vars(feed):
                source["description"] = feed.description

            if 'logo' in vars(feed):
                source["logo"] = feed.logo

            sourceid = db_source_insert(**source)


            # 2. ADD TOPIC IF IT DOESN'T EXIST
            topic_exists = db_topic_exists(category)
            if topic_exists['exists'] == False:
                topicid = db_topic_insert(name=category)
            else:
                topicid = topic_exists['id']
            
            # 3. ADD TOPIC-SOURCE REL
            relid = db_sourcetopic_insert(sourceid, topicid)

            

            
            

            
            



    



# 2. ML Dump

# from db_queries import db_get_articles, db_article_update_mono, db_article_update_portada, db_article_update_sense
# from ai import score
# from tqdm import tqdm


# for art in tqdm(db_get_articles()):
#     text = art['title'] + ' [SEP] ' + art['summary'].strip()
#     sense = score(text, 'sense')
#     portada = score(text, 'portada')
#     db_article_update_sense(art['id'], float(sense))
#     db_article_update_portada(art['id'], float(portada))


# for art in tqdm(db_get_articles()):
#     sense = art['sense']
#     portada = art['portada']
#     mono = sense + portada

#     db_article_update_mono(art['id'], float(mono))
