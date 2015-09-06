#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: mysql_sche_backup_standalone.py
# @File_path: E:\开源程序\my_dba_release\app\tools\mysql_sche_backup_standalone.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2014-11-20 11:07:44


from torndb import Connection
import remote_db_execute as func

"""
Basic example showing how to start the scheduler and schedule a job that
executes on 3 second intervals.
nohup test_sche2.py &
"""
#import paramiko
#from datetime import datetime
import time

from apscheduler.scheduler import Scheduler

import logging
logging.basicConfig()

import os,sys  
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import config


def log_w(text):
    logfile = "/tmp/mysql_bakcup.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()

def backup(from_host,
        mysql_port,
        os_user,
        os_password
        ):

    func.remote_mysql_backup(from_host, mysql_port, os_user, os_password)

#func.remote_mysql_backup()




if __name__ == '__main__':
    scheduler = Scheduler(standalone=True)
    #scheduler = Scheduler(daemon=True)
    #连接配置中心库，获取数据库备份周期等信息
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_sql = r"""SELECT b.ip,b.port,a.backup_interval_type,a.backup_start_time from mysql_ins_bak_setup a,tag b where 
        a.instance_id=b.id """

    print v_sql

    os_user = config.OS_USER

    os_password = config.OS_APPS_PASSWD

    bak_server_list = db.query(v_sql)

    if bak_server_list: # 有server需要配置

        i=0

        for bak_server in bak_server_list:

            from_host = bak_server['ip']

            print from_host

            mysql_port = bak_server['port']

            backup_interval_type = bak_server['backup_interval_type']

            backup_start_time = bak_server['backup_start_time']

            str_start_date= time.strftime("%Y-%m-%d") + ' ' + backup_start_time

            print str_start_date 

            if backup_interval_type == 1: # every day

                print from_host, mysql_port, os_user, os_password

                #scheduler.add_interval_job(backup, days=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password])
                scheduler.add_interval_job(backup, days=1, start_date='2014-07-18 18:17:01', args=[from_host, mysql_port, os_user, os_password])

            elif backup_interval_type == 2: # every week

                scheduler.add_interval_job(backup, weeks=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password])

            elif backup_interval_type == 3: # every hour

                scheduler.add_interval_job(backup, hours=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password])

            i=i+1


    db.close()

    #scheduler.add_interval_job(func.remote_mysql_backup, seconds=5, args=[from_host, port, os_user, os_password])
    #scheduler.add_interval_job(log_w, seconds=5, start_date='2014-07-18 16:21', args=['abc'])
    

    if bak_server_list: # 有server需要配置

        print('Press Ctrl+C to exit')

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass