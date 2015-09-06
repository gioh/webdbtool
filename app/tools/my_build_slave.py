#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: my_build_slave.py
# @File_path: E:\开源程序\my_dba_release\app\tools\my_build_slave.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-07-06 19:55:39


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
from torndb import Connection
import remote_db_execute as func

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import config



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
    logfile = "/tmp/db_build_slave.log"
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
        self, master_host,from_host, to_host, db_ip_priv,

        os_user,os_password_source,os_password_target,os_password_priv,

        db_user,db_user_pwd_source,db_user_pwd_target, db_user_pwd_priv,

        db_port_master,db_port_source, db_port_target,db_port_priv,

        db_user_name_rep,db_rep_pwd,
        
        db_root_user,db_root_pwd_target):

        self.master_host = master_host
        self.from_host = from_host
        self.to_host = to_host
        self.db_ip_priv = db_ip_priv

        self.port = 22   #ssh 端口

        self.os_user = os_user
        self.os_password_source = os_password_source
        self.os_password_target = os_password_target
        self.os_password_priv = os_password_priv


        self.db_user_name = db_user
        self.db_user_pwd_source = db_user_pwd_source
        self.db_user_pwd_target = db_user_pwd_target
        self.db_user_pwd_priv = db_user_pwd_priv

        self.db_port_master = db_port_master
        self.db_port_source = db_port_source
        self.db_port_target = db_port_target
        self.db_port_priv = db_port_priv

        self.db_user_name_rep = db_user_name_rep
        self.db_rep_pwd = db_rep_pwd

        self.db_root_user = db_root_user
        self.db_root_pwd_target = db_root_pwd_target
        
                
        self.today = datetime.date.today().strftime("%Y%m%d")
        self.xtra_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')

        self.xtrabackup_bin_path = config.xtrabackup_bin_path
        self.xtrabackup_export_path = config.xtrabackup_export_path
        #self.xtrabackup_restore_path = config.xtrabackup_restore_path
        self.xtrabackup_restore_path = config.mysql_datadir_path

        self.mysql_client_path = config.mysql_client_path
        self.mydumper_bin_path = config.mydumper_bin_path
        self.mydumper_export_path = config.mydumper_export_path
        self.mydumper_import_path = config.mydumper_import_path

        self.db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

        
    def export_database_metadata(self,v_prosess_id):  # 导出数据库的表结构和视图以及存储过程

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
            # 不能加grep -v ，因为logplatform 数据库会被一起过滤掉
            conm_db_list_1 = r'''%s/mysql -N -u%s %s -e"show databases"|grep -v information_schema|grep -v common_schema|grep -v performance_schema|grep -v mysql|tr "\n" " "''' % (
                self.mysql_client_path,self.db_user_name,v_db_socket)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_db_list_1 +''' ' where id= '''+ str(v_prosess_id)
            print conm_db_list_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm_db_list = r'''%s/mysql -N -u%s -p'%s' %s -e"show databases"|grep -v information_schema|grep -v common_schema|grep -v performance_schema|grep -v mysql|tr "\n" " "''' % (
                self.mysql_client_path,self.db_user_name,self.db_user_pwd_source,v_db_socket)

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
            conm_1 = r'''mkdir -p %s/bak;%s/mysqldump -u%s %s -f --single-transaction -d -R --skip-triggers -B %s > %s/struc.sql''' % (
                self.mydumper_export_path,self.mysql_client_path,self.db_user_name,v_db_socket, db_list_str,self.mydumper_export_path)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
            print conm_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm = r'''mkdir -p %s/bak;%s/mysqldump -u%s -p'%s' %s -f --single-transaction -d -R --skip-triggers -B %s > %s/struc.sql''' % (
                self.mydumper_export_path,self.mysql_client_path,self.db_user_name,self.db_user_pwd_source,v_db_socket, db_list_str,self.mydumper_export_path)

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
                text = "%s Mysqldump export table structure Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Mysqldump export table structure  Error ! Error Reason: %s" % (e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return text

    def export_database(self,v_prosess_id):  # 导出远程主机的数据库的数据
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
            conm_1 =  r'''rm -rf %s/bak/*;%s/mydumper --less-locking --use-savepoints -u %s  %s --no-schemas --regex \'^(?!(mysql|information_schema|common_schema|performance_schema))\' --outputdir=%s/bak --logfile=%s/mydumper.log;cd %s;tar cf bak.tar struc.sql bak''' % (
                self.mydumper_export_path,self.mydumper_bin_path,self.db_user_name,v_db_socket,self.mydumper_export_path,self.mydumper_export_path,self.mydumper_export_path)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
            print conm_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm = r'''rm -rf %s/bak/*;%s/mydumper --less-locking --use-savepoints -u %s -p '%s' %s --no-schemas --regex '^(?!(mysql|information_schema|common_schema|performance_schema))' --outputdir=%s/bak --logfile=%s/mydumper.log;cd %s;tar cf bak.tar struc.sql bak''' % (
                self.mydumper_export_path,self.mydumper_bin_path,self.db_user_name,self.db_user_pwd_source,v_db_socket,self.mydumper_export_path,self.mydumper_export_path,self.mydumper_export_path)

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
                text = "%s Mydumper export data Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Mydumper export data   Error ! Error Reason: %s" % (e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return text
            #sys.exit()

    def scp_bet_two_servers(self,v_prosess_id): # 远程第三方执行，在另两个server间copy mydumper导出文件

        text = "%s %s" % (
            datetime.datetime.now(), "Three:  Scp between two servers,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色

        log_w(text)

        #from_file = '/apps/bak_db_%s.sql' % self.today
        from_file = '%s/bak.tar' % (self.mydumper_export_path)

        #to_dir = '/apps/mydumper_import'
        to_dir = self.mydumper_import_path
        
        v_scp_bet_two_server = 'scp -r apps@%s:%s apps@%s:%s' % (self.from_host,from_file,self.to_host,to_dir)
        v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + v_scp_bet_two_server +''' ' where id= '''+ str(v_prosess_id)
        print v_update_sql    
        self.db.execute(v_update_sql)

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
            text = "%s Scp between two servers Execute Error ! %s" % (datetime.datetime.now(),r)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

        return r


    def import_data(self,v_prosess_id):  # 导入数据库到目标机器

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

            conm_import_struc_1 =  r'''rm -rf %s/bak;cd %s;tar xf bak.tar;%s/mysql -u%s %s  < %s/struc.sql''' % (
                self.mydumper_import_path,self.mydumper_import_path,self.mysql_client_path,self.db_user_name,v_db_socket,self.mydumper_import_path)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_import_struc_1 +''' ' where id= '''+ str(v_prosess_id)
            print conm_import_struc_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm_import_struc = r'''rm -rf %s/bak;cd %s;tar xf bak.tar;%s/mysql -u%s -p'%s' %s  < %s/struc.sql''' % (
                self.mydumper_import_path,self.mydumper_import_path,self.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket,self.mydumper_import_path)

            print conm_import_struc

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
                text = "%s Import table structure  Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                return result # 执行失败，退出

            # myloader导入数据

            # -e, --enable-binlog   Enable binary logging of the restore data,默认不记录binlgo

            conm_1 =  r'''%s/myloader -u %s %s -e -d %s/bak ''' % (
                self.mydumper_bin_path,self.db_user_name,v_db_socket,self.mydumper_import_path)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
            print conm_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm = r'''%s/myloader -u %s -p '%s' %s -e -d %s/bak ''' % (
                self.mydumper_bin_path,self.db_user_name,self.db_user_pwd_target,v_db_socket,self.mydumper_import_path)

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
                text = "%s Mydumper import data Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                
            return result

        except Exception, e:
            print e.message
            text = "Import data sys Error %s, the reason is %s!" % (
                datetime.datetime.now(), e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return text
            #sys.exit()

    def change_master(self,v_prosess_id):  # Mysql 从库 change master

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
            [apps@192.168.30.240(商城DB(主)) bak]$ more metadata 
            Started dump at: 2014-09-05 18:13:04
            SHOW MASTER STATUS:
                    Log: mysql-bin.000049
                    Pos: 349384271

            Finished dump at: 2014-09-05 18:14:01
            ---------------------------------------------------
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
            con_cnt_1 =  r'''cat %s/bak/metadata |wc -l''' % (self.mydumper_import_path)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + con_cnt_1 +''' ' where id= '''+ str(v_prosess_id)
            print con_cnt_1
            print v_update_sql
            self.db.execute(v_update_sql)

            con_cnt=r'''cat %s/bak/metadata |wc -l''' % (self.mydumper_import_path)

            stdin, stdout, stderr = s.exec_command(con_cnt)

            v_con_cnt = stdout.readlines()[-1].strip()

            # 从主库导出 

            if self.master_host==self.from_host and self.db_port_master==self.db_port_source:

                v_master_host = self.master_host

                v_master_port = self.db_port_master

                # 导出当前数据库的当前导出点的binlog name 
                conm2_1 =  r'''cat %s/bak/metadata |sed -n \'3p\'|awk -F: \'{print $2}\'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm2_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm2_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm2 = r'''cat %s/bak/metadata |sed -n '3p'|awk -F: '{print $2}'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                
                
                stdin, stdout, stderr = s.exec_command(conm2)

                v_master_log_file = stdout.readlines()[-1].strip()


                # 导出当前数据库 的当前导出点的binlog Pos
                conm3_1 =  r'''cat %s/bak/metadata |sed -n \'4p\'|awk -F: \'{print $2}\'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm3_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm3_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm3 = r'''cat %s/bak/metadata |sed -n '4p'|awk -F: '{print $2}'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)

                stdin, stdout, stderr = s.exec_command(conm3)

                v_master_log_pos = int(stdout.readlines()[-1].strip())


            else: #从master的从库进行导出的
                conm1_1 =  r'''cat %s/bak/metadata |sed -n \'7p\'|awk -F: \'{print $2}\'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm1_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm1_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm1 = r'''cat %s/bak/metadata |sed -n '7p'|awk -F: '{print $2}'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                
                stdin, stdout, stderr = s.exec_command(conm1)

                v_master_host = stdout.readlines()[-1].strip()

                print v_master_host

                if v_master_host != self.master_host :

                    text = "%s Metadata 读出的Master IP或端口 和 从前台界面获取的master IP或端口 不一致 Error !" % datetime.datetime.now()
                    log_w(text)
                    print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                    return 'Metadata 读出的Master IP或端口 和 从前台界面获取的master IP或端口 不一致!!'



                v_master_port = self.db_port_master


                # 导出数据库的master 的当前导出点的binlog name 

                conm2_1 =  r'''cat %s/bak/metadata |sed -n \'8p\'|awk -F: \'{print $2}\'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm2_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm2_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm2 = r'''cat %s/bak/metadata |sed -n '8p'|awk -F: '{print $2}'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                
                
                stdin, stdout, stderr = s.exec_command(conm2)

                v_master_log_file = stdout.readlines()[-1].strip()


                # 导出数据库的master 的当前导出点的binlog Pos
                conm3_1 =  r'''cat %s/bak/metadata |sed -n \'9p\'|awk -F: \'{print $2}\'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm3_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm3_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm3 = r'''cat %s/bak/metadata |sed -n '9p'|awk -F: '{print $2}'|sed s/[[:space:]]//g ''' % (self.mydumper_import_path)

                stdin, stdout, stderr = s.exec_command(conm3)

                v_master_log_pos = int(stdout.readlines()[-1].strip())

           
           # 执行mysql change master

            conm_1 =   r'''%s/mysql -u%s %s -e"stop slave;change master to master_host=\'%s\', MASTER_PORT=%d ,master_user=\'%s\', master_password= , master_log_file=\'%s\' , master_log_pos=%d ;start slave;" ''' % (
                self.mysql_client_path,self.db_user_name,v_db_socket,v_master_host,
                v_master_port,self.db_user_name_rep,v_master_log_file,v_master_log_pos)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
            print conm_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm = r'''%s/mysql -u%s -p'%s' %s -e"stop slave;change master to master_host='%s', MASTER_PORT=%d ,master_user='%s', master_password='%s', master_log_file='%s' , master_log_pos=%d ;start slave;" ''' % (
                self.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket,v_master_host,
                v_master_port,self.db_user_name_rep,self.db_rep_pwd,v_master_log_file,v_master_log_pos)

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
                text = "%s Mysql change master Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Mysql change master sys Error %s, the reason is %s!" % (
                datetime.datetime.now(), e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return text



    def import_database_priv(self,v_prosess_id):  # 导入数据库权限
        text = "%s %s" % (
            datetime.datetime.now(), "Six: Begin import database priv,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        # root@localhost, 放在导出过滤条件中，会导致远程执行出错，原因不明,暂时去掉

        v_pt_str = r""" --ignore=''@localhost,dba@%,dba@localhost,jiankongbao@127.0.0.1,jiankongbao@localhost,rep@%,root@127.0.0.1,root@::1,dbaquery@192.168.%"""

        # 导出权限

        return_str=func.remote_export_db_priv(
            self.db_ip_priv,self.os_user,self.os_password_priv,
            self.db_port_priv,self.db_user_name,self.db_user_pwd_priv,v_pt_str)

        print return_str

        # target 数据库导入权限

        v_sql = "set sql_log_bin=0;" #因为主从权限一般不一样，权限不复制到从库

        exe_sql = v_sql+return_str+"flush privileges;"

        v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = '数据库执行grant给予权限 ' where id= '''+ str(v_prosess_id)
        print v_update_sql
        self.db.execute(v_update_sql)

        result = func.remote_exe_sql(
            self.to_host,self.os_user,self.os_password_target,self.db_port_target,
            'mysql',exe_sql,self.db_root_user,self.db_root_pwd_target)

        return result   

    def xtrabackup_prepare(self):  # 检查target 机器，若实例开启，则关闭

        text = "%s %s" % (
            datetime.datetime.now(), "One: xtrabackup check target server,if on then shutdown,Please wait ....")

        log_w(text)
        print "\033[1;32;40m%s\033[0m" % text

        result_status = func.remote_judge_mysql_status(
            self.to_host,self.os_user, self.os_password_target,self.db_port_target)

        print result_status

        if int(result_status)==1: # 实例启动状态,则shutdown server

            result = func.remote_shutdown_mysql_server(
                self.to_host,self.os_user, self.os_password_target,self.db_port_target,self.db_root_pwd_target)

        else:

            result=''


        if result == '':
            text = "%s xtrabackup prepare  Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
        else:
            text = "%s xtrabackup prepare  Execute Error ! %s " % (datetime.datetime.now(),result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

        return result # 返回空串，执行成功，非空串，执行失败


        

    def xtrabackup_dump(self,v_prosess_id):  # 源端xtrabackup备份导出
        text = "%s %s" % (
            datetime.datetime.now(), "Two: xtrabackup begin export ,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色

        log_w(text)

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_source)+'.sock'

        # 获得mysqld_safe 配置文件路径
        # 
        v_cnf_path = func.remote_get_mycnf_path(self.from_host, self.os_user, self.os_password_source,self.db_port_source)

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.from_host, self.port, self.os_user, self.os_password_source)

                        
            # xtrabackup 导出
            # 
            v_xtra_bak_path="%s/%s" % (self.xtrabackup_export_path,self.xtra_time)
            
            v_xtra_log="%s/%s.log" % (self.xtrabackup_export_path,self.xtra_time)

            print v_xtra_bak_path,v_xtra_log

            conm = r'''%s/innobackupex --ibbackup=%s/xtrabackup --user=%s --password=%s %s --slave-info --lock-wait-timeout=120 --no-timestamp --defaults-file=%s %s 1>%s 2>&1''' % (
                self.xtrabackup_bin_path,self.xtrabackup_bin_path,self.db_user_name,self.db_user_pwd_source,v_db_socket,v_cnf_path,v_xtra_bak_path,v_xtra_log)
            
            conm_1 = r'''%s/innobackupex --ibbackup=%s/xtrabackup --user=%s %s --slave-info --lock-wait-timeout=120 --no-timestamp --defaults-file=%s %s 1>%s 2>&1''' % (
                self.xtrabackup_bin_path,self.xtrabackup_bin_path,self.db_user_name,v_db_socket,v_cnf_path,v_xtra_bak_path,v_xtra_log)
            
            
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
            
            
            print conm_1

            print v_update_sql
            
            self.db.execute(v_update_sql)

            print conm

            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()

            s.close()

            if result == '':
                text = "%s  xtrabackup export data  Execute complete,begin to check backup result !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色

                # 开始检查结果日志，判断是否成功
                v_check_complete_cmd = '''grep -a -c  "completed OK" %s''' % (v_xtra_log)
                print v_check_complete_cmd

                v_check_result=func.remote_shell_cmd(self.from_host,self.os_user,self.os_password_source,v_check_complete_cmd)
                
                if v_check_result: #list 不为空

                    v_check_complete_cnt = int(''.join(v_check_result)) 


                else:      # list 为空，但对象存在 

                    result = 'xtra 导出完毕，判断 "completed OK" 字符串数量时出现异常，导出失败!'

                    text = "%s xtrabackup export data Execute Error ! %s " % (datetime.datetime.now(),result)
                    log_w(text)
                    print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                print v_check_complete_cnt

                if v_check_complete_cnt!=2:  #结果日志里面，没有包含两个"completed OK"，export 失败

                    result = 'xtra 导出完毕，但结果日志里面，没有包含两个"completed OK"，导出失败!'

                    text = "%s xtrabackup export data Execute Error ! %s " % (datetime.datetime.now(),result)
                    log_w(text)
                    print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                else:

                    pass  # result = ''


            else:
                
                text = "%s xtrabackup export data Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                return result  #退出返回
                
            return result

        except Exception, e:
            print e.message
            text = "xtrabackup export data   Error ! Error Reason: %s" % (e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return text
            #sys.exit() 

    # 远程第三方执行，在另两个server间copy xrabackup的备份文件,并在target上 mv 目录
    
    def scp_xtra_bet_two_servers(self,v_prosess_id): 

        text = "%s %s" % (
            datetime.datetime.now(), "Three:  Scp between two servers,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色

        log_w(text)

        from_file="%s/%s" % (self.xtrabackup_export_path,self.xtra_time)

               
        to_dir = self.xtrabackup_restore_path  # datadir= /apps/dbdat

        v_scp_bet_two_server = 'scp -r apps@%s:%s apps@%s:%s' % (self.from_host,from_file,self.to_host,to_dir)
        v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + v_scp_bet_two_server +''' ' where id= '''+ str(v_prosess_id)
        print v_update_sql    
        self.db.execute(v_update_sql)

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

            # 把target 机器的datadir move，然后把新copy的xtra 目录，move 为原来的数据目录名
             
            # 首先获取Target datadir 目录名 mariadb10_data3306
            # 
            v_target_datadir_path = func.remote_off_get_datadir_path(self.to_host,self.db_port_target,2)
            
            # cd /apps/dbdat; mv mariadb10_data3306 mariadb10_data3306_时间戳;
            # mv self.xtra_time mariadb10_data3306
            v_exe_cmd = r'''cd %s;mv %s %s_%s;mv %s %s''' % (
                to_dir,v_target_datadir_path,v_target_datadir_path,self.xtra_time,self.xtra_time,v_target_datadir_path)
            
            v_exe_cmd_1 = r'''cd %s;mv %s %s_%s;mv %s %s''' % (
                to_dir,v_target_datadir_path,v_target_datadir_path,self.xtra_time,self.xtra_time,v_target_datadir_path)
            
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + v_exe_cmd_1 +''' ' where id= '''+ str(v_prosess_id)
            print v_exe_cmd_1
            print v_update_sql
            self.db.execute(v_update_sql)

            print v_exe_cmd


            r = func.remote_shell_cmd_no_result(self.to_host,self.os_user, self.os_password_target,v_exe_cmd)

            
            #r 返回空串表示成功
        else:
            text = "%s Scp between two servers Execute Error ! %s" % (datetime.datetime.now(),r)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色



        return r

    def xtrabackup_apply_log(self,v_prosess_id):  # Target 端 xtrabackup Apply log
        text = "%s %s" % (
            datetime.datetime.now(), "Four: xtrabackup begin Apply log ,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        

        # 首先获取Target datadir 完整目录名 /apps/dbdat/mariadb10_data3306
        # 
        v_restore_datadir_path = func.remote_off_get_datadir_path(self.to_host,self.db_port_target,1)
        
        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.to_host, self.port, self.os_user, self.os_password_target)

                        
            # xtrabackup Apply log
            
            
            v_xtra_restore_log="%s/restore_%s.log" % (v_restore_datadir_path,self.xtra_time)

            print v_xtra_restore_log

            conm = r'''%s/innobackupex --ibbackup=%s/xtrabackup --apply-log --use-memory=4G %s 1>%s 2>&1''' % (
                self.xtrabackup_bin_path,self.xtrabackup_bin_path,v_restore_datadir_path,v_xtra_restore_log)

            print conm

            v_conm_1 = r'''%s/innobackupex --ibbackup=%s/xtrabackup --apply-log --use-memory=4G %s 1>%s 2>&1''' % (
                self.xtrabackup_bin_path,self.xtrabackup_bin_path,v_restore_datadir_path,v_xtra_restore_log)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + v_conm_1 +''' ' where id= '''+ str(v_prosess_id)
            print v_conm_1
            print v_update_sql
            self.db.execute(v_update_sql)

            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()

            s.close()

            if result == '':
                text = "%s  xtrabackup Apply log  Execute complete,begin to check Apply log result !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色

                # 开始检查结果日志，判断是否成功
                v_check_complete_cmd = '''grep -a -c  "completed OK" %s''' % (v_xtra_restore_log)
                print v_check_complete_cmd

                v_check_result=func.remote_shell_cmd(self.to_host,self.os_user,self.os_password_target,v_check_complete_cmd)
                
                if v_check_result: #list 不为空

                    v_check_complete_cnt = int(''.join(v_check_result)) 


                else:      # list 为空，但对象存在 

                    result = 'xtra apply log完毕，判断 "completed OK" 字符串数量时出现异常，apply log失败!'

                    text = "%s xtrabackup apply log Execute Error ! %s " % (datetime.datetime.now(),result)
                    log_w(text)
                    print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                print v_check_complete_cnt

                if v_check_complete_cnt!=2:  #结果日志里面，没有包含两个"completed OK"，apply log 失败

                    result = 'xtra apply log完毕，但结果日志里面，没有包含两个"completed OK"，apply log失败!'

                    text = "%s xtrabackup apply log Execute Error ! %s " % (datetime.datetime.now(),result)
                    log_w(text)
                    print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                else:

                    pass  # result = ''


            else:
                
                text = "%s xtrabackup Apply log Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色

                return result  #退出返回
                
            return result

        except Exception, e:
            print e.message
            text = "xtrabackup Apply log   Error ! Error Reason: %s" % (e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            #return "xtrabackup Apply log   Error !"
            return text
            #sys.exit() 

    def xtrabackup_start_target(self,v_prosess_id):  # Target 端 启动Mysql实例
        text = "%s %s" % (
            datetime.datetime.now(), "Five: Target start mysql instance ,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        
        # 远程Start mysql server
        # 
        v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = 'start slave mysql' where id= '''+ str(v_prosess_id)
        
        print v_update_sql
        self.db.execute(v_update_sql)

        result = func.remote_start_mysql_server(self.to_host, self.os_user, self.os_password_target,self.db_port_target)
        
        if result == '':
            text = "%s  Target start mysql instance success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色

            
        else:
            
            text = "%s Target start mysql instance Failure ! %s " % (datetime.datetime.now(),result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

            
            
        return result

    def xtra_change_master(self,v_prosess_id):  # Mysql 从库 change master

        text = "%s %s" % (
            datetime.datetime.now(), "Six:  Xtra Slave change master to ,Please wait ....")

        log_w(text)
        print "\033[1;32;40m%s\033[0m" % text

        # 首先获取Target datadir 完整目录名 /apps/dbdat/mariadb10_data3306
        # 
        v_restore_datadir_path = func.remote_off_get_datadir_path(self.to_host,self.db_port_target,1)
        

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_target)+'.sock'

        v_master_host = self.master_host
                
        v_master_port = self.db_port_master

       

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.to_host, self.port, self.os_user, self.os_password_target)

            '''
            [apps@mall-mysql-S3 mariadb10_data3308]$ more xtrabackup_binlog_info
            mysql-bin.000041        23957068
            #master_Log= cat /apps/dbdat/mariadb10_data3308/xtrabackup_binlog_info|awk '{print $1}'|sed s/[[:space:]]//g

            #master_pos = cat /apps/dbdat/mariadb10_data3308/xtrabackup_binlog_info|awk '{print $2}'|sed s/[[:space:]]//g

            ---------------------------------------------------
            [apps@mall-mysql-S3 mariadb10_data3308]$ more xtrabackup_slave_info
            CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000028', MASTER_LOG_POS=23957044
            #master_Log= cat /apps/dbdat/mariadb10_data3308/xtrabackup_slave_info|awk -F=\' '{print $2}'|awk -F\' '{print $1}|sed s/[[:space:]]//g
            #master_pos = cat /apps/dbdat/mariadb10_data3308/xtrabackup_slave_info|awk -F, '{print $2}'|awk -F= '{print $2}'|sed s/[[:space:]]//g
            '''

           
            
            # 从主库导出 

            if self.master_host==self.from_host and self.db_port_master==self.db_port_source:

                # 导出当前数据库的当前导出点的binlog name 
                
                conm2 = r'''cat %s/xtrabackup_binlog_info |awk '{print $1}'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)
                
                v_conm2_1 = r'''cat %s/xtrabackup_binlog_info |awk \'{print $1}\'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)

                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' '''+v_conm2_1+''' ' where id= '''+ str(v_prosess_id)
                
                print v_conm2_1
                
                print v_update_sql
                
                self.db.execute(v_update_sql)
                
                stdin, stdout, stderr = s.exec_command(conm2)

                v_master_log_file = stdout.readlines()[-1].strip()


                # 导出当前数据库 的当前导出点的binlog Pos
                v_conm3_1 = r'''cat %s/xtrabackup_binlog_info |awk \'{print $2}\'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' '''+v_conm3_1+ ''' ' where id= '''+ str(v_prosess_id)
                print v_conm3_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm3 = r'''cat %s/xtrabackup_binlog_info |awk '{print $2}'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)

                stdin, stdout, stderr = s.exec_command(conm3)

                v_master_log_pos = int(stdout.readlines()[-1].strip())


            else: #从master的从库进行导出的


                # 导出数据库的master 的当前导出点的binlog name 
                v_comn2_1 = r'''cat %s/xtrabackup_slave_info |awk -F=\' \'{print $2}\'|awk -F\' \'{print $1}\'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' '''+v_conm2_1+ ''' ' where id= '''+ str(v_prosess_id)
                print v_conm2_1
                print v_update_sql
                self.db.execute(v_update_sql)
                conm2 = r'''cat %s/xtrabackup_slave_info |awk -F=\' '{print $2}'|awk -F\' '{print $1}'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)
                
                print conm2
                
                stdin, stdout, stderr = s.exec_command(conm2)

                v_master_log_file = stdout.readlines()[-1].strip()

                print v_master_log_file


                # 导出数据库的master 的当前导出点的binlog Pos
                v_conm3_1 = r'''cat %s/xtrabackup_slave_info |awk -F, \'{print $2}\'|awk -F= \'{print $2}\'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' '''+v_conm3_1+ ''' ' where id= '''+ str(v_prosess_id)
                print v_conm3_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm3 = r'''cat %s/xtrabackup_slave_info |awk -F, '{print $2}'|awk -F= '{print $2}'|sed s/[[:space:]]//g ''' % (v_restore_datadir_path)

                print conm3

                stdin, stdout, stderr = s.exec_command(conm3)

                v_master_log_pos = int(stdout.readlines()[-1].strip())

                print v_master_log_pos

           
           # 执行mysql change master
            v_conm_1 = r'''%s/mysql -u%s -p %s -e"stop slave;change master to master_host=\'%s\', MASTER_PORT=%d ,master_user=\'%s\', master_password=\'%s\', master_log_file=\'%s\' , master_log_pos=%d ;start slave;" ''' % (
                self.mysql_client_path,self.db_user_name,v_db_socket,v_master_host,
                v_master_port,self.db_user_name_rep,self.db_rep_pwd,v_master_log_file,v_master_log_pos)
            v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' '''+v_conm_1+ ''' ' where id= '''+ str(v_prosess_id)
            print v_conm_1
            print v_update_sql
            self.db.execute(v_update_sql)

            conm = r'''%s/mysql -u%s -p'%s' %s -e"stop slave;change master to master_host='%s', MASTER_PORT=%d ,master_user='%s', master_password='%s', master_log_file='%s' , master_log_pos=%d ;start slave;" ''' % (
                self.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket,v_master_host,
                v_master_port,self.db_user_name_rep,self.db_rep_pwd,v_master_log_file,v_master_log_pos)

            print conm


            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()
           
            s.close()

            if result == '':
                text = "%s Xtra Mysql change master  Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Xtra Mysql change master Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
            
            self.db.close()    
            return result

        except Exception, e:
            print e.message
            text = "Xtar Mysql change master sys Error %s, the reason is %s!" % (
                datetime.datetime.now(), e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return text
            #return "Xtar Mysql change master Error !"