import os
# Statement for enabling the development environment
DEBUG = True
# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
MEDIA_FOLDER = os.path.join("A:/", "nft_finder_temp_images")
# CELERY MONGO SETTINGS
MONGODB_DB = 'nft-finder'
MONGODB_CONNECTION_STRING = 'mongodb://localhost:27017'
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
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# Use a secure, unique and absolutely secret key for
# signing the data. 
#CSRF_SESSION_KEY = 'e16d77a31be1a1937524214f74f20a5b'

# Secret key for signing cookies
SECRET_KEY = '9febb642f19b6d58f5a92ba405252f65'
# Cache setting
CACHE_TYPE = "SimpleCache"