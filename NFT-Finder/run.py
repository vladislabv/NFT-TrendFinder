# Run a test server.
#!flask/bin/python
from __future__ import absolute_import, unicode_literals
from app import app

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True)