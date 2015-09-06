#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: inception_test.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\inception_test.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-05-27 14:03:33


from torndb import Connection
#import remote_db_execute as func

"""
Basic example showing how to start the scheduler and schedule a job that
executes on 3 second intervals.
nohup test_sche2.py &
"""
#import paramiko
#from datetime import datetime
import time

#pip uninstall apscheduler
#pip install apscheduler==2.1.2  3.0 版本没有 Scheduler（）方法


#import logging
#logging.basicConfig()  # 设置logging 模块的默认配置

import os,sys  
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import config


def log_w(text):
    logfile = "/tmp/process_list.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()



def upload_processlist():

    #连接配置中心库
    # db = Connection('/home/apps/inception/inc.socket',
    #                 '',
    #                 '',
    #                 '',
    #                 time_zone='+8:00')

    db = Connection('127.0.0.1:6669',
                    '',
                    '',
                    '',
                    time_zone='+8:00')

    print 'aa'

    v_sql = r"""/*--user=mysqladmin;--password=mysql;--host=172.26.137.125;
    --enable-check;--port=3306;*/  
    inception_magic_start;  
    use test;  
    CREATE TABLE adaptive_office23(id int);  
    inception_magic_commit;"""

    #print v_sql

    upload_server_list = db.iter(v_sql)

    if upload_server_list: # 对实例表进行循环

        i=0

        print upload_server_list

        for upload_server in upload_server_list:

            stage = upload_server['stage']

            print stage

            stagestatus = upload_server['stagestatus']

            print stagestatus

        #     mysql_port = upload_server['port']

        #     v_host =host_ip + ':' + str(mysql_port)

            

        #     i=i+1


    db.close()






if __name__ == "__main__":


    upload_processlist()

  