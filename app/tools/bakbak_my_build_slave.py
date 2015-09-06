#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: bakbak_my_build_slave.py
# @File_path: E:\开源程序\my_dba_release\app\tools\bakbak_my_build_slave.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-02-28 18:15:52



import sys
import datetime
import time
import subprocess
import os
#import MySQLdb
import paramiko
#import check_module
import getpass
#import psutil

import remote_db_execute as func


def check_module(my_module):

    package = my_module
    try:
        #import MySQLdb
        return __import__(package)
        # print 'Module %s is installed.' % package

    except ImportError, e:
        text = "Module %s is not installed." % package
        print "\033[1;31;40m%s\033[0m" % text

        if getpass.getuser() != 'root':
            text = "Need to run using ROOT user"
            print "\033[1;32;40m%s\033[0m" % text
            sys.exit()

        if package == "MySQLdb":
            pip_package = "MySQL-python"
        else:
            pip_package = package

        cmd = "/usr/local/bin/pip install %s -i http://pypi.v2ex.com/simple" % pip_package
        print cmd
        #subprocess.Popen(cmd, shell=True)
        subprocess.call(cmd, shell=True)


def log_w(text):
    logfile = "/tmp/db_mig.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()

'''
def pre_check():

    check_module.check_module('MySQLdb')
    check_module.check_module('paramiko')

 '''


class Database:

    """docstring for ClassName"""

    def __init__(
        self, from_host, to_host, os_password_source,os_password_target,
        db_user_pwd_source,db_user_pwd_target, db_port_source, db_port_target):
        self.from_host = from_host
        self.to_host = to_host
        self.os_user = 'apps'
        self.db_user_name = 'dba'
        self.os_password_source = os_password_source
        self.os_password_target = os_password_target
        self.db_user_pwd_source = db_user_pwd_source
        self.db_user_pwd_target = db_user_pwd_target
        self.port = 22
        self.db_port_source = db_port_source
        self.db_port_target = db_port_target
        self.today = datetime.date.today().strftime("%Y%m%d")

    def export_database_metadata(self):  # 导出数据库的表结构和视图以及存储过程
        text = "%s %s" % (
            datetime.datetime.now(), 
            "One: Begin export master Database table stru,views,procs, Please wait ....")

        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_source)+'.sock'

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.from_host, self.port, self.os_user, self.os_password_source)
            
            # 获取 mysqldump 要导出的数据库列表清单

            conm_db_list = r'''/apps/svr/mysql5/bin/mysql -N -u%s -p'%s' %s -e"show databases"|grep -v log|grep -v information_schema|grep -v performance_schema|grep -v mysql|tr "\n" " "''' % (
                self.db_user_name,self.db_user_pwd_source,v_db_socket)

            print conm_db_list

            stdin, stdout, stderr = s.exec_command(conm_db_list)

            if stdout.channel.recv_exit_status() ==0:

                db_list_str = stdout.readlines()[-1]  #返回值本身就一行

                text = "%s  Get mysqldump db list  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色

            else:

                result = stderr.readlines()[-1].strip()

                text = "%s Get mysqldump db list execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                return result  # 退出

            # mysqldump 导出 表结构和视图和存储过程

            conm = r'''/apps/svr/mysql5/bin/mysqldump -u%s -p'%s' %s --single-transaction -d -R --skip-triggers -B %s > /apps/mydumper_export/struc.sql''' % (
                self.db_user_name,self.db_user_pwd_source,v_db_socket, db_list_str)

            print conm

            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()

            s.close()

            if result == '':
                text = "%s  Mysqldump export table structure  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Mysqldump export table structure Execute Error !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Mysqldump export table structure  Error !"
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return "Mysqldump table structure   Error !"

    def export_database(self):  # 导出远程主机的数据库的数据
        text = "%s %s" % (
            datetime.datetime.now(), "Two: Mydumper export master Database data,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_source)+'.sock'

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.from_host, self.port, self.os_user, self.os_password_source)
            
            # mydumper 导出数据,并把表结构和数据，一起打个tar包

            conm = r'''rm -rf /apps/mydumper_export/bak/*;/apps/sh/mysql/ffback/backup_tools/mydumper/bin/mydumper -u %s -p '%s' %s --no-schemas --regex '^(?!(mysql|log|information_schema|performance_schema))' --outputdir=/apps/mydumper_export/bak --logfile=/apps/mydumper_export/mydumper.log;cd /apps/mydumper_export;tar cf bak.tar struc.sql bak''' % (
                self.db_user_name,self.db_user_pwd_source,v_db_socket)

            print conm

            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()

            s.close()

            if result == '':
                text = "%s  Mydumper export data  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Mydumper export data Execute Error !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Mydumper export data   Error !"
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return "Mydumper export data   Error !"
            #sys.exit()

    def scp_bet_two_servers(self): # 远程第三方执行，在另两个server间copy

        text = "%s %s" % (
            datetime.datetime.now(), "Three:  Scp between two servers,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色

        log_w(text)

        #from_file = '/apps/bak_db_%s.sql' % self.today
        from_file = '/apps/mydumper_export/bak.tar'

        to_dir = '/apps/mydumper_import'

        r=func.remote_exe_scp_bet_two_servers(
            self.from_host,
            self.to_host,
            self.os_password_source,
            self.os_password_target,
            from_file,
            to_dir
            )

        if r == '':
            text = "%s Scp between two servers  Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
        else:
            text = "%s Scp between two servers Execute Error !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

        return r


    def import_data(self):  # 导入数据库到目标机器

        text = "%s %s" % (
            datetime.datetime.now(), "Four: Import master database,Please wait ....")

        log_w(text)
        print "\033[1;32;40m%s\033[0m" % text

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_target)+'.sock'

       

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.to_host, self.port, self.os_user, self.os_password_target)

            #mysql 命令导入表结构和视图及存储过程

            conm_import_struc = r'''rm -rf /apps/mydumper_import/bak;cd /apps/mydumper_import;tar xf bak.tar;/apps/svr/mysql5/bin/mysql -u%s -p'%s' %s  < /apps/mydumper_import/struc.sql''' % (
                self.db_user_name,self.db_user_pwd_target,v_db_socket)


            stdin, stdout, stderr = s.exec_command(conm_import_struc)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()

            if result == '':
                text = "%s Import table structure  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Import table structure  Execute Error !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                return result # 执行失败，退出

            # myloader导入数据

            conm = r'''/apps/sh/mysql/ffback/backup_tools/mydumper/bin/myloader -u %s -p '%s' %s -d /apps/mydumper_import/bak ''' % (
                self.db_user_name,self.db_user_pwd_target,v_db_socket)

            print conm


            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()
           
            s.close()

            if result == '':
                text = "%s Mydumper import data  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Mydumper import data Execute Error !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                
            return result

        except Exception, e:
            print e.message
            text = "Import data sys Error %s, the reason is %s!" % (
                datetime.datetime.now(), e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return "Import database to target Error !"
            #sys.exit()

    def change_master(self):  # Mysql 从库 change master

        text = "%s %s" % (
            datetime.datetime.now(), "Five:  Slave change master to ,Please wait ....")

        log_w(text)
        print "\033[1;32;40m%s\033[0m" % text

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_target)+'.sock'

       

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.to_host, self.port, self.os_user, self.os_password_target)

            '''
            [apps@192.168.30.241(ERP_DB(从)) bak]$ more metadata 
            Started dump at: 2014-06-04 18:35:05
            SHOW MASTER STATUS:
                    Log: mysql-bin.000019
                    Pos: 338263317

            SHOW SLAVE STATUS:
                    Host: 192.168.30.240
                    Log: mysql-bin.000021
                    Pos: 489318589

            '''

            #master_ip= cat /apps/mydumper_import/bak/metadata |sed -n '7p'|awk -F: '{print $2}'|sed s/[[:space:]]//g
            #master_Log= cat /apps/mydumper_import/bak/metadata |sed -n '8p'|awk -F: '{print $2}'|sed s/[[:space:]]//g

            #master_pos = cat /apps/mydumper_import/bak/metadata |sed -n '9p'|awk -F: '{print $2}'|sed s/[[:space:]]//g

            # 导出数据库的master ip

            conm1 = r'''cat /apps/mydumper_import/bak/metadata |sed -n '7p'|awk -F: '{print $2}'|sed s/[[:space:]]//g '''
            
            stdin, stdout, stderr = s.exec_command(conm1)

            v_master_host = stdout.readlines()[-1].strip()

            v_master_port = 3306  # 临时设置


            # 导出数据库的master 的当前导出点的binlog name 

            conm2 = r'''cat /apps/mydumper_import/bak/metadata |sed -n '8p'|awk -F: '{print $2}'|sed s/[[:space:]]//g '''
            
            
            stdin, stdout, stderr = s.exec_command(conm2)

            v_master_log_file = stdout.readlines()[-1].strip()


            # 导出数据库的master 的当前导出点的binlog Pos

            conm3 = r'''cat /apps/mydumper_import/bak/metadata |sed -n '9p'|awk -F: '{print $2}'|sed s/[[:space:]]//g '''

            stdin, stdout, stderr = s.exec_command(conm3)

            v_master_log_pos = int(stdout.readlines()[-1].strip())

           
           # 执行mysql change master

            conm = r'''/apps/svr/mysql5/bin/mysql -u%s -p'%s' %s -e"change master to master_host='%s', MASTER_PORT=%d ,master_user='rep', master_password='rep!@#$', master_log_file='%s' , master_log_pos=%d ;start slave;" ''' % (
                self.db_user_name,self.db_user_pwd_target,v_db_socket,v_master_host,v_master_port,v_master_log_file,v_master_log_pos)

            print conm


            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()
           
            s.close()

            if result == '':
                text = "%s Mysql change master  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Mysql change master Execute Error !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Mysql change master sys Error %s, the reason is %s!" % (
                datetime.datetime.now(), e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return "Mysql change master Error !"

