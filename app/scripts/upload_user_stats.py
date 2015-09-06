#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: upload_user_stats.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\upload_user_stats.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-05-15 11:09:38


from torndb import Connection

#from datetime import datetime
import time


#import logging
#logging.basicConfig()  # 设置logging 模块的默认配置

import os,sys  
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import tools.remote_db_execute as func

import config


def log_w(text):
    logfile = "/tmp/upload_user_stats.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()


# 上传percona user stat,每周执行一次

def upload_user_stats():  

    #连接配置中心库
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    db.execute('truncate table meta_table_statistics')  # 先truncate 再插入

    db.execute('truncate table meta_index_statistics')  # 先truncate 再插入

    


    # 由于id为64的E4S 服务器不在平台管辖，先手工剔除 b.id !=64
    v_sql = r"""SELECT b.ip,b.port,b.id as instance_id,a.id as schema_id,a.name as db_name from 
    resources_schema a,tag b where b.online_flag=1 and a.owner=b.id and b.id !=64 order by a.id,b.id"""

    #print v_sql

    upload_tables_list = db.query(v_sql)

    if upload_tables_list: # 对实例表进行循环

        i=0

        

        for upload_table in upload_tables_list:

            instance_id = upload_table['instance_id']

            schema_id = upload_table['schema_id']

            db_name = upload_table['db_name']

            host_ip = upload_table['ip']

            mysql_port = upload_table['port']

            v_host =host_ip + ':' + str(mysql_port)

            #连接远程实例
            db_remote = Connection(v_host,
                            'information_schema',
                            config.DBA_QUERY_USER,
                            config.DBA_QUERY_PASSWD,
                            time_zone='+8:00')

            # 取表的元信息然后插入

            v_pl = r"""SELECT table_schema,table_name,rows_read,rows_changed,rows_changed_x_indexes 
            from table_statistics where table_schema='%s' """ % (db_name)

            #print v_pl

            table_list = db_remote.query(v_pl)

            for table_row in table_list:

            

                table_schema = table_row['table_schema']

                table_name = table_row['table_name']

                rows_read = table_row['rows_read']

                rows_changed = table_row['rows_changed']


                rows_changed_x_indexes = table_row['rows_changed_x_indexes']

                
                
                #try:
                v_insert_sql='''insert into meta_table_statistics(instance_id,schema_id,table_schema,
                table_name,rows_read,rows_changed,rows_changed_x_indexes) 
                values(%d,%d,'%s','%s',%d,%d,%d)''' % (
                instance_id,schema_id,table_schema,
                table_name,rows_read,rows_changed,rows_changed_x_indexes
                )

                #print v_insert_sql

                db.execute(v_insert_sql.replace('%','%%'))

                    
                # except Exception, e:
                #     print e.message
                #     print v_insert_sql
                #     text = "insert meta tables error!," + e.message + ',' + v_insert_sql
                #     log_w(text)

            

            # 取索引的元信息，然后插入

            v_pl2 = r"""SELECT table_schema,table_name,index_name,rows_read from index_statistics 
            where TABLE_SCHEMA='%s' """ % (db_name)


            table_list2 = db_remote.query(v_pl2)

            for table_row2 in table_list2:

                

                table_schema = table_row2['table_schema']

                table_name = table_row2['table_name']

                index_name = table_row2['index_name']

                
                rows_read = table_row2['rows_read']

                
                #try:
                v_insert_sql2='''insert into meta_index_statistics(instance_id,schema_id,table_schema,
                table_name,index_name,rows_read) 
                values(%d,%d,'%s','%s','%s',%d)''' % (
                instance_id,schema_id,table_schema,
                table_name,index_name,rows_read
                )

                #print v_insert_sql

                db.execute(v_insert_sql2.replace('%','%%'))

                    
                # except Exception, e:
                #     print e.message
                #     print v_insert_sql
                #     text = "insert meta tables error!," + e.message + ',' + v_insert_sql
                #     log_w(text)



            db_remote.close()


            # 开始生成log_hot_tables 统计表数据

            # statistic_time 为统计数据的实际生成时间


            v_insert_sql3='''insert into log_hot_tables(instance_id,schema_id,table_schema,
                table_name,TABLE_COMMENT,TABLE_CREATE_TIME,rows_read,rows_changed,
                rows_changed_x_indexes) select a.instance_id,a.schema_id,a.TABLE_SCHEMA,
                a.TABLE_NAME,b.TABLE_COMMENT,b.CREATE_TIME,a.ROWS_READ,a.ROWS_CHANGED,
                a.ROWS_CHANGED_X_INDEXES from meta_table_statistics a,meta_tables b where 
                a.instance_id=%d and a.schema_id=%d and 
                a.TABLE_SCHEMA='%s' and a.instance_id=b.instance_id and a.TABLE_SCHEMA=b.TABLE_SCHEMA 
                and a.TABLE_NAME=b.TABLE_NAME''' % (
                instance_id,schema_id,table_schema
                )

            print v_insert_sql3

            db.execute(v_insert_sql3.replace('%','%%'))
            


            

            i=i+1


    db.close()

   # 开始远程flush 统计信息表

    # for remote execute

    os_user = 'apps'

    OS_APPS_PASSWD = config.OS_APPS_PASSWD

    DB_USER = config.DB_USER

    DB_PASSWD = config.DB_PASSWD

    #连接配置中心库
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    # 由于id为64的E4S 服务器不在平台管辖，先手工剔除 b.id !=64
    v_sql = r"""SELECT distinct b.ip,b.port from 
    resources_schema a,tag b where b.online_flag=1 and a.owner=b.id and b.id !=64 order by a.id,b.id"""

    #print v_sql

    server_list = db.query(v_sql)

    if server_list: # 对实例表进行循环

        i=0

        for single_server in server_list:


            host_ip = single_server['ip']

            mysql_port = single_server['port']


            # 远程paramiko调用 在本机执行sql

            exe_sql = 'flush table_statistics;flush index_statistics;'  

            result = func.remote_exe_sql(host_ip,os_user,OS_APPS_PASSWD,mysql_port,'information_schema',exe_sql,DB_USER,DB_PASSWD)

            if result == '':
                result = '执行成功!'

            print result



if __name__ == "__main__":


    upload_user_stats()

  