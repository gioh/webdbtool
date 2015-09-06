#!/bin/bash
gunicorn -c gunicorn.conf app:app 
#nohup gunicorn -b 172.26.152.6:5000 -w 2 app:app
#--log-file /apps/data_platform/dba_flask/run.log
#gunicorn -b 172.26.152.6:5000 -w 2 app:app >> run.log