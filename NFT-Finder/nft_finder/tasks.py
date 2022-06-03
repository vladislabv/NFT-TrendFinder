import time
import json
import pickle
from pprint import pprint
from mongoengine import connect
from config import MONGODB_DB, MONGODB_CONNECTION_STRING
from nft_finder import celery
#from nft_finder import db_client as client
from nft_finder.dashboard.prepare_data import prepare_data
from nft_finder.dashboard.mongo_queries import AGG_PIPELINES_DICT
from nft_finder.dashboard.models import NftItem, ItemAttribute
from nft_finder.helpers.add_extensions import id_generator


def mongo_connect():
    conn_str =f"{MONGODB_CONNECTION_STRING}/{MONGODB_DB}"
    return connect(host = conn_str)

@celery.task()
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True

@celery.task(bind = True)
def get_dashboard_data(self):
    result_raw = []
    mongo_connect()
    total = len(AGG_PIPELINES_DICT) + 1
    for i, pipeline_name in enumerate(AGG_PIPELINES_DICT):
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i, 
                'total': total,
                'status': f"Starting query #{i+1}"
                }
        )
        time.sleep(0.5)
        collection = AGG_PIPELINES_DICT[pipeline_name][0]
        pipeline = AGG_PIPELINES_DICT[pipeline_name][1]
        if collection == "item_attribute":
            pip_result_raw = ItemAttribute.objects().aggregate(pipeline)
        else:
            pip_result_raw = NftItem.objects().aggregate(pipeline)
        self.update_state(
            state='PROGRESS',
            meta={
                'current': i, 
                'total': total,
                'status': f"Done query #{i+1}"
                }
            )
        time.sleep(1)
        result_raw.append((list(pip_result_raw), pipeline_name))
    
    self.update_state(
            state='PROGRESS',
            meta={
                'current': total - 1, 
                'total': total,
                'status': "Prepairing data..."
                }
            )

    result = prepare_data(result_raw)
    result_path = str(f'celery_results/result_{id_generator(size=4)}.dat')
    with open(result_path, 'wb+') as file:
        pickle.dump(result, file)

    return {
        'current': 100, 
        'total': 100, 
        'status': 'Completed!',
        'result': result_path
        }
    #return result_path