#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import sys
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import tools.remote_db_execute as func

import logging
logging.basicConfig()


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



def init_start_schedule():


    scheduler = BlockingScheduler()


    #scheduler.shutdown(wait=False)

    url = 'sqlite:////home/apps/dbajob.sqlite'

    scheduler.add_jobstore('sqlalchemy', url=url, alias='sqlite_js')

    scheduler.print_jobs()

    scheduler.start()


    print 'success!'

    scheduler.print_jobs()


if __name__ == '__main__':

    init_start_schedule()

    