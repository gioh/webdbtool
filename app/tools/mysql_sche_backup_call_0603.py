#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: mysql_sche_backup_call_0603.py
# @File_path: E:\开源程序\my_dba_release\app\tools\mysql_sche_backup_call_0603.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-06-04 16:16:00


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

def backup(from_host,
        mysql_port,
        os_user,
        os_password
        ):

    localfile = "/home/apps/my_prog/my_dba_release/app/scripts/new_backup_mysql.sh"

    remotefile = "/apps/sh/mysql/new_backup_mysql.sh"

    v_os_port = 22

    # 把备份脚本文件推送到远程服务器

    func.put_sql_to_remote(from_host,v_os_port,os_user,os_password,localfile,remotefile)

    # 远程调用此脚本

    func.remote_mysql_backup(from_host, mysql_port, os_user, os_password)

#func.remote_mysql_backup()


def start_schedule():

#if __name__ == '__main__':
    os_user = config.OS_USER

    os_password = config.OS_APPS_PASSWD

    
    scheduler = Scheduler(daemonic = False)

    scheduler.print_jobs()

    #scheduler.remove_jobstore('file',close=True)

    #scheduler.shutdown(wait=False)

    

    scheduler.shutdown()

    #scheduler.unschedule_func(backup)

    scheduler.add_jobstore(ShelveJobStore('/tmp/db_schedule'), 'file')

    v_current_jobs = scheduler.get_jobs()

    print v_current_jobs

    if v_current_jobs:  # 如果job存在的话,先请客

     

        scheduler.unschedule_func(backup)

    

    #scheduler = Scheduler(standalone=True)
    #scheduler = Scheduler(daemon=True)
    #连接配置中心库，获取数据库备份周期等信息
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_sql = r"""SELECT a.instance_id,b.ip,b.port,a.backup_interval_type,a.backup_start_time from mysql_ins_bak_setup a,tag b where 
        a.instance_id=b.id """

    print v_sql

    bak_server_list = db.query(v_sql)

    if bak_server_list: # 有server需要配置

        i=0

        # 把还没有开始的调度任务，置为手工结束 backup_result_type=4
        v_manual_end_sql = 'update mysql_ins_bak_log set backup_result_type=4 where backup_result_type=0'

        db.execute(v_manual_end_sql)

        for bak_server in bak_server_list:

            instance_id = bak_server['instance_id']

            from_host = bak_server['ip']

            #print from_host

            mysql_port = bak_server['port']

            backup_interval_type = bak_server['backup_interval_type']

            backup_start_time = bak_server['backup_start_time']

            str_start_date= time.strftime("%Y-%m-%d") + ' ' + backup_start_time

            print str_start_date 

            if backup_interval_type == 1: # every day

                #内存jobstore

                #scheduler.add_interval_job(backup, days=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password])

                #文件jobstore jobstore='file'

                scheduler.add_interval_job(backup, days=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password], jobstore='file')
               
                #scheduler.add_interval_job(backup, days=1, start_date='2014-07-18 18:17:01', args=[from_host, mysql_port, os_user, os_password])

            elif backup_interval_type == 2: # every week

                scheduler.add_interval_job(backup, weeks=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password])

            elif backup_interval_type == 3: # every hour

                scheduler.add_interval_job(backup, hours=1, start_date=str_start_date, args=[from_host, mysql_port, os_user, os_password])

            # 开始在数据库记录备份的调度任务状态 0:调度任务已启动，实际备份还没有开始

            v_sche_start_sql = """insert into mysql_ins_bak_log(instance_id,backup_result_type) 
            values(%d,0)""" % (instance_id)

            db.execute(v_sche_start_sql)

            i=i+1


    db.close()


    if bak_server_list: # 有server需要配置

        scheduler.start()

        print 'success!'

        scheduler.print_jobs()

        '''
        print('Press Ctrl+C to exit')

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass
        '''

def restart_file_schedule():

    scheduler = Scheduler(daemonic = False)

    scheduler.print_jobs()

    #scheduler.remove_jobstore('file',close=True)

    #scheduler.shutdown(wait=False)

    scheduler.add_jobstore(ShelveJobStore('/tmp/db_schedule'), 'file')

    scheduler.start()

    print 'success!'

    scheduler.print_jobs()

def err_listener(ev):    
    err_logger = logging.getLogger('schedErrJob')    
    if ev.exception:    
        err_logger.exception('%s error.', str(ev.job))    
    else:    
        err_logger.info('%s miss', str(ev.job))


if __name__ == "__main__":

    restart_file_schedule()   #重新程序发布后，手工执行