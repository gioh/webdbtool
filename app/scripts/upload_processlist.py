#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: upload_processlist.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\upload_processlist.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-05-14 08:32:29


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

                # 若是空，变成mysql的null，否则加上引号再传递进去，格式为%s ,而不是'%s'
                if vp_db is None:
                    vp_db = 'NULL'
                else:
                    vp_db = "'"+vp_db+"'"

                #print vp_db

                vp_command = process_row['COMMAND']

                vp_time = process_row['TIME']

                vp_state = process_row['STATE']

                vp_info = process_row['INFO']

                if vp_info is None:
                    vp_info = 'NULL'
                else:
                    #vp_info = "'"+vp_info+"'"
                    vp_info = vp_info.replace('"',"'") # 双引号替换为单引号
                    vp_info = '"'+vp_info+'"'   # 防止字符里面本身包含单引号

                vp_time_ms = process_row['TIME_MS']

                vp_rows_sent = process_row['ROWS_SENT']

                vp_rows_examined = process_row['ROWS_EXAMINED']

                # v_insert_sql='''insert into log_processlist(instance_id,TID,USER,HOST,DB,COMMAND,TIME,STATE,INFO,
                # TIME_MS,ROWS_SENT,ROWS_EXAMINED) values(%d,%d,'%s','%s','%s','%s',%d,'%s','%s',%d,%d,%d)''' % (
                # instance_id,vp_id,vp_user,vp_host,vp_db,vp_command,vp_time,vp_state,vp_info,vp_time_ms,vp_rows_sent,vp_rows_examined)
                
                #try:
                v_insert_sql='''insert into log_processlist(instance_id,TID,USER,HOST,DB,COMMAND,TIME,STATE,INFO,
                TIME_MS,ROWS_SENT,ROWS_EXAMINED) values(%d,%d,'%s','%s',%s,'%s',%d,'%s',%s,%d,%d,%d)''' % (
                instance_id,vp_id,vp_user,vp_host,vp_db,vp_command,vp_time,vp_state,vp_info,vp_time_ms,vp_rows_sent,vp_rows_examined)


                #print v_insert_sql

                db.execute(v_insert_sql.replace('%','%%'))

                    #db.execute(v_insert_sql)
                # except Exception, e:
                #     print e.message
                #     print v_insert_sql
                #     text = "insert process_list error!," + e.message + ',' + v_insert_sql
                #     log_w(text)

            db_remote.close()

            

            i=i+1


    db.close()






if __name__ == "__main__":


    upload_processlist()

  