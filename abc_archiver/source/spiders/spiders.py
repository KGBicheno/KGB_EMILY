#! /usr/bin/python/env
import scrapy
from scrapy.crawler import CrawlerProcess
import json
from pprint import pprint
import re
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

PSQL_PASS = os.getenv("PSQL_PASS")

print("spider is a go")

TAG_RE = re.compile(r"<[^>]+>")

def remove_tags(text):
    return TAG_RE.sub('', text)

def quote(value):
    if type(value) == str():
        value = "\"" + value + "\""
    if type(value) == list():
        for value in list:
            if type(value) == str():
                value = "\"" + value + "\""
    return value

class NewsSpider(scrapy.Spider):
    name = "ABC"
    allowed_domains = ['abc.net.au']


    def start_requests(self):
        yield scrapy.Request("https://www.abc.net.au/news/justin/", self.parse, connection)


    def parse(self, response, connection):
        cursor = connection.cursor()
        print(connection.get_dsn_parameters(), "\n")
        page_url = response.url         #.split("/")[3]
        print("Page: ", page_url)
        title = response.selector.xpath("//@content")[2].get()
        print("Title: ", title)
        headtext = response.css('h1::text').get()
        print("Headtext: ", headtext)
        byline = response.selector.xpath('//span/span/p/a/text()').getall()
        print("Byline: ", byline)
        authors = response.selector.xpath("//@content")[12:14].getall()
        print("Authors: ", authors)
        pub_date = response.selector.xpath("//@datetime").get()
        if pub_date is not None:
            print_date = pub_date[0:10] + " " + pub_date[11:19] + "+10"
        else:
            print_date = "2000-01-01 01:01:01+10"
        print("Print_date: ", print_date)
        tease = response.selector.xpath("//@content")[3].get()
        print("Tease: ", tease)
        bodytext = []
        clean_bodytext = []
        bodytext = response.css("p._1HzXw").getall()
        for par in bodytext:
            clean_bodytext.append(remove_tags(par))
        #print("Bodytext: ", clean_bodytext)
        keywords = response.selector.xpath("//@content")[4].get()
        print("Keywords: ", keywords)
        article_tags = []
        for element in response.css('meta').getall():
            if "property=\"article:tag\"" in element:
                element = element.replace("\">", "")
                article_tags.append(element.replace("<meta data-react-helmet=\"true\" property=\"article:tag\" content=\"", ""))
        for item in article_tags:
            print("Tag: ", item)

        if page_url != "https://www.abc.net.au/news/justin/":
            postgres_insert_query = """ INSERT INTO articles (page_url, title, headtext, byline, authors, print_date, tease, bodytext, keywords, tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            record_to_insert = (page_url, title, headtext, byline, authors, print_date, tease, clean_bodytext, keywords, article_tags)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            count = cursor.rowcount
            print("**************************************\n")
            print(count, " record added to the articles table. \n")
            print("**************************************\n")
        cursor.close()
        #article_dict  =  {
        #    "title" : quote(title),
        #    "headtext" : quote(headtext),
        #    "byline " : quote(byline),
        #    "authors" : quote(authors),
        #    "print_date" : quote(print_date),
        #    "tease " : quote(tease),
        #    "bodytext " : quote(clean_bodytext),
        #    "keywords" : quote(keywords),
        #    "article_tags" : quote(article_tags)
        #}
        #data['Stories'].append(article_dict)
        #with open("abc_archive.json", "w") as archive:
        #    archive = json.dump(data, archive, indent=2)
        #with open("abc_archive.json", "r") as queue:
        #    url_update = json.load(queue)
        #this_article = { quote(response.url) : "done" }
        #url_update["Stories"].append(this_article)
        #with open("abc_archive.json", "w") as new_queue:
        #    new_queue =json.dump(url_update, new_queue, indent=2)
        next_page = response.css('a._3OwCD').xpath('@href').getall()
        for page in next_page:
            if "/news/20" in page[:8]:
                yield response.follow(page, callback=self.parse)

process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {"format": "json"},
    },
})

try:
    connection = psycopg2.connect(
        user = "websinthe",
        password = PSQL_PASS,
        host = "192.168.1.7",
        port = "5432",
        database = "websinthe"
    )

    cursor = connection.cursor()
    print(connection.get_dsn_parameters(), "\n")
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("Successfully connected to ", record, "\n")
    cursor.close()

    process.crawl(NewsSpider)
    process.start()


except (Exception, psycopg2.Error) as error:
    print("Error while connection to database: ", error)
finally:
    if(connection):
        cursor.close()
        connection.close()
        print("Connection to database has been closed.")