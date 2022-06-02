import os
import time
import logging
import string
import random
import functools
import asyncio
from contextlib import contextmanager
import requests
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image
from io import BytesIO
from .custom_exceptions import ItemIndexError
# set logger
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
    @functools.wraps(f)
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

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_picture(url: str):
    filename = None
    if len(url):
        if url.endswith('.mp3') or url.endswith('.mp4') or url.endswith('.gif'):
            extension = None
        elif url.endswith('.svg'):
            extension = None
        elif url.endswith('.jpg'):
            extension = 'jpg'
        elif url.endswith('.png'):
            extension = 'png'
        else:
            extension = None
        
        if extension is not None and extension != 'svg':
            try:
                img = Image.open(BytesIO(requests.get(url).content))
            except Exception as err:
                print(err)
                return None
            img_id = id_generator()
            filename = f"A:/nft_finder_temp_images/image_{img_id}.{extension}"
            if img.mode in ("RGBA", "P"): 
                try:
                    img = img.convert("RGB")
                except OSError as err:
                    print(err)
                    return None
            img.save(filename)
        elif extension == 'svg':
            try:
                r = requests.get(url, allow_redirects=True)
            except Exception as err:
                print(err)
                return None
            img_id = id_generator()
            filename = f"A:/nft_finder_temp_images/image_{img_id}.{extension}"
            with open(filename, 'wb', encoding='utf-8') as img:
                img.write(r.content)
            drawing = svg2rlg(filename)
            filename_converted = f"temp_images/image_{img_id}.png"
            os.remove(filename)
            filename = filename_converted
            renderPM.drawToFile(drawing, filename_converted, fmt='PNG')
        else:
            img = None
    return filename

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def validate_item(item) -> bool:
    """Look for non-deleted, ever sold, image items"""
    item = SafeDict(item)
    try:
        item_content = SafeList(item['meta']['content'])
        item_type = item_content.get( 0, SafeDict({}) )['@type']
    except IndexError as e:
        logging.exception(ItemIndexError(item, e))
    #print(item)
    return all(
        [
            not item['deleted'], # still exists
            ('IMAGE' == item_type), # is image
            len(item['lastSale']), # was ever sold
            len(item['meta']['attributes']) # has at least some attributes
        ]
    )

def validate_activity(activity) -> bool:
    activity = SafeDict(activity)
    is_valid = False
    # is valid, if it has info about a nft behind it, i.e. itemId or contract + tokenId
    if activity['nft']['type'].get('type', 'Not defined') == 'SolanaNftAssetType':
        is_valid = True
    elif activity['nft']['type'].get('tokenId', False):
        activity['nft']['type']['itemId'] = activity['nft']['type']['contract'] + ':' + activity['nft']['type']['tokenId']
        is_valid = True
    else:
        is_valid = False

    return is_valid

def duration(func):
    @contextmanager
    def wrapping_logic():
        start_ts = time.monotonic()
        yield
        dur = time.monotonic() - start_ts
        logger.info('{} took {:.2} seconds'.format(func.__name__, dur))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            with wrapping_logic():
                return func(*args, **kwargs)
        else:
            async def tmp():
                with wrapping_logic():
                    return (await func(*args, **kwargs))
            return tmp()
    return wrapper

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()