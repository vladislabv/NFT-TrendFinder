import requests
import json
import time

query = {'Blockchain':'ETHEREUM', 'size': 100}
for i in range(100):
	resp = requests.get('https://api.rarible.org/v0.1/items/all', params=query, timeout=60)
	query['continuation'] = resp.json()['continuation']
	items = resp.json()['items']
	for i in items:
		#print(i.keys())
		print(i['creators'], i['id'])
		break
	time.sleep(10)
