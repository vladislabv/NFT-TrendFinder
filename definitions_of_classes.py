"""In this file are collected all classes used in the project."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time

from retry import retry
import pandas as pd
#import numpy as np
import requests
from pymongo import MongoClient

from custom_exceptions import ItemIndexError, RequestFailedException

class SafeDict(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value
    
class SafeList(list):
    # https://stackoverflow.com/a/5125712
    def get(self, index, default=None):
        try:
            return self.__getitem__(index)
        except IndexError:
            return default

@dataclass
class MongoDB:
    CONNECTION_STRING: str

    def get_database():

        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/myFirstDatabase"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        
        client = MongoClient(CONNECTION_STRING)

        # Create the database for our example (we will use the same database throughout the tutorial
        return client['user_shopping_list']

class PreparedItem:
    """Class for extracting items from MongoDB and prepare them for further analysis"""
    TOTAL_OBJECTS = 0
    # collect output of all object under a class variable
    # OUTPUT_TABLE = pd.DataFrame()

    def __init__(self, item: dict) -> None:
        PreparedItem.TOTAL_OBJECTS += 1
        self.item = SafeDict(item)
        self.meta = self.item.pop('meta')
        self.attributes = self.meta.pop('attributes')
        self.last_sale = self.item.pop('lastSale')
        self.content_info = self.meta.pop('content')

    def form_attributes(self) -> SafeDict:
        """Returns pivoted item attributes"""
        #attr_df = pd.DataFrame(self.attributes)
        #attr_df['id'] = self.item['id']

        #self.attributes = attr_df

        return SafeDict(self.attributes)

    def form_content(self) -> SafeDict:
        content_list = SafeList(self.content_info)
        content_dict = SafeDict({})
        content_dict['url'] = content_list.get(0, SafeDict({}) )['url']
        # = pd.DataFrame.from_dict(self.content_info)
        
        #self.content_info = content_df.head(1)[['url']]
        return content_dict
    
    def form_last_sale(self) -> SafeDict:
        sale_dict = SafeDict({})
        sale_dict['currency'] = self.last_sale.pop('currency').get('@type', 'ETH')
        sale_dict['sold_date'] = self.last_sale.pop('date', datetime.now)
        sale_dict['seller_id'] = self.last_sale.pop('seller', None)
        sale_dict['buyer_id'] = self.last_sale.pop('buyer', None)

        #self.last_sale['currency'] = self.last_sale.pop('currency').get('@type')
        #sale_df = pd.DataFrame(self.last_sale, index=[0])

        #sale_df.drop(columns=['value'], inplace=True)
        #sale_df.rename(columns={'date':'sold_date', 'seller':'seller_id', 'buyer':'buyer_id'}, inplace=True)

        #add_sell_cols = ['seller_id', 'buyer_id']
        #for col in add_sell_cols:
        #    if col not in sale_df.columns:
        #        sale_df[col] = None
        
        #self.last_sale = sale_df
        return sale_dict

    def form_item(self) -> SafeDict:
        keys = ['id', 'creators', 'mintedAt']
        item_dict = SafeDict(self.item)
        item_dict = {k: v for k, v in item_dict.items() if k in keys}
        item_dict['minted_at'] = item_dict.pop('mintedAt')
        item_dict['_id'] = item_dict.pop('id')
        #self.item['creator_id'] = self.item.pop('creators')[0]['account']
        
        #self.item = pd.DataFrame(self.item, index=[0])
        return item_dict

    def form_output(self) -> SafeDict:
        # form interim class attributes
        output = SafeDict({})
        output.update(self.form_attributes())
        output.update(self.form_content())
        output.update(self.form_last_sale())
        output.update(self.form_item())



        return output

        #base_info = pd.concat(
        #    [self.item, self.content_info, self.last_sale],
        #    axis=1
        #    )

        #output = base_info.merge(self.attributes, on='id', how='inner')

        #PreparedItem.OUTPUT_TABLE = pd.concat([PreparedItem.OUTPUT_TABLE, output], axis=0)


@dataclass
class OutputAPI:
    """The class is needed for fetching data from Rarible API and convert it into 
    the table form.
    """
    duration: int = 1
    to_date: datetime = field(default_factory=datetime.now)
    BLOCKCHAIN_REQUEST = 'ETHEREUM' 
    SIZE_RESPONSE = 100
    OUTPUT_LIMIT = 10_000
    REQUEST_TIMEOUT = 10
    BASE_URL = 'https://api.rarible.org/v0.1/items/all'

    def form_dict(self) -> dict:
        from_date = self.to_date - timedelta(days=self.duration)
        date_unix = time.mktime(from_date.timetuple())
        return {
            "size": self.SIZE_RESPONSE, 
            "blockchains": self.BLOCKCHAIN_REQUEST, 
            "lastUpdatedFrom": int(date_unix)
            }

    @retry(RequestFailedException, tries=3, delay=2)
    def get_raw_items(self) -> list[dict]:

        self.query = self.form_dict()
        response = requests.get(self.BASE_URL, params=self.query)
        if response.status_code == 200:
            result = SafeDict(response.json())
            self.query["continuation"] = result.get("continuation")
            # items is required field
            if len(result['items']):
                return SafeList(result['items'])
        else:
            raise RequestFailedException(response)

    def get_filtered_items(self) -> list[dict]:

        def validate(item) -> bool:
            """Look for non-deleted, ever sold, image items"""
            try:
                item_content = SafeList(item['meta']['content'])
                item_type = item_content.get( 0, SafeDict({}) )['@type']
            except IndexError as e:
                raise ItemIndexError(item, e)

            return all([
                    not item['deleted'], # still exists
                    ('IMAGE' == item_type), # is image
                    len(item['lastSale']), # was ever sold
                    len(item['meta']['attributes']) # has at least some attributes
                ])

        raw_items = self.get_raw_items()
        return list(
            filter(
                validate, raw_items
            )
        )
    
    def fetch_items_from_API(self) -> pd.DataFrame:
        cycles = int(self.OUTPUT_LIMIT / self.SIZE_RESPONSE)
        result_table = pd.DataFrame()
        for i in range(cycles):
            print(f'Processing data, cycles left {cycles - i}.\n')
            filtered_items = self.get_filtered_items()
            _ = [PreparedItem(item).form_output() for item in filtered_items]
            result_table = pd.concat(
                [result_table, PreparedItem.OUTPUT_TABLE],
                axis=0
                )
            PreparedItem.OUTPUT_TABLE = pd.DataFrame()
        return result_table