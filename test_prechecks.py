import pyping

def test_internet_con(): 
    websites = (
        'www.google.com',
        'www.facebook.com',
        'www.microsoft.com'
    )
    replies = []
    for site in websites:
        reply = pyping.ping(site)
        replies.append(reply.ret_code)
    
    assert all(replies != 0)