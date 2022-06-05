import os
import re
import time
import pickle
import subprocess
import datetime
from mongoengine import connect
from config import MONGODB_DB, MONGODB_CONNECTION_STRING, DALLE_ENV, DALLE_FOLDER
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

@celery.task(bind=True)
def generate_picture(self, data: str):
    num_images = 1
    shell_command = f'A: && cd {DALLE_FOLDER} && {DALLE_ENV} && python generate.py --dalle_path ./dalle.pt --text="{data.lower()}" --num_images={num_images}'
    self.update_state(
        state = 'PROGRESS',
        meta = {
            'current': 0,
            'total': 100,
            'status': 'Your query is being processed...'
        }
    )
    subpr = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE)
    result_path = ''
    pattern = '\"outputs.((.*?)_)+(.*?)$'
    i = 0
    while subpr.poll() is None:
        out_line_raw = subpr.stdout.readline()
        out_line_text = out_line_raw.decode('cp1251')
        if out_line_text is not None and len(out_line_text) > 0:
            i += 1
            self.update_state(
                state = 'PROGRESS',
                meta = {
                    'current': i,
                    'total': 100,
                    'status': out_line_text
                }
            )
            if 'outputs\\' in out_line_text:
                result_path = os.path.join(
                    DALLE_FOLDER, 
                    str(
                        re.search(pattern, out_line_text)[0]
                        ).replace('"', '')
                    )
    return {
        'current': 100, 
        'total': 100, 
        'status': 'Completed!',
        'result': os.path.join(DALLE_FOLDER, result_path)
        }

@celery.task(bind = True)
def get_dashboard_data(self, num_items, start_date, end_date):
    result_raw = []
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d") or ""
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d") or ""
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
        for item in pipeline:
            if item.get('$limit'):
                item['$limit'] = num_items
            elif item.get('$match', {}).get('sold_date'):
                if not isinstance(start_date, str) and not isinstance(end_date, str):
                    item['$match']['sold_date']['$gte'] = start_date
                    item['$match']['sold_date']['$lt'] = end_date
            elif item.get('$match', {}).get('related_item.sold_date'):
                if not isinstance(start_date, str) and not isinstance(end_date, str):
                    item['$match']['related_item.sold_date']['$gte'] = start_date
                    item['$match']['related_item.sold_date']['$lt'] = end_date
            else:
                pass
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