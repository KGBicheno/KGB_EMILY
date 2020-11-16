import scrapy


class AphSpider(scrapy.Spider):
    name = 'aph'
    allowed_domains = ['aph.gov.au']
    start_urls = ['http://aph.gov.au/']

    def parse(self, response):
        pass
