from typing import List
import scrapy
import json
# custom logging which saves all the loggin into a txt file
from rmp.utils.logging.rmp_logger import logging
import os

from rmp.scraper.utils import parse_teacher, create_rmp_url

from rmp.utils.sqlite.database import SqlConnector
from rmp.models.models import Teacher

logging.root.setLevel(logging.DEBUG)


class RMPSpider(scrapy.Spider):
    name = "rmp"

    def __init__(self, *args, **kwargs):
        super(RMPSpider, self).__init__(*args, **kwargs)
        input_path = os.path.join(
            os.environ['DATAROOT'], 'scraping', kwargs['input_file'])

        with open(input_path) as fp:
            spider_input = json.load(fp)

        self.college_sid = spider_input['college_sid']
        self.names = spider_input['names']
        logging.info(
            f'Running scraping job on school SID {self.college_sid}. Got names: {self.names}')

        db_path = os.path.join(os.environ['DATAROOT'], 'db', kwargs['db_file'])

        self.sql = SqlConnector(db_path, spider_input['table_name'])
        logging.info(
            f'Initialized RMP spider with db at {db_path}, and table name {spider_input["table_name"]}')

    def start_requests(self):
        for name in self.names:
            url = create_rmp_url(name, self.college_sid)
            logging.debug(f"Parsing url: {url}")
            yield scrapy.Request(url=url, callback=self.parseRMP)

    def parseRMP(self, response: scrapy.Request):
        urls = response.xpath("//a[contains(@class,'TeacherCard')]//@href").getall()
        urls = ["https://www.ratemyprofessors.com" + url for url in urls]
        logging.debug(f'Response from {response.url}, urls: [{urls}]')
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_teachers)

    def parse_teachers(self, response) -> Teacher:
        teacher = parse_teacher(response)
        self.sql.insert(teacher)
        logging.debug(f'Successfully parsed teacher: {teacher.last} {teacher.first}')
        yield teacher
