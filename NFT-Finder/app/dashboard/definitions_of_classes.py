"""In this file are collected all classes used in the project."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import time
import json
import typing

from retry import retry
#from app import db
#import numpy as np
import requests
import mongoengine as me

from .custom_exceptions import ItemIndexError, RequestFailedException
from .models import NftItem, ItemAttribute
from .add_extensions import SafeDict, SafeList, get_picture

class PreparedItem:
    """Class for extracting items from MongoDB and prepare them for further analysis"""
    TOTAL_OBJECTS_IMPORTED = 0
    # collect output of all object under a class variable
    # OUTPUT_TABLE = pd.DataFrame()

    def __init__(self, item: dict) -> None:
        self.item = SafeDict(item)
        self.meta = self.item.pop('meta')
        self.attributes = self.meta.pop('attributes')
        self.last_sale = self.item.pop('lastSale')
        self.content_info = self.meta.pop('content')

    def import_attributes(self) -> SafeDict:
        """Returns pivoted item attributes"""
        for attribute in self.attributes:
            attribute = SafeDict(attribute)
            if 'key' not in attribute.keys():
                attribute['key'] = ''
            if 'value' not in attribute.keys():
                attribute['value'] = ''
            if len(attribute['key']) and len(attribute['value']):
                try:
                    ItemAttribute(
                        item_id = self.item['id'],
                        key = attribute['key'],
                        value = attribute['value']
                    ).save()
                except me.ValidationError as err:
                    print(err)
                    pass

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
        sale_dict['sold_date'] = datetime.strptime(self.last_sale.pop('date', datetime.now), '%Y-%m-%dT%H:%M:%SZ')
        sale_dict['seller_id'] = self.last_sale.pop('seller', None)
        sale_dict['buyer_id'] = self.last_sale.pop('buyer', None)
        sale_dict['price'] = float(self.last_sale.pop('price', None))

        return sale_dict

    def form_item(self) -> SafeDict:
        keys = ['id', 'creators', 'mintedAt']
        item_dict = SafeDict(self.item)
        item_dict = {k: v for k, v in item_dict.items() if k in keys}
        item_dict['minted_at'] = datetime.strptime(item_dict.pop('mintedAt'), '%Y-%m-%dT%H:%M:%SZ')
        item_dict['_id'] = item_dict.pop('id').split(':')[1]
        item_dict['creators'] = [creator['account'] for creator in item_dict.pop('creators')]

        return item_dict

    def form_output(self) -> SafeDict:
        # form interim class attributes
        output = SafeDict({})
        self.import_attributes()
        output.update(self.form_content())
        output.update(self.form_last_sale())
        output.update(self.form_item())
        #print(output)
        #print(output['_id'])
        try:
            output_item = NftItem(
                _id = output['_id'],
                minted_at = output['minted_at'],
                url = output['url'], 
                creators = output['creators'],
                seller_id = output['seller_id'],
                buyer_id = output['buyer_id'],
                sold_date = output['sold_date'],
                price = output['price'],
                currency = output['currency'],
                key = output['attributes']['key'],
                value = output['attributes']['value']
            )
            output_item.save()
            PreparedItem.TOTAL_OBJECTS_IMPORTED += 1
            
            if output['url']:
                avatar_img = get_picture(output['url'])
                output_item.put(avatar_img)

        except (me.ValidationError) as err:
            print(err)
            pass

        #return output


@dataclass
class OutputAPI:
    """The class is needed for fetching data from Rarible API and convert it into 
    the table form.
    """
    task: 'typing.Any'
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

        response = requests.get(self.BASE_URL, params=self.query)
        if response.status_code == 200:
            result = response.json()
            self.query["continuation"] = result["continuation"]
            # items is required field
            if len(result['items']):
                return SafeList(result['items'])
        else:
            raise RequestFailedException(response)

    def get_filtered_items(self) -> list[dict]:
        """test_string"""
        def validate(item) -> bool:
            """Look for non-deleted, ever sold, image items"""
            item = SafeDict(item)
            try:
                item_content = SafeList(item['meta']['content'])
                item_type = item_content.get( 0, SafeDict({}) )['@type']
            except IndexError as e:
                raise ItemIndexError(item, e)
            #print(item)
            return all([
                    not item['deleted'], # still exists
                    ('IMAGE' == item_type), # is image
                    len(item['lastSale']), # was ever sold
                    len(item['meta']['attributes']) # has at least some attributes
                ])

        raw_items = self.get_raw_items()

        return list( filter(validate, raw_items) )
    
    def fetch_items_from_API(self) -> None:
        self.query = self.form_dict()
        left = self.OUTPUT_LIMIT
        while left > 0:
            #left = self.OUTPUT_LIMIT - PreparedItem.TOTAL_OBJECTS_IMPORTED
            self.task.update_state(
                state = 'PROGRESS',
                meta = {
                    'current': PreparedItem.TOTAL_OBJECTS_IMPORTED, 
                    'total': self.OUTPUT_LIMIT,
                    'status': f'Items left: {left}'
                    }
                )

            filtered_items = self.get_filtered_items()

            for item in filtered_items:
                _ = PreparedItem(item).form_output()

            left -= PreparedItem.TOTAL_OBJECTS_IMPORTED

        return {
            'state': 'FINISHED',
            'current': self.OUTPUT_LIMIT, 
            'total': self.OUTPUT_LIMIT,
            'status': f'Objects were fetched: {PreparedItem.TOTAL_OBJECTS_IMPORTED}'
            }