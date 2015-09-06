#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: upload_auto_increment.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\upload_auto_increment.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-05-21 09:33:55

    
from torndb import Connection

# 加载上级目录到sys.path

import os,sys
reload(sys)
sys.setdefaultencoding('utf-8')
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import tools.remote_db_execute as func

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
    logfile = "/tmp/auto_increment.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()



def upload_auto_increment():

    #连接配置中心库
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_sql = r"""SELECT id,ip,port from tag b where online_flag=1 and is_showprocesslist=1"""

    print v_sql

    upload_server_list = db.query(v_sql)

    if upload_server_list: # 对实例表进行循环

        i=0

        

        for upload_server in upload_server_list:

            instance_id = upload_server['id']

            host_ip = upload_server['ip']

            mysql_port = upload_server['port']

            v_host =host_ip + ':' + str(mysql_port)

            print v_host

            #连接远程实例
            db_remote = Connection(v_host,
                            'information_schema',
                            config.DBA_QUERY_USER,
                            config.DBA_QUERY_PASSWD,
                            time_zone='+8:00')


            v_pl = r"""select information_schema . columns . TABLE_SCHEMA AS TABLE_SCHEMA,
                        information_schema . columns . TABLE_NAME AS TABLE_NAME,
                        information_schema . columns . COLUMN_NAME AS COLUMN_NAME,
                        information_schema . columns . DATA_TYPE AS DATA_TYPE,
                        information_schema . columns . COLUMN_TYPE AS COLUMN_TYPE,
                        ((case information_schema . columns . DATA_TYPE
                        when 'tinyint' then
                            255
                        when 'smallint' then
                            65535
                        when 'mediumint' then
                            16777215
                        when 'int' then
                            4294967295
                        when 'bigint' then
                            18446744073709551615
                        end) >>
                        if((locate('unsigned', information_schema . columns . COLUMN_TYPE) > 0),
                            0,
                            1)) AS MAX_VALUE,
                        information_schema . tables . AUTO_INCREMENT AS AUTO_INCREMENT,
                        (information_schema . tables .
                        AUTO_INCREMENT /
                        ((case information_schema . columns . DATA_TYPE
                            when 'tinyint' then
                                255
                            when 'smallint' then
                                65535
                            when 'mediumint' then
                                16777215
                            when 'int' then
                                4294967295
                            when 'bigint' then
                                18446744073709551615
                        end) >>
                        if((locate('unsigned', information_schema . columns . COLUMN_TYPE) > 0),
                            0,
                            1))) AS AUTO_INCREMENT_RATIO
                        from (information_schema . columns join information_schema . tables
                          on(((information_schema . columns . TABLE_SCHEMA = information_schema .
                               tables . TABLE_SCHEMA) and
                               (information_schema . columns . TABLE_NAME = information_schema .
                               tables . TABLE_NAME))))
                        where ((information_schema . columns .TABLE_SCHEMA not in
                                    ('mysql', 'INFORMATION_SCHEMA', 'performance_schema','common_schema')) and
                                    (information_schema . tables . TABLE_TYPE = 'BASE TABLE') and
                                    (information_schema . columns . EXTRA = 'auto_increment'))"""

            print v_pl

            process_list = db_remote.query(v_pl)

            for process_row in process_list:

                vp_server_ip = v_host

                vp_instance_id = instance_id

                #vp_id = process_row['ID']
                vp_table_schema = process_row['TABLE_SCHEMA']

                vp_table_name = process_row['TABLE_NAME']

                vp_column_name = process_row['COLUMN_NAME']

                vp_data_type = process_row['DATA_TYPE']

                # 若是空，变成mysql的null，否则加上引号再传递进去，格式为%s ,而不是'%s'
                #if vp_db is None:
                #    vp_db = 'NULL'
                #else:
                #    vp_db = "'"+vp_db+"'"

                #print vp_db

                vp_column_type = process_row['COLUMN_TYPE']

                vp_max_value = process_row['MAX_VALUE']

                vp_auto_increment = process_row['AUTO_INCREMENT']

                vp_auto_increment_ratio = process_row['AUTO_INCREMENT_RATIO']

                #vp_info = process_row['INFO']

                #if vp_info is None:
                #    vp_info = 'NULL'
                #else:
                #    #vp_info = "'"+vp_info+"'"
                #    vp_info = vp_info.replace('"',"'") # 双引号替换为单引号
                #    vp_info = '"'+vp_info+'"'   # 防止字符里面本身包含单引号

                # v_insert_sql='''insert into log_processlist(instance_id,TID,USER,HOST,DB,COMMAND,TIME,STATE,INFO,
                # TIME_MS,ROWS_SENT,ROWS_EXAMINED) values(%d,%d,'%s','%s','%s','%s',%d,'%s','%s',%d,%d,%d)''' % (
                # instance_id,vp_id,vp_user,vp_host,vp_db,vp_command,vp_time,vp_state,vp_info,vp_time_ms,vp_rows_sent,vp_rows_examined)
                
                #try:
                v_delete_sql='''delete from  auto_increment_list where INSTANCE_ID = '%s' and TABLE_SCHEMA = '%s' and TABLE_NAME = '%s' and COLUMN_NAME = '%s' ''' % (
                vp_instance_id,vp_table_schema,vp_table_name,vp_column_name)


                print v_delete_sql

                db.execute(v_delete_sql)


                v_insert_sql='''insert into auto_increment_list(instance_id,server_ip,TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,DATA_TYPE,COLUMN_TYPE,MAX_VALUE,AUTO_INCREMENT,AUTO_INCREMENT_RATIO) 
                values(%d,'%s','%s','%s','%s','%s','%s',%d,%d,%d)''' % (
                vp_instance_id,vp_server_ip,vp_table_schema,vp_table_name,vp_column_name,vp_data_type,vp_column_type,int(vp_max_value),int(vp_auto_increment),int(vp_auto_increment_ratio))


                print v_insert_sql

                db.execute(v_insert_sql)

                    #db.execute(v_insert_sql)
                # except Exception, e:
                #     print e.message
                #     print v_insert_sql
                #     text = "insert process_list error!," + e.message + ',' + v_insert_sql
                #     log_w(text)

            db_remote.close()

            

            i=i+1

        
        v_sendmail_sql=r'''select count(*) count
                    from auto_increment_list b where AUTO_INCREMENT_RATIO >= 80 '''
        

        
        if_list = db.query(v_sendmail_sql)
        
        for if_row in if_list:
            v_if = if_row['count']
            print v_if    
            if v_if >= 1 :
                print '11'
                
                
                v_warn_sql=r'''select SERVER_IP,TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,MAX_VALUE,AUTO_INCREMENT,AUTO_INCREMENT_RATIO 
                            from auto_increment_list b where AUTO_INCREMENT_RATIO >= 80 '''
                print v_warn_sql
                warn_list = db.query(v_warn_sql)
                v_server_ip = '\r\n'
                for warn_row in warn_list:
                    v_server_ip = v_server_ip + warn_row['SERVER_IP'] +'|对象名:' + warn_row['TABLE_SCHEMA'] +'|表名:'+ warn_row['TABLE_NAME'] + '|字段名:' + warn_row['COLUMN_NAME']+'\r\n'                  
                    
                print v_server_ip
                v_msg_text = v_server_ip
                v_receiver = 'dengwt@szlanyou.com,dingyiran@szlanyou.com'
                v_subject = '有快溢出的自增ID，细节请去监控页面查看'
                v_return = func.send_mail_to_devs(v_receiver,v_subject,v_msg_text)

    db.close()






if __name__ == "__main__":


    upload_auto_increment()

  