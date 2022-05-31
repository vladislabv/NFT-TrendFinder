from app import celery
from flask import request

import json
import os

from .definitions_of_classes import OutputAPI
from .models import NftItem
from .selenium_class import RaribleSearchUser
from selenium.webdriver.firefox.options import Options


@celery.task(bind=True)
def fetch_item_info(self, nb_days):
    fetcher_inst = OutputAPI(task = self, duration = nb_days)

    result_state = fetcher_inst.fetch_items_from_API()

    return result_state


@celery.task(bind=True)
def fetch_user_info():

    # fetch unique user ids from db, temporarily only seller_ids
    seller_ids = set(json.loads(obj.to_json())['seller_id'] for obj in NftItem.objects.only("seller_id"))

    options = Options()
    options.add_argument('--headless')

    # start_date = date(2022, 3, 17)
    # fetch user infos
    RaribleSearchUser(
        os.getenv('BASE_URL'),
        request.form.get('dr_path') or os.getenv('DRIVER_PATH'),
        options
    ).get_user_info(user_ids=seller_ids)