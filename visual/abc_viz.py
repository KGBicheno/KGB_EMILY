from datetime import date, time, datetime, timedelta
import psycopg2
import pprint
from matplotlib import pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
import os
import spacy
from dotenv import load_dotenv
import csv
import re
load_dotenv()

spacy.prefer_gpu()

nlp = spacy.load("en_core_web_lg")

PSQL_PASS = os.getenv("PSQL_PASS")

db_string = "postgresql+psycopg2://websinthe:" + PSQL_PASS + "@192.168.132.19:5432/websinthe"

engine = create_engine(db_string)

def word_count(copy: str):
    count_list = copy.split(" ", -1)
    return len(count_list)

def article_word_count(engine):
    with engine.connect() as conn, conn.begin():
        article_proxy = pd.read_sql_query("""Select page_url, headtext, tease, bodytext, print_date from articles ORDER BY print_date DESC;""", conn)

    headline_counts = article_proxy['headtext'].map(lambda a: len(a.split(" ", -1)))

    tease_counts = article_proxy['tease'].map(lambda a: len(a.split(" ", -1)))

    # This section joins the sentences held as seperate lists in the body text of each article.

    body_joined = article_proxy['bodytext'].map(lambda a: "|".join(a))
    body_joined = body_joined.map(lambda a: a.replace("|", ""))
    body_counts = body_joined.map(lambda a: len(a.split(" ", -1)))

    body_counts.hist(bins=300)

    counts = { "page_url": article_proxy['page_url'], "headline_counts": headline_counts, "tease_counts": tease_counts, "body_counts": body_counts}
    article_numbers = pd.DataFrame(counts)

    article_numbers.sort_values(by=['body_counts'], inplace=True)

    print(article_numbers)


def author_story_counts(engine):
    with engine.connect() as conn, conn.begin():
        time_counts = pd.read_sql_query("""SELECT articles.page_url, articles.byline, articles.print_date, counts.body_counts, counts.headline_counts, counts.tease_counts FROM articles INNER JOIN counts ON articles.page_url=counts.page_url;""", conn)

    authors = []

    for byline in time_counts['byline']:
        for author in byline:
            authors.append(author)

    print(len(authors))

    bylines = set(authors)

    print(len(bylines))

    author_story_counts = []
    author_story_count = 0

    for byline in bylines:
        for authors in time_counts['byline']:
            if byline in authors:
                author_story_count += 1
        byline_dict = dict(byline=byline, stories=author_story_count)
        author_story_counts.append(byline_dict)
        author_story_count = 0


    stories_per_author = pd.DataFrame(author_story_counts)

    print(stories_per_author.head)

    print(time_counts.head())

def people_in_teases(engine):
    with engine.connect() as conn, conn.begin():
        nre_docs = pd.read_sql_query("""SELECT tease FROM articles LIMIT 100;""", conn)

    print(nre_docs.head)

    nre_lines = nre_docs.to_string(header=False, index=False)

    doc = nlp(nre_lines)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            print(ent.text)

def POS_tag_headlines(engine):
    with engine.connect() as conn, conn.begin():
        pos_headlines = pd.read_sql_query("""SELECT headtext FROM articles LIMIT 10;""", conn)
    
    pos_headers = pos_headlines.to_string(header=False, index=False)
    
    headlines_tagged = nlp(pos_headers)
    for token in headlines_tagged:
        print(token.text, " - ", token.dep_)

def nca_authors_unique(engine):
    with engine.connect() as conn, conn.begin():
        authors_raw = pd.read_sql_query("""SELECT DISTINCT authors FROM nca_articles;""", conn)

    authors_split = []
    authors_temp = []

    authors_list = authors_raw.to_string(header=False, index=False)
    r = re.compile('(\\n\s\s+)')
    r.sub(',', authors_list)
    print(authors_list.split('\n'))
    for author in authors_list.split(','):
        author = author.strip()
        print(author)
    # for author in authors_list:
    #     print(author)
    #     author.replace('and', ',').replace('with', ',')
    #     authors_temp.append(author.split(','))
    #     for name in authors_temp:
    #         name = str(name)
    #         print(name.strip())
    #         authors_split.append(name.strip())
    # with open ('nca_authors.csv', 'w') as listfile:
    #     wr = csv.writer(listfile, dialect='excel')
    #     wr.writerow(authors_split)




nca_authors_unique(engine)
