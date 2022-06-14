import time
import logging
import string
import random
import functools
import asyncio
from contextlib import contextmanager
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

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

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