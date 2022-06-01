from flask import request
from pymongo import MongoClient
import requests
import json
import os
import sys
import time
from app import celery

@celery.task
def get_dog_pics(breed_type, limit):
    url = "<https://dog.ceo/api/breed/>" + breed_type + "/images/random/" + limit
    r = requests.get(url)
    files = r.json()

    for file in files["message"]:
        with open("url.txt", "a") as myfile:
            myfile.write(" " + file)
    return files["message"]