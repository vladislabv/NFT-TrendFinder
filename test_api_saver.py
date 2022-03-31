"""What this file does?"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from retry import retry
import pandas as pd
import numpy as np
import requests

import time

""" query = {'Blockchain':'ETHEREUM', 'size': 100}
for i in range(100):
	resp = requests.get('https://api.rarible.org/v0.1/items/all', params=query, timeout=60)
	query['continuation'] = resp.json()['continuation']
	items = resp.json()['items']
	for i in items:
		#print(i.keys())
		print(i['creators'], i['id'])
		break
	time.sleep(10) """

# ApiItem - class responsible for extracting data from api and store
#
#
#

@dataclass
class ItemsTable:
    """The class is needed for fetching data from Rarible API and convert it into 
    the table form.
    """
    duration: int = 1
    to_date: datetime = field(default_factory=datetime.now)
    BLOCKCHAIN_REQUEST = 'ETHEREUM' 
    SIZE_RESPONSE = 100
    REQUEST_TIMEOUT = 10
    BASE_URL = 'https://api.rarible.org/v0.1/items/all'

    def form_dict(self) -> dict:
        to_unix_timestamp = lambda x: time.mktime(x.timetuple())
        date_unix = self.to_date - timedelta(days=self.duration)
        return {
            "size": self.SIZE_RESPONSE, 
            "blockchains": self.BLOCKCHAIN_REQUEST, 
            "lastUpdatedFrom": int(to_unix_timestamp(date_unix))
            }
    @retry(Exception, tries=3, delay=2)
    def get_response(self) -> requests.Response:
        self.query = self.form_dict()
        response = requests.get(self.BASE_URL, params=self.query)
        result = response.json()
        self.query["continuation"] = result.get("continuation")
        df = pd.DataFrame(result.get('items'))
        df['meta'] = df['meta'].fillna({})
        meta_df = pd.DataFrame(list(df['meta']))
        df['content'] = meta_df['content'].explode().fillna(dict())
        meta_df['attributes'] = np.where(meta_df['attributes'].isna(), np.array([None]), meta_df['attributes'])
        attr_df = pd.DataFrame(list(df['attributes']))




if __name__ == '__main__':
    a = ItemsTable(5)

    a.get_response()















