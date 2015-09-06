#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: schedule_upload_processlist.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\schedule_upload_processlist.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-04-29 13:26:46


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

from apscheduler.scheduler import Scheduler

from apscheduler.jobstores.shelve_store import ShelveJobStore

import logging
logging.basicConfig()  # 设置logging 模块的默认配置

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



def upload_processlist():

    #连接配置中心库
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_sql = r"""SELECT id,ip,port from tag b where online_flag=1 and is_showprocesslist=1"""

    #print v_sql

    upload_server_list = db.query(v_sql)

    if upload_server_list: # 对实例表进行循环

        i=0

        

        for upload_server in upload_server_list:

            instance_id = upload_server['id']

            host_ip = upload_server['ip']

            mysql_port = upload_server['port']

            v_host =host_ip + ':' + str(mysql_port)

            #连接远程实例
            db_remote = Connection(v_host,
                            'information_schema',
                            config.DBA_QUERY_USER,
                            config.DBA_QUERY_PASSWD,
                            time_zone='+8:00')


            v_pl = r"""SELECT ID,USER,HOST,DB,COMMAND,TIME,STATE,INFO,TIME_MS,ROWS_SENT,ROWS_EXAMINED from PROCESSLIST"""

            #print v_pl

            process_list = db_remote.query(v_pl)

            for process_row in process_list:

                vp_id = process_row['ID']

                vp_user = process_row['USER']

                vp_host = process_row['HOST']

                vp_db = process_row['DB']

                vp_command = process_row['COMMAND']

                vp_time = process_row['TIME']

                vp_state = process_row['STATE']

                vp_info = process_row['INFO']

                vp_time_ms = process_row['TIME_MS']

                vp_rows_sent = process_row['ROWS_SENT']

                vp_rows_examined = process_row['ROWS_EXAMINED']

                v_insert_sql='''insert into processlist(instance_id,TID,USER,HOST,DB,COMMAND,TIME,STATE,INFO,
                TIME_MS,ROWS_SENT,ROWS_EXAMINED) values(%d,%d,'%s','%s','%s','%s',%d,'%s','%s',%d,%d,%d)''' % (
                instance_id,vp_id,vp_user,vp_host,vp_db,vp_command,vp_time,vp_state,vp_info,vp_time_ms,vp_rows_sent,vp_rows_examined)

                db.execute(v_insert_sql)

            db_remote.close()

            

            i=i+1


    db.close()



def start_schedule():

#if __name__ == '__main__':

    
    scheduler_pl = Scheduler(daemonic = False)

    scheduler_pl.print_jobs()


    scheduler_pl.shutdown()

    
    scheduler_pl.add_jobstore(ShelveJobStore('/tmp/db_pl_schedule'), 'file')

    v_current_jobs = scheduler_pl.get_jobs()

    print v_current_jobs

    if v_current_jobs:  # 如果job存在的话,先请客


        scheduler_pl.unschedule_func(upload_processlist) 

    scheduler_pl.add_interval_job(upload_processlist, minutes=1)
            



    scheduler_pl.start()

    print 'success!'

    scheduler_pl.print_jobs()

    '''
    print('Press Ctrl+C to exit')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    '''

def restart_file_schedule():

    scheduler_pl = Scheduler(daemonic = False)

    scheduler_pl.print_jobs()

    #scheduler.remove_jobstore('file',close=True)

    #scheduler.shutdown(wait=False)

    scheduler_pl.add_jobstore(ShelveJobStore('/tmp/db_pl_schedule'), 'file')

    scheduler_pl.start()

    print 'success!'

    scheduler_pl.print_jobs()

def err_listener(ev):    
    err_logger = logging.getLogger('schedErrJob')    
    if ev.exception:    
        err_logger.exception('%s error.', str(ev.job))    
    else:    
        err_logger.info('%s miss', str(ev.job))


if __name__ == "__main__":

    #start_schedule()

    upload_processlist()

    #restart_file_schedule()   #重新程序发布后，手工执行