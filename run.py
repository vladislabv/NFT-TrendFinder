# Run a test server.
#!flask/bin/python
from __future__ import absolute_import, unicode_literals
from nft_finder import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)