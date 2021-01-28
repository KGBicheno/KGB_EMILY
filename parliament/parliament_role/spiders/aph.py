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

print("APH spider is a go")

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


class AphSpider(scrapy.Spider):
    name = 'aph'
    allowed_domains = ['aph.gov.au']
    start_urls = [
        'https://www.aph.gov.au/Senators_and_Members/Parliamentarian_Search_Results?q=&mem=1&par=-1&gen=0&ps=96&st=1',
        'https://www.aph.gov.au/Senators_and_Members/Parliamentarian_Search_Results?page=2&q=&mem=1&par=-1&gen=0&ps=96&st=1'
    ]

    def parse(self, response):
        print("Parsing URL")
        try:
            print("Attempting connection.")
            connection = psycopg2.connect(
            user = "websinthe",
            password = PSQL_PASS,
            host = "192.168.132.19",
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
            # response.xpath('//h1/text()').get() << Hon Anthony Albanese MP
            # response.xpath('//h3/text()').getall()[6] << Granyndler, New South Wales
            # response.xpath('//dl/dd/text()').getall()[0:3]
            # ['Leader of the Opposition',
            # 'Australian Labor Party',
            # 'House of Representatives',
            # response.xpath('//div/strong/following-sibling::p/text()').getall()
            # ['\r\n                                    334A Marrickville Road',
            # '\r\n                                    Marrickville, NSW, 2204\r\n                                ',
            # '\r\n                                     PO Box 5100',
            # '\r\n                                      Marrickville, NSW, 2204\r\n                                       \r\n                                ']
