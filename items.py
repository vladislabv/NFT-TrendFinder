# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from datetime import datetime
import scrapy

@dataclass
class RaribleUser:
    id: str
    url: str
    picture: str

@dataclass
class RaribleNftItem:
    # define the fields for your item here like:
    id: str
    url: str
    picture: str
    date: datetime
    price: float
    currency: str
    
