# Run a test server.
#!flask/bin/python
from __future__ import absolute_import, unicode_literals
from app import app

app.run(host='127.0.0.1', port=8080, debug=True)