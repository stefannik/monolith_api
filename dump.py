from pydantic import HttpUrl
from db_queries import *
from rss_handler import fetch_rss_feed
import csv


def insert_into_db(url: HttpUrl, origin: str, topics: str):
    if db_source_exists(url) is False: # Check feed url doesn't exist in DB already
        fetched = fetch_rss_feed(url) # Call RSS handler, extract and format data
        if fetched["valid_feed"]:
            fetched['origin'] = origin
            fetched['topics'] = topics
            source_in_db_id = db_insert_source(fetched) # Insert into DB
            return source_in_db_id
        else:
            return "The url is not a valid RSS feed or the feed's format is not supported."
    else:
        return "Url already exists in DB"


# filename = "sources_dump.csv"

# with open(filename, 'r') as csvfile:
#     datareader = csv.reader(csvfile)
#     for row in datareader:
#         try:
#             print(row[0])
#             print(insert_into_db(row[0], "rss", row[1]))
#             print("------------------------------------------------------------------")
#         except:
#             print(row[0])
#             print("ERROR")
#             print("------------------------------------------------------------------")


# print(insert_into_db("http://www.nytimes.com/services/xml/rss/nyt/MediaandAdvertising.xml", "rss", "media"))

