"""In this file are collected all classes used in the project."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time

import pymongo
from retry import retry
import pandas as pd
# import numpy as np
import requests
from custom_exceptions import ItemIndexError, RequestFailedException


@dataclass
class MongoDB:
    CONNECTION_STRING: str

    def get_database():
        client = pymongo.MongoClient(
            "mongodb+srv://admin:admin@cluster0.rb36j.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        )
        db = client.test
        print(db)


class PreparedItem:
    """Class for extracting items from MongoDB and prepare them for further analysis"""
    TOTAL_OBJECTS = 0
    # collect output of all object under a class variable
    OUTPUT_TABLE = pd.DataFrame()

    def __init__(self, item: dict) -> None:
        PreparedItem.TOTAL_OBJECTS += 1
        self.item = item
        self.meta = self.item.pop('meta')
        self.attributes = self.meta.pop('attributes')
        self.last_sale = self.item.pop('lastSale')
        self.content_info = self.meta.pop('content')

    def form_attributes(self) -> None:
        """Returns pivoted item attributes"""
        attr_df = pd.DataFrame(self.attributes)
        attr_df['id'] = self.item['id']

        self.attributes = attr_df

    def form_content(self) -> None:
        content_df = pd.DataFrame.from_dict(self.content_info)

        self.content_info = content_df.head(1)[['url']]

    def form_last_sale(self) -> None:
        self.last_sale['currency'] = self.last_sale.pop('currency').get('@type')
        sale_df = pd.DataFrame(self.last_sale, index=[0])

        sale_df.drop(columns=['value'], inplace=True)
        sale_df.rename(columns={'date': 'sold_date', 'seller': 'seller_id', 'buyer': 'buyer_id'}, inplace=True)

        add_sell_cols = ['seller_id', 'buyer_id']
        for col in add_sell_cols:
            if col not in sale_df.columns:
                sale_df[col] = None

        self.last_sale = sale_df

    def form_item(self) -> None:
        keys = ['id', 'creators', 'mintedAt']
        self.item = {k: v for k, v in self.item.items() if k in keys}
        self.item['creator_id'] = self.item.pop('creators')[0]['account']

        self.item = pd.DataFrame(self.item, index=[0])

    def form_output(self) -> None:
        # form interim class attributes
        self.form_attributes()
        self.form_content()
        self.form_last_sale()
        self.form_item()

        base_info = pd.concat(
            [self.item, self.content_info, self.last_sale],
            axis=1
        )

        output = base_info.merge(self.attributes, on='id', how='inner')

        PreparedItem.OUTPUT_TABLE = pd.concat([PreparedItem.OUTPUT_TABLE, output], axis=0)


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
            result = response.json()
            self.query["continuation"] = result.get("continuation")
            # items is required field
            return result['items']
        else:
            raise RequestFailedException(response)

    def get_filtered_items(self) -> list[dict]:
        def filter_valid_sold_items(item) -> bool:
            """Look for non-deleted, ever sold, image items"""
            try:
                is_alive = not item['deleted']
                is_sold = item.get('lastSale', False)
                item_meta = item.get('meta', False)
                item_type = ''
                item_attr = []
                if item_meta:
                    item_attr = item_meta['attributes']
                    item_content = item_meta['content']
                    if len(item_content):
                        item_type = item_content[0].get('@type', '')
            except IndexError as e:
                raise ItemIndexError(item, e)

            return is_alive and is_sold and ('IMAGE' == item_type) and len(item_attr)

        raw_items = self.get_raw_items()
        return list(
            filter(
                filter_valid_sold_items, raw_items
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
