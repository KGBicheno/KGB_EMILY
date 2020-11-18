from datetime import date, time, datetime, timedelta
import psycopg2
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

PSQL_PASS = os.getenv("PSQL_PASS")

db_string = "postgresql+psycopg2://websinthe:" + PSQL_PASS + "@192.168.1.7:5432/websinthe"

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
