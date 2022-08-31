import pyping
from config import RUN_APP_ON_PORT

def test_website_reply(): 
    reply = pyping.ping(f'localhost:{RUN_APP_ON_PORT}')
    assert reply.ret_code == 0