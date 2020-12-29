#! /usr/bin/python/env
from datetime import date, time
from datetime import datetime, timedelta
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

print("NCA spider is a go")

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
    name = "NCA"
    allowed_domains = ['news.com.au']
    custom_settings = {
        'DEPTH_PRIORITY' : 1,
        'SCHEDULER_DISK_QUEUE' : 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE' : 'scrapy.squeues.FifoMemoryQueue'
    }


    def start_requests(self):
        yield scrapy.Request("https://www.news.com.au/national/breaking-news", self.parse)


    def parse(self, response):
        print("Parsing URL")
        try:
            print("Attempting connection.")
            connection = psycopg2.connect(
            user = "websinthe",
            password = PSQL_PASS,
            host = "192.168.1.19",
            port = "5432",
            database = "websinthe"
            )
            cursor = connection.cursor()
            print(connection.get_dsn_parameters(), "\n")
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("Successfully connected to ", record, "\n")
            cursor.close()
            cursor = connection.cursor()
            print(connection.get_dsn_parameters(), "\n")
            page_url = response.url         #.split("/")[3]
            print("Page: ", page_url)
            title = response.css("h1.story-headline::text").get()
            print("Title: ", title)
            headtext = response.css("h1.story-headline::text").get()
            print("Headtext: ", headtext)
            byline = response.selector.xpath('//span/span/p/a/text()').getall()
            print("Byline: ", byline)
            authors = response.css(".name::text").get()
            print("Authors: ", authors)
            pub_date = response.css(".date::text").get()
            pub_time = response.css(".time::text").get()
            if pub_date is not None:
                pub_date = pub_date + " " + pub_time
                pub_date = datetime.strptime(pub_date, "%B %d, %Y %I:%M%p")
                print_date = pub_date.strftime("%Y/%m/%d %H:%M:%S")
                print_date = print_date + "+10"
            else:
                print_date = "2000-01-01 01:01:01+10"
            print("Print_date: ", print_date)
            tease = response.css(".intro::text").get()
            print("Tease: ", tease)
            bodytext = []
            clean_bodytext = []
            bodytext = response.css(".intro::text").get()
            if "Video:" in bodytext:
                clean_bodytext = bodytext[2:-7]
            else:
                clean_bodytext = bodytext[1:-7]
            #print("Bodytext: ", clean_bodytext)
            keyword_list = response.selector.xpath("//meta/@content").getall()
            keywords = keyword_list[7]
            print("Keywords: ", keywords)
            article_tags = []
            article_tags = keywords.split(",")

            if page_url != "https://www.news.com.au/national/breaking-news":
                postgres_insert_query = """ INSERT INTO nca_articles (page_url, title, headtext, byline, authors, print_date, tease, bodytext, keywords, tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                record_to_insert = (page_url, title, headtext, byline, authors, print_date, tease, clean_bodytext, keywords, article_tags)
                cursor.execute(postgres_insert_query, record_to_insert)
                connection.commit()
                print("**************************************\n")
                print("Record added to the articles table. \n")
                print("**************************************\n")
        except (Exception, psycopg2.Error) as error:
            print("Error while connection to database: ", error)
        finally:
            if(connection):
                cursor.close()
                connection.close()
                print("Connection to database has been closed.")
        sections_list = ['/natio', '/world', '/lifes', '/trave', '/enter', '/techn', '/finan', '/sport']
        next_page = response.selector.xpath("//a/@href").getall()
        for page in next_page:
            for section in sections_list:
                if section in page[23:30]:
                    yield response.follow(page, callback=self.parse)

process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {"format": "json"},
    },
})



process.crawl(NewsSpider)
process.start()
