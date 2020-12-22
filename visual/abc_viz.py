from datetime import date, time, datetime, timedelta
import psycopg2
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

PSQL_PASS = os.getenv("PSQL_PASS")

db_string = "postgresql+psycopg2://websinthe:" + PSQL_PASS + "@192.168.132.85:5432/websinthe"

engine = create_engine(db_string)

# with engine.connect() as conn, conn.begin():
    # article_count = pd.read_sql_query("""SELECT title, print_date FROM articles;""", conn)

# YOU NEED TO FIGURE OUT HOW TO HISTOGRAM THIS SHIT, MAYBE TRY GETTING THE WHOLE COLUMN AND USING PANDAS

#print(db_string)
#print(article_count)

# print("Print sorted latest.\n")
# article_count = article_count.sort_values(by="print_date", ascending=False)
# print(article_count.head())
# print("Print extracted latest.\n")
# articles = article_count.loc[article_count['print_date'].idxmax()]
# print (articles.head())

def word_count(copy: str):
    count_list = copy.split(" ", -1)
    return len(count_list)

with engine.connect() as conn, conn.begin():
    article_proxy = pd.read_sql_query("""Select page_url, headtext, tease, bodytext, print_date from articles ORDER BY print_date DESC;""", conn)

headline_counts = article_proxy['headtext'].map(lambda a: len(a.split(" ", -1)))
# print(headline_counts.head())
# headline_counts.hist()

tease_counts = article_proxy['tease'].map(lambda a: len(a.split(" ", -1)))
# print(tease_counts.head())
# tease_counts.hist()

body_joined = article_proxy['bodytext'].map(lambda a: "|".join(a))
body_joined = body_joined.map(lambda a: a.replace("|", ""))
# print(body_joined.head())
body_counts = body_joined.map(lambda a: len(a.split(" ", -1)))
# print(body_counts.head())

# body_counts.hist(bins=300)

counts = { "page_url": article_proxy['page_url'], "headline_counts": headline_counts, "tease_counts": tease_counts, "body_counts": body_counts}
article_numbers = pd.DataFrame(counts)

# print(article_numbers)

with engine.connect() as conn, conn.begin():
    article_numbers.to_sql("counts", conn, if_exists="append", chunksize=1000, index=False)