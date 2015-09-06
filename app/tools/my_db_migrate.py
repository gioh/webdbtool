#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: my_db_migrate.py
# @File_path: E:\SVN\邓文通\数据建模和迁移\02_配置开发\02_数据库管理工具201501批次\my_dba_release\app\tools\my_db_migrate.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-05-13 11:06:46


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
        db_user_pwd_source,db_user_pwd_target, db_port_source, db_port_target, dumpdb,
        db_user_name,os_user,v_table,to_db_name):
    
        self.from_host = from_host
        self.to_host = to_host
        self.os_user = os_user
        #self.os_user = 'apps'
        #self.db_user_name = 'dba'
        self.db_user_name = db_user_name
        self.os_password_source = os_password_source
        self.os_password_target = os_password_target
        self.db_user_pwd_source = db_user_pwd_source
        self.db_user_pwd_target = db_user_pwd_target
        self.port = 22
        self.db_port_source = db_port_source
        self.db_port_target = db_port_target
        self.dumpdb = dumpdb
        self.today = datetime.date.today().strftime("%Y%m%d")
        self.v_table= v_table
        self.to_db_name = to_db_name
        self.db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    
    def export_database(self,v_prosess_id):  # 导出远程主机的数据库
        text = "%s %s" % (
            datetime.datetime.now(), "Export master Database,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_source)+'.sock'

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.from_host, self.port, self.os_user, self.os_password_source)
            

            #conm = r'''/apps/svr/mysql5/bin/mysqldump -u%s -p'%s' %s -B %s > /apps/bak_db_%s.sql''' % (
            #    self.db_user_name,self.db_user_pwd_source,v_db_socket, self.dumpdb, self.today)
            
            # 若导出类型为数据库，则v_table变量为空串 
            # -B 去掉 ，导出多个数据库才用
            if self.v_table=='':  #导出数据库

                # conm = r'''%s/mysqldump --single-transaction --opt -u%s -p'%s' %s -B %s> /apps/bak_db_%s.sql;bzip2 -f /apps/bak_db_%s.sql''' % (
                #     config.mysql_client_path,self.db_user_name,self.db_user_pwd_source,v_db_socket, self.dumpdb, self.today, self.today)
                conm_1 = r'''%s/mysqldump --single-transaction --opt -u%s %s -B %s> /apps/bak_db_%s.sql''' % (
                    config.mysql_client_path,self.db_user_name,v_db_socket, self.dumpdb, self.today)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm_1
                print v_update_sql
                self.db.execute(v_update_sql)
                print '1111'
                conm = r'''%s/mysqldump --single-transaction --opt -u%s -p'%s' %s -B %s> /apps/bak_db_%s.sql''' % (
                    config.mysql_client_path,self.db_user_name,self.db_user_pwd_source,v_db_socket, self.dumpdb, self.today)
            else:
                # conm = r'''%s/mysqldump --single-transaction --opt -u%s -p'%s' %s  %s %s> /apps/bak_db_%s.sql;bzip2 -f /apps/bak_db_%s.sql''' % (
                #     config.mysql_client_path,self.db_user_name,self.db_user_pwd_source,v_db_socket, self.dumpdb, self.v_table, self.today, self.today)
                conm_1 = r'''%s/mysqldump --single-transaction --opt -u%s %s  %s %s> /apps/bak_db_%s.sql''' % (
                    config.mysql_client_path,self.db_user_name,v_db_socket, self.dumpdb, self.v_table, self.today)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm_1
                print v_update_sql
                self.db.execute(v_update_sql)

                print '1111'
                conm = r'''%s/mysqldump --single-transaction --opt -u%s -p'%s' %s  %s %s> /apps/bak_db_%s.sql''' % (
                    config.mysql_client_path,self.db_user_name,self.db_user_pwd_source,v_db_socket, self.dumpdb, self.v_table, self.today)

            print conm
            
            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                #print 'status Error Status:'+

                result = stderr.readlines()[-1].strip()

            s.close()

            if result == '':
                text = "%s    Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Execute Error ! %s " % (datetime.datetime.now(),result)
                log_w(text)
                print "\033[1;31;40m%s\033[0m" % text  # 古铜色
                
            return result

        except Exception, e:
            print e.message
            text = "Dump database from source  Error ! Error Reason: %s" % (e.message)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text

            return "Dump database from source  Error !"
            #sys.exit()

    def scp_bet_two_servers(self,v_prosess_id): # 远程第三方执行，在另两个server间copy

        text = "%s %s" % (
            datetime.datetime.now(), "Scp between two servers,Please wait ....")
        print "\033[1;32;40m%s\033[0m" % text  # 绿色

        log_w(text)

        from_file = '/apps/bak_db_%s.sql' % self.today
        #from_file = '/apps/bak_db_%s.sql.bz2' % self.today


        to_dir = '/apps'
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
            text = "%s    Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
        else:
            text = "%s Execute Error ! %s" % (datetime.datetime.now(),r)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

        return r


    def import_data(self,v_prosess_id):  # 导入数据库到目标机器

        text = "%s %s" % (
            datetime.datetime.now(), "Import master database,Please wait ....")

        log_w(text)
        print "\033[1;32;40m%s\033[0m" % text

        v_db_socket='--socket=/tmp/mysql'+str(self.db_port_target)+'.sock'

        
        dir = '/apps/'
        db = 'bak_db_%s.sql' % self.today
        #db_bz2 = dir + 'bak_db_%s.sql.bz2' % self.today

        try:
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(self.to_host, self.port, self.os_user, self.os_password_target)

            #conm = r'''/apps/svr/mysql5/bin/mysql -u%s -p'%s' %s  < %s%s''' % (
            #    self.db_user_name,self.db_user_pwd_target,v_db_socket, dir, db)
            
            if self.v_table=='':  #导出数据库

                # conm = r'''bzip2 -d -f %s;%s/mysql -u%s -p'%s' %s  < %s%s''' % (
                #     db_bz2,config.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket, dir, db)
                conm_1 =  r'''%s/mysql -u%s %s  < %s%s''' % (
                    config.mysql_client_path,self.db_user_name,v_db_socket, dir, db)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm = r'''%s/mysql -u%s -p'%s' %s  < %s%s''' % (
                    config.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket, dir, db)
            else:

                # conm = r'''bzip2 -d -f %s;%s/mysql -u%s -p'%s' %s %s < %s%s''' % (
                #     db_bz2,config.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket,self.to_db_name, dir, db)
                conm_1 =  r'''%s/mysql -u%s %s %s < %s%s''' % (
                    config.mysql_client_path,self.db_user_name,v_db_socket,self.to_db_name, dir, db)
                v_update_sql = '''update dba_job_progress set cur_prog_shell_cmd = ' ''' + conm_1 +''' ' where id= '''+ str(v_prosess_id)
                print conm_1
                print v_update_sql
                self.db.execute(v_update_sql)

                conm = r'''%s/mysql -u%s -p'%s' %s %s < %s%s''' % (
                    config.mysql_client_path,self.db_user_name,self.db_user_pwd_target,v_db_socket,self.to_db_name, dir, db)


            stdin, stdout, stderr = s.exec_command(conm)

            if stdout.channel.recv_exit_status() ==0:

                result = ''

            else:

                result = stderr.readlines()[-1].strip()
           
            s.close()

            if result == '':
                text = "%s    Execute success !" % datetime.datetime.now()
                log_w(text)
                print "\033[1;32;40m%s\033[0m" % text  # 绿色
            else:
                text = "%s Execute Error ! %s " % (datetime.datetime.now(),result)
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
"""
    def down_back(self):  # 备份文件copy到本地
        local_dir = '/tmp/'
        remote_dir = '/tmp/'
        try:
            t = paramiko.Transport((self.host, self.port))
            t.connect(username=self.user, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)
            files = sftp.listdir(remote_dir)
            text = "Download back file,Please wait ...."
            log_w(text)

            text = '    Beginning to download file  from %s  %s ' % (
                self.host, datetime.datetime.now())
            print "\033[1;32;40m%s\033[0m" % text
            log_w(text)

            for f in files:
                if f.find('bak_db_' + self.today) != -1:
                    text = "        Downloading file:%s:%s" % (
                        self.host, os.path.join(remote_dir, f))
                    log_w(text)
                    print text
                    sftp.get(
                        os.path.join(remote_dir, f), os.path.join(local_dir, f))
                    # sftp.put(os.path.join(local_dir,f),os.path.join(remote_dir,f))
            t.close()
            text = '    Download All back file success %s ' % datetime.datetime.now(
            )
            log_w(text)
            print text
        except Exception, e:
            print e.message
            text = "SFTP connect Error !"
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text
            sys.exit()

"""

"""


if __name__ == "__main__":

    # find_ip()
    check_module('MySQLdb')
    check_module('paramiko')
    import MySQLdb
    import paramiko
    master_ip = raw_input('Enter :Master_eth1_ip :')
    #master_pass = raw_input('Enter :Master OS Pass :')
    master_pass = getpass.getpass('Enter :Master OS Pass :')
    export_db = raw_input('Enter :Export db list,space seperate:')
    boss = Database(master_ip, master_pass, export_db)
    # boss.check_mysql()
    boss.export_database()
    boss.down_back()
    # boss.unbz2()
    boss.import_data()
    # boss.restart_mysql()
    # boss.slave_start()

"""
