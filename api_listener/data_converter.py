"""Defined class for converting raw API output into the feasible form, that collections accept"""
import logging
from typing import List, Tuple
from datetime import datetime
from helpers.add_extensions import SafeDict, SafeList

# setting logger
logger = logging.getLogger(__name__)

class PreparedItem:
    """Class for extracting items from the MongoDB and preparing them for further analysis"""
    TOTAL_OBJECTS_IMPORTED = 0
    def __init__(self, item: dict) -> None:
        self.item = SafeDict(item)
        self.item['_id'] = self.item.pop('id').split(':')[1]
        self.meta = self.item.pop('meta')
        self.attributes = self.meta.pop('attributes')
        self.last_sale = self.item.pop('lastSale', None)
        self.content_info = self.meta.pop('content')
        

    def import_attributes(self) -> Tuple[List[SafeDict], str]:
        """Function sorting out keys and values < 3 characters and creates non-existing fields if needed

        Returns:
            tuple[list[SafeDict], str]: A tuple containing list of dicts 
            with NFT attributes and a string, which holds them in a concatenated version
        """
        output_items = SafeList([])
        attribute_str_global = ''
        number_of_attributes = len(self.attributes)
        attributes_imported = 0
        for attribute in self.attributes:
            attribute = SafeDict(attribute)
            if 'key' not in attribute.keys():
                attribute['key'] = ''
            if 'value' not in attribute.keys():
                attribute['value'] = ''
            if len(attribute['key']) and len(attribute['value']):
                output_item = SafeDict(
                    {
                        'item_id': self.item['_id'],
                        'key': attribute['key'],
                        'value': attribute['value']
                    }
                )
                output_items.append(output_item)
                attributes_imported += 1
                if len(attribute_str_global):
                    attribute_str_global += ', ' + attribute['value'] + ' ' + attribute['key']
                else:
                    attribute_str_global += attribute['value'] + ' ' + attribute['key']

        assert attributes_imported <= number_of_attributes

        return output_items, attribute_str_global


    def form_content(self) -> SafeDict:
        """Function converting meta information of a NFT into feasible form

        Returns:
            SafeDict: A dictionary containing following keys: 'url', 'description', 'name'
        """
        content_list = SafeList(self.content_info)
        content_dict = SafeDict({})
        content_dict['url'] = content_list.get(0, SafeDict({}) )['url']
        content_dict['description'] = self.meta.get('description')
        if content_dict['description']:
            content_dict['description'] = content_dict['description'][:300]
        content_dict['name'] = self.meta.get('name')

        return content_dict

    
    def form_last_sale(self) -> SafeDict:
        """Method summarizes information about the last sale of a NFT

        Returns:
            SafeDict: Dictionary containing following keys: 'currency','sold_date','seller_id','buyer_id','price'
        """
        sale_dict = SafeDict({})
        if self.last_sale:
            sale_dict['currency'] = self.last_sale.pop('currency').get('@type', 'ETH')
            sale_dict['sold_date'] = self.last_sale.pop('date', datetime.now)
            try:
                sale_dict['sold_date'] = datetime.strptime(sale_dict['sold_date'], '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                sale_dict['sold_date'] = datetime.strptime(sale_dict['sold_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            sale_dict['seller_id'] = self.last_sale.pop('seller', None).split(':')[-1]
            sale_dict['buyer_id'] = self.last_sale.pop('buyer', None).split(':')[-1]
            sale_dict['price'] = float(self.last_sale.pop('price', None))
        else:
            sale_dict['currency'] = 'ETH'
            sale_dict['sold_date'] = datetime.now
            sale_dict['seller_id'] = ''
            sale_dict['buyer_id'] = ''
            sale_dict['price'] = 0
        return sale_dict


    def form_item(self) -> SafeDict:
        """Function renames fields got from the API and summarizes information about the creators and creation date 

        Returns:
            SafeDict: Dictionary containing keys: '_id','minted_at','creators'
        """
        keys = ['_id', 'creators', 'mintedAt']
        item_dict = SafeDict(self.item)
        item_dict = {k: v for k, v in item_dict.items() if k in keys}
        item_dict['minted_at'] = item_dict.pop('mintedAt', datetime.now)
        try:
            item_dict['minted_at'] = datetime.strptime(item_dict['minted_at'], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            item_dict['minted_at'] = datetime.strptime(item_dict['minted_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        item_dict['creators'] = [creator['account'].split(':')[-1] for creator in item_dict.pop('creators')]
        if len(item_dict['creators']):
            item_dict['creators'] = item_dict['creators'][0]
        else:
            item_dict['creators'] = ''

        return item_dict
        

    def form_output(self) -> Tuple[List[dict], dict]:
        """Function summarizes separately prepared item contents

        Returns:
            tuple[list[dict], dict]: A tuple containing list of the prepaired item attributes and the nft itself
        """
        output = SafeDict({})
        attributes, attr_string = self.import_attributes()
        if len(attributes):
            output.update(self.form_content())
            output.update(self.form_last_sale())
            output.update(self.form_item())

            output_item = SafeDict(
                {
                    '_id': output['_id'],
                    'minted_at': output['minted_at'],
                    'name': output['name'],
                    'url': output['url'], 
                    'description': output['description'],
                    'creators': output['creators'],
                    'seller_id': output['seller_id'],
                    'buyer_id': output['buyer_id'],
                    'sold_date': output['sold_date'],
                    'price': output['price'],
                    'currency': output['currency']
                }
            )
        else:
            logger.exception(Exception(f"No attributes could be retrieved by nft item: {output['_id']}."))
            output_item = None
        return attributes, output_item
