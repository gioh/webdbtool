#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: admin.py
# @File_path: D:\my_dba_release_oracle\app\views\admin.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-08-26 15:39:10



from flask import render_template, Blueprint, g, request, jsonify, session, redirect, url_for
#from .. import config

import hashlib

#import copy
#from .. import utils
#from ..utils import judge_is_login

# 加载上级目录到sys.path

import os,sys  
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  
sys.path.insert(0,parentdir)


import tools.remote_db_execute as func


#from flask import current_app



bp = Blueprint('admin', __name__)

@bp.route('/admin_show', methods=['GET', 'POST'])
@bp.route("/", methods=["GET", "POST"])
def admin_show():
    """show app,server ,db priv"""

    if (not 'user_id' in session) or (not 'role_id' in session):
        return redirect(url_for('site.login'))

    #if session['role_id'] !=1:
    #    return redirect(url_for('site.login'))

    # Role表格显示
    str_role_sql = '''select a.role_id,a.role_name_en,a.role_name_cn,a.priority,a.create_date,CASE a.role_type WHEN 1 THEN 'root_role' WHEN 2 THEN 'plat_role' WHEN 3 THEN 'app_role' END as role_type,
                    IFNULL((select concat(app_code,':',app_name) from T_DB_APPS where app_id=IFNULL(a.app_id,0)),0) as app_info,
                    IFNULL((select concat(plat_code,':',plat_name) from T_DB_PLATS where plat_id=IFNULL(a.plat_id,0)),0) as plat_info
                    from T_DB_ROLES a'''
    
    role_list = g.db.iter(str_role_sql)
    s_role_list = g.db.iter(str_role_sql)
    #print role_list.next()
    #print role_list.next()
    #print role_list.next()

    # 所有项目展示
    str_app_sql = '''select B.app_id, B.app_name from  T_DB_APPS B where state=1'''  
    app_list = g.db.iter(str_app_sql)
    
    str_user_sql = '''select x.*,y.default_role from 
                    (
                    select a.user_id,a.user_name_en,a.user_name_ch,a.email,a.create_date,
                    (select concat(plat_code,':',plat_name) from T_DB_PLATS where plat_id=a.dept_id) as dept_name,
                    group_concat(c.role_name_en order by c.role_id SEPARATOR '\\n') as role_info
                    from T_DB_USERS a inner join T_USER_ROLE_REL b on a.user_id=b.user_id
                    inner join T_DB_ROLES c on b.role_id=c.role_id where a.state=1 and b.state=1 and  c.state=1
                    group by a.user_id,a.user_name_en,a.user_name_ch,a.email
                    )x,
                    (
                     select a.user_id,c.role_name_en as default_role from T_DB_USERS a inner join T_USER_ROLE_REL b on a.user_id=b.user_id
                    inner join T_DB_ROLES c on b.role_id=c.role_id where a.state=1 and b.state=1 and  c.state=1
                    and b.is_default=1
                    )y 
                    where x.user_id=y.user_id'''
    user_list = g.db.iter(str_user_sql)
       
    return render_template(
        'admin/admin_manage.html', 
        d_role_list=role_list,
        s_role_list=s_role_list,
        app_list=app_list,
        d_user_list=user_list)



# 添加角色

@bp.route("/add_role", methods=["GET", "POST"])
def add_role():
    if request.method == 'POST':      
        str_role_name = request.form['str_role_name']      
        str_role_desc = request.form['str_role_desc']
        s_role_type = request.form['s_role_type']
        s_belong_app = request.form['s_belong_app']
        s_product_dept = request.form['s_product_dept']     
        if str_role_name!='' and str_role_desc!='':
            v_exe_sql = "insert into T_DB_ROLES(role_name_en,role_name_cn,role_type,app_id,plat_id,priority,state,creator) values('%s','%s','%s','%s','%s',%d,%d,%d)" %(
                str_role_name,str_role_desc,s_role_type,s_belong_app,s_product_dept,10,1,10000)
            print v_exe_sql
            v_pk_id = g.db.execute(v_exe_sql)
            str_sql = '''select a.role_id,a.role_name_en,a.role_name_cn,a.priority,a.create_date,CASE a.role_type WHEN 1 THEN 'root_role' WHEN 2 THEN 'plat_role' WHEN 3 THEN 'app_role' END as role_type,
                        IFNULL((select concat(app_code,':',app_name) from T_DB_APPS where app_id=IFNULL(a.app_id,0)),0) as app_info,
                        IFNULL((select concat(plat_code,':',plat_name) from T_DB_PLATS where plat_id=IFNULL(a.plat_id,0)),0) as plat_info
                        from T_DB_ROLES a where a.role_id=%d''' % v_pk_id   
            new_role_list = g.db.query(str_sql)
            return jsonify(new_role_list=new_role_list)



# 添加平台访问用户
@bp.route("/add_user", methods=["GET", "POST"])
def add_user():
    if request.method == 'POST':    

        print 'aa'

        s_user_name = request.form['s_user_name']  
        print 'a1'
        s_user_name_cn = request.form['s_user_name_cn']
        print 'a2'
        s_user_pass = request.form['s_user_pass']
        print 'a3'
        s_role_default = request.form['s_role_default']
        print 'a4'
        s_email = request.form['s_email']
        print 'a5'
        s_dept = request.form['s_dept']
        print 'bb'
        #得到md5密码
        e = hashlib.md5()
        e.update(s_user_pass)
        _pwd = e.hexdigest()
       
        #_s_role_default = int(s_role_default)
     
        if s_user_name!='' and s_user_pass!='':
            v_exe_user_sql = "insert into T_DB_USERS(user_name_en,user_name_ch,password,email,dept_id,state,creator) values('%s','%s','%s','%s',%d,%d,%d)" %(
                s_user_name,s_user_name_cn,_pwd,s_email,int(s_dept),1,10000)
            print v_exe_user_sql
            v_pk_user_id = g.db.execute(v_exe_user_sql)
            

            v_exe_user_role_rel_sql = "insert into T_USER_ROLE_REL(user_id,role_id,state,is_default,creator) values(%d,%d,%d,%d,%d)" %(
            v_pk_user_id,int(s_role_default),1,1,10000)
            v_pk_user_role_rel_id = g.db.execute(v_exe_user_role_rel_sql)

            v_new_user_list = '''select x.*,y.default_role from 
                    (
                    select a.user_id,a.user_name_en,a.user_name_ch,a.email,a.create_date,
                    (select concat(plat_code,':',plat_name) from T_DB_PLATS where plat_id=a.dept_id) as dept_name,
                    group_concat(c.role_name_en order by c.role_id) as role_info
                    from T_DB_USERS a inner join T_USER_ROLE_REL b on a.user_id=b.user_id
                    inner join T_DB_ROLES c on b.role_id=c.role_id where a.state=1 and b.state=1 and  c.state=1
                    group by a.user_id,a.user_name_en,a.user_name_ch,a.email
                    )x,
                    (
                     select a.user_id,c.role_name_en as default_role from T_DB_USERS a inner join T_USER_ROLE_REL b on a.user_id=b.user_id
                    inner join T_DB_ROLES c on b.role_id=c.role_id where a.state=1 and b.state=1 and  c.state=1
                    and b.is_default=1
                    )y 
                    where x.user_id=y.user_id and x.user_id=%d''' % v_pk_user_id
            new_user_list = g.db.query(v_new_user_list)
            print v_pk_user_id
            print v_new_user_list
            print new_user_list
            return jsonify(new_user_list=new_user_list)
                 

# 可选用户角色关系(分配角色)
@bp.route("/list_assign_role", methods=["GET", "POST"])
def list_assign_role():
    if request.method == 'POST':    
        s_assign_user_name = request.form['s_assign_user_name']
        v_exe_user_sql = '''select count(*) as cnt from T_DB_USERS where user_name_en='%s' '''%(s_assign_user_name)
        is_user = g.db.get(v_exe_user_sql)
        if is_user['cnt']!=0:
            v_list_assign_role = '''select x.role_id,x.role_name_en,x.role_name_cn
                                    FROM T_DB_ROLES x
                                    WHERE role_type!=1 and NOT EXISTS(
                                    SELECT 1
                                    FROM T_USER_ROLE_REL a,T_DB_USERS b
                                    WHERE a.user_id=b.user_id AND b.user_name_en='%s' AND a.role_id=x.role_id)'''%(s_assign_user_name)
            s_list_assign_role = g.db.query(v_list_assign_role)
        else:
            s_list_assign_role =''

    return jsonify(s_list_assign_role=s_list_assign_role)


#用户角色分配
@bp.route("/assign_user_role", methods=["GET", "POST"])
def assign_user_role():
    if request.method == 'POST':    
        s_assign_user_name = request.form['s_assign_user_name']
        s_assign_user_role = request.form['s_assign_user_role']
        v_exe_user_sql = '''select user_id from T_DB_USERS where user_name_en='%s' '''%(s_assign_user_name)
        is_user = g.db.get(v_exe_user_sql)
        if is_user:
            v_exe_user_role_rel_sql = "insert into T_USER_ROLE_REL(user_id,role_id,state,is_default,creator) values(%d,%d,%d,%d,%d)" %(
            is_user['user_id'],int(s_assign_user_role),1,0,10000)
            v_pk_user_role_rel_id = g.db.execute(v_exe_user_role_rel_sql)
        else:
            v_pk_user_role_rel_id =''

    return jsonify(v_pk_user_role_rel_id=v_pk_user_role_rel_id)