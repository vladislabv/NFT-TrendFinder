import os
import sys
import logging
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from helpers.add_extensions import duration
# set logger
logger = logging.getLogger(__name__)

@duration
async def execute_agg_pipeline(db, collection, agg_pipeline, pipeline_name):
    result = await db[collection].aggregate(agg_pipeline).to_list(length = None)

    return result, pipeline_name

# ---*--- Aggregation Pipelines ---*---
pair_aggregation = [
  { "$addFields": { "pair": { "$concat": [ "$value", " ", "$key" ] } } },
  { "$match": { "value":{ "$nin": [ "None", "???" ] } } },
  { "$group": { "_id": "$pair", "totalAmount": {"$sum": 1} } },
  { "$sort": { "totalAmount": -1 } },
  { "$limit": 15 }
]

key_aggregation = [
  { "$match": { "value":{ "$nin": [ "None", "???" ] } } },
  { "$group": { "_id": "$key", "totalAmount": {"$sum": 1} } },
  { "$sort": { "totalAmount": -1 } },
  { "$limit": 15 }
]

value_aggregation = [
  { "$match": { "value":{ "$nin": [ "None", "???" ] } } },
  { "$group": { "_id": "$value", "totalAmount": {"$sum": 1} } },
  { "$sort": { "totalAmount": -1 } },
  { "$limit": 15 }
]

rich_items = [
    {
        '$sort': {
            'price': -1
        }
    }, {
        '$limit': 15
    }, {
        '$lookup': {
            'from': 'item_attribute', 
            'localField': '_id', 
            'foreignField': 'item_id', 
            'as': 'test'
        }
    }, {
        '$unwind': {
            'path': '$test', 
            'preserveNullAndEmptyArrays': False
        }
    }, {
        '$project': {
            '_id': 0, 
            'price': 1,
            'name': 1,
            'filename': 1,
            'key': '$test.key', 
            'value': '$test.value'
        }
    }, {
        '$addFields': {
            'pair': {
                '$concat': [
                    '$value', ' ', '$key'
                ]
            }
        }
    }, {
        '$group': {
            '_id': {
              'price': '$price',
              'name': '$name',
              'filename': '$filename'
              }, 
            'pairs': {
                '$push': '$pair'
            }
        }
    },
    {
      '$sort': {
        '_id.price': -1
      }
    }
]
# ---*--- Selection Queries ---*---
    
AGG_PIPELINES_DICT = {
    'pair_aggregation': ('item_attribute', pair_aggregation),
    'key_aggregation': ('item_attribute', key_aggregation),
    'value_aggregation': ('item_attribute', value_aggregation),
    'rich_items': ('nft_item', rich_items)
}
