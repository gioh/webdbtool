#!/usr/bin/env python

from app import app
app.run(debug = True, host='0.0.0.0',threaded=True, port=8000)
#app.run(debug = True, host='172.26.152.6', port=6000)