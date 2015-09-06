#!/bin/bash
#kill `cat /tmp/gunicorn2.pid`
pkill gunicorn
sleep 10
rm -rf /tmp/gunicorn2.pid
rm -rf /home/apps/my_prog/my_dba_release_prod
cp -r /home/apps/my_prog/my_dba_release /home/apps/my_prog/my_dba_release_prod
cd /home/apps/my_prog/my_dba_release_prod
gunicorn -c /home/apps/my_prog/my_dba_release_prod/gunicorn.conf app:app 
# 开启Mysql备份调度定时器
#cd /home/apps/my_prog/my_dba_release_for_dev/app/tools
#python mysql_sche_backup_call.py >>/tmp/start_schedule.log

#nohup gunicorn -b 10.1.1.91:5000 -w 2 app:app
#--log-file /home/apps/my_prog/dba_flask/run.log
#gunicorn -b 10.1.1.91:5000 -w 2 app:app >> run.log