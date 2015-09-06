#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: inception_test2.py
# @File_path: E:\开源程序\my_dba_release\app\scripts\inception_test2.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-07-21 18:27:14
# @Last Modified by:   丁以然
# @Last Modified time: 2015-05-29 19:38:08
import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import config


import MySQLdb

# sql='/\*--user=username;--password=password;--host=172.26.137.125;--execute=1;--port=3306;*/\
# inception_magic_start;\
# use mysql;\
# CREATE TABLE adaptive_office(id int);\
# inception_magic_commit;'

# --enable-check
#--execute=1;
# --user=mysqladmin;--password=mysql;

# v_sql = r"""/*--host=172.26.137.125;
# --enable-execute;--port=3306;*/  
# inception_magic_start;
# use test; 
# CREATE TABLE `slow_app41` (
#     `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
#     `host` VARCHAR(30) NOT NULL COMMENT '慢查询的发起app的服务器IP',
#     `project` VARCHAR(32) NULL DEFAULT NULL COMMENT '对应的机器描述或者对应的项目',
#     `version` INT(11) NOT NULL DEFAULT '1',
#     `last_update_time` INT(10) UNSIGNED NULL DEFAULT NULL,
#     `belong_app` TINYINT(4) NULL DEFAULT NULL COMMENT '所属域，对应slow_app_domain表的id 字段，0表示不属于任何域',
#     PRIMARY KEY (`id`),
#     UNIQUE INDEX `unq_host` (`host`, `version`)
# )
# COMMENT='slow_app' 
# COLLATE='utf8_general_ci'
# ENGINE=InnoDB;  
# inception_magic_commit;"""

# v_sql = r"""/*--host=172.26.137.125;
# --execute=1;--port=3306;*/  
# inception_magic_start;   
# alter table test.t_eap_form_history add column test_id int not null default 1; 
# inception_magic_commit;"""

# --user=mysqladmin;--password=mysql;

# insert into test.slow_app(host,project,version,last_update_time,belong_app) values('3','a',1,1,1);

# --execute=1       --check=1

# v_sql = r"""/*--host=172.26.137.125;--user=dbaquery;--password=GXBpmRYsh#fJIvv1;
# --execute=1;--port=3306;*/  
# inception_magic_start;
# alter table test.t_eap_form_history add column test_assid2 int not null default 1;

# inception_magic_commit;"""

v_sql = r"""/*--host=172.26.137.125;--port=3306;--user=dbaquery;--password=GXBpmRYsh#fJIvv1;
    --execute=1;*/
    inception_magic_start;
    use test;
    insert into testaa(a,ab) values(3,5);
    inception_magic_commit;"""



# insert into testaa(a,ab) values(3,5);

v_inception_ip=config.INCEPTION_IP
v_inception_port=int(config.INCEPTION_PORT)

#v_inception_ip='127.0.0.1'
#v_inception_port=6669

try:
    #conn=MySQLdb.connect(host='127.0.0.1',user='',passwd='',db='',port=6669)
    conn=MySQLdb.connect(host=v_inception_ip,user='',passwd='',db='',port=v_inception_port)
    cur=conn.cursor()
    print 'aa'
    ret=cur.execute(v_sql)
    print 'bb'
    result=cur.fetchall()
    num_fields = len(cur.description) 
    field_names = [i[0] for i in cur.description]
    print field_names
    for row in result:
        print row[0], "|",row[1],"|",row[2],"|",row[3],"|",row[4],"|",row[5],"|",row[6],"|",row[7],"|",row[8],"|",row[9],"|",row[10]
    cur.close()
    conn.close()
except MySQLdb.Error,e:
     print "Mysql Error %d: %s" % (e.args[0], e.args[1])

  