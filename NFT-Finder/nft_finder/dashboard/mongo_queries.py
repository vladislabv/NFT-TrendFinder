import logging
import datetime
from nft_finder.helpers.add_extensions import duration
# set logger
logger = logging.getLogger(__name__)

@duration
async def execute_agg_pipeline(db, collection, agg_pipeline, pipeline_name):
    result = await db[collection].aggregate(agg_pipeline).to_list(length = None)

    return result, pipeline_name

# ---*--- Aggregation Pipelines ---*---
pair_aggregation = [
  { "$match": { 
    "value":{ "$nin": [ "None", "none", "???" ] }
    }
  },
  { "$addFields": { "pair": { "$concat": [ "$value", " ", "$key" ] } } },
  { "$group": { "_id": "$pair", "totalAmount": {"$sum": 1}, "identificator": {"$first": "$item_id"} } },
  { "$sort": { "totalAmount": -1 } },
  {
    '$lookup': {
        'from': 'nft_item', 
        'localField': 'identificator', 
        'foreignField': '_id', 
        'as': 'related_item'
    }
  },
  { "$match": { 
      'related_item.sold_date': { '$gte': datetime.date(2022, 4, 1), '$lt': datetime.date.today() } 
      } 
  },
  {'$unset': 'related_item'},
  { "$limit": 15 }
]

key_aggregation = [
  { "$group": { "_id": "$key", "totalAmount": {"$sum": 1}, "identificator": {"$first": "$item_id"} } },
  { "$sort": { "totalAmount": -1 } },
  {
    '$lookup': {
        'from': 'nft_item', 
        'localField': 'identificator', 
        'foreignField': '_id', 
        'as': 'related_item'
    }
  },
  { "$match": { 
      "value":{ "$nin": [ "None", "none", "???" ] },
      'related_item.sold_date': { '$gte': datetime.date(2022, 4, 1), '$lt': datetime.date.today() } 
      } 
  },
  {'$unset': 'related_item'},
  { "$limit": 15 }
]

value_aggregation = [
  { "$group": { "_id": "$value", "totalAmount": {"$sum": 1}, "identificator": {"$first": "$item_id"} } },
  { "$sort": { "totalAmount": -1 } },
  {
    '$lookup': {
        'from': 'nft_item', 
        'localField': 'identificator', 
        'foreignField': '_id', 
        'as': 'related_item'
    }
  },
  { "$match": { 
      "value":{ "$nin": [ "None", "none", "???" ] },
      'related_item.sold_date': { '$gte': datetime.date(2022, 4, 1), '$lt': datetime.date.today() } 
      } 
  },
  {'$unset': 'related_item'},
  { "$limit": 15 }
]

rich_items = [
    {
        '$match': { 
            'filename': { '$exists': True },
            'sold_date': { '$gte': datetime.date(2022, 4, 1), '$lt': datetime.date.today() }
            }
    },
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
        '$addFields': {
            'pairs': { '$setUnion': [ '$pairs', [] ] }
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
