# Import flask and template operators
import os
import sys
import logging
from celery import Celery
from flask_caching import Cache
from flask import Flask
from dotenv import load_dotenv
from config import MONGODB_DB, MONGODB_CONNECTION_STRING
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

# all variables from .env will be loaded into environment
load_dotenv(
    os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)
        )), # get path of the current file
        "env\.env" # file name
        )
    )

logging.basicConfig(
    level=logging.INFO, 
    filename='myapp.txt', 
    format='%(asctime)s %(levelname)s:%(message)s'
    )

logger = logging.getLogger(__name__)

"""
By design, asyncio does not allow its event loop to be nested and patches asyncio to allow nested use of 
asyncio.run and loop.run_until_complete.
"""

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_BACKEND_URL'],
        broker=app.config['CELERY_BROKER_URL'],
        include=[f"app.tasks"]
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(force=True)

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
celery = make_celery(app)
cache = Cache(app)

import routes

from app.dashboard import dashboard_bp as dashboard_module
app.register_blueprint(dashboard_module)
