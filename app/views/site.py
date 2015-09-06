#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project_name: my_dba_release
# @File_name: site.py
# @File_path: D:\my_dba_release_oracle\app\views\site.py
# @Author: 丁以然
# @Email:  dingyiran@szlanyou.com
# @Create_time:   2014-06-17 15:04:21
# @Last Modified by:   丁以然
# @Last Modified time: 2015-09-06 17:38:40


from flask import render_template, Blueprint, redirect, url_for, request, session, g, flash,jsonify
import hashlib
#from ..models import db, Work, WorkImage, WorkReview, Author, Dynasty

bp = Blueprint('site', __name__)


@bp.route('/')
def index():
    """首页"""

    
    if not 'user_id' in session:

        print 'not login'

        #flash(u'请先登录，再执行操作!', 'error')

        #flash(u'请先登录，再执行操作!')

        return redirect(url_for('site.login'))

        #return render_template('dml_ddl/flash_test.html')
    else:
        pass
    #return redirect(url_for('dml_ddl.dml'))
    print 'login'
    str_role_sql = '''SELECT b.role_id,c.role_name_en from T_USER_ROLE_REL b inner join T_DB_ROLES c on b.role_id=c.role_id where b.state=1 and  c.state=1  and b.user_id= %s''' % session['user_id']    
    role_list = g.db.iter(str_role_sql)
    #print role_list.next()
    #return redirect(url_for('db_register.db_register_show'))
    #return render_template('db_register/db_register_show.html')
    str_sql = '''select A.app_id, B.app_name from T_DB_ROLES A  inner join T_DB_APPS B on A.app_id=B.app_id where A.role_id= %s''' % session['role_id']    
    app_list = g.db.iter(str_sql)
    app_list2 = g.db.iter(str_sql)

    #获取已注册DB列表
    print int(session['role_id'])
    v_db_list_sql = """select A.instance_id, concat(A.ip,':',A.listen_port) as ipport, A.instance_name, B.db_name_en, B.db_name_cn, B.is_cluster, A.inst_id, C.app_name, C.app_manager, D.plat_name, A.create_date 
                        from T_DB_INSTANCES A 
                        INNER JOIN T_DB_DATABASES B ON A.database_id=B.database_id 
                        INNER JOIN T_DB_APPS C ON B.app_id=C.app_id 
                        INNER JOIN T_DB_PLATS D ON C.plat_id=D.plat_id 
                        LEFT JOIN T_DB_ROLES E ON C.app_id=(case E.role_type WHEN 3 THEN E.app_id ELSE 0 END)
                        LEFT JOIN T_DB_ROLES F ON D.plat_id=(case E.role_type WHEN 2 THEN E.plat_id ELSE 0 END)
                        where E.role_id=%d or F.role_id=%d
                                order by A.database_id desc,A.instance_id desc"""%(int(session['role_id']),int(session['role_id']) )
    db_register_list = g.db.iter(v_db_list_sql)
    print db_register_list
    return render_template('site/index.html',
        role_list=role_list,
        app_list=app_list,
        app_list2=app_list2,
        db_register_list=db_register_list)

"""
@bp.route('/works', methods=['POST'])
def works():
    '''生成首页需要的作品json数据'''
    works = Work.query.order_by(db.func.rand()).limit(4)
    return render_template('macro/index_works.html', works=works)
"""

@bp.route('/about')
def about():
    """关于页"""
    return render_template('site/about.html')

@bp.route('/logout')
def logout():
    # 如果会话中有用户名就删除它。
    session.pop('user_id', None)
    session.pop('user_name_en', None)
    session.pop('role_id', None)
    #return redirect('site/login.html')
    return render_template('site/login.html')

@bp.route("/login")
def login():

    if not 'user_id' in session:

        print 'not login'

        #flash(u'请先登录，再执行操作!', 'error')

        #flash(u'请先登录，再执行操作!')

        error = u'请先登录，再执行操作!'

    else:

        error = None

    print error

    return render_template('site/login.html', error=error)

@bp.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['password']

        #print passwd
        
        if username!='' and passwd!='':
            e = hashlib.md5()
            e.update(passwd)
            _pwd = e.hexdigest()

            #print _pwd
            newsitems = g.db.get("select a.user_id,a.user_name_en,b.role_id,c.role_name_en from T_DB_USERS a inner join  T_USER_ROLE_REL b on a.user_id=b.user_id inner join T_DB_ROLES c on b.role_id=c.role_id where a.state=1 AND b.state=1 and  c.state=1 and b.is_default=1 and user_name_en='" + username + "' and password='" + _pwd + "'")
            print newsitems
            if newsitems is None:

                
                success = 'false';
                print success

                return success

            else:

                success = 'true';

                print success

                session['user_id'] = newsitems['user_id']
                session['user_name_en'] = newsitems['user_name_en']
                session['role_id'] = newsitems['role_id']
                session['role_name_en'] = newsitems['role_name_en']
                return success


    return render_template('site/login.html')


@bp.route("/switch_role", methods=["GET", "POST"])
def switch_role():
    switch_role_name=''
    if request.method == 'POST':
        current_role = request.form['current_role']
        print session['role_id']
        session['role_id'] = int(current_role)
        print session['role_id']
        str_role_sql = '''select c.role_name_en from T_DB_ROLES c where  c.state=1  and c.role_id= %s''' % session['role_id']    
        role_name_en = g.db.get(str_role_sql)
        session['role_name_en'] = role_name_en['role_name_en']
        switch_role_name = session['role_name_en']
        print switch_role_name

        str_sql = '''select A.app_id, B.app_name from T_DB_ROLES A  inner join T_DB_APPS B on A.app_id=B.app_id where A.role_id= %s''' % session['role_id']    
        app_list2 = g.db.query(str_sql)

        #获取已注册DB列表
        print int(session['role_id'])
        v_db_list_sql = """select A.instance_id, concat(A.ip,':',A.listen_port) as ipport, A.instance_name, B.db_name_en, B.db_name_cn, B.is_cluster, A.inst_id, C.app_name, C.app_manager, D.plat_name, A.create_date 
                            from T_DB_INSTANCES A 
                            INNER JOIN T_DB_DATABASES B ON A.database_id=B.database_id 
                            INNER JOIN T_DB_APPS C ON B.app_id=C.app_id 
                            INNER JOIN T_DB_PLATS D ON C.plat_id=D.plat_id 
                            LEFT JOIN T_DB_ROLES E ON C.app_id=(case E.role_type WHEN 3 THEN E.app_id ELSE 0 END)
                            LEFT JOIN T_DB_ROLES F ON D.plat_id=(case E.role_type WHEN 2 THEN E.plat_id ELSE 0 END)
                            where E.role_id=%d or F.role_id=%d
                                    order by A.database_id desc,A.instance_id desc"""%(int(session['role_id']),int(session['role_id']) )
        db_register_list = g.db.query(v_db_list_sql)
        print db_register_list

    return jsonify(switch_role_name=switch_role_name,
        app_list2=app_list2,
        db_register_list=db_register_list)


@bp.route("/init_role_list", methods=["GET", "POST"])
def init_role_list():
    str_role_sql = '''select b.role_id,c.role_name_en from T_USER_ROLE_REL b inner join T_DB_ROLES c on b.role_id=c.role_id where b.state=1 and  c.state=1  and b.user_id= %s''' % session['user_id']    
    role_list = g.db.query(str_role_sql)
    #print role_list.next()
    #return redirect(url_for('db_register.db_register_show'))
    #return render_template('db_register/db_register_show.html')
    return jsonify(role_list=role_list)
