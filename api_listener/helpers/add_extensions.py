import os
import time
import logging
import string
import random
import functools
from io import BytesIO
from contextlib import contextmanager
import asyncio
import aiohttp
import aiofiles as aiof
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from helpers.custom_exceptions import ItemIndexError

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

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

async def upload_picture(url: str) -> str:
    filename = os.path.join(os.getenv('MEDIA_FOLDER'), "image_")
    #filename_desc = os.path.join(TXT_MEDIA_FOLDER, "image_")
    async with aiohttp.ClientSession() as session:
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
                extension = 'png'
            
            if extension is not None and extension != 'svg':
                async with session.get(url) as response:
                    try: 
                        img = Image.open(BytesIO(await response.read()))
                    except Exception as err:
                        logger.error(err)
                        return None
                img_id = id_generator()
                filename += img_id + '.' + extension
                #filename_desc += img_id + '.' + 'txt'
                if img.mode in ("RGBA", "P"): 
                    try:
                        img = img.convert("RGB")
                    except OSError as err:
                        logger.error(err)
                        return None
                img.save(filename)
                #async with aiof.open(filename_desc, 'wb+', encoding='cp1252') as file:
                    #file.write(description)
            elif extension == 'svg':
                async with session.get(url) as response:
                    try:
                        result = await response.read()
                    except Exception as err:
                        logger.error(err)
                        return None
                img_id = id_generator()
                filename += img_id + '.' + extension
                #filename_desc += img_id + '.' + 'txt'
                async with aiof.open(filename, 'wb+', encoding='utf-8') as img:
                    img.write(result)
                #async with aiof.open(filename_desc, 'wb+', encoding='cp1252') as file:
                    #file.write(description)
                drawing = svg2rlg(filename)
                filename_converted += img_id + '.png'
                os.remove(filename)
                filename = filename_converted
                renderPM.drawToFile(drawing, filename_converted, fmt = 'PNG')
            else:
                img = None
                return None
        else:
            return None
    return filename


def find_nth(haystack: str, needle: str, n: int) -> int:
    """Function finding the nth occurance of a substring

    Args:
        haystack (str): Source string
        needle (str): Character or substring to look for
        n (int): The occurance of the needle

    Returns:
        int: Haystack's index, where the nth occurance was found
    """
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def validate_item(item: dict) -> bool:
    """Method looking for non-deleted, ever sold, image items

    Args:
        item (dict): A dictionary containing information about a NFT item

    Returns:
        bool: True if an item can be further processed
    """
    item = SafeDict(item)
    try:
        item_content = SafeList(item['meta']['content'])
        item_type = item_content.get( 0, SafeDict({}) )['@type']
    except IndexError as e:
        logging.exception(ItemIndexError(item, e))
    return all(
        [
            not item['deleted'], # still exists
            ('IMAGE' == item_type), # is image
            len(item['lastSale']), # was ever sold
            len(item['meta']['attributes']) # has at least some attributes
        ]
    )

def validate_activity(activity: dict) -> bool:
    """Method looking for valid sold NFT items

    Args:
        activity (dict): A dictionary with meta infomation about a user activity on https://www.rarible.com

    Returns:
        bool: True if an activity can be further processed
    """
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