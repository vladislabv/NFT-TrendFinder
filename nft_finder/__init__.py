# Import flask and template operators
import os
import sys
import logging
from pymongo import MongoClient
from celery import Celery
from flask_caching import Cache
from flask import Flask
from dotenv import load_dotenv

# all variables from .env will be loaded into environment
load_dotenv(
    os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)
        )),
        "secrets",
        ".env"
        )
    )

logging_path = os.getenv('PATH_TO_LOGS')

logging.basicConfig(
    level=logging.INFO, 
    filename=f'{logging_path}/nft_finder.log', 
    format='%(asctime)s %(levelname)s:%(message)s'
    )

logger = logging.getLogger(__name__)

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_BACKEND_URL'],
        broker=app.config['CELERY_BROKER_URL'],
        include=[f"{app.import_name}.tasks"]
    )
    celery.conf.update(app.config)
    #celery.conf.broker_transport_options = {"visibility_timeout": float("inf")}
    #celery.autodiscover_tasks(force=True)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Define the WSGI application object
app = Flask(__name__)
# Configurations
app.config.from_object('config')
app.config.update(
    CELERY_BROKER_URL=os.environ.get("CELERY_BROKER_URL"),
    CELERY_BACKEND_URL=os.environ.get("CELERY_BACKEND_URL"),
)
# make sure that celery and db are connected
while True:
    try:
        celery = make_celery(app)
        celery.control.purge()
        db_client = MongoClient(os.getenv('MONGODB_CONNECTION_STRING'))
        cache = Cache(app)
        break
    except Exception:
        raise Exception("Could not connect to MongoDB and Celery.")

import nft_finder.routes

from nft_finder.dashboard import dashboard_bp as dashboard_module
app.register_blueprint(dashboard_module)
