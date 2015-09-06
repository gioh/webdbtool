#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: db_register.py
# @File_path: D:\my_dba_release_oracle\app\views\db_register.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-08-25 10:46:30


from flask import render_template, Blueprint, g, request, jsonify, session, redirect, url_for
from .. import config
#import copy
#from .. import utils
#from ..utils import judge_is_login

# 加载上级目录到sys.path
import hashlib
import os,sys  
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)


import tools.remote_db_execute as func


#from flask import current_app



bp = Blueprint('db_register', __name__)

@bp.route('/db_register_show', methods=['GET', 'POST'])
@bp.route("/", methods=["GET", "POST"])
def db_register_show():
    """show app,server ,db priv"""
    if (not 'user_id' in session) or (not 'role_id' in session):
        return redirect(url_for('site.login'))

    #if session['role_id'] !=10000:

    #    return redirect(url_for('site.login'))


    #根据角色权限获取对应权限的DB域的列表

    str_sql = '''select A.app_id, B.app_name from T_DB_ROLES A  inner join T_DB_APPS B on A.app_id=B.app_id where A.role_id= %s''' % session['role_id']    
    app_list = g.db.iter(str_sql)
    app_list2 = g.db.iter(str_sql)

    #获取已注册DB列表

    v_db_list_sql = """select A.instance_id, concat(A.ip,':',A.listen_port) as ipport, A.instance_name, B.db_name_en, B.db_name_cn, B.is_cluster, A.inst_id, C.app_name, C.app_manager, D.plat_name, A.create_date from T_DB_INSTANCES A INNER JOIN T_DB_DATABASES B ON A.database_id=B.database_id INNER JOIN T_DB_APPS C ON B.app_id=C.app_id INNER JOIN T_DB_PLATS D ON C.plat_id=D.plat_id  order by A.database_id desc,A.instance_id desc"""
    db_register_list = g.db.iter(v_db_list_sql)
    
    return render_template(
        'db_register/db_register_show.html', 
        app_list=app_list, 
        app_list2=app_list2, 
        db_register_list=db_register_list)



# 注册db语句

@bp.route("/register_execute_cmd", methods=["GET", "POST"])
def register_execute_cmd():
    if request.method == 'POST':
        text_db_ip = request.form['text_db_ip']
        text_db_port = request.form['text_db_port']
        text_db_sid = request.form['text_db_sid']
        text_db_niname = request.form['text_db_niname']
        text_db_master = request.form['text_db_master']
        s_db_type = request.form['s_db_type']
        s_db_inst_cnt = request.form['s_db_inst_cnt']
        belong_app = request.form['belong_app']
        text_app_name = request.form['text_app_name']
        text_app_code = request.form['text_app_code']
        text_app_manager = request.form['text_app_manager']
        product_dept = request.form['product_dept']
        is_new_app = request.form['is_new_app']
        os_oracle_username = request.form['os_oracle_username']
        os_oracle_password = request.form['os_oracle_password']
        app_oracle_username = request.form['app_oracle_username']
        app_oracle_password = request.form['app_oracle_password']

        exe_sql ="""select instance_name,host_name,version,startup_time,status,name,db_unique_name,log_mode,platform_name from v$instance,v$database;"""
        # 远程paramiko调用 在本机执行sql  
        print text_db_ip,os_oracle_username,os_oracle_password,text_db_port,text_db_sid,exe_sql,app_oracle_username,app_oracle_password
        result = func.remote_exe_sql(text_db_ip,os_oracle_username,os_oracle_password,text_db_port,text_db_sid,exe_sql,app_oracle_username,app_oracle_password)

        list_add_db = ''
        print is_new_app
        if result != 'ng' :
            result = '执行成功!'
            result_type = 1

            if is_new_app == '1':
                print text_app_code,text_app_name,text_app_manager,session['user_id'],product_dept;
                v_ins_app_sql = """insert into T_DB_APPS(app_code,app_name,app_manager,state,creator,plat_id) 
                values("%s","%s","%s",%d,%d,%d)""" % (
                    text_app_code,text_app_name,text_app_manager,1,int(session['user_id']),int(product_dept))
                print v_ins_app_sql
                #current_app.logger.info(v_log_sql)
                # 把 exe_sql 中可能包含的%字符串 替换为 %%, 避免因为本身的字符串%格式化倾向，而发生TypeError: not enough arguments for format string 错误
                v_pk_app_id = g.db.execute(v_ins_app_sql.replace('%','%%'))
                belong_app = v_pk_app_id;
            else:
                pass
            v_ins_db_sql = """insert into T_DB_DATABASES(db_name_en,db_unique_name,db_name_cn,db_type,db_version,app_id,is_cluster,is_archivelog,is_dataguard,os_platform,state,creator,db_master)
                        values("%s","%s","%s",%d,"%s",%d,%d,%d,%d,"%s",%d,%d,"%s")""" % (
                        'vv','vv','vv',int(s_db_type),'vv',int(belong_app),0,0,0,'vv',1,session['user_id'],text_db_master)
            v_pk_db_id = g.db.execute(v_ins_db_sql.replace('%','%%'))
            v_ins_inst_sql = """insert into T_DB_INSTANCES(database_id,ip,listen_port,instance_name,is_cluster,inst_id,host_name,instance_version,state,creator,os_oracle_username,os_oracle_password)
                        values(%d,"%s","%s","%s",%d,%d,"%s","%s",%d,%d,"%s","%s")""" % (
                        v_pk_db_id,text_db_ip,text_db_port,text_db_sid,0,1,'vv','vv',1,session['user_id'],os_oracle_username,os_oracle_password)
            v_pk_inst_id = g.db.execute(v_ins_inst_sql.replace('%','%%'))
            # 新增加的log记录返回给前端
            v_reg_add_list_sql = """select A.instance_id, concat(A.ip,':',A.listen_port) as ipport, A.instance_name, B.db_name_en, B.db_name_cn, B.is_cluster, A.inst_id, C.app_name, C.app_manager, D.plat_name, A.create_date from T_DB_INSTANCES A INNER JOIN T_DB_DATABASES B ON A.database_id=B.database_id INNER JOIN T_DB_APPS C ON B.app_id=C.app_id INNER JOIN T_DB_PLATS D ON C.plat_id=D.plat_id and A.instance_id= %d order by A.database_id,A.instance_id """ % (v_pk_inst_id) 
            list_add_db = g.db.query(v_reg_add_list_sql.replace('%','%%'))

        else:
            result = '执行失败!'
            result_type = 2   
                
            print list_add_db

            print  result;

    return jsonify(list_add_db=list_add_db)


#当前已注册DB信息显示 查询过滤

@bp.route("/db_list_get_query", methods=["GET", "POST"])
def db_list_get_query():
    if request.method == 'POST':
        db_type = int(request.form['db_type'])
        app_id = int(request.form['app_list2'])
        db_name_query = request.form['db_name_query']
        ipport_query = request.form['ipport_query']

        if db_type!=0:
            v_db_type_str = ' and B.db_type=%d' % db_type
        else:
            v_db_type_str = ''


        if app_id!=0:
            v_app_id_str = ' and B.app_id=%d' % app_id
        else:
            v_app_id_str = ''


        if db_name_query!='':
            v_db_name_query_str = " and instr(B.db_name_en,'%s')>0" % db_name_query
        else:
            v_db_name_query_str = ''


        if ipport_query!='':
            v_ipport_query_str = " and concat(B.ip,':',B.listen_port)='%s'" % ipport_query
        else:
            v_ipport_query_str = ''


        #获取Mysql DB列表 

        v_db_list_sql = """select A.instance_id, concat(A.ip,':',A.listen_port) as ipport, A.instance_name, B.db_name_en, B.db_name_cn, B.is_cluster, A.inst_id, C.app_name, C.app_manager, D.plat_name, A.create_date from T_DB_INSTANCES A INNER JOIN T_DB_DATABASES B ON A.database_id=B.database_id INNER JOIN T_DB_APPS C ON B.app_id=C.app_id INNER JOIN T_DB_PLATS D ON C.plat_id=D.plat_id where 1=1 %s %s %s %s ORDER by A.database_id,A.instance_id""" % (v_db_type_str,v_app_id_str,v_db_name_query_str,v_ipport_query_str)

        print v_db_list_sql

        db_list = g.db.query(v_db_list_sql)
        

        return jsonify(db_list=db_list)

                     

