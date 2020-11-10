#! /usr/bin/python/env
import scrapy
from scrapy.crawler import CrawlerProcess
import json
from pprint import pprint
import re

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
    print(value)
    return value

class NewsSpider(scrapy.Spider):
    name = "ABC"
    allowed_domains = ['abc.net.au']


    def start_requests(self):
        yield scrapy.Request("https://www.abc.net.au/news/justin/", self.parse)


    def parse(self, response):
        with open("abc_archive.json", "r") as source:
            data = json.load(source)
        page = response.url.split("/")[3]
        print("Page: ", page)
        title = response.selector.xpath("//@content")[2].get()
        print("Title: ", title)
        headtext = response.css('h1::text').get()
        print("Headtext: ", headtext)
        byline = response.selector.xpath('//span/span/p/a/text()').getall()
        print("Byline: ", byline)
        authors = response.selector.xpath("//@content")[12:14].getall()
        print("Authors: ", authors)
        print_date = response.selector.xpath("//@datetime").get()
        print("Print_date: ", print_date)
        tease = response.selector.xpath("//@content")[3].get()
        print("Tease: ", tease)
        bodytext = []
        clean_bodytext = []
        bodytext = response.css("p._1HzXw").getall()
        for par in bodytext:
            clean_bodytext.append(remove_tags(par))
        print("Bodytext: ", clean_bodytext)
        keywords = response.selector.xpath("//@content")[4].get()
        print("Keywords: ", keywords)
        article_tags = []
        for element in response.css('meta').getall():
            if "property=\"article:tag\"" in element:
                element = element.replace("\">", "")
                article_tags.append(element.replace("<meta data-react-helmet=\"true\" property=\"article:tag\" content=\"", ""))
        for item in article_tags:
            print("Tag: ", item)

        article_dict  =  {
            "title" : quote(title),
            "headtext" : quote(headtext),
            "byline " : quote(byline),
            "authors" : quote(authors),
            "print_date" : quote(print_date),
            "tease " : quote(tease),
            "bodytext " : quote(clean_bodytext),
            "keywords" : quote(keywords),
            "article_tags" : quote(article_tags)
        }
        data['Stories'].append(article_dict)
        with open("abc_archive.json", "w") as archive:
            archive = json.dump(data, archive, indent=2)
        with open("abc_archive.json", "r") as queue:
            url_update = json.load(queue)
        this_article = { quote(response.url) : "done" }
        url_update["Stories"].append(this_article)
        with open("abc_archive.json", "w") as new_queue:
            new_queue =json.dump(url_update, new_queue, indent=2)
        next_page = response.css('a._3OwCD').xpath('@href').getall()
        for page in next_page:
            if "/news/20" in page[:8]:
                yield response.follow(page, callback=self.parse)

process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {"format": "json"},
    },
})

process.crawl(NewsSpider)
process.start()