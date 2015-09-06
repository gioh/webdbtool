#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: upload_meta_tables.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\upload_meta_tables.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-07-14 08:39:35


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
    logfile = "/tmp/meta_tables.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()


# 上传表和索引的元信息,以及common_schema.redundant_keys的冗余索引信息 每天执行一次


def upload_meta_tables():  
    #连接配置中心库
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    db.execute('truncate table meta_tables')  # 先truncate 再插入

    db.execute('truncate table meta_statistics')  # 先truncate 再插入

    db.execute('truncate table meta_redundant_keys')  # 先truncate 再插入

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

            v_pl = r"""SELECT table_catalog,table_schema,table_name,table_type,engine,version,row_format,
            table_rows,avg_row_length,data_length,max_data_length,index_length,data_free,auto_increment,create_time,
            update_time,check_time,table_collation,checksum,
            create_options,table_comment from tables where table_type='BASE TABLE' and TABLE_SCHEMA='%s' """ % (db_name)

            #print v_pl

            table_list = db_remote.query(v_pl)

            for table_row in table_list:

                table_catalog = table_row['table_catalog']

                table_schema = table_row['table_schema']

                table_name = table_row['table_name']

                table_type = table_row['table_type']

                engine = table_row['engine']


                version = table_row['version']

                row_format = table_row['row_format']

                table_rows = table_row['table_rows']

                avg_row_length = table_row['avg_row_length']

                data_length = table_row['data_length']

                max_data_length = table_row['max_data_length']

                index_length = table_row['index_length']

                data_free = table_row['data_free']

                auto_increment = table_row['auto_increment']

                # 本来Int类型，但为了处理Null值插入，以字符串类型%s 进行插入
                if auto_increment is None:
                    auto_increment = 'NULL'
                else:
                    auto_increment = "'"+str(auto_increment)+"'"

                # 日期型插入，由于要处理null值插入，经过处理后，以%s 进行插入
                create_time = table_row['create_time']

                if create_time is None:
                    create_time = 'NULL'
                else:
                    create_time = "'"+str(create_time)+"'"
                

                # 日期型插入，由于要处理null值插入，经过处理后，以%s 进行插入
                update_time = table_row['update_time']

                if update_time is None:
                    update_time = 'NULL'
                else:
                    update_time = "'"+str(update_time)+"'"


                check_time = table_row['check_time']

                if check_time is None:
                    check_time = 'NULL'
                else:
                    check_time = "'"+str(check_time)+"'"


                table_collation = table_row['table_collation']

                # 本来Int类型，但为了处理Null值插入，以字符串类型%s 进行插入

                checksum = table_row['checksum']

                if checksum is None:
                    checksum = 'NULL'
                else:
                    checksum = "'"+str(checksum)+"'"
                


                create_options = table_row['create_options']

                table_comment = table_row['table_comment']

                
                #try:
                v_insert_sql='''insert into meta_tables(instance_id,schema_id,table_catalog,table_schema,table_name,
                table_type,engine,version,row_format,table_rows,avg_row_length,data_length,max_data_length,
                index_length,data_free,auto_increment,create_time,update_time,check_time,table_collation,
                checksum,create_options,table_comment) 
                values(%d,%d,'%s','%s','%s',
                '%s','%s',%d,'%s',%d,%d,%d,%d,
                %d,%d,%s,%s,%s,%s,'%s',
                %s,'%s','%s')''' % (
                instance_id,schema_id,table_catalog,table_schema,table_name,
                table_type,engine,version,row_format,table_rows,avg_row_length,data_length,max_data_length,
                index_length,data_free,auto_increment,create_time,update_time,check_time,table_collation,
                checksum,create_options,table_comment
                )

                #print v_insert_sql

                db.execute(v_insert_sql.replace('%','%%'))

                    
                # except Exception, e:
                #     print e.message
                #     print v_insert_sql
                #     text = "insert meta tables error!," + e.message + ',' + v_insert_sql
                #     log_w(text)


            # 取索引的元信息，然后插入

            v_pl2 = r"""SELECT table_catalog,table_schema,table_name,non_unique,index_schema,
            index_name,seq_in_index,column_name,collation,cardinality,sub_part,packed,nullable,
            index_type,comment,index_comment from statistics where TABLE_SCHEMA='%s' """ % (db_name)


            table_list2 = db_remote.query(v_pl2)

            for table_row2 in table_list2:

                table_catalog = table_row2['table_catalog']

                table_schema = table_row2['table_schema']

                table_name = table_row2['table_name']

                non_unique = table_row2['non_unique']

                index_schema = table_row2['index_schema']


                index_name = table_row2['index_name']

                seq_in_index = table_row2['seq_in_index']

                column_name = table_row2['column_name']

                collation = table_row2['collation']

                cardinality = table_row2['cardinality']

                # 本来Int类型，但为了处理Null值插入，以字符串类型%s 进行插入

                if cardinality is None:
                    cardinality = 'NULL'
                else:
                    cardinality = "'"+str(cardinality)+"'"


                sub_part = table_row2['sub_part']

                # 本来Int类型，但为了处理Null值插入，以字符串类型%s 进行插入

                if sub_part is None:
                    sub_part = 'NULL'
                else:
                    sub_part = "'"+str(sub_part)+"'"


                packed = table_row2['packed']

                if packed is None:
                    packed = 'NULL'
                else:
                    
                    packed = '"'+packed+'"'   # 防止字符里面本身包含单引号


                nullable = table_row2['nullable']
                
                index_type = table_row2['index_type']

                comment = table_row2['comment']

                index_comment = table_row2['index_comment']

                

                
                #try:
                v_insert_sql2='''insert into meta_statistics(instance_id,schema_id,table_catalog,
                table_schema,table_name,non_unique,index_schema,index_name,seq_in_index,
                column_name,collation,cardinality,sub_part,packed,nullable,index_type,comment,index_comment) 
                values(%d,%d,'%s',
                '%s','%s',%d,'%s','%s',%d,
                '%s','%s',%s,%s,%s,'%s','%s','%s','%s')''' % (
                instance_id,schema_id,table_catalog,
                table_schema,table_name,non_unique,index_schema,index_name,seq_in_index,
                column_name,collation,cardinality,sub_part,packed,nullable,index_type,comment,index_comment
                )

                #print v_insert_sql

                db.execute(v_insert_sql2.replace('%','%%'))

                    
                # except Exception, e:
                #     print e.message
                #     print v_insert_sql
                #     text = "insert meta tables error!," + e.message + ',' + v_insert_sql
                #     log_w(text)

            db_remote.close()


            #连接远程实例,提取冗余索引信息
            db_remote2 = Connection(v_host,
                            'common_schema',
                            config.DBA_QUERY_USER,
                            config.DBA_QUERY_PASSWD,
                            time_zone='+8:00')

            # 取common_schema.redundant_keys 视图信息然后插入

            v_pl3 = r"""SELECT table_schema,table_name,redundant_index_name,redundant_index_columns,
            redundant_index_non_unique,dominant_index_name,dominant_index_columns,
            dominant_index_non_unique,subpart_exists,sql_drop_index 
            from redundant_keys where table_schema='%s' """ % (db_name)

            #print v_pl

            table_list3 = db_remote2.query(v_pl3)

            for table_row3 in table_list3:

            

                table_schema = table_row3['table_schema']

                table_name = table_row3['table_name']

                redundant_index_name = table_row3['redundant_index_name']

                redundant_index_columns = table_row3['redundant_index_columns']


                redundant_index_non_unique = table_row3['redundant_index_non_unique']

                dominant_index_name = table_row3['dominant_index_name']

                dominant_index_columns = table_row3['dominant_index_columns']

                dominant_index_non_unique = table_row3['dominant_index_non_unique']


                subpart_exists = table_row3['subpart_exists']

                sql_drop_index = table_row3['sql_drop_index']

                
                
                #try:
                v_insert_sql3='''insert into meta_redundant_keys(instance_id,schema_id,table_schema,
                table_name,redundant_index_name,redundant_index_columns,redundant_index_non_unique,
                dominant_index_name,dominant_index_columns,
                dominant_index_non_unique,subpart_exists,sql_drop_index) 
                values(%d,%d,'%s',
                '%s','%s','%s',%d,
                '%s','%s',
                %d,%d,'%s')''' % (
                instance_id,schema_id,table_schema,
                table_name,redundant_index_name,redundant_index_columns,redundant_index_non_unique,
                dominant_index_name,dominant_index_columns,
                dominant_index_non_unique,subpart_exists,sql_drop_index
                )

                #print v_insert_sql

                db.execute(v_insert_sql3.replace('%','%%'))


            db_remote2.close()

            

            i=i+1


    db.close()






if __name__ == "__main__":


    upload_meta_tables()

  