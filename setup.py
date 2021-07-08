# 1. Add inital list of topics to DB
# 2. Add RSS sources

from rss_handler import RSSFeed
from ai import score
from db_queries import db_article_exists, db_source_exists, db_sourcearticle_insert, db_topic_insert, db_topic_exists, db_source_insert, db_sourcetopic_insert, db_article_insert
import csv
from peewee import IntegrityError


filename = 'database/base_sources2.csv'

with open(filename, 'r') as csvfile:
    datareader = csv.reader(csvfile)

    count = 0
    for row in datareader:
        subscription = row[3]
        media_type = row[4]
        category = row[5]

        feed = RSSFeed(row[2])
        feed.setup()

        count = count + 1
        est_analysis = len(feed.entries)*6
        print('Starting: {}/69'.format(count))
        print(row[2])
        
        # try:
        if feed.valid_feed():
            # 1. PREP SOURCE OBJECT
            source = vars(feed).copy()
            source['subscription'] = subscription
            source['media_type'] = media_type
            source['origin'] = 'RSS'
            source['status'] = feed.valid_feed()
            source.pop('entries')
            source.pop('entries_dates')
            source.pop('raw_content')
            source.pop('parsed_content')

            # 2. ADD SOURCE IF IT DOESN'T EXIST
            source_exists = db_source_exists(feed.name)
            if source_exists['exists'] == False:
                sourceid = db_source_insert(**source)
            else:
                sourceid = source_exists['id']
            
            print('Source: {}, {}'.format(sourceid, feed.name))

            # 3. ADD TOPIC IF IT DOESN'T EXIST
            topic_exists = db_topic_exists(category)
            if topic_exists['exists'] == False:
                topicid = db_topic_insert(name=category)
            else:
                topicid = topic_exists['id']
            
            print('Topic: {}, {}'.format(topicid, category))
            
            # 4. ADD TOPIC-SOURCE REL
            try:
                relid = db_sourcetopic_insert(sourceid, topicid)
            except IntegrityError:
                print('ERROR: topic-rel exists')    

            # 5. EVAL AND ADD ARTICLES
            for entry in feed.entries:
                if entry.valid_article():
                    article = vars(entry)
                    article.pop('data')

                    sense_score = score(entry.title, 'sense')
                    portada_score = score(entry.title, 'portada')
                    impact_score = (sense_score + portada_score) / 2
                    article['sense_score'] = float(sense_score)
                    article['portada_score'] = float(portada_score)
                    article['impact_score'] = float(impact_score)

                    
                    article_exists = db_article_exists(article['url'])
                    if article_exists['exists'] == False:
                        articleid = db_article_insert(**article)
                    else:
                        articleid = article_exists['id']

                    print('Article: {}, {}'.format(articleid, article['title']))

                    try:
                        db_sourcearticle_insert(sourceid, articleid)
                    except IntegrityError:
                        print('Article is duplicate: {}'.format(article['title']))

                    
        # except:
        #     print("BIG FUCKING ERRROR")
        
        print("-------------------------------------------------------")







            

            
            

            
            



    



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
