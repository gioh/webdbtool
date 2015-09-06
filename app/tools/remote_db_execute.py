#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: remote_db_execute.py
# @File_path: D:\my_dba_release_oracle\app\tools\remote_db_execute.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-08-24 17:45:54


import sys
import datetime
import time
import subprocess
import os
#import MySQLdb
import paramiko
#import check_module
import getpass
import pexpect
from torndb import Connection
import MySQLdb
 
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)

import config

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import os.path
import mimetypes

#import psutil

'''
                   _ooOoo_
                  o8888888o
                  88" . "88
                  (| -_- |)
                  O\  =  /O
               ____/`---'\____
             .'  \\|     |//  `.
            /  \\|||  :  |||//  \
           /  _||||| -:- |||||-  \
           |   | \\\  -  /// |   |
           | \_|  ''\---/''  |   |
           \  .-\__  `-`  ___/-. /
         ___`. .'  /--.--\  `. . __
      ."" '<  `.___\_<|>_/___.'  >'"".
     | | :  `- \`.;`\ _ /`;.`/ - ` : | |
     \  \ `-.   \_ __\ /__ _/   .-` /  /
======`-.____`-.___\_____/___.-`____.-'======
                   `=---='
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
         佛祖保佑       永无BUG
'''


# 检查python 模块是否具备 ，废弃
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

# 发送邮件
def send_mail_to_devs(v_receiver,v_subject,v_msg_text):
    
    msg = MIMEText(v_msg_text,_charset='utf-8')
    msg['Subject'] = v_subject
    #msg['From'] = 'david.ding@corp.globalmarket.com'
    msg['From'] = config.MAIL_DEFAULT_SENDER
    msg['To'] = v_receiver  #逗号隔开的字符串
    #msg['Cc'] = 
    smtp = smtplib.SMTP()
    v_connect='%s:25' % (config.MAIL_SERVER)
    #smtp.connect('smtp.globalmarket.com:25')
    smtp.connect(v_connect)
    #smtp.login('name', 'passwd')
    smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
    #smtp.sendmail('david.ding@corp.globalmarket.com', [v_receiver], msg.as_string())
    smtp.sendmail(config.MAIL_DEFAULT_SENDER, v_receiver.split(','), msg.as_string())
    smtp.quit()
    

    return '发送成功！'

# 发送HTML 邮件,并带附件，有CC对象
def send_html_att_mail_to_devs(v_receiver,v_cc,v_subject,v_msg_text,v_att_path):


    # 构造MIMEMultipart对象做为根容器
    main_msg = MIMEMultipart()

    # 构造MIMEText对象做为邮件显示内容并附加到根容器
    msg = MIMEText(v_msg_text,_charset='utf-8')
    main_msg.attach(msg)

    ## 读入文件内容并格式化 [方式1]－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－  
    data = open(v_att_path, 'rb')  
    ctype,encoding = mimetypes.guess_type(v_att_path)  
    if ctype is None or encoding is not None:  
        ctype = 'application/octet-stream'  
    maintype,subtype = ctype.split('/',1)  
    file_msg = MIMEBase(maintype, subtype)  
    file_msg.set_payload(data.read())  
    data.close( )  
    encoders.encode_base64(file_msg)#把附件编码  
    ''''' 
     测试识别文件类型：mimetypes.guess_type(v_att_path) 
     rar 文件             ctype,encoding值：None None（ini文件、csv文件、apk文件） 
     txt text/plain None 
     py  text/x-python None 
     gif image/gif None 
     png image/x-png None 
     jpg image/pjpeg None 
     pdf application/pdf None 
     doc application/msword None 
     zip application/x-zip-compressed None 
      
    '''  

    ## 设置附件头  
    basename = os.path.basename(v_att_path)  
    file_msg.add_header('Content-Disposition','attachment', filename = basename)#修改邮件头  
    main_msg.attach(file_msg)

    main_msg['Subject'] = v_subject
    main_msg['From'] = config.MAIL_DEFAULT_SENDER
    main_msg['To'] = v_receiver  #逗号隔开的字符串
    main_msg['Cc'] = v_cc
    #main_msg['Date'] = email.Utils.formatdate( )

    smtp = smtplib.SMTP()
    v_connect='%s:25' % (config.MAIL_SERVER)
    smtp.connect(v_connect)
    #smtp.login('name', 'passwd')
    smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)


    #smtp.sendmail('david.ding@corp.globalmarket.com', [v_receiver], msg.as_string())
    smtp.sendmail(config.MAIL_DEFAULT_SENDER, v_receiver.split(','), main_msg.as_string())
    smtp.quit()
    

    return '发送成功！'

# 记录操作日志到/tmp/my_dba_release.log 文件
def log_w(text):
    logfile = "/tmp/oracle_dba_release.log"
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    tt = str(now) + "\t" + str(text) + "\n"
    f = open(logfile, 'a+')
    f.write(tt)
    f.close()

# 根据config.py 里面的SHOW_ENV_TYPE 配置 得到”选择环境“下拉列表的iter
# 1 显示所有，2 仅显示生产环境 3 显示非生产环境（开发、测试等）
def get_env_iter():

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')


    v_show_env_type = config.SHOW_ENV_TYPE

    if v_show_env_type==1:

        v_more_sql = ''

    elif v_show_env_type==2:  #id =3 表示生产环境

        v_more_sql = ' and id=3'

    elif v_show_env_type==3:

        v_more_sql = ' and id!=3'

    else:
        pass

    str_sql = "select id,name from resources_env where 1=1 %s order by id"  % (v_more_sql)
    

    env_list = db.iter(str_sql)

    db.close()

    return env_list

# 根据选择的环境，得到域的下拉列表
def get_domain_list_from_env(v_role_id,belong_env):

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')


    str_sql = '''select b.id,b.name from resources_role_app a,resources_app b where 
    a.app_id = b.id and a.role_id = %d and b.app_type= %d ''' % (v_role_id,belong_env)
        
    

    app_list = db.query(str_sql)

    db.close()

    return app_list

# 把sql语句写入到 /tmp/my_dba_exe_sql.sql 文件中
def sql_to_file(text):
    sql_logfile = "/tmp/my_dba_exe_sql.sql"
    tt = "set pagesize 0 feedback off verify off heading off echo off;\n"+str(text)+"\nexit;"
    f = open(sql_logfile, 'w+')
    #f.write('set pagesize 0 feedback off verify off heading off echo off;')
    f.write(tt)
    #f.write('exit;')
    f.close()

# 把文件推送至远程服务器端cur_prog_shell_cmd
def put_sql_to_remote(v_host,v_os_port,v_os_user,v_os_password,localfile,remotefile):

    
    try:
        t = paramiko.Transport((v_host, v_os_port))
        t.connect(username=v_os_user, password=v_os_password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(localfile, remotefile)
        t.close()

    except Exception, e:
        print e.message
        text = "SFTP connect Error ! Error Reason: %s" % (e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text
         

# 初始化job任务
def initial_dba_job(v_op_user,v_op_comment):

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_add_job_sql = '''insert into dba_jobs(op_user,job_desc) values('%s','%s')''' % (
            v_op_user,v_op_comment)

    v_job_id=db.execute(v_add_job_sql.replace('%','%%'))

    db.close()

    return v_job_id

# 记录job 进程状态
def log_dba_jobs_progress(v_job_id,v_cur_prog_desc,v_cur_cum_prog_desc,v_cur_prog_com_rate):

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_add_job_progress_sql='''insert into dba_job_progress(job_id,cur_prog_desc,cur_cum_prog_desc,cur_prog_com_rate) values(%d,'%s','%s',%d)''' % (
                v_job_id,v_cur_prog_desc,v_cur_cum_prog_desc,v_cur_prog_com_rate)

    db.execute(v_add_job_progress_sql.replace('%','%%'))

    db.close()

# 记录job 进程状态
def log_dba_jobs_progress_r(v_job_id,v_cur_prog_desc,v_cur_cum_prog_desc,v_cur_prog_com_rate):

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_add_job_progress_sql='''insert into dba_job_progress(job_id,cur_prog_desc,cur_cum_prog_desc,cur_prog_com_rate) values(%d,'%s','%s',%d)''' % (
                v_job_id,v_cur_prog_desc,v_cur_cum_prog_desc,v_cur_prog_com_rate)

    v_id=db.execute(v_add_job_progress_sql.replace('%','%%'))

    db.close()

    return v_id

# 完成job，数据库标志状态
def final_dba_job(v_job_id):

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    # 更新job队列状态为完成
    v_update_job_sql = '''update dba_jobs set status=1 where job_id=%d''' % (
        v_job_id)


    db.execute(v_update_job_sql.replace('%','%%'))

    db.close()

# 获取job执行进度
def get_job_status(v_job_id):

    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    v_get_sql = '''SELECT cur_cum_prog_desc,cur_prog_com_rate,cur_prog_shell_cmd from dba_job_progress where id=(select max(id) from dba_job_progress where job_id=%d)''' % (
        v_job_id)

    job_list = db.query(v_get_sql)
            

    db.close()

    return job_list

# 返回数据库db列表清单
def return_db_list(
    v_host,v_os_user,v_os_password,
    v_db_port,
    v_db_user,v_db_pwd,v_type):  # 返回数据库db列表清单

    v_port = 22

    v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'

    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_host, v_port, v_os_user, v_os_password)
        
        # 获取 Target 数据库的数据库列表清单

        if v_type==1:  # 显示完整数据库清单

            conm_db_list = r'''%s/mysql -N -u%s -p'%s' %s -e"show databases"|tr "\n" " "''' % (
            config.mysql_client_path,v_db_user,v_db_pwd,v_db_socket)

        else: # v_type=2 ,排除掉系统数据库,后续把要排除的数据库列表放到一个配置表中

            conm_db_list = r'''%s/mysql -N -u%s -p'%s' %s -e"show databases"|grep -v log|grep -v information_schema|grep -v performance_schema|grep -v mysql|grep -v m2cchina|tr "\n" " "''' % (
            config.mysql_client_path,v_db_user,v_db_pwd,v_db_socket)


        print conm_db_list

        stdin, stdout, stderr = s.exec_command(conm_db_list)

        if stdout.channel.recv_exit_status() ==0:
            #若返回空串可能会报错 list index out of range
            
            #print len(stdout.readlines())
            # print stdout.readlines()
            # v_len = len(stdout.readlines()) 前面管道用一次，再用，就是返回0了,不能用这种方法
            # print v_len
            # if v_len>0:

            #     db_list_str = stdout.readlines()[-1]  #返回值本身就一行

            #     print 'return:' + db_list_str

            # else:

            #     db_list_str=''

            result2 = stdout.readlines()

            if result2: #list 不为空

                db_list_str = ''.join(result2) # list to str, then to web front


            else:      # list 为空，但对象存在 

                db_list_str=''

            text = "%s  Return target db list  Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色

            result = db_list_str  #type is str

            #result = ''.join(db_list_str) # list to str, then to web front

        else:

            result = stderr.readlines()[-1].strip()

            text = "%s %s:%d Return target db list execute Error ! %s " % (datetime.datetime.now(),v_host,v_db_port,result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

            
        s.close()

            
        return result

    except Exception, e:
        print e.message
        text = "%s:%d Return target db list Error ! Error Reason: %s" % (v_host,v_db_port,e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        #return "Return target db list   Error !"
        return text

# 返回某个数据库的Table列表字符串，逗号隔开
def return_table_list(
    v_host,v_os_user,v_os_password,
    v_db_port,
    v_db_user,v_db_pwd,v_db):  # 返回某个数据库的Table列表字符串，逗号隔开

    v_port = 22

    v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'

    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_host, v_port, v_os_user, v_os_password)
        
        # 获取 Target 数据库的数据库列表清单

        

        conm_table_list = r'''%s/mysql -N -u%s -p'%s' %s %s -e"show tables"|tr "\n" ","''' % (
        config.mysql_client_path,v_db_user,v_db_pwd,v_db_socket,v_db)

        

        print conm_table_list

        stdin, stdout, stderr = s.exec_command(conm_table_list)

        if stdout.channel.recv_exit_status() ==0:

            table_list_str = stdout.readlines()[-1]  #返回值本身就一行

            text = "%s  Return target table list  Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色

            result = table_list_str  #type is str

            #result = ''.join(db_list_str) # list to str, then to web front

        else:

            result = stderr.readlines()[-1].strip()

            text = "%s %s:%d Return target table list execute Error ! %s " % (datetime.datetime.now(),v_host,v_db_port,result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

            
        s.close()

            
        return result

    except Exception, e:
        print e.message
        text = "%s:%d Return target table list Error ! Error Reason: %s" % (v_host,v_db_port,e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        #return "Return target table list   Error !"
        return text

# 返回某个数据库的某个参数的值
def return_variables_list(
    v_host,v_os_user,v_os_password,
    v_db_port,
    v_db_user,v_db_pwd,v_variables):  # 返回某个数据库的某个参数的值

    v_port = 22

    v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'

    v_variables='show global variables like \'%s\''%(v_variables)
    print v_variables
    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_host, v_port, v_os_user, v_os_password)
        
        # 获取 Target 数据库的数据库列表清单
    
        

        conm_variables_list = r'''%s/mysql -N -u%s -p'%s' %s %s -e"%s"''' % (
        config.mysql_client_path,v_db_user,v_db_pwd,v_db_socket,v_db_socket,v_variables,)

        

        print conm_variables_list

        stdin, stdout, stderr = s.exec_command(conm_variables_list)
        print stdin
        print stdout
        print stderr
        if stdout.channel.recv_exit_status() ==0:
            
            variables_list_str = stdout.readlines()[-1]  #返回值本身就一行

            text = "%s  Return target variables value  Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
            
            result = variables_list_str  #type is str

            #result = ''.join(db_list_str) # list to str, then to web front

        else:
            print 2
            result = stderr.readlines()[-1].strip()

            text = "%s %s:%d Return target variables value execute Error ! %s " % (datetime.datetime.now(),v_host,v_db_port,result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色

            
        s.close()

            
        return result

    except Exception, e:
        print 3
        print e.message
        text = "%s:%d Return variables value  Error ! Error Reason: %s" % (v_host,v_db_port,e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        #return "Return target table list   Error !"
        return text

# 远程执行sql命令,操作类的，不需要返回结果
def remote_exe_sql(
    v_host,v_os_user,v_os_password,
    v_db_port,v_db_sid,v_exe_sql,
    v_db_user,v_db_pwd):  # 远程执行sql命令,操作类的，不需要返回结果

    text = "%s %s" % (
        datetime.datetime.now(), "Begin execute sql,Please wait ....")
    print "\033[1;32;40m%s\033[0m" % text  # 绿色
    log_w(text)

    v_os_port = 22

    # 把sql语句生成本地文件

    sql_to_file(v_exe_sql)

    localfile = "/tmp/my_dba_exe_sql.sql"

    remotefile = "/tmp/my_dba_exe_sql2.sql"

    # 把sql语句推送到远程服务器

    put_sql_to_remote(v_host,v_os_port,v_os_user,v_os_password,localfile,remotefile)


    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_host, v_os_port, v_os_user, v_os_password)
        #conm = r'''/apps/svr/mysql5/bin/mysql -udba -plocaldba %s %s -e"%s"''' % (
        #    v_db_socket, v_db_name, v_exe_sql)

        #conm = r'''/apps/svr/mysql5/bin/mysql -udba -plocaldba %s %s < %s''' % (
        #    v_db_socket, v_db_name, remotefile)

        conm = r'''export ORACLE_HOME='/opt/oracle/112';$ORACLE_HOME/bin/sqlplus -S -L -R 3 %s/'%s'@//%s:%s/%s @%s''' % (
            v_db_user,v_db_pwd,v_host, v_db_port, v_db_sid,remotefile)

        stdin, stdout, stderr = s.exec_command(conm,timeout=10)

        ok = "ng"
        if stdout.channel.recv_exit_status() ==0: 
            #result = ''
            result = stdout.readlines()[-1].strip()
            print result
            ok = "ok"

        else:

            print stderr.readlines()[-1].strip()

        s.close()

        if ok == "ok":
            text = "%s Call Function:remote_exe_sql Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
        else:
            text = "%s %s:%d Call Function:remote_exe_sql Execute Error ! Error Reason: %s Sql:%s" % (datetime.datetime.now(),v_host,v_db_port,result,v_exe_sql)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色
            
        return ok

    except Exception, e:
        print e.message
        text = "%s:%s Call Function:remote_exe_sql Error ! Error Reason: %s Sql:%s" % (v_host,v_db_port,e.message,v_exe_sql)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        #return "Call remote_exe_sql function Error !"
        return "ng"
        #sys.exit()

# 远程导出DB 权限

def remote_export_db_priv(v_host,v_os_user,v_os_password,
    v_db_port,v_db_user,v_db_pwd,v_pt_str): 

    # v_pt_str 权限导出过滤字符串 
    
    v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'
    
    v_exe_cmd = r'''%s/pt-show-grants -u%s -p'%s' %s --noheader %s''' % (
                config.percona_tool_bin_path,v_db_user,v_db_pwd,v_db_socket, v_pt_str)

    print v_exe_cmd

    # 远程paramiko调用 在本机执行sql  

    result = remote_shell_cmd(v_host,v_os_user,v_os_password,v_exe_cmd)

    print result

    if result: #list 不为空

        return_str = ''.join(result) # list to str, then to web front


    else:      # list 为空，但对象存在 

        return_str=''

    return return_str

# 远程执行Shell命令,需要返回结果

def remote_shell_cmd(v_host,v_os_user,v_os_password,v_exe_cmd):  

    text = "%s %s" % (
        datetime.datetime.now(), "Begin remote execute shell cmd,Please wait ....")
    print "\033[1;32;40m%s\033[0m" % text  # 绿色
    log_w(text)

    v_os_port = 22


    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_host, v_os_port, v_os_user, v_os_password)


        stdin, stdout, stderr = s.exec_command(v_exe_cmd)
        #print stdout.channel.recv_exit_status()

        #print stdout.read
        #print stderr.read
        if stdout.channel.recv_exit_status() ==0:
            #若返回空串可能会报错 list index out of range
            '''
            v_len = len(stdout.readlines())
            print v_len
            if v_len>0:
                print 'aa'
                result = stdout.readlines() # return a list
                print result
            else:
                print 'bb'
                result=[]
            '''
            result = stdout.readlines()
            v_is_success = 1
        else:
            v_is_success = 0
            #result = stderr.readlines()[-1].strip()
            result = stderr.readlines()
            v_error_result = stderr.readlines()[-1].strip()
        s.close()
        if v_is_success == 1:
            text = "%s  Call Function:remote_shell_cmd  Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
        else:          
            text = "%s %s Function:remote_shell_cmd cmd:%s Execute Error ! Error Reason: %s" % (datetime.datetime.now(),v_host,v_exe_cmd,v_error_result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色
            
        return result  # return a list

    except Exception, e:
        print e.message
        text = "%s Call remote_shell_cmd function Error ! cmd:%s Error Reason: %s" % (v_host,v_exe_cmd,e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        #return "Call remote_shell_cmd function Error !"
        return text
        #sys.exit()

# 远程执行Shell命令,不需要返回结果

def remote_shell_cmd_no_result(v_host,v_os_user,v_os_password,v_exe_cmd):  

    print v_host,v_os_user,v_os_password,v_exe_cmd

    text = "%s %s" % (
        datetime.datetime.now(), "Begin remote execute shell cmd,Please wait ....")
    print "\033[1;32;40m%s\033[0m" % text  # 绿色
    log_w(text)

    v_os_port = 22


    try:
        s = paramiko.SSHClient()

        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_host, v_os_port, v_os_user, v_os_password)


        stdin, stdout, stderr = s.exec_command(v_exe_cmd)

        print stdout.channel.recv_exit_status()

        #print stdout.read
        #print stderr.read

        if stdout.channel.recv_exit_status() ==0:

            result = ''

        else:

            result = stderr.readlines()[-1].strip()

        s.close()

        
        if result == '':
            text = "%s Call remote_shell_cmd_no_result function   Execute success !" % datetime.datetime.now()
            log_w(text)
            print "\033[1;32;40m%s\033[0m" % text  # 绿色
        else:
            text = "%s %s Call remote_shell_cmd_no_result function Execute Error ! Error Reason: %s" % (datetime.datetime.now(),v_host,result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色
            
        return result

    except Exception, e:
        print e.message
        text = "%s Call remote_shell_cmd_no_result function Error ! Error Reason: %s" % (v_host,e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        return text
        #sys.exit()
        #

# 远程获取 mysqld_safe my.cnf 配置文件路径

def remote_get_mycnf_path(v_host,v_os_user,v_os_password,
    v_db_port): 

        
    #v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'
    
    v_get_cnf_path_cmd="""ps -ef |grep  mysqld_safe|grep %d|grep -v grep|awk -F "defaults-file=" '{print $2}'""" % (v_db_port)

    print v_get_cnf_path_cmd

    # 远程paramiko调用 在本机执行sql  

    result = remote_shell_cmd(v_host,v_os_user,v_os_password,v_get_cnf_path_cmd)


    if result: #list 不为空

        return_str = ''.join(result) # list to str, then to web front
        return_str = return_str.strip()


    else:      # list 为空，但对象存在 

        return_str=''

    print return_str

    return return_str
   

# 实例开启状态下，远程获取 mysql datadir 文件路径

def remote_on_get_datadir_path(v_host,v_os_user,v_os_password,
    v_db_port): 

        
    #v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'
    
    v_get_datadir_path_cmd="""ps -ef |grep mysqld|grep -v mysqld_safe|grep %d|grep -v grep|awk -F'datadir=' '{print $2}'|awk '{print $1}'""" % (v_db_port)

    print v_get_datadir_path_cmd

    # 远程paramiko调用 在本机执行sql  

    result = remote_shell_cmd(v_host,v_os_user,v_os_password,v_get_datadir_path_cmd)

    if result: #list 不为空

        return_str = ''.join(result) # list to str, then to web front
        return_str = return_str.strip()


    else:      # list 为空，但对象存在 

        return_str=''

    print return_str

    return return_str
    
    
# 实例关闭状态下，远程获取 mysql datadir 文件路径
# v_type=1 返回完整目录 ,v_type =2 返回最后级的目录名

def remote_off_get_datadir_path(v_host,v_db_port,v_type): 

        
    # v_mysql_version 1: mysql5 4:mariadb5 5:mariadb10
    # 
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    # 获得Mysql server 版本: mysql5,mariadb5,mariadb10
    v_get_sql = r'''SELECT case mysql_version when 1 then 'mysql5' when 4 then 'mariadb5' when 5 then 'mariadb10' when 6 then 'percona5.6' when 7 then 'pxc5.6' end mysql_version from tag where ip='%s' and port=%d ''' % (v_host,int(v_db_port))

    v_list = db.get(v_get_sql)

    v_mysql_version = v_list['mysql_version']
            

    db.close()

    # /apps/dbdat/mariadb10_data3306
    # 
    if v_type==1:

        v_datadir_path = '%s/%s_data%s' % (config.mysql_datadir_path,v_mysql_version,v_db_port)

    else:

        v_datadir_path = '%s_data%s' % (v_mysql_version,v_db_port)
    
   
    print v_datadir_path

    
    
    return v_datadir_path


# 远程判断 mysql server 运行状态，启动还是关闭:  0 没有运行, 1 运行

def remote_judge_mysql_status(v_host,v_os_user,v_os_password,
    v_db_port): 

        
    #v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'
    
    v_exe_cmd = r'''ps -ef|grep mysqld_safe|grep %d|grep -v grep |wc -l''' % (v_db_port)

    #v_exe_cmd = r'''ps -ef|grep mysqld_safe|grep %d|grep -v grep''' % (v_db_port)

    print v_exe_cmd

    # 远程paramiko调用 在本机执行sql  

    result = remote_shell_cmd(v_host,v_os_user,v_os_password,v_exe_cmd)

    print result

    return_str = ''.join(result)

    #print return_str

    # 0 没有运行 1 运行

    #result_status = int(return_str.strip())  

    
    return return_str  

# 远程Shutdown mysql server

def remote_shutdown_mysql_server(v_host,v_os_user,v_os_password,
    v_db_port,v_db_root_pwd): 

        
    v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'
    
    v_exe_cmd = r'''%s/mysqladmin -uroot -p'%s' %s  shutdown''' % (
                config.mysql_client_path,v_db_root_pwd,v_db_socket)

    print v_exe_cmd

    # 远程paramiko调用 在本机执行sql  

    result = remote_shell_cmd_no_result(v_host,v_os_user,v_os_password,v_exe_cmd)

    
    return result  #返回空串表示成功

# 远程Start mysql server
# 配置文件的路径确定是根据，在配置中心tag表的mysql_version 字段，
# 'mysql安装版本 1：Mysql5 4：Mariadb5 5：Mariadb10' ,再拼接端口，得到配置文件的名字
# 同理 svr mysql5/mariadb5/mariadb10/ 也是根据mysql_version 来设置
# /apps/svr/mariadb10/bin/mysqld_safe --defaults-file=/apps/conf/mysql/mariadb10_3306.cnf &

def remote_start_mysql_server(v_host,v_os_user,v_os_password,
    v_db_port): 

    # v_mysql_version 1: mysql5 4:mariadb5 5:mariadb10
    # 
    db = Connection('/tmp/mysql3306.sock',
                    config.DB_NAME,
                    config.DB_USER,
                    config.DB_PASSWD,
                    time_zone='+8:00')

    # 获得Mysql server 版本: mysql5,mariadb5,mariadb10
    v_get_sql = r'''SELECT case mysql_version when 1 then 'mysql5' when 4 then 'mariadb5' when 5 then 'mariadb10' when 6 then 'percona5.6' when 7 then 'pxc5.6' end mysql_version from tag where ip='%s' and port=%d ''' % (v_host,int(v_db_port))

    v_list = db.get(v_get_sql)

    v_mysql_version = v_list['mysql_version']
            

    db.close()

            
    #v_db_socket='--socket=/tmp/mysql'+str(v_db_port)+'.sock'
    #nohup 防止paramiko 进程退出后，中断执行
    # 必须要加 1>/dev/null 2>&1,否则命令不执行。可能是paramiko 模式下，不加的话，执行命令时日志无法输出
    
    v_exe_cmd = r'''nohup /apps/svr/%s/bin/mysqld_safe --defaults-file=%s/%s_%d.cnf 1>/dev/null 2>&1 &''' % (
                v_mysql_version,config.mysql_conf_path,v_mysql_version,v_db_port)

    print v_exe_cmd

    # 远程paramiko调用 在本机执行sql  

    result = remote_shell_cmd_no_result(v_host,v_os_user,v_os_password,v_exe_cmd)

    time.sleep(20)   # 等待20秒 mysql 完全启动，更好的方法是，做个循环判断mysql 完全起来了，再退出



    
    return result  #返回空串表示成功

# 远程第三方执行，在另两个server间copy
def remote_exe_scp_bet_two_servers(
    from_host,to_host,
    os_password_source,os_password_target,
    from_file,to_dir): # 远程第三方执行，在另两个server间copy
    
    #ssh = pexpect.spawn('scp -rp root@192.168.1.107:/backup root@192.168.1.102:/data')

    v_scp_str = 'scp -r apps@%s:%s apps@%s:%s' % (from_host,from_file,to_host,to_dir)

    print v_scp_str

    print os_password_source,os_password_target

    ssh = pexpect.spawn(v_scp_str,timeout=None)

    return_str = ''

    try:
        #i = ssh.expect(['Enter password: '])
        i = ssh.expect(['password: ', 'continue connecting (yes/no)?'])  #匹配多个可能的模式
        if i == 0 :                                                      #匹配第一个,直接输入密码
            ssh.sendline(os_password_source)
        elif i == 1:                                                     # 匹配第二个,先提示是否连接
            ssh.sendline('yes')
            ssh.expect('password:')
            ssh.sendline(os_password_source)
        b=ssh.expect(['password: ','continue connecting (yes/no)?'])
        if b==0:
            ssh.sendline(os_password_target)
        elif b==1:
            ssh.sendline('yes')
            ssh.expect('password:')
            ssh.sendline(os_password_target)
    except pexpect.EOF:
        ssh.close()

        return_str = 'scp failure!!'
    else:
        r = ssh.read()
        print r
        ssh.expect(pexpect.EOF)
        ssh.close()
    return return_str

# 远程调用本机的备份脚本,进行数据库备份
def remote_mysql_backup(
    v_from_host,
    v_mysql_port,
    v_os_user,
    v_os_password):

    print v_from_host, v_mysql_port, v_os_user, v_os_password

    v_now = time.strftime("%Y%m%d%H%M%S")

    v_os_port = 22

    text = "%s %s %s:%d" % (
        datetime.datetime.now(), 
        "Begin backup mysql server ,Please wait ....",
        v_from_host, v_mysql_port)
    print "\033[1;32;40m%s\033[0m" % text  # 绿色
    log_w(text)

    v_db_socket='--socket=/tmp/mysql'+str(v_mysql_port)+'.sock'

    try:
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(v_from_host, v_os_port, v_os_user, v_os_password)
       
        conm = r'''sh /apps/sh/mysql/new_backup_mysql.sh %s >> /apps/tmp/dump_mysql%d_%s.log &''' % (
            v_db_socket, v_mysql_port, v_now)

        print conm
        
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
            text = "%s %s:%d Call remote_mysql_backup Execute Error ! Error Reason: %s" % (datetime.datetime.now(),v_from_host,v_mysql_port,result)
            log_w(text)
            print "\033[1;31;40m%s\033[0m" % text  # 古铜色
            
        return result

    except Exception, e:
        print e.message
        text = "%s:%d Mysql backup database Error ! Error Reason: %s" % (v_from_host,v_mysql_port,e.message)
        log_w(text)
        print "\033[1;31;40m%s\033[0m" % text

        #return "Mysql backup database Error !"
        return text

# 连接inception 执行sql
def remote_inception_exe_sql(
    v_host,v_db_port,
    v_db_name,v_exe_sql,v_type):  # type =1 查询模式, type=2 执行模式

    text = "%s %s" % (
        datetime.datetime.now(), "Begin inception execute sql,Please wait ....")
    print "\033[1;32;40m%s\033[0m" % text  # 绿色
    log_w(text)

    v_inception_ip=config.INCEPTION_IP
    v_inception_port=int(config.INCEPTION_PORT)

    v_inception_user=config.DBA_INCEPTION_USER
    v_inception_passwd=config.DBA_INCEPTION_PASSWD

    # --execute=1       --check=1

    # type =1 查询模式, type=2 执行模式

    if v_type==1:
        v_type_str='--check=1;'
    elif v_type==2:
        v_type_str='--execute=1;'
    else:
        pass

    v_sql = r"""/*--host=%s;--port=%d;--user=%s;--password=%s;
    %s*/
    inception_magic_start;
    use %s;
    %s;
    inception_magic_commit;""" %(
        v_host,v_db_port,v_inception_user,v_inception_passwd,v_type_str,v_db_name,v_exe_sql)

    print v_sql

    #result_list=[]
    result_dict={}

    #print v_inception_ip,v_inception_port

    try:
        #conn=MySQLdb.connect(host='127.0.0.1',user='',passwd='',db='',port=6669)
        conn=MySQLdb.connect(host=v_inception_ip,user='',passwd='',db='',port=v_inception_port,charset='utf8')
        cur=conn.cursor()
        ret=cur.execute(v_sql)
        result=cur.fetchall()
        #num_fields = len(cur.description) 
        #field_names = [i[0] for i in cur.description]
        #print field_names
        
        i=0
        for row in result:

            print row[0], "|",row[1],"|",row[2],"|",row[3],"|",row[4],"|",row[5],"|",row[6],"|",row[7],"|",row[8],"|",row[9],"|",row[10]

            i=i+1
            if i==2:  # 等到实际sql处理才逻辑判断，第一条为use DB
                # row[2] = errlevel
                # row[4] = errormessage
                # row[6] = affected_rows
                # row[9] = execute_time
                # row[10] = sqlsha1

                print row[2],row[4]

                
                result_dict['errlevel']=row[2]
                result_dict['errormessage']=row[4]
                result_dict['affected_rows']=row[6]
                result_dict['execute_time']=row[9]
                result_dict['sqlsha1']=row[10]

                #result_list.append(result_dict)


            #print row[0], "|",row[1],"|",row[2],"|",row[3],"|",row[4],"|",row[5],"|",row[6],"|",row[7],"|",row[8],"|",row[9],"|",row[10]
        cur.close()
        conn.close()
    except MySQLdb.Error,e:

        v_error = "inception execute ,Mysql Error %d: %s" % (e.args[0], e.args[1])

        text = "%s %s" % (
            datetime.datetime.now(), v_error)

        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)
        
    return result_dict
    #return result_list



# 连接inception 获取OSC 执行进度
def remote_inception_get_progress(
    v_sqlsha1):  #

    text = "%s %s" % (
        datetime.datetime.now(), "Begin inception get progress,Please wait ....")
    #print "\033[1;32;40m%s\033[0m" % text  # 绿色
    #log_w(text)

    v_inception_ip=config.INCEPTION_IP
    v_inception_port=int(config.INCEPTION_PORT)

    # --execute=1       --check=1

    v_sql = r"""
    inception get osc_percent '%s';

    """ % (v_sqlsha1)

    #print v_sql

    result_list=[]
    result_dict={}

    try:
        #conn=MySQLdb.connect(host='127.0.0.1',user='',passwd='',db='',port=6669)
        conn=MySQLdb.connect(host=v_inception_ip,user='',passwd='',db='',port=v_inception_port,charset='utf8')
        cur=conn.cursor()
        ret=cur.execute(v_sql)
        result=cur.fetchall()
        #num_fields = len(cur.description) 
        #field_names = [i[0] for i in cur.description]
        #print field_names
        
        for row in result:
            
            #result_dict['percent']=row[3]
            result_dict['cur_prog_com_rate']=row[3]
            result_dict['remain_time']=row[4]

            result_list.append(result_dict)


            #print row[0], "|",row[1],"|",row[2],"|",row[3],"|",row[4],"|",row[5],"|",row[6],"|",row[7],"|",row[8],"|",row[9],"|",row[10]
        cur.close()
        conn.close()

        #print result_list

        #return result_dict
        return result_list

    except MySQLdb.Error,e:

        v_error = "inception get progress ,Mysql Error %d: %s" % (e.args[0], e.args[1])

        text = "%s %s" % (
            datetime.datetime.now(), v_error)

        print "\033[1;32;40m%s\033[0m" % text  # 绿色
        log_w(text)

        return ''



