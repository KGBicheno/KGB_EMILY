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
    article_proxy = pd.read_sql_query("""Select headtext, tease, bodytext, print_date from articles ORDER BY print_date DESC LIMIT 50;""", conn)

headline_counts = article_proxy['headtext'].map(lambda a: len(a.split(" ", -1)))
# print(headline_counts.head())
headline_counts.hist()

tease_counts = article_proxy['tease'].map(lambda a: len(a.split(" ", -1)))
# print(tease_counts.head())

body_joined = article_proxy['bodytext'].map(lambda a: "|".join(a))
body_counts = body_joined.map(lambda a: len(a.split(" ", -1)))
# print(body_counts.head())