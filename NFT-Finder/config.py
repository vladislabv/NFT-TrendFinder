# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

# Define the database - we are working with
# MongoDB for this example
MONGODB_SETTINGS = {
    'db': 'nft-finder',
    'host': '127.0.0.1',
    'port': 27017
}
MONGODB_DB = 'nft-finder'
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_CONNECT = True
#MONGODB_USERNAME = 'webapp'
#MONGODB_PASSWORD = 'pwd123'

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
#CSRF_ENABLED = True

# setting celery tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'mongodb://localhost:27017'

# Use a secure, unique and absolutely secret key for
# signing the data. 
#CSRF_SESSION_KEY = 'e16d77a31be1a1937524214f74f20a5b'

# Secret key for signing cookies
SECRET_KEY = '9febb642f19b6d58f5a92ba405252f65'