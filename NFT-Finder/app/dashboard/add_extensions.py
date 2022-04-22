from PIL import Image
from io import BytesIO
import requests
from functools import wraps
import time
import logging

# set logger

logging.basicConfig(
    level=logging.INFO, 
    filename='myapp.txt', 
    format='%(asctime)s %(levelname)s:%(message)s'
    )
logger = logging.getLogger(__name__)

class SafeDict(dict):
    # https://stackoverflow.com/a/3405143/190597
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value
    
class SafeList(list):
    # https://stackoverflow.com/a/5125712
    def get(self, index, default=None):
        try:
            return self.__getitem__(index)
        except IndexError:
            return default

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        logger.info('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts)
        )
        return result
    return wrap

def convert_to_int(like_num):

    strings = ['B', 'M', 'K', '']
    nums = [1_000_000_000, 1_000_000, 1_000, 1]

    for i, j in zip(strings, nums):
        if i in like_num:
            num_str = like_num.replace(i, '')
            try:
                num = int(float(num_str) * j)
                break
            except ValueError as e:
                num = None
                logging.exception(e)
    
    return num

def get_picture(url: str):
    if len(url):
        if url.endswith('.mp3') or url.endswith('.mp4') or url.endswith('.gif'):
            extension = None
        elif url.endswith('.svg'):
            extension = 'svg'
        elif url.endswith('jpg'):
            extension = 'svg'
        else:
            extension = 'png'
        
        if extension:
            img = Image.open(BytesIO(requests.get(url).content))
        else:
            img = None
    return img