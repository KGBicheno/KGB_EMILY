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

with engine.connect() as conn, conn.begin():
    article_count = pd.read_sql_query("""SELECT title, print_date FROM articles;""", conn)

# YOU NEED TO FIGURE OUT HOW TO HISTOGRAM THIS SHIT, MAYBE TRY GETTING THE WHOLE COLUMN AND USING PANDAS

#print(db_string)
#print(article_count)

print("Print sorted latest.\n")
article_count = article_count.sort_values(by="print_date", ascending=False)
print(article_count.head())
print("Print extracted latest.\n")
articles = article_count.loc[article_count['print_date'].idxmax()]
print (articles.head())

def extract_date(timestamp):
    if type(timestamp) == str():
        article_date_whole = str(timestamp)
        article_date = article_date_whole[0:9]
        return article_date
    else:
        article_date = timestamp.date()
        return article_date.date()

def extract_time(timestamp):
    if type(timestamp) == str():
        article_time_whole = str(timestamp)
        article_time = article_time_whole[0:10]
        return article_time
    else:
        article_time = timestamp.time()
        return article_time.time()

with engine.connect() as conn, conn.begin():
    article_proxy = pd.read_sql_query("""SELECT print_date FROM articles LIMIT 3;""", conn)

article_date = article_proxy.loc[2, 'print_date']

print("Base value: ", article_date, "\n")
article_date_text = str(article_date)
print("String Value stripped: ", article_date_text[0:10])
