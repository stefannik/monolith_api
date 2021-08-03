import json
from datetime import time, timedelta
from datetime import datetime
from db_queries import db_source_full_list, db_article_exists, db_article_insert, db_source_select, db_source_update, db_sourcearticle_insert, db_source_full_list, db_source_select_list
from rss_handler import RSSFeed
from ai import score
from peewee import IntegrityError
from numpy import average
from typing import Optional


class SourceUpdater:
    def __init__(self, source_id, force: Optional[bool] = False):
        self.source_id = source_id
        self.force = force
        self.now = datetime.now()
        self.active = False
        self.needs_update = False
        self.updated_info = False
        self.added_entries = False
        

    def setup(self):
        self.source = db_source_select(self.source_id)
        gap_since_last_updated = self.now - self.source['last_updated']
        gap_since_last_ping = self.now - self.source['last_ping']
        avg_update_gap = timedelta(seconds=self.source['avg_update_gap'])
        ping_interval = avg_update_gap * 0.2

        if gap_since_last_updated < timedelta(days=90):
            self.active = True

        if gap_since_last_ping > ping_interval or gap_since_last_ping > timedelta(hours=24):
            self.needs_update = True
        
    
    def add_new_articles(self):
        feed = RSSFeed(self.source['rss_url'])
        feed.setup()

        if feed.valid_feed():
            entries_dates = sorted([ent.published for ent in feed.entries], reverse=True)
            self.last_updated = entries_dates[0]

            gaps = []
            for ind, date in enumerate(entries_dates):
                if ind != len(entries_dates)-1:
                    diff = date - entries_dates[ind+1]
                    gaps.append(diff.total_seconds())
            self.avg_update_gap = average(gaps)

            for entry in feed.entries:
                if entry.valid_article():
                    article_in_db = db_article_exists(entry.url)
                    if article_in_db['exists'] == False:
                        article = vars(entry)
                        article.pop('data')

                        sense_score = score(entry.title, 'sense')
                        portada_score = score(entry.title, 'portada')
                        impact_score = (sense_score + portada_score) / 2
                        article['sense_score'] = float(sense_score)
                        article['portada_score'] = float(portada_score)
                        article['impact_score'] = float(impact_score)

                        try:
                            articleid = db_article_insert(**article)
                            db_sourcearticle_insert(self.source_id, articleid)
                            self.added_entries = True
                        except IntegrityError:
                            continue
    

    def update_info(self):
        data = {"last_ping": self.now}

        if self.added_entries:
            data["last_updated"] = self.last_updated
            data["avg_update_gap"] = self.avg_update_gap
        
        db_source_update(self.source_id, **data)


    def run(self):
        if (self.active and self.needs_update) or self.force:
            # print("UPDATING ", self.source_id)
            self.add_new_articles()
            self.update_info()
            

def main_program():
    while True:
        sources = [src['id'] for src in db_source_full_list()]
        for src_id in sources:
            src = SourceUpdater(src_id, True)
            src.setup()
            src.run()
            with open('/home/monolith_api/update_deamon_logger.txt', 'a+') as fh:
                fh.write("Updated Source: {}, at: {}\n".format(src_id, datetime.now()))
        time.sleep(1)

# import daemon

# with daemon.DaemonContext(
#     working_directory='/home/monolith_api'
# ):
#         main_program()

main_program()

# for src_id in range(1, 67):
#     print("updating ", src_id)
#     src = SourceUpdater(src_id, True)
#     src.setup()
#     src.run()


# import timeit
# start = timeit.default_timer()
# end = timeit.default_timer()
# print(end-start)
