from datetime import date, time, datetime, timedelta
import psycopg2
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

PSQL_PASS = os.getenv("PSQL_PASS")

db_string = "postgresql+psycopg2://websinthe:" + PSQL_PASS + "@192.168.132.19:5432/websinthe"

engine = create_engine(db_string)

def word_count(copy: str):
    count_list = copy.split(" ", -1)
    return len(count_list)

with engine.connect() as conn, conn.begin():
    article_proxy = pd.read_sql_query("""Select page_url, headtext, tease, bodytext, print_date from articles ORDER BY print_date DESC;""", conn)

headline_counts = article_proxy['headtext'].map(lambda a: len(a.split(" ", -1)))

tease_counts = article_proxy['tease'].map(lambda a: len(a.split(" ", -1)))

body_joined = article_proxy['bodytext'].map(lambda a: "|".join(a))
body_joined = body_joined.map(lambda a: a.replace("|", ""))
body_counts = body_joined.map(lambda a: len(a.split(" ", -1)))

# body_counts.hist(bins=300)

counts = { "page_url": article_proxy['page_url'], "headline_counts": headline_counts, "tease_counts": tease_counts, "body_counts": body_counts}
article_numbers = pd.DataFrame(counts)

# print(article_numbers)

with engine.connect() as conn, conn.begin():
    time_counts = pd.read_sql_query("""SELECT articles.page_url, articles.print_date, counts.body_counts, counts.headline_counts, counts.tease_counts FROM articles INNER JOIN counts ON articles.page_url=counts.page_url;""", conn)

print(time_counts.head())
