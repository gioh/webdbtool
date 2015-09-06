#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Administrator
# @Date:   2014-06-17 15:04:20
# @Last Modified by:   丁以然
# @Last Modified time: 2015-08-25 19:38:01

import sys
from flask import Flask, request, url_for, g, render_template, session, redirect
from torndb import Connection
#from datetime import timedelta
#import os
#from flask_wtf.csrf import CsrfProtect
#from flask.ext.uploads import configure_uploads
from flask_debugtoolbar import DebugToolbarExtension
#from .utils import get_current_user, get_current_user_role
from . import config

from apscheduler.schedulers.background import BackgroundScheduler


#import chartkick

# convert python's encoding to utf8
reload(sys)
sys.setdefaultencoding('utf8')

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # CSRF protect
    #CsrfProtect(app)

    if app.debug:
        #DebugToolbarExtension(app)
        pass

    from .mails import mail
    mail.init_app(app)

   # register_db(app)
    register_routes(app)
   # register_jinja(app)
    register_error_handle(app)
    register_logger(app)
   # register_uploadsets(app)

    # before every request
  

    @app.before_request
    def connect_db():
        g.db = Connection(config.DB_HOST,
                          config.DB_NAME,
                          config.DB_USER,
                          config.DB_PASSWD,
                          time_zone='+8:00')
    
    @app.after_request
    def close_connection(response):
        g.db.close()
        #g.db2.close()
        return response


    return app




def register_logger(app):
    """Send error log to admin by smtp"""

    import logging
    from logging.handlers import RotatingFileHandler
    from logging import Formatter
    # 1073741824 =1G , backupCount=2 保留2份备份
    handler = RotatingFileHandler('print_track.log', maxBytes=1073741824 , backupCount=2)
    handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    #handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)

    # 在应用程序中添加如下信息
    #app.logger.warning('A warning occurred (%d apples)', 42)
    #app.logger.error('An error occurred')
    #app.logger.info('Info')

    
    #if not app.debug:
    
    from logging.handlers import SMTPHandler
    credentials = (config.MAIL_USERNAME, config.MAIL_PASSWORD)
    mail_handler = SMTPHandler((config.MAIL_SERVER, config.MAIL_PORT),
                               config.MAIL_DEFAULT_SENDER, config.MAIL_ADMIN_ADDR, 'my_dba_release-log',
                               credentials)
    
    mail_handler.setFormatter(Formatter('''
    Message type:       %(levelname)s
    Location:           %(pathname)s:%(lineno)d
    Module:             %(module)s
    Function:           %(funcName)s
    Time:               %(asctime)s

    Message:

    %(message)s
    '''))
    
    mail_handler.setLevel(logging.ERROR)
    #mail_handler.setLevel(logging.INFO)
    app.logger.addHandler(mail_handler)
    

def register_routes(app):
    '''
    from .views import site,dml_ddl,dml_ddl_query,show_orzdba,grant_db_priv,db_migrate
    from .views import build_db_slave,remote_upload,remote_shell_cmd,wssh_webshell,variables_set
    from .views import slow_query,admin,setup_master_slave_map,slow_query_top
    from .views import mysql_web_install,ddl_audit_inyard,dba_audit_inyard,remote_batch_put
    from .views import db_register,process_list,db_weekly_report,auto_increment
    from .views import dml_ddl_inception
    from .views import mysql_schedule_backup
    '''
    from .views import db_register,site,admin
    #from .views import slow_log_setup
    #from .views import dba_jobs

    app.register_blueprint(site.bp, url_prefix='')
    #app.register_blueprint(export.bp, url_prefix='/export')
    '''
    app.register_blueprint(dml_ddl.bp, url_prefix='/dml_ddl')
    app.register_blueprint(dml_ddl_query.bp, url_prefix='/dml_ddl_query')
    app.register_blueprint(show_orzdba.bp, url_prefix='/show_orzdba')
    app.register_blueprint(grant_db_priv.bp, url_prefix='/grant_db_priv')
    app.register_blueprint(db_migrate.bp, url_prefix='/db_migrate')
    app.register_blueprint(build_db_slave.bp, url_prefix='/build_db_slave')
    app.register_blueprint(variables_set.bp, url_prefix='/variables_set')
    app.register_blueprint(remote_upload.bp, url_prefix='/remote_upload')
    app.register_blueprint(remote_shell_cmd.bp, url_prefix='/remote_shell_cmd')
    app.register_blueprint(wssh_webshell.bp, url_prefix='/wssh_webshell')
    app.register_blueprint(slow_query.bp, url_prefix='/slow_query')
    app.register_blueprint(slow_query_top.bp, url_prefix='/slow_query_top')
    app.register_blueprint(mysql_schedule_backup.bp, url_prefix='/mysql_schedule_backup')
    
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(setup_master_slave_map.bp, url_prefix='/setup_master_slave_map')
    app.register_blueprint(mysql_web_install.bp, url_prefix='/mysql_web_install')
    app.register_blueprint(ddl_audit_inyard.bp, url_prefix='/ddl_audit_inyard')
    app.register_blueprint(dba_audit_inyard.bp, url_prefix='/dba_audit_inyard')
    app.register_blueprint(remote_batch_put.bp, url_prefix='/remote_batch_put')
    app.register_blueprint(db_register.bp, url_prefix='/db_register')
    #app.register_blueprint(slow_log_setup.bp, url_prefix='/slow_log_setup')

    app.register_blueprint(process_list.bp, url_prefix='/process_list')
    app.register_blueprint(auto_increment.bp, url_prefix='/auto_increment')
    app.register_blueprint(db_weekly_report.bp, url_prefix='/db_weekly_report')
    app.register_blueprint(dml_ddl_inception.bp, url_prefix='/dml_ddl_inception')
    '''
    app.register_blueprint(db_register.bp, url_prefix='/db_register')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    #app.register_blueprint(dba_jobs.bp, url_prefix='/dba_jobs')
    
    #app.jinja_env.add_extension("chartkick.ext.charts")

    '''
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(topic.bp, url_prefix='/topic')
    app.register_blueprint(dynasty.bp, url_prefix='/dynasty')
    app.register_blueprint(author.bp, url_prefix='/author')
    app.register_blueprint(work.bp, url_prefix='/work')
    app.register_blueprint(user.bp, url_prefix='/user')
    '''


def register_error_handle(app):
    @app.errorhandler(403)
    def page_403(error):
        return render_template('site/403.html'), 403

    @app.errorhandler(404)
    def page_404(error):
        return render_template('site/404.html'), 404

    @app.errorhandler(500)
    def page_500(error):
        return render_template('site/500.html'), 500
    



app = create_app()

'''
def register_uploadsets(app):
    from .uploadsets import workimages
    configure_uploads(app, (workimages))
'''

'''
def register_jinja(app):
    from . import filters

    app.jinja_env.filters['timesince'] = filters.timesince
    app.jinja_env.filters['clean_work'] = filters.clean_work
    app.jinja_env.filters['markdown_work'] = filters.markdown_work
    app.jinja_env.filters['format_year'] = filters.format_year
    app.jinja_env.filters['format_text'] = filters.format_text
    app.jinja_env.filters['is_work_collected'] = filters.is_work_collected
    app.jinja_env.filters['is_work_image_collected'] = filters.is_work_image_collected

    from . import roles, permissions

    # inject vars into template context
    @app.context_processor
    def inject_vars():
        return dict(
            douban_login_url=config.DOUBAN_LOGIN_URL,
            roles=roles,
            permissions=permissions
        )

    # url generator for pagination
    def url_for_other_page(page):
        view_args = request.view_args.copy()
        args = request.args.copy().to_dict()
        args['page'] = page
        view_args.update(args)
        return url_for(request.endpoint, **view_args)

    app.jinja_env.globals['url_for_other_page'] = url_for_other_page





def register_db(app):
    from .models import db
    db.init_app(app)

'''




#app = Flask(__name__)

#app.debug = True

#app.permanent_session_lifetime = timedelta(minutes=5)

#app.secret_key = 'A0Zr98j/3yX R~XHH!LWX/,?'
#app.secret_key = os.urandom(24)

#from app import views

#from app import app



