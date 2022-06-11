"""Defined JSON Schemas for the MONGO Database"""

ntf_item_schema = {
    '$jsonSchema': {
         'bsonType': "object",
         'required': ["_id", "sold_date", "price", "currency", "url", "minted_at"],
         'properties': {
            '_id': {
                'bsonType': "string",
                'description': "must be a string and is required, usually id fetched from the API"
            },
            'name': {
               'bsonType': "string",
               'description': "must be a string, provides name of a ntf item"
            },
            'description': {
                'bsonType': "string",
                'minLength': 0,
                'maxLength': 300,
                'description': "must be a string, provides short description of a nft item"
            },
            'url': {
                'bsonType': "string",
                'description': "redirects to the image in internet, must be a string and is required"
            },
            'filename': {
                'bsonType': "string",
                'pattern': "\/.*?\.[\w:]+",
                'description': "must be a string, relates to the local path, where an image is stored"
            },
            'minted_at': {
                'bsonType': "date",
                'description': "must be a python datatime object and is required, serves as the creation date of a nft item"
            },
            'sold_date': {
                'bsonType': "date",
                'description': "must be a python datetime object and is required, serves as the date of last sale of a nft item"
            },
            'price': {
                'bsonType': "double",
                'description': "must be a float and is required, displays the price of last sale"
            },
            'currency': {
                'bsonType': "string",
                'description': "must be a string and is required, relates to the crypto which used in last sale"
            },
            'creators': {
                'bsonType': "string",
                'description': "must be a string, the id relates to the user issued the item, collaboration is excluded"
            },
            'seller_id': {
                'bsonType': "string",
                'description': "must be a string, the id relates to the user sold the item, can be same as the creator"
            },
            'buyer_id': {
                'bsonType': "string",
                'description': "must be a string, the id relates to the user bought the item"
            },
            'attr_string': {
                'bsonType': "string"
            }
         }
      }
    }

item_attribute_schema = {
    '$jsonSchema': {
         'bsonType': "object",
         'required': ["item_id", "key", "value"],
         'properties': {
            'item_id': {
               'bsonType': "string",
               'description': "must be a string and is required, relates to an existing nft item"
            },
            'key': {
                'bsonType': "string",
                'minLength': 3,
                'description': "must be a string and is required"
            },
            'value': {
                'bsonType': "string",
                'minLength': 3,
                'description': "must be a string and is required"
            }
         }
      }
    }

schemas = {
    'nft_item': ntf_item_schema,
    'item_attribute': item_attribute_schema
}