#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: remote_shell_cmd.py
# @File_path: E:\开源程序\my_dba_release\app\views\remote_shell_cmd.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-02-28 18:04:09


from flask import render_template, Blueprint, g, request, jsonify, session, redirect, url_for
from .. import config
#import copy
#from .. import utils
#from ..utils import judge_is_login

# 加载上级目录到sys.path

import os,sys  
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)


import tools.remote_db_execute as func


#from flask import current_app



bp = Blueprint('remote_shell_cmd', __name__)

@bp.route('/remote_shell_cmd_show', methods=['GET', 'POST'])
@bp.route("/", methods=["GET", "POST"])
def remote_shell_cmd_show():
    """show app,server ,db priv"""

    if (not 'user_id' in session) or (not 'role_id' in session):
        return redirect(url_for('site.login'))

    if session['role_id'] !=1:

        return redirect(url_for('site.login'))


    #根据角色权限获取对应权限的DB域的列表

    str_sql = 'select b.id,b.name from resources_role_app a,resources_app b where a.app_id = b.id and a.role_id = %s' % session['role_id']
    

    app_list_target = g.db.iter(str_sql)

    
    
    return render_template('remote_shell_cmd/remote_shell_cmd_show.html', app_list_target=app_list_target)

#获取前端下拉列表的server列表信息

@bp.route("/get_server_list", methods=["GET", "POST"])

def get_server_list():
    if request.method == 'POST':
        belong_app = request.form['belong_app']
        
        if belong_app!='':

            #belong_app = int(belong_app)

            
            server_list = g.db.query("SELECT id,ip,port,role from tag where belong_app=" + belong_app + "")
            #server_list = g.db.iter("SELECT id,ip,port,role from tag where is_master=1 and belong_app=" + belong_app + "")
            print server_list
            #print jsonify(server_list=server_list)

            return jsonify(server_list=server_list)


# 执行sql语句

@bp.route("/execute_cmd", methods=["GET", "POST"])
def execute_cmd():
    if request.method == 'POST':

        
        server_id_target = request.form['str_server_id']
        
        
        shell_cmd = request.form['shell_cmd']

        
        if server_id_target!='' and shell_cmd!='':

            server_target = g.db.get("SELECT ip,port,belong_app from tag where id=" + server_id_target + "")


            db_ip_target = server_target['ip']

            #db_port_target = server_target['port']


            belong_app_target = server_target['belong_app']

            os_user = 'apps'


            if belong_app_target ==4 or belong_app_target ==5: #商城erp 开发测试域

                os_password_target = config.OS_APPS_PASSWD_TEST


            else:

                os_password_target = config.OS_APPS_PASSWD

            

            print db_ip_target,os_password_target

            # 远程paramiko调用 在本机执行sql  

            result = func.remote_shell_cmd(db_ip_target,os_user,os_password_target,shell_cmd)

            """
            if result == '':
                result = '执行成功!'
                result_type = 1

            else:

                result_type = 0

            current_app.logger.info(v_log_sql)
            """
            
            print result  #type is list

            if result: #list 不为空

                return_str = ''.join(result) # list to str, then to web front

            else:      # list 为空，但对象存在 

                return_str='执行成功!'

            print return_str

            '''
            if result is None:

                return_str='执行成功!'

            else:


                return_str = ''.join(result) # list to str, then to web front

            '''

            # [u'Filesystem      Size  Used Avail Use% Mounted on\n',....]

           
                

            return return_str

            #return jsonify(result=result)

                     

